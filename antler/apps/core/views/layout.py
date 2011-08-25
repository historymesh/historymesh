import math
import pprint
import random
from cStringIO import StringIO
from collections import deque
from django.http import HttpResponse
from django.views.generic import TemplateView, View
from core.models import Edge, Node

class LayoutView(TemplateView):

    template_name = "layout_test.html"

    def get_context_data(self):
        engine = NodeLayoutEngine()
        engine.lay_out()
        return {
            "strings": engine.strings,
            "nodes": engine.annotated_nodes(),
        }


class LayoutImage(View):

    width = 500
    height = 300
    start_date = 1880
    end_date = 2020

    def transform(self, node):
        x = (node.timeline_date - self.start_date) / float(self.end_date - self.start_date) * self.width
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
        iterations = request.GET.get('iterations')
        if iterations is not None:
            iterations = int(iterations)
        self.engine = NodeLayoutEngine(iterations)
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

    iterations = 3

    repulsion_factor = 0.5 # Range 0..1
    repulsion_min_distance = 3
    repulsion_max_distance = 25

    attraction_factor = 0.5 # Range 0..1
    attraction_min_distance = 35
    attraction_max_distance = 100

    slowdown_factor = 1

    vertical_separation = 30

    angle_factor = 0.1

    def __init__(self, iterations=None):
        if iterations is not None:
            self.iterations = iterations

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
        # Sort them
        self.nodes = sorted(self.nodes, key=lambda node: node.timeline_date)

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
        edges = list(Edge.objects.filter(story__isnull=False))
        self.edges_by_subject = {}
        self.edges_by_object = {}
        for edge in edges:
            self.do_if_shown(
                lambda node: self.edges_by_subject.setdefault(node, []).append(edge),
                edge.subject,
            )
            self.do_if_shown(
                lambda node: self.edges_by_object.setdefault(node, []).append(edge),
                edge.object,
            )
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
            self.strings.add(String(string))
        # Second phase: assign neighbouring strings
        for string in self.strings:
            string.left_strings = []
            string.right_strings = []
            for other_string in self.strings:
                for edge in self.edges_by_object.get(string.first, []):
                    if edge.subject in other_string:
                        string.left_strings.append(other_string)
                for edge in self.edges_by_subject.get(string.last, []):
                    if edge.object in other_string:
                        string.right_strings.append(other_string)
            print string, string.left_strings, string.right_strings

    def position_strings(self):
        """
        Goes through the strings and lays them out along the
        non-time axis.
        """
        for i in range(self.iterations):
            forces = {}
            # First pass: calculate forces
            for string in self.strings:
                forces[string] = 0
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
                    forces[string] += sub_force
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
                           offset * self.angle_factor
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
                           offset * self.angle_factor
                        )

            # Work out slowdown/friction multiplier
            slowdown = (1 - (1.0/self.iterations) * i)
            # Second pass: USE THE FORCE
            moved = sum(map(abs, forces.values())) * slowdown
            print "Iteration %i: Moved %s, %s" % (i, moved, slowdown)
            for string in self.strings:
                string.position += forces[string] * slowdown 
                
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

    def annotated_nodes(self):
        for node in self.nodes:
            node.position = self.node_position(node)
            yield node
        
    def visible_edges(self):
        for edge_set in self.edges_by_subject.values():
            for edge in edge_set:
                yield edge


class String(object):

    def __init__(self, nodes):
        assert nodes, "Strings must contain at least one node"
        self.nodes = tuple(
            sorted(nodes, key=lambda node: node.timeline_date)
        )
        gen = random.Random(x=hash(self.nodes))
        self.position = gen.random() * 70
    
    @property
    def start(self):
        return self.first.timeline_date
    
    @property
    def end(self):
        return self.last.timeline_date

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
        return "<String: %r>" % repr(self.nodes)
