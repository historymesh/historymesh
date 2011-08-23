from django.db import models
from django.db.models.query import QuerySet

class Edge(models.Model):
    """
    Models a relationship between two other model instances.
    In the form [subject] [verb] [object]
    e.g. [Brunel] [invented] [tunneling shield]
    """

    subject_type = models.CharField(max_length=255)
    subject_id = models.IntegerField()
    object_type = models.CharField(max_length=255)
    object_id = models.IntegerField()
    verb = models.CharField(max_length=255)

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
        model = self._model_from_type_string(self.object_type)
        return model.objects.get(pk=self.object_id)

    def set_subject(self, subject):
        self.subject_type = self._type_string_from_model(subject)
        self.subject_id = subject.pk

    def get_subject(self):
        model = self._model_from_type_string(self.subject_type)
        return model.objects.get(pk=self.subject_id)


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


class Node(models.Model, EdgesMixin):
    """
    Abstract superclass for Nodes in our graph.
    """

    class Meta:
        abstract = True

    def __unicode__(self):
        return "%s:%d" % (
            self._meta.object_name,
            self.pk,
        )


class Person(Node):
    pass


class Event(Node):
    pass


class Concept(Node):
    pass


class Object(models.Model, EdgesMixin):
    pass

