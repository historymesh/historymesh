from django.db import models
from django.db.models.query import QuerySet
from django.core.urlresolvers import reverse
from django.template.defaultfilters import slugify
from django.db.models.signals import pre_save
import urlparse

def generate_slug_as_needed(sender, instance, **kwargs):
    """
    Set the slug based on the name for a given instance if it has
    both a slug and a name field.
    """
    try:
        if instance.name and instance.slug == '':
            instance.slug = slugify(instance.name)
    except AttributeError:
        pass

pre_save.connect(generate_slug_as_needed)


class Edge(models.Model):
    """
    Models a relationship between two other model instances.
    In the form [subject] [verb] [object]
    e.g. [Brunel] [invented] [tunneling shield]
    """

    VERBS = [
        "invented",
        "conceived",
        "discovered",
        "preceded",
        "was friends with",
        "was parent to",
        "was described by",
        "was married to",
        "dined with",
        "inspired",
        "enabled",
        "depicted",
        "affected",
        "owned",
        "created",
        "primary",
        "secondary",
        "described_by", # For linking to StoryContent nodes
    ]

    subject_type = models.CharField(max_length=255)
    subject_id = models.IntegerField()
    object_type = models.CharField(max_length=255)
    object_id = models.IntegerField()
    verb = models.CharField(max_length=255, choices=[(x,x) for x in VERBS])
    story = models.ForeignKey("Story", blank=True, null=True, related_name="edges")

    class Meta:
        unique_together = [
            (
                "subject_type",
                "subject_id",
                "object_type",
                "object_id",
                "verb",
                "story",
            ),
        ]

    @classmethod
    def _type_string_from_model(self, instance):
        return "%s.%s" % (
            instance._meta.app_label,
            instance._meta.object_name.lower(),
        )

    @classmethod
    def _model_from_type_string(self, type_string):
        app_label, object_name = type_string.split(".")
        return models.get_model(app_label, object_name)

    def set_object(self, object):
        self.object_type = self._type_string_from_model(object)
        self.object_id = object.pk

    def get_object(self):
        if not (self.object_type and self.object_id):
            return None
        model = self._model_from_type_string(self.object_type)
        return model.objects.get(pk=self.object_id)

    object = property(get_object, set_object)

    def set_subject(self, subject):
        self.subject_type = self._type_string_from_model(subject)
        self.subject_id = subject.pk

    def get_subject(self):
        if not (self.subject_type and self.subject_id):
            return None
        model = self._model_from_type_string(self.subject_type)
        return model.objects.get(pk=self.subject_id)

    subject = property(get_subject, set_subject)

    def linked_object(self):
        return u"<a href='%(url)s'>%(text)s</a>" % {
            'url': self.object.url(),
            'text': self.object.name,
        }
    linked_object.allow_tags = True

    def linked_subject(self):
        return u"<a href='%(url)s'>%(text)s</a>" % {
            'url': self.subject.url(),
            'text': self.subject.name,
        }
    linked_subject.allow_tags = True

    def get_absolute_url(self):
        return self.url()

    def url(self):
        return self.subject.url()


class EdgeObjectQuerySet(QuerySet):
    """
    QuerySet subclass that allows you to easily follow edges to their object.
    """
    def follow(self):
        to_load = {}
        for edge in self:
            if edge.object_type not in to_load:
                to_load[edge.object_type] = []
            to_load[edge.object_type].append(edge.object_id)

        loaded = []
        for type_string in to_load:
            model = Edge._model_from_type_string(type_string)
            instances = model.objects.in_bulk(to_load[type_string]).values()
            loaded.extend(instances)

        return loaded

    def by_verb(self):
        """
        From a query set of edges, get all of the edges' objects grouped by
        the edges' verbs.
        """
        to_load = {}
        for edge in self:
            to_load.setdefault(edge.object_type, [])
            to_load[edge.object_type].append((edge.verb, edge.object_id, ))

        loaded = {}
        for type_string in to_load:
            model = Edge._model_from_type_string(type_string)
            pks = [pk for verb, pk in to_load[type_string]]
            instances = model.objects.in_bulk(pks)
            for verb, pk in to_load[type_string]:
                loaded.setdefault(verb, [])
                loaded[verb].append(instances[pk])

        return loaded


class EdgeSubjectQuerySet(QuerySet):
    """
    QuerySet subclass that allows you to easily follow edges to their subject.
    """
    def follow(self):
        to_load = {}
        for edge in self:
            if edge.subject_type not in to_load:
                to_load[edge.subject_type] = []
            to_load[edge.subject_type].append(edge.subject_id)

        loaded = []
        for type_string in to_load:
            model = Edge._model_from_type_string(type_string)
            instances = model.objects.in_bulk(to_load[type_string]).values()
            loaded.extend(instances)

        return loaded

    def by_verb(self):
        """
        From a query set of edges, get all of the edges' subject grouped by
        the edges' verbs.
        """
        to_load = {}
        for edge in self:
            to_load.setdefault(edge.subject_type, [])
            to_load[edge.subject_type].append((edge.verb, edge.subject_id, ))

        loaded = {}
        for type_string in to_load:
            model = Edge._model_from_type_string(type_string)
            pks = [pk for verb, pk in to_load[type_string]]
            instances = model.objects.in_bulk(pks)
            for verb, pk in to_load[type_string]:
                loaded.setdefault(verb, [])
                loaded[verb].append(instances[pk])

        return loaded


class EdgesMixin(object):
    def outgoing(self, verb=None):
        """
        Finds all edges for which self is the edge's subject.
        Returns a EdgeObjectQuerySet. Calling follow() on the returned query
        set will give a list of the edges' objects.
        """
        queryset = Edge.objects.filter(
            subject_type=Edge._type_string_from_model(self),
            subject_id=self.pk,
        )
        if verb is not None:
            queryset = queryset.filter(
                verb=verb,
            )
        return queryset._clone(
            klass=EdgeObjectQuerySet,
            setup=True,
        )

    def incoming(self, verb=None):
        """
        Finds all edges for which self is the edge's object.
        Returns a EdgeSubjectQuerySet. Calling follow() on the returned query
        set will give a list of the edges' subjects.
        """
        queryset = Edge.objects.filter(
            object_type=Edge._type_string_from_model(self),
            object_id=self.pk,
        )
        if verb is not None:
            queryset = queryset.filter(
                verb=verb,
            )
        return queryset._clone(
            klass=EdgeSubjectQuerySet,
            setup=True,
        )

    def stories(self):
        """
        Returns all the stories that have primary edges into or out of
        the current node. The stories' current nodes will be set to this
        node so you can use next and previous on them 
        (see Story.set_current_node)
        """
        queryset = self.incoming() | self.outgoing()
        queryset = queryset.filter(verb__in=['primary', 'secondary'])
        story_ids = queryset.distinct().values_list('story', flat=True)
        stories = Story.objects.in_bulk(list(story_ids)).values()
        for story in stories:
            story.set_current_node(self)
        return stories

    def readable_name(self):
        return "%s: %s" % (
            self._meta.object_name,
            self.name,
        )

    @property
    def select_tuple(self):
        return (
            "%s:%d" % (
                Edge._type_string_from_model(self),
                self.pk,
            ),
            self.readable_name()
        )


class BaseNode(models.Model, EdgesMixin):
    """
    Abstract base for nodes - has no fields, only useful
    methods.
    """

    class Meta:
        abstract = True

    def __unicode__(self):
        return "%s (%s:%d)" % (
            self.name,
            self._meta.object_name,
            self.pk,
        )

    def object_name(self):
        return self._meta.object_name.lower()


class Node(BaseNode):
    """
    Abstract superclass for Nodes in our graph that have
    a presence in time.
    """

    hidden_in_map = False

    name = models.CharField(max_length=1024, unique=True)
    slug = models.SlugField(max_length=1024, unique=True, default='', blank=True)
    text = models.TextField(blank=True)

    timeline_date = models.IntegerField(blank=True, null=True, help_text="Years since 0AD")
    display_date = models.CharField(max_length=255, blank=True)

    reference_url = models.URLField(verify_exists=False, blank=True)

    named_url = None

    def name_possibly_lowercased(self):
        return self.name

    class Meta:
        abstract = True

    @classmethod
    def all_child_classes(self):
        return [
            Person,
            Event,
            Concept,
            Object,
            ExternalLink,
            StoryContent,
            Image,
        ]
    
    def get_absolute_url(self):
        try:
            return self.url()
        except AttributeError:
            return None

    def search_data(self):
        return {
            'name': self.name,
            'text': self.text,
            'timeline_date': self.timeline_date,
            'display_date': self.display_date,
        }

    def url(self):
        return reverse(self.named_url, kwargs={'slug': self.slug})

    def reference_name(self):
        if self.reference_url:
            host = urlparse.urlsplit( self.reference_url ).netloc
            if host.find('10.0.0.') >= 0:
                return 'Weaver'     # in-fort links
            if host.find('wikipedia.org') >= 0:
                return 'Wikipedia'
            else:
                return host.replace('www.', '')

    def link_url(self):
        # just used in links; something that has no text and isn't
        # in any stories should use its reference_url instead.
        if not self.text and self.reference_url and len(self.stories())==0:
            return self.reference_url
        else:
            return self.url()


class Person(Node):
    """
    A person.
    """

    named_url = 'person'

    class Meta:
        verbose_name_plural = "people"


class Event(Node):
    """
    A thing that happened at a given point in time.
    """

    named_url = 'event'


class Concept(Node):
    """
    A concept that was developed or discovered, e.g. punch cards, communism
    """

    named_url = 'concept'


class Object(Node):
    """
    A physical thing which arose from a concept, e.g. the Jacquard Loom
    """

    named_url = 'object'

    def name_possibly_lowercased(self):
        if self.name.startswith(u'The '):
            return u'the %s' % self.name[4:]
        else:
            return self.name


class ExternalLink(BaseNode):
    """
    A link to an external site.
    """

    hidden_in_map = True

    name = models.CharField(max_length=1024, unique=True)
    url = models.URLField(max_length=255, verify_exists=False)

    def __unicode__(self):
        return "%s (%s:%d)" % (
            self.name,
            self._meta.object_name,
            self.pk,
        )


class Image(BaseNode):
    """
    An image attached to one or more other nodes.
    """

    hidden_in_map = True

    image = models.ImageField(upload_to="images/%Y-%m/")
    caption = models.TextField(blank=True)

    @property
    def name(self):
        return str(self.image)
    
    def url(self):
        return self.image.url

    def __unicode__(self):
        return "%s (%s:%s)" % (
            self.image,
            self._meta.object_name,
            self.pk,
        )


class Story(models.Model):
    """
    A story is a collection of edges describing a directed narrative
    """

    name = models.CharField(max_length=255, unique=True)
    slug = models.SlugField(max_length=255, unique=True, default='')
    text = models.TextField(blank=True, help_text="Brief description about the story for appearing on the homepage")
    colour = models.CharField(max_length=8, help_text="Colour as a hexdecimal string with no #, e.g. '0932f5'", blank=True)
    featured = models.BooleanField(default=True, help_text="Whether this story is featured on the homepage")

    def start(self):
        story_edges = Edge.objects.filter(story=self)
        subject_nodes = set(edge.subject for edge in story_edges)
        object_nodes = set(edge.object for edge in story_edges)
        return (subject_nodes - object_nodes).pop()

    def set_current_node(self, node):
        """
        Sets the current nodes so that the next and preivous functions make
        sense.
        """
        self.current_node = node

    def next(self):
        """Return the next node in this story.
        
        Return the next node in the primary thread if on the primary thread for
        this story; fall back to a secondary thread if off the primary.
        
        """
        return self._successor('primary') or self._successor('secondary')
    
    def next_primary(self):
        """Return the next node in this story's primary thread."""
        return self._successor('primary')
    
    def next_secondary(self):
        """Return the next node in this story's secondary thread."""
        return self._successor('secondary')
    
    def _successor(self, verb):
        if not getattr(self, 'current_node'):
            return None
        nodes = self.current_node.outgoing(verb).filter(story=self).follow()
        return nodes[0] if nodes else None
    
    def previous(self):
        """Return the previous node in this story.
        
        Return the previous node in the primary thread if on the primary thread
        for this story; fall back to a secondary thread if off the primary.
        
        """
        return self._predecessor('primary') or self._predecessor('secondary')
    
    def previous_primary(self):
        return self._predecessor('primary')
    
    def previous_secondary(self):
        return self._predecessor('secondary')
    
    def _predecessor(self, verb):
        if not getattr(self, 'current_node'):
            return None
        nodes = self.current_node.incoming(verb).filter(story=self).follow()
        return nodes[0] if nodes else None

    def story_content(self):
        """
        Returns the story content for the current node in the current story.
        Call set_current_node first so that this makes sense.
        """
        try:
            nodes = self.current_node.outgoing('described_by').filter(story=self).follow()
        except AttributeError:
            return

        if len(nodes) > 0:
            return nodes[0]

    def __unicode__(self):
        return self.name
        
    class Meta:
        verbose_name_plural = 'Stories'


class StoryContent(BaseNode):
    """
    Extra info about a node relating to a story, for instance "Brunnel in Automota"
    """
    
    hidden_in_map = True

    text = models.TextField(blank=True)

    @property
    def story(self):
        try:
            return self.incoming("described_by").get(story__isnull=False).story
        except Edge.DoesNotExist:
            return None

    @property
    def subject(self):
        try:
            return self.incoming("described_by").get(story__isnull=False).subject
        except Edge.DoesNotExist:
            return None

    @property
    def name(self):
        try:
            return self.story.name
        except AttributeError:
            return "Unknown"

    def get_absolute_url(self):
        return self.url()
    
    def url(self):
        return self.subject.url() + "?story=" + self.story.slug
