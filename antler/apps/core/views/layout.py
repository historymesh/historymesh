import pprint
from django.http import HttpResponse
from core.models import Edge, Node


def layout_view(request):
    nodes = NodeLayoutEngine().lay_out()
    return HttpResponse(("%r" % nodes).replace("<", "&lt;"))


class NodeLayoutEngine(object):
    """
    Lays out nodes in a rough time-like order.
    """

    max_per_era = 6
    era_sizes = [1, 5, 10, 50, 100, 500, 1000]

    def lay_out(self):
        # First, fetch a list of all the nodes
        self.load_nodes()
        # Then, march down the nodes grouping them into
        # rounded historical eras.
        self.decide_eras()
        # Return the layout
        return {}

    def load_nodes(self):
        """
        Fetches all of the nodes in date order.
        """
        # Fetch all of the nodes into a list (partially sorted)
        self.nodes = []
        for node_class in Node.all_child_classes():
            self.nodes.extend(
                node_class.objects.filter(
                    timeline_date__isnull = False,
                ).order_by("timeline_date")
            )
        # Finish sorting them
        self.nodes.sort(key=lambda node: node.timeline_date)

    def year_to_era(self, year, era_size):
        return year // era_size * era_size

    def decide_eras(self):
        """
        Goes down the list of nodes and decides what historical
        eras to use for grouping.
        """
        # Go through the nodes and bucket them by all possible era
        # sizes.
        buckets = dict((era_size, {}) for era_size in self.era_sizes)
        for node in self.nodes:
            for era_size in self.era_sizes:
                era = self.year_to_era(node.timeline_date.year, era_size)
                buckets[era_size].setdefault(era, []).append(node)
        pprint.pprint(buckets)
        # Go through the possible buckets and pick the ones that are
        # closest to the optimal size
        earliest = min(buckets[1].keys())
        latest = max(buckets[1].keys())
        boundaries = []
        current = earliest
        while current <= latest:
            # Find the best-sized era
            for era_size in reversed(sorted(self.era_sizes)):
                # Work out the size this bucket would be
                era = self.year_to_era(current, era_size)
                bucket_size = len(buckets[era_size][era])
                # If it's available, and best, use it
                if bucket_size < self.max_per_era and \
                   (not buckets or buckets[-1] < era):
                    break
            boundaries.append(era)
        pprint.pprint(boundaries)

