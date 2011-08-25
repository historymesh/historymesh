from django import forms
from core.models import Person, Edge, Node, StoryContent, Story

class NodeList(object):

    def __iter__(self):
        choices_to_return = []
        for model in Node.all_child_classes():
            for node_object in model.objects.all():
                choices_to_return.append(node_object.select_tuple)
        return iter(sorted(
            choices_to_return,
            key=lambda node: node[1],
        ))


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


class StoryContentAdminForm(forms.ModelForm):

    subject = SpecialChoices()
    story = forms.ModelChoiceField(Story.objects.all())

    def __init__(self, *args, **kwargs):
        super(StoryContentAdminForm, self).__init__(*args, **kwargs)
        if self.instance:
            print self.instance.incoming("described_by")
            try:
                story_edge = self.instance.incoming("described_by").get(story__isnull=False)
            except Edge.DoesNotExist:
                pass
            else:
                self.initial["story"] = story_edge.story.pk
                self.initial["subject"] = story_edge.subject.select_tuple[0]

    def save(self, commit=True):
        instance = super(StoryContentAdminForm, self).save(commit)
        self.save_m2m = self.save_m2m_real
        return instance

    def save_m2m_real(self):
        edge = Edge(verb="described_by")
        edge.subject = self.cleaned_data['subject']
        edge.object = self.instance
        edge.story = self.cleaned_data['story']
        edge.save()

    class Meta:
        model = StoryContent
