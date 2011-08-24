from django import forms
from core.models import Person, Edge, Node

class SpecialChoices(forms.ChoiceField):
    def __init__(self, *args, **kwargs):
        super(SpecialChoices, self).__init__(*args, **kwargs)
        self.widget.choices = self.choices

    def _get_choices(self):
        choices_to_return = []
        for model in Node.all_child_classes():
            for node_object in model.objects.all():
                choices_to_return.append(node_object.select_tuple)
        return sorted(choices_to_return, key=lambda node:node[1])


    def _set_choices(self,value):
        pass

    choices = property(_get_choices, _set_choices)

class EdgeForm(forms.Form):

    subject = SpecialChoices()
    verb = forms.ChoiceField(choices=[(x,x) for x in Edge.VERBS])
    object = SpecialChoices()

    def clean_subject(self):
        return self._get_object_for_select_string(self.cleaned_data['subject'])

    def clean_object(self):
        return self._get_object_for_select_string(self.cleaned_data['object'])
        
    def _get_object_for_select_string(self, select_string):
        subject_string, pk = select_string.split(":")
        subject_model = Edge._model_from_type_string(subject_string)
        return subject_model.objects.get(pk=pk)
    