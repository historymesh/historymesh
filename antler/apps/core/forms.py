from django import forms
from core.models import Person, Edge

NODES = [(1, 'dave'),(2,'jim')]

class EdgeForm(forms.Form):
	subject = forms.ChoiceField(choices=NODES)
	verb = forms.ChoiceField(choices=[(x,x) for x in Edge.VERBS])
	object = forms.ChoiceField(choices=NODES)
	