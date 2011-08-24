from django import forms
from core.models import Person, Edge, Node

class SpecialChoices(forms.ChoiceField):
	def __init__(self, *args, **kwargs):
		super(SpecialChoices, self).__init__(*args, **kwargs)
		self.widget.choices = self.choices

	def _get_choices(self):
		choices_to_return = []
		for model in Node.all_child_classes():
			print model
			for node_object in model.objects.all():
				print node_object
				choices_to_return.append(node_object.select_tuple)
		return sorted(choices_to_return, key=lambda node:node[1])


	def _set_choices(self,value):
		pass

	choices = property(_get_choices, _set_choices)

class EdgeForm(forms.Form):


	subject = SpecialChoices()
	verb = forms.ChoiceField(choices=[(x,x) for x in Edge.VERBS])
	object = SpecialChoices()
	