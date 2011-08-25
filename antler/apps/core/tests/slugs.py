from django.test import TestCase
from core.models import Person

class SlugTest(TestCase):
    def test_generating_slug(self):
        person = Person(name='Charles Babbage')
        person.save()

        self.assertEqual(
            person.slug,
            'charles-babbage',
        )
