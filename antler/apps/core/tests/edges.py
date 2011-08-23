from django.test import TestCase
from core.models import Person, Concept


class EdgeTest(TestCase):
    fixtures = [ 'edges' ]

    def test_outgoing_links(self):
        person = Person.objects.get(pk=1)
        inventions = person.outgoing("invented").follow()

        self.assertEqual(
            inventions,
            [ Concept.objects.get(pk=1) ],
        )

    def test_incoming_links(self):
        concept = Concept.objects.get(pk=2)
        inspirations = concept.incoming("inspired").follow()

        self.assertEqual(
            inspirations,
            [ Concept.objects.get(pk=1) ],
        )
