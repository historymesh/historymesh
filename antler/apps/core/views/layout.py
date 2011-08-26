import math
import pprint
import random
from cStringIO import StringIO
from collections import deque
from django.http import HttpResponse
from django.views.generic import TemplateView, View
from core.models import Edge, Node


class MapView(TemplateView):

    template_name = "map.html"

    def get_context_data(self):
        engine = NodeLayoutEngine()
        engine.lay_out()
        return {
            "next":  self.request.GET.get('next'),
            "story": self.request.GET.get('story'),
            "nodes": list(engine.annotated_nodes()),
            "edges": list(engine.visible_edges()),
        }


class LayoutView(TemplateView):

    template_name = "layout_test.html"

    def get_context_data(self):
        engine = NodeLayoutEngine()
        engine.lay_out()
        return {
            "strings": list(engine.strings),
            "nodes": list(engine.annotated_nodes()),
            "edges": list(engine.visible_edges()),
        }


class LayoutImage(View):

    width = 500
    height = 300

    def transform(self, node):
        start_date = self.engine.horizontal_start
        end_date = self.engine.horizontal_end
        x = (self.engine.node_horizontal_position(node) - start_date) / float(end_date - start_date) * self.width
        y = (self.height / 2) + (self.engine.node_position(node) * 1)
        return x, y

    def get(self, request):
        import tempfile
        import cairo
        # Make a blank surface
        surface = cairo.ImageSurface(cairo.FORMAT_ARGB32, self.width, self.height)
        ctx = cairo.Context(surface)
        ctx.set_source_rgb(.9, .9, .9)
        ctx.paint()
        self.engine = NodeLayoutEngine()
        self.engine.lay_out()
        # Paint on the links
        ctx.set_source_rgb(1, 0, 0)
        for edge in self.engine.visible_edges():
            x1, y1 = self.transform(edge.subject)
            x2, y2 = self.transform(edge.object)
            ctx.move_to(x1, y1)
            ctx.line_to(x2, y2)
            ctx.stroke()
        # Paint on the nodes
        ctx.set_source_rgb(0, 0, 0)
        ctx.stroke()
        for node in self.engine.nodes:
            x, y = self.transform(node)
            ctx.rectangle(x-5, y-5, 10, 10)
            ctx.fill()
        # Return the image
        sio = StringIO()
        surface.write_to_png(sio)
        return HttpResponse(sio.getvalue(), mimetype="image/png")



class NodeLayoutEngine(object):
    """
    Lays out nodes in a rough time-like order.
    """

    iterations_crossover_only = 20
    iterations_both = 100
    iterations_repulsion = 100

    repulsion_factor = 0.1 # Range 0..1
    repulsion_min_distance = 3
    repulsion_max_distance = 100

    attraction_factor = 0 # Range 0..1
    attraction_min_distance = 35
    attraction_max_distance = 100

    slowdown_factor = 1

    vertical_separation = 60

    # How strong the push to get even angles should be; range 0..1
    # Hint; it seems to be a good idea for this to be at least as strong as the
    # repulsion factor, or it gets overpowered in awkward situations.
    angle_factor = 0.2

    # How strong a push to make to fix crossovers
    crossover_factor = 0.5

    # Minimum distance to use when calculating crossover pushes
    crossover_min = 20

    # Stop iterating if the total movement is less than this.
    minimum_total_movement = 0.1

    max_node_distance = 5
    horizontal_scale_factor = 5

    def lay_out(self):
        # First, fetch a list of all the nodes
        self.load_nodes()
        self.construct_strings()
        self.position_strings()

    def do_if_shown(self, function, node):
        """
        Runs the function with node as argument if node is visible on the map
        """
        if not node.hidden_in_map:
            function(node)

    def load_nodes(self):
        """
        Fetches all of the nodes in date order.
        """
        # Fetch all of the nodes into a list (partially sorted)
        self.nodes = set()
        self.edges = set()
        for edge in Edge.objects.filter(story__isnull=False):
            self.do_if_shown(self.nodes.add, edge.subject)
            self.do_if_shown(self.nodes.add, edge.object)
            self.edges.add(edge)
        # Sort them
        self.nodes = sorted(self.nodes, key=lambda node: node.timeline_date)
        if len(self.nodes) == 0:
            return

        self.horizontal_positions = {}

        # Rewrite dates to enforce min and max separation.
        last_node = self.nodes[0]
        self.horizontal_positions[last_node] = 0
        for node in self.nodes[1:]:
            delta = node.timeline_date - last_node.timeline_date
            delta = min(delta, self.max_node_distance)
            delta *= self.horizontal_scale_factor
            self.horizontal_positions[node] = \
                self.horizontal_positions[last_node] + delta
            last_node = node

        self.horizontal_start = 0
        self.horizontal_end = self.horizontal_positions[last_node]

    def construct_strings(self):
        """
        Works out the strings of single-pathed nodes.

        A string is a group of nodes that form a singly-linked
        path. The string ends whenever a node has more than one
        successor; that node is included as the end of the string,
        and the successors form the start of new strings.
        """
        # Strings.
        self.strings = set()
        # Queue-based string processor
        queue = deque()
        edges = list(self.edges)
        self.edges_by_subject = {}
        self.edges_by_object = {}
        for edge in edges:
            if not (edge.subject.hidden_in_map or edge.object.hidden_in_map):
                self.edges_by_subject.setdefault(edge.subject, []).append(edge)
                self.edges_by_object.setdefault(edge.object, []).append(edge)
        # Start with all nodes with no incoming edges
        for node in set(self.nodes) - set(self.edges_by_object):
            queue.append(node)
        # Process!
        while queue:
            node = queue.popleft()
            # Start a new string, follow it till it splits
            string = [node]
            while True:
                # If there's one outgoing edge and the node at the
                # end of the edge only has one incoming edge,
                # continue the string
                outgoing_edges = self.edges_by_subject.get(node, [])
                if len(outgoing_edges) == 1:
                    node = self.edges_by_subject[node][0].object
                    if not node.hidden_in_map:
                        if len(self.edges_by_object.get(node, [])) != 1:
                            queue.append(node)
                            break
                        else:
                            string.append(node)
                # If there's none, stop here.
                elif len(outgoing_edges) == 0:
                    break
                # If there's 2 or more, add them to the queue
                else:
                    for edge in outgoing_edges:
                        self.do_if_shown(queue.append, edge.object)
                    break
            # Save the string
            self.strings.add(String(self, string))
        # Second phase: assign neighbouring strings
        self.string_edges = set()
        for string in self.strings:
            string.left_strings = []
            string.right_strings = []
            for other_string in self.strings:
                for edge in self.edges_by_object.get(string.first, []):
                    if edge.subject in other_string:
                        string.left_strings.append(other_string)
                        self.string_edges.add(StringEdge(other_string, string))
                for edge in self.edges_by_subject.get(string.last, []):
                    if edge.object in other_string:
                        string.right_strings.append(other_string)
                        self.string_edges.add(StringEdge(string, other_string))
        #print string, string.left_strings, string.right_strings
        #print self.string_edges

    def init_forces(self):
        forces = {}
        for string in self.strings:
            forces[string] = 0
        return forces

    def position_strings(self):
        """
        Goes through the strings and lays them out along the
        non-time axis.
        """
        for i in range(self.iterations_crossover_only):
            forces = self.init_forces()
            self.set_forces_from_overlaps(forces, i)
            if not self.apply_forces(forces, i):
                break

        for i in range(self.iterations_both):
            forces = self.init_forces()
            self.set_forces_from_connections(forces, i, self.iterations_both)
            self.set_forces_from_overlaps(forces, i)
            if not self.apply_forces(forces, i):
                break

        for i in range(self.iterations_repulsion):
            forces = self.init_forces()
            self.set_forces_from_connections(forces, i, self.iterations_both)
            if not self.apply_forces(forces, i):
                break

    def set_forces_from_connections(self, forces, i, iterations):
        # Work out slowdown/friction multiplier
        slowdown = (1 - (1.0/iterations) * i)

        for string in self.strings:
            # First, find all other strings that overlap us
            overlapping_strings = [
                other_string
                for other_string in self.strings
                if (
                    string != other_string and 
                    string.overlaps(other_string)
                )
            ]
            # Then, work out the repulsion for each
            for other_string in overlapping_strings:
                if string.position < other_string.position:
                    direction = -1
                else:
                    direction = 1
                sub_force = (
                    self.calculate_repulsion(string, other_string) -
                    self.calculate_attraction(string, other_string)
                ) * direction 
                forces[string] += sub_force * slowdown
            # Now, run the angle solver
            number_left_strings = len(string.left_strings)
            number_right_strings = len(string.right_strings)
            if number_left_strings > 1:
                delta = (
                    self.vertical_separation *
                    0.5 *
                    math.tan(
                        math.pi / (float(number_left_strings * 2))
                    )
                )
                left_strings = sorted(
                    string.left_strings,
                    key = lambda string: string.position,
                )
                for j, other_string in enumerate(left_strings):
                    number_deltas = (
                        (j * 2) -
                        (number_left_strings - 1)
                    )
                    target_position = (
                        string.position +
                        (delta * number_deltas)
                    )
                    offset = target_position - other_string.position
                    forces[other_string] += (
                        offset * self.angle_factor * slowdown
                    )
            if number_right_strings > 1:
                delta = (
                    self.vertical_separation *
                    0.5 *
                    math.tan(
                        math.pi / (float(number_right_strings * 2))
                    )
                )
                right_strings = sorted(
                    string.right_strings,
                    key = lambda string: string.position,
                )
                for j, other_string in enumerate(right_strings):
                    number_deltas = (
                        (j * 2) -
                        (number_right_strings - 1)
                    )
                    target_position = (
                        string.position +
                        (delta * number_deltas)
                    )
                    offset = target_position - other_string.position
                    forces[other_string] += (
                        offset * self.angle_factor * slowdown
                    )

    def set_forces_from_overlaps(self, forces, i):
        for edge in self.string_edges:
            # Look for crossovers on the left.
            for other_edge in self.string_edges:
                if other_edge == edge:
                    continue
                if not other_edge.overlaps(edge):
                    continue
                if edge.crosses(other_edge):
                    print "Pushing to fix crossover of %s %s" % (
                        edge, other_edge)
                    self.push_to_resolve_crossing(forces, edge, other_edge)

            for string in self.strings:
                if edge.crosses(string):
                    print "Pushing to fix crossover of %s %s" % (
                        edge, string)
                    self.push_to_resolve_crossing(forces, edge, string)

    def apply_forces(self, forces, i):
        """USE THE FORCE

        """
        moved = sum(map(abs, forces.values()))
        print "Iteration %i: Moved %s" % (i, moved)
        for string in self.strings:
            string.position += forces[string]
        return moved >= self.minimum_total_movement

    def push_to_resolve_crossing(self, forces, edge, other_edge):
        left_diff = abs(other_edge.start_position - edge.start_position)
        right_diff = abs(other_edge.end_position - edge.end_position)

        if left_diff < right_diff:
            # Push left hand strings to crossover
            push = max(abs(edge.start_position - other_edge.start_position),
                       self.crossover_min) * self.crossover_factor
            if edge.start_position < other_edge.start_position:
                forces[edge.left] += push
                forces[other_edge.left] += -push
            else:
                forces[edge.left] += -push
                forces[other_edge.left] += push
        else:
            # Push right hand strings to crossover
            push = max(abs(edge.end_position - other_edge.end_position),
                       self.crossover_min) * self.crossover_factor
            if edge.end_position < other_edge.end_position:
                forces[edge.right] += push
                forces[other_edge.right] += -push
            else:
                forces[edge.right] += -push
                forces[other_edge.right] += push

    def set_forces_to_flip(self, forces, edge):
        """Set the forces on the strings at each end of an edge to push towards
        flipping the gradient of the edge.

        """
        diff = edge.end_position - edge.start_position
        push = (min(abs(diff), self.crossover_min)) * self.crossover_factor
        if diff < 0:
            forces[edge.left] = -push
            forces[edge.right] = +push
        else:
            forces[edge.left] = push
            forces[edge.right] = -push
                
    def calculate_repulsion(self, string, other):
        distance = abs(string.position - other.position)
        distance = float(max(
            min(
                distance,
                self.repulsion_max_distance
            ),
            self.repulsion_min_distance,
        ))
        return ((
            self.repulsion_max_distance / distance
        ) - 1) * self.repulsion_factor

    def calculate_attraction(self, string, other):
        distance = abs(string.position - other.position)
        distance = max(
            min(
                distance,
                self.attraction_max_distance
            ),
            self.attraction_min_distance,
        )
        distance -= self.attraction_min_distance
        return distance * self.attraction_factor

    def node_position(self, node):
        for string in self.strings:
            if node in string:
                return string.position

    def node_horizontal_position(self, node):
        return self.horizontal_positions[node]

    def annotated_nodes(self):
        for node in self.nodes:
            node.position = self.node_position(node)
            node.horizontal_position = self.node_horizontal_position(node)
            yield node
        
    def visible_edges(self):
        for edge_set in self.edges_by_subject.values():
            for edge in edge_set:
                yield edge


class String(object):

    def __init__(self, engine, nodes):
        assert nodes, "Strings must contain at least one node"
        self.engine = engine
        self.nodes = tuple(
            sorted(nodes, key=lambda node: engine.node_horizontal_position(node))
        )
        # seed random generator based on number of strings so far
        gen = random.Random(x=len(engine.strings))
        self.position = gen.random() * 70
        print "Initialpos %s for %r" % (self.position, self)
    
    @property
    def start(self):
        return self.engine.node_horizontal_position(self.first)
    
    @property
    def end(self):
        return self.engine.node_horizontal_position(self.last)

    @property
    def start_position(self):
        return self.position

    @property
    def end_position(self):
        return self.position

    @property
    def left(self):
        return self

    @property
    def right(self):
        return self

    @property
    def first(self):
        return self.nodes[0]
    
    @property
    def last(self):
        return self.nodes[-1]

    def __eq__(self, other):
        return self.nodes == other.nodes
    
    def __hash__(self):
        return hash(self.nodes)

    def __contains__(self, item):
        return item in self.nodes
    
    def overlaps(self, other):
        return (
            not (self.start > other.end + 0.5) and
            not (other.start > self.end + 0.5)
        )

    def __repr__(self):
        return "<String: %s %r>" % (self.position, self.nodes)


class StringEdge(object):
    """ An edge between two strings."""

    def __init__(self, left, right):
        """left and right are the strings on the left and right"""
        self.left = left
        self.right = right
    
    @property
    def start(self):
        """ The start date of the edge. """
        return self.left.end

    @property
    def end(self):
        """ The end date of the edge. """
        return self.right.start

    @property
    def start_position(self):
        return self.left.position

    @property
    def end_position(self):
        return self.right.position

    def __eq__(self, other):
        return self.left == other.left and self.right == other.right
    
    def __hash__(self):
        return hash((self.left, self.right))

    def overlaps(self, other):
        """Return true iff the edge overlaps or nearly overlaps with the time range given."""
        return (
            not (self.start >= other.end) and
            not (other.start >= self.end)
        )

    def crosses(self, other):
        """Check if the edge crosses other.

        Returns None if the edge doesn't cross the other edge.

        Returns 

        """
        if self.end == self.start or other.end == other.start:
            # Any degenerate edges where start == end can't be crossovers.
            return
        if (
            self.start_position == other.start_position or
            self.end_position == other.end_position
        ):
            # If both edges start or end at the same height, can't be a
            # crossover.
            return


        #print "Checking crossover of %s and %s" % (self, other)

        a0 = self.start_position
        a1 = self.end_position
        a_grad = (a1 - a0) / float(self.end - self.start)
        b0 = other.start_position
        b1 = other.end_position
        b_grad = (b1 - b0) / float(other.end - other.start)
        overlap_start = max(self.start, other.start)
        overlap_end = min(self.end, other.end)

        if overlap_start >= overlap_end:
            return False

        #print "OVERLAP from %d to %d ((%f, %f)-(%f, %f) and (%f, %f)-(%f, %f))" % (
        #    overlap_start, overlap_end,
        #    self.start, a0,
        #    self.end, a1,
        #    other.start, b0,
        #    other.end, b1,
        #)

        a_start = a0 + a_grad * (overlap_start - self.start)
        b_start = b0 + b_grad * (overlap_start - other.start)

        a_end = a0 + a_grad * (overlap_end - self.start)
        b_end = b0 + b_grad * (overlap_end - other.start)

        #print "a_start: %f, a_end: %f, b_start: %f, b_end: %f" % (
        #    a_start, a_end, b_start, b_end,
        #)

        if (
            (a_start < b_start and a_end > b_end) or
            (a_start > b_start and a_end < b_end)
        ):
            print "Found crossover of %s and %s" % (self, other)
        return (
            (a_start < b_start and a_end > b_end) or
            (a_start > b_start and a_end < b_end)
        )

    def __repr__(self):
        return "<StringEdge: %s %s %s %s>" % (
                                              self.start,
                                              self.start_position,
                                              self.end,
                                              self.end_position,
                                             )
