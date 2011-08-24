from django.test import TestCase
from core.models import Story, Person

class StoryTest(TestCase):
    fixtures = [ 'story_nodes' ]

    def test_start(self):
      story = Story.objects.get(pk=1)
      start = story.start()

      self.assertEqual(
          start,
          Person.objects.get(pk=1),
      )
