from django.http import Http404
from django.test import TestCase
from core.views.nodes import RandomNodeView

class RandomNodeViewTest(TestCase):
    
    fixtures = ['live_data']
    
    def test_random_view(self):
        """Probabilistically test the random item view."""
        for _ in xrange(100):
            response = self.client.get('/random')
            self.assertTrue(response.status_code in (302, 303))


class RandomNodeView404Test(TestCase):
    
    def test_random_view_404(self):
        """Test that the random view 404s if there is nothing to choose."""
        self.assertEqual(self.client.get('/random').status_code, 404)
