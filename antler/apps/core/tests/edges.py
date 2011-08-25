from django.test import TestCase
from core.models import Person, Concept, Edge, Object, Event, Story


class FollowingTest(TestCase):
    fixtures = [ 'edges' ]
    
    maxDiff = None
    
    def test_outgoing_links(self):
        person = Person.objects.get(pk=1)
        inventions = person.outgoing("invented").follow()

        self.assertEqual(
            inventions,
            [
                    Concept.objects.get(pk=1),
                    Concept.objects.get(pk=2),
                    Object.objects.get(pk=1),
                    Object.objects.get(pk=2),
            ],
        )

    def test_incoming_links(self):
        concept = Concept.objects.get(pk=2)
        inspirations = concept.incoming("inspired").follow()

        self.assertEqual(
            inspirations,
            [ Concept.objects.get(pk=1) ],
        )

    def test_grouped_outgoing_links(self):
        person = Person.objects.get(pk=1)
        links = person.outgoing().by_verb()

        self.assertEqual(
            links,
            {
                'dined_with': [
                    Person.objects.get(pk=2),
               ],
                'invented': [
                    Concept.objects.get(pk=1),
                    Concept.objects.get(pk=2),
                    Object.objects.get(pk=1),
                    Object.objects.get(pk=2),
                ],
            },
        )

    def test_grouped_incoming_links(self):
        concept = Concept.objects.get(pk=2)
        links = concept.incoming().by_verb()

        self.assertEqual(
            links,
            {
                'inspired': [
                    Concept.objects.get(pk=1),
                ],
                'invented': [
                    Person.objects.get(pk=1),
                ],
            },
        )

    def test_nothing(self):
        concept = Concept.objects.get(pk=3)
        self.assertEqual([], concept.incoming().follow())
        self.assertEqual([], concept.outgoing().follow())
        self.assertEqual({}, concept.incoming().by_verb())
        self.assertEqual({}, concept.outgoing().by_verb())


class EdgeTest(TestCase):
    fixtures = [ 'edges' ]

    def test_type_string_generation(self):
        person = Person.objects.get(pk=1)
        self.assertEqual("core.person", Edge._type_string_from_model(person))

        concept = Concept.objects.get(pk=1)
        self.assertEqual("core.concept", Edge._type_string_from_model(concept))

    def test_model_from_type_string(self):
        self.assertEqual(Person, Edge._model_from_type_string("core.person"))


class StoryEdgeTest(TestCase):
    fixtures = [ 'stories' ]

    def test_finding_a_nodes_stories(self):
        babbage = Person.objects.get(pk=1)
        lovelace = Person.objects.get(pk=2)
        people_story = Story.objects.get(pk=1)
        loom_story = Story.objects.get(pk=2)

        self.assertEqual(
            babbage.stories(),
            [ people_story ],
        )

        self.assertEqual(
            lovelace.stories(),
            [ people_story, loom_story ],
        )

