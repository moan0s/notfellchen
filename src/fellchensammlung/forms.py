import datetime

from django import forms

from .models import AdoptionNotice, Animal, Image, ReportAdoptionNotice, ReportComment, ModerationAction, User, Species, \
    Comment
from django_registration.forms import RegistrationForm
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Submit, Layout, Fieldset, HTML, Row, Column, Field
from django.utils.translation import gettext_lazy as _
from notfellchen.settings import MEDIA_URL


class DateInput(forms.DateInput):
    input_type = 'date'


class AdoptionNoticeForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        if 'in_adoption_notice_creation_flow' in kwargs:
            in_flow = kwargs.pop('in_adoption_notice_creation_flow')
        else:
            in_flow = False
        super().__init__(*args, **kwargs)
        self.helper = FormHelper()

        self.helper.form_id = 'form-adoption-notice'
        self.helper.form_class = 'card'
        self.helper.form_method = 'post'

        if in_flow:
            submit = Submit('save-and-add-another-animal', _('Speichern und Tiere hinzufügen'))

        else:
            submit = Submit('submit', _('Submit'))

        self.helper.layout = Layout(
            Fieldset(
                _('Vermittlungsdetails'),
                'name',
                'group_only',
                'searching_since',
                'location_string',
                'description',
                'further_information',
            ),
            submit)

    class Meta:
        model = AdoptionNotice
        fields = ['name', "group_only", "further_information", "description", "searching_since", "location_string"]


class AnimalForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        if 'in_adoption_notice_creation_flow' in kwargs:
            adding = kwargs.pop('in_adoption_notice_creation_flow')
        else:
            adding = False
        super().__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.form_class = 'form-animal'
        if adding:
            self.helper.add_input(Submit('save-and-add-another-animal', _('Speichern und weiteres Tier hinzufügen')))
            self.helper.add_input(Submit('save-and-finish', _('Speichern und beenden')))
        else:
            self.helper.add_input(Submit('submit', _('Speichern')))

    class Meta:
        model = Animal
        fields = ["name", "date_of_birth", "species", "sex", "description"]


class ImageForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        if 'in_flow' in kwargs:
            in_flow = kwargs.pop('in_flow')
        else:
            in_flow = False
        super().__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.form_id = 'form-animal-photo'
        self.helper.form_class = 'card'
        self.helper.form_method = 'post'
        if in_flow:
            self.helper.add_input(Submit('save-and-add-another', _('Speichern und weiteres Foto hinzufügen')))
            self.helper.add_input(Submit('submit', _('Speichern')))
        else:
            self.helper.add_input(Submit('submit', _('Submit')))

    class Meta:
        model = Image
        fields = ('image', 'alt_text')


class ReportAdoptionNoticeForm(forms.ModelForm):
    class Meta:
        model = ReportAdoptionNotice
        fields = ('reported_broken_rules', 'user_comment')


class ReportCommentForm(forms.ModelForm):
    class Meta:
        model = ReportComment
        fields = ('reported_broken_rules', 'user_comment')


class CommentForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.form_class = 'form-comments'
        self.helper.add_input(Submit('submit', _('Kommentieren')))

    class Meta:
        model = Comment
        fields = ('text',)


class ModerationActionForm(forms.ModelForm):
    class Meta:
        model = ModerationAction
        fields = ('action', 'public_comment', 'private_comment')


class CustomRegistrationForm(RegistrationForm):
    class Meta(RegistrationForm.Meta):
        model = User


def _get_distances():
    return {i: i for i in [10, 20, 50, 100, 200, 500]}


class AdoptionNoticeSearchForm(forms.Form):
    postcode = forms.CharField(max_length=20, label=_("Postleitzahl"))
    max_distance = forms.ChoiceField(choices=_get_distances, label=_("Max. Distanz"))
