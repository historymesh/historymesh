from django import forms
from core.models import Person, Edge, Node

class NodeList(object):

    def __iter__(self):
        choices_to_return = []
        for model in Node.all_child_classes():
            for node_object in model.objects.all():
                choices_to_return.append(node_object.select_tuple)
        return iter(sorted(choices_to_return, key=lambda node:node[1]))


class SpecialChoices(forms.ChoiceField):
    def __init__(self, *args, **kwargs):
        super(SpecialChoices, self).__init__(*args, **kwargs)
        self.widget.choices = self.choices

    def _get_choices(self):
        return NodeList()

    def _set_choices(self,value):
        pass

    def clean(self, value):
        subject_string, pk = value.split(":")
        subject_model = Edge._model_from_type_string(subject_string)
        return subject_model.objects.get(pk=pk)

    choices = property(_get_choices, _set_choices)


class EdgeForm(forms.Form):

    subject = SpecialChoices()
    verb = forms.ChoiceField(choices=[(x,x) for x in Edge.VERBS])
    object = SpecialChoices()


class EdgeAdminForm(forms.ModelForm):

    subject = SpecialChoices()
    verb = forms.ChoiceField(choices=[(x,x) for x in Edge.VERBS])
    object = SpecialChoices()

    def __init__(self, *args, **kwargs):
        super(EdgeAdminForm, self).__init__(*args, **kwargs)
        if self.instance:
            if self.instance.object:
                self.initial["object"] = self.instance.object.select_tuple[0]
            if self.instance.subject:
                self.initial["subject"] = self.instance.subject.select_tuple[0]

    def save(self, commit=True):
        instance = super(EdgeAdminForm, self).save(commit=False)
        instance.subject = self.cleaned_data['subject']
        instance.object = self.cleaned_data['object']
        if commit:
            instance.save()
            self.save_m2m()
        return instance

    class Meta:
        model = Edge
        fields = ("subject", "verb", "object", "story")
        exclude = (
            "subject_type",
            "subject_id", 
            "object_type",
            "object_id",
        )
