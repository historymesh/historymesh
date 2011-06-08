from django.db import models
from django.db.models.query import QuerySet
from django.core.urlresolvers import reverse
from django.template.defaultfilters import slugify
from django.db.models.signals import pre_save

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
        "killed",
        "preceded",
        "befriended",
        "married",
        "dined_with",
        "inspired",
        "enabled",
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

    def url(self):
        return reverse('edge', kwargs={'slug': self.slug})


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
        queryset = self.incoming() | self.outgoing()
        queryset = queryset.filter(verb__in=['primary', 'secondary'])
        story_ids = queryset.distinct().values_list('story', flat=True)
        return Story.objects.in_bulk(list(story_ids)).values()

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


class Node(models.Model, EdgesMixin):
    """
    Abstract superclass for Nodes in our graph.
    """

    hidden_in_map = False

    name = models.CharField(max_length=1024, unique=True)
    slug = models.SlugField(max_length=1024, unique=True, default='', blank=True)
    text = models.TextField(blank=True)

    timeline_date = models.IntegerField(blank=True, null=True, help_text="Years since 0AD")
    display_date = models.CharField(max_length=255, blank=True)

    reference_url = models.URLField(verify_exists=False, blank=True)

    class Meta:
        abstract = True

    def __unicode__(self):
        return "%s (%s:%d)" % (
            self.name,
            self._meta.object_name,
            self.pk,
        )

    @classmethod
    def all_child_classes(self):
        return [Person, Event, Concept, Object, ExternalLink, StoryContent, Image]
    
    def get_absolute_url(self):
        try:
            return self.url()
        except AttributeError:
            return None


class Person(Node):
    """
    A person.
    """

    class Meta:
        verbose_name_plural = "people"

    def url(self):
        return reverse('person', kwargs={'slug': self.slug})


class Event(Node):
    """
    A thing that happened at a given point in time.
    """

    def url(self):
        return reverse('event', kwargs={'slug': self.slug})


class Concept(Node):
    """
    A concept that was developed or discovered, e.g. punch cards, communism
    """

    def url(self):
        return reverse('concept', kwargs={'slug': self.slug})


class Object(Node):
    """
    A physical thing which arose from a concept, e.g. the Jacquard Loom
    """

    def url(self):
        return reverse('object', kwargs={'slug': self.slug})


class ExternalLink(models.Model, EdgesMixin):
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


class Image(models.Model, EdgesMixin):
    """
    An image attached to one or more other nodes.
    """

    hidden_in_map = True

    image = models.ImageField(upload_to="images/%Y-%m/")
    caption = models.TextField(blank=True)

    @property
    def name(self):
        return str(self.image)

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

    def __unicode__(self):
        return self.name
        
    class Meta:
        verbose_name_plural = 'Stories'


class StoryContent(Node):
    """
    Extra info about a node relating to a story, for instance "Brunnel in Automota"
    """
    
    hidden_in_map = True
