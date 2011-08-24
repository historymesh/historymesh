import pprint
from collections import deque
from django.http import HttpResponse
from django.views.generic import TemplateView
from core.models import Edge, Node

class LayoutView(TemplateView):

    template_name = "layout_test.html"

    def get_context_data(self):
        return {"strings": NodeLayoutEngine().lay_out()}


class NodeLayoutEngine(object):
    """
    Lays out nodes in a rough time-like order.
    """

    min_per_era = 3
    era_sizes = [1, 5, 10, 50, 100, 500, 1000]

    def lay_out(self):
        # First, fetch a list of all the nodes
        self.load_nodes()
        self.construct_strings()
        self.position_strings()
        # Return the layout
        return self.strings

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
        edges_by_subject = {}
        edges_by_object = {}
        for edge in edges:
            self.do_if_shown(
                lambda node: edges_by_subject.setdefault(node, []).append(edge),
                edge.subject,
            )
            self.do_if_shown(
                lambda node: edges_by_object.setdefault(node, []).append(edge),
                edge.object,
            )
        # Start with all nodes with no incoming edges
        for node in set(self.nodes) - set(edges_by_object):
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
                outgoing_edges = edges_by_subject.get(node, [])
                if len(outgoing_edges) == 1:
                    node = edges_by_subject[node][0].object
                    if not node.hidden_in_map:
                        if len(edges_by_object.get(node, [])) != 1:
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
        future_strings = deque(sorted(
            list(self.strings.values()),
            key = lambda string: string[0].timeline_date,
        ))
        active_strings = [future_strings.popleft()]
        # First pass: march through the data, storing what strings
        # are in each one
        start_date = datetime.
        while active_strings:
            # Pop the lowest
            pass

        
