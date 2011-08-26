from django.http import Http404
from django.views.generic.base import TemplateView, View
from core.models import Person, Concept, Event, Object, Story, Edge
from django.shortcuts import HttpResponseRedirect as Redirect, get_object_or_404
import random


class NodeView(TemplateView):
    template_name = 'nodes/show.html'

    def model_name(self):
        return self.model._meta.object_name.lower()
    
    def get_context_data(self, slug):
        instance = get_object_or_404(self.model, slug=slug)

        try:
            story_slug = self.request.GET.get('story')
            story = Story.objects.get(slug=story_slug)
            story.set_current_node(instance)
        except Story.DoesNotExist:
            story = None

        outgoing_primary = instance.outgoing('primary')
        story_next = outgoing_primary.filter(story=story).follow()
        if len(story_next) > 0:
            story_next = story_next[0]

        incoming_primary = instance.incoming('primary')
        story_prev = incoming_primary.filter(story=story).follow()
        if len(story_prev) > 0:
            story_prev = story_prev[0]

        nodes,edges = self.story_node_map(story)

        # Group the nodes by century(ish) for <noscript> output
        #
        # The groups we want are:
        groups = {
           -4000: { "label": ' ', "nodes": [], "display_mark": False },
               0: { "label": 'BC/BCE', "nodes": [] },
            1000: { "nodes": [] },
            1200: { "nodes": [] },
            1600: { "nodes": [] },
            1700: { "nodes": [] },
            1800: { "nodes": [] },
            1900: { "nodes": [] },
            9999: { "nodes": [] },
        }

        keys = sorted(groups.keys())
        group = groups[keys[0]]
        marks = []
        i = 0
        node_separation = 45
        last_node = None
        for node in nodes:
            while len(keys) and node.timeline_date > keys[0]:
                if last_node and group.get("display_mark") != False:

                    if not len(group.get("nodes")):
                        marks.pop()
                    since = keys[0] - last_node.timeline_date
                    diff = node.timeline_date - last_node.timeline_date
                    pos = last_node.position + (since / float(diff)) * node_separation
                    label = group.get("label")
                    if label == None:
                        label = keys[0]
                    marks.append({
                        "label": label,
                        "position": pos
                    })
                keys = keys[1:]
                group = groups[keys[0]]
            node.position = node_separation * i
            group.get("nodes").append(node)
            last_node = node
            i += 1

        return {
            "subject": instance,
            "incoming": instance.incoming().by_verb(),
            "outgoing": instance.outgoing().by_verb(),
            "story": story,
            "map_nodes": nodes,
            "map_edges": edges,
            "map_marks": marks,
            "century_grouped_nodes": groups,
        }

    def story_node_map(self, story):
        nodes = set()
        edges = set()
        for edge in Edge.objects.filter(story=story):
            nodes.add(edge.subject)
            nodes.add(edge.object)
            edges.add(edge)
        # Sort them
        nodes = sorted(nodes, key=lambda node: node.timeline_date)
        return nodes,edges



class PersonView(NodeView):
    model = Person

        
class EventView(NodeView):
    model = Event

        
class ConceptView(NodeView):
    model = Concept


class ObjectView(NodeView):
    model = Object


class NodeIndexView(TemplateView):
    template_name = 'nodes/index.html'

    def get_context_data(self):
        return {
            'people': Person.objects.order_by('timeline_date'),
            'events': Event.objects.order_by('timeline_date'),
            'concepts': Concept.objects.order_by('timeline_date'),
            'objects': Object.objects.order_by('timeline_date'),
        }

class RandomNodeView(View):
    
    def get(self, request):
        # Pick a node type from those available
        node_classes = [model for model in [Person, Concept, Event, Object]
                        if model.objects.exists()]
        if not node_classes:
            raise Http404
        node_class = random.choice(node_classes)
        
        node = node_class.objects.order_by("?")[0]
        return Redirect( node.url() )
