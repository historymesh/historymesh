import pprint
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
            "nodes": engine.nodes,
        }


class LayoutImage(View):

    width = 500
    height = 300
    start_date = 1880
    end_date = 2020

    def transform(self, node):
        x = (node.timeline_date - self.start_date) / float(self.end_date - self.start_date) * self.width
        y = (self.height / 2) + (self.engine.node_position(node) * 100)
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
        # Strings. Stored by first node.
        self.strings = {}
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
            self.strings[string[0]] = string

    def position_strings(self):
        """
        Goes through the strings and lays them out along the
        non-time axis.
        """
        # Start with only the earliest-starting string
        sorted_strings = deque(sorted(
            map(deque, self.strings.values()),
            key = lambda string: string[0].timeline_date,
        ))
        # First pass: work out all dates for the ends of the strings
        string_dates = [
            (
                string[0].timeline_date,
                string[-1].timeline_date,
                string[0],
            )
            for string in sorted_strings
        ]
        # Second pass: work out the horizontal positions
        self.maximum_offset = 0
        self.positions = {}
        for node in self.nodes:
            # Work out which strings are around at this point
            visible_strings = [
                start_node
                for start, end, start_node in string_dates
                if (
                    start <= node.timeline_date and
                    end >= node.timeline_date
                )
            ]
            # Work out its string
            for start_node, string in self.strings.items():
                if node in string:
                    break
            # Save that position
            self.positions[node] = visible_strings.index(start_node) - (
                (len(visible_strings)-1) / 2.0
            )
            self.maximum_offset = max(
                self.maximum_offset,
                abs(self.positions[node]),
            )

    def node_position(self, node):
        return self.positions[node]
        
    def visible_edges(self):
        for edge_set in self.edges_by_subject.values():
            for edge in edge_set:
                yield edge
