import pprint
from collections import deque
from django.http import HttpResponse
from core.models import Edge, Node


def layout_view(request):
    nodes = NodeLayoutEngine().lay_out()
    return HttpResponse(("%r" % (nodes,)).replace("<", "&lt;"))


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
        # Return the layout
        return self.nodes, self.strings

    def load_nodes(self):
        """
        Fetches all of the nodes in date order.
        """
        # Fetch all of the nodes into a list (partially sorted)
        self.nodes = set()
        for edge in Edge.objects.filter(story__isnull=False):
            self.nodes.add(edge.subject)
            self.nodes.add(edge.object)
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
        for edge in edges:
            edges_by_subject.setdefault(edge.subject, []).append(edge)
        # Start with all nodes with no incoming edges
        for node in set(self.nodes) - set(edge.object for edge in edges):
            queue.append(node)
        # Process!
        while queue:
            node = queue.popleft()
            # Start a new string, follow it till it splits
            string = [node]
            while True:
                # If there's one outgoing edge, continue the string
                if len(edges_by_subject[node]) == 1:
                    node = edges_by_subject[node][0].object
                    string.append(node)
                # If there's none, stop here.
                elif len(edges_by_subject[node]) == 0:
                    break
                # If there's 2 or more, add them to the queue
                else:
                    for other_node in edges_by_subject[node]:
                        queue.append(other_node)
                    break
            # Save the string
            self.strings[string[0]] = string

    def decide_eras(self):
        """
        Goes down the list of nodes and decides what historical
        eras to use for grouping.
        """
        
