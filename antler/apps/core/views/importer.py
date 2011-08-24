import json
from django.views.generic import View
from django.views.decorators.csrf import csrf_exempt
from django.http import HttpResponse
from core.models import Object, Person, Event, Concept, Edge


class ImportView(View):
    """
    A view that allows importable data to be POSTed to it.
    """

    dispatch = csrf_exempt(View.dispatch)

    def post(self, request):
        data = json.loads(request.raw_post_data)
        import_from_json(data, clean=True)
        return HttpResponse("YAY\n")

type_map = {
    "object": Object,
    "person": Person,
    "concept": Concept,
    "event": Event,
}

def import_from_json(data, clean=False, verbose=False):
    """
    Given an already-parsed JSON object, imports the data within
    into the database.
    """

    # If we're cleaning, clean.
    if clean:
        for model in Node.all_child_classes + [Edge]:
            model.objects.all().delete()

    # First pass: insert the things into the database
    relationships = []
    object_cache = {}
    for thing in data:
        # Get the class it maps to
        try:
            klass = type_map[thing['type']]
        except KeyError:
            raise ValueError("Invalid thing (bad type): %r" % thing)
        # Get the object if it exists
        instance = klass.objects.get_or_create(name=thing['name'])[0]
        # Delete all edges coming off of the object
        instance.outgoing().delete()
        # Store relationships for later use
        for verb, targets in thing['relationships'].items():
            for target in targets:
                relationships.append((instance, target, verb))
        # Cache object
        object_cache[thing['name']] = instance
        if verbose:
            print "Imported %s" % thing['name']
    
    # Second pass: create relationships
    if verbose:
        print "Creating relationships..."
    for subject, object_name, verb in relationships:
        for verb, targets in thing['relationships'].items():
            edge = Edge(verb=verb)
            edge.subject = instance
            try:
                edge.object = object_cache[object_name]
            except KeyError:
                raise ValueError("Relationship from %s to non-existent object %s" % (subject, object_name))
            edge.save()
