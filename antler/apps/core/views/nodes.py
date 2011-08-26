try:
    import json
except ImportError:
    import simplejson as json

from django import http
from django.http import Http404
from django.template import RequestContext
from django.db import models
from django.views.generic.base import TemplateView, View
from django.template.loader import render_to_string
from django.template.defaultfilters import slugify
from core.models import Person, Concept, Event, Object, Story, Edge
from django.shortcuts import HttpResponseRedirect as Redirect, get_object_or_404
import random


class NodeView(TemplateView):
    template_name = 'nodes/show.html'

    node_separation = 45

    def model_name(self):
        return self.model._meta.object_name.lower()

    def get_context_data(self, slug):
        instance = get_object_or_404(self.model, slug=slug)

        try:
            story_slug = self.request.GET.get('story')
            story = Story.objects.get(slug=story_slug)
            if story in instance.stories():
                story.set_current_node(instance)
            else:
                story = None
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

        return {
            "subject": instance,
            "incoming": instance.incoming().by_verb(),
            "outgoing": instance.outgoing().by_verb(),
            "story": story,
            "map": self._prepare_story_map(instance,story)
        }

    def _prepare_story_map(self, instance, story):
        nodes,edges, secondary_nodes, secondary_edges = self.story_node_map(story)

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
                    pos = self._calculate_position(last_node, node, keys[0])
                    label = group.get("label")
                    if label == None:
                        label = keys[0]
                    marks.append({
                        "label": label,
                        "position": pos
                    })
                keys = keys[1:]
                group = groups[keys[0]]
            node.position = self.node_separation * i
            node.horizontal_position = 0
            group.get("nodes").append(node)
            last_node = node
            i += 1

        # After we have collected all the main story nodes (and thus know
        # where the speration) we can position the other forks
        for node in nodes:
            other_nodes,other_edges = self.other_story_links(node, story)

            if len(other_nodes) == 0:
                continue
            node.forks = { "nodes": other_nodes, "edges": other_edges }

            for other_node in other_nodes:
                # We want to find the two nodes in the mainline on either side of other_node to work out its position
                try:
                    before,after = self._get_bracketing_nodes(other_node, nodes)
                    other_node.position = self._calculate_position(before, after, other_node.timeline_date)
                except:
                    # import traceback
                    # traceback.print_exc()
                    if nodes[-1].timeline_date <= other_node.timeline_date:
                        other_node.position = node.position + 2*self.node_separation
                    else:
                        other_node.position = node.position - self.node_separation


        # Put the other_edges in first so that the main story node is the right color
        # edges = other_edges.union(edges)
        return {
            "nodes": nodes,
            "edges": edges,
            "marks": marks,
            "century_grouped_nodes": groups,
        }

    def _calculate_position(self, before, after, timeline_date):
        since = timeline_date - before.timeline_date
        diff = after.timeline_date - before.timeline_date
        return before.position + (since / float(diff)) * self.node_separation


    # TODO: hadle cases where target is outside the range in nodes
    def _get_bracketing_nodes(self, target, nodes):
        prev = None
        for node in nodes:
            if not prev:
                prev = node
                continue
            if prev.timeline_date <= target.timeline_date and target.timeline_date <= node.timeline_date:
                return prev,node
            prev = node
        raise "Couldn't find bracketing nodes"

    def story_node_map(self, story):
        nodes = set()
        edges = set()
        secondary_nodes = set()
        secondary_edges = set()
        for edge in Edge.objects.filter(story=story, verb=("primary")):
            if edge.verb == "primary":
                node = edge.object
                node.story = edge.story
                nodes.add(node)

                node = edge.subject
                node.story = edge.story
                nodes.add(node)

                edges.add(edge)
            else:
                secondary_nodes.add(edge.subject)
                secondary_nodes.add(edge.object)
                secondary_edges.add(edge)

        # Sort them
        nodes = sorted(nodes, key=lambda node: node.timeline_date)
        secondary_nodes = sorted(nodes, key=lambda node: node.timeline_date)
        return nodes,edges,secondary_nodes,secondary_edges

    def other_story_links(self, instance, story):
        edges = set()
        nodes = set()
        type_str = Edge._type_string_from_model(instance)
        outgoing = Edge.objects.filter(verb="primary", subject_id=instance.id, subject_type=type_str).exclude(story=story)
        second_out = Edge.objects.filter(verb="secondary", subject_id=instance.id, subject_type=type_str, story=story)
        incoming = Edge.objects.filter(verb="primary", object_id=instance.id, object_type=type_str).exclude(story=story)
        second_in = Edge.objects.filter(verb="secondary", object_id=instance.id, object_type=type_str, story=story)

        outgoing = outgoing or second_out
        incoming = incoming or second_in

        for edge in outgoing:
            node = edge.object
            node.horizontal_position = -self.node_separation
            node.story = edge.story

            nodes.add(node)
            edges.add(edge)

        for edge in incoming:
            # The incoming links kink the wrong way on the map. Reversing the link fixes this. We do it in the view
            edge.incoming = True

            node = edge.subject
            node.horizontal_position = self.node_separation
            node.story = edge.story
            nodes.add(node)
            edges.add(edge)
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


class NodeJsonView(NodeView):
    def get(self, request, type, slug):
        # Attempt to find the requested model instance
        try:
            self.model = models.get_model("core", type)
            instance = get_object_or_404(self.model, slug=slug)
            status_code = 200
        except AttributeError:
            status_code = 404

        # Attempt to find the story
        try:
            story_slug = request.GET.get("story")
            story = Story.objects.get(slug=story_slug)
        except Story.DoesNotExist:
            story = None

        title = instance.name
        if story:
            title = "%s in %s" % (
                title,
                story.name,
            )

        # Set up the payload
        payload = {
            "storySlug": story_slug,
            "nodeType": type,
            "nodeSlug": slug,
            "objectId": slugify(instance),
            "title": title,
            "map_node": instance.select_tuple[0],
            "html": render_to_string(
                'nodes/_node_content.html',
                RequestContext(request, self.get_context_data(slug)),
            )
        }

        # Return a JSON payload
        response = http.HttpResponse(
            json.dumps(payload),
            mimetype="application/json",
        )
        response.status_code = status_code
        return response

