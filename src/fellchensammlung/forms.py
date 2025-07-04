from django import forms

from .models import AdoptionNotice, Animal, Image, ReportAdoptionNotice, ReportComment, ModerationAction, User, Species, \
    Comment, SexChoicesWithAll, DistanceChoices, SpeciesSpecificURL
from django_registration.forms import RegistrationForm
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Submit, Layout, Fieldset, HTML, Row, Column, Field, Hidden
from django.utils.translation import gettext_lazy as _
from notfellchen.settings import MEDIA_URL
from crispy_forms.layout import Div


def animal_validator(value: str):
    value = value.lower()
    animal_list = ["ratte", "farbratte", "katze", "hund", "kaninchen", "hase", "kuh", "fuchs", "cow", "rat", "cat",
                   "dog", "rabbit", "fox", "fancy rat"]
    if value not in animal_list:
        raise forms.ValidationError(_("Dieses Tier kenne ich nicht. Probier ein anderes"))


class DateInput(forms.DateInput):
    input_type = 'date'


class AdoptionNoticeForm(forms.ModelForm):
    template_name = "fellchensammlung/forms/form_snippets.html"

    class Meta:
        model = AdoptionNotice
        fields = ['name', "group_only", "further_information", "description", "searching_since", "location_string",
                  "organization"]
        widgets = {
            'searching_since': DateInput(format=('%Y-%m-%d')),
        }


class AdoptionNoticeFormAutoAnimal(AdoptionNoticeForm):
    def __init__(self, *args, **kwargs):
        super(AdoptionNoticeFormAutoAnimal, self).__init__(*args, **kwargs)
        self.fields["num_animals"] = forms.fields.IntegerField(min_value=1, max_value=30, label=_("Zahl der Tiere"))
        animal_form = AnimalForm()
        self.fields["species"] = animal_form.fields["species"]
        self.fields["sex"] = animal_form.fields["sex"]
        self.fields["date_of_birth"] = animal_form.fields["date_of_birth"]
        self.fields["date_of_birth"].widget = DateInput(format=('%Y-%m-%d'))


class AnimalForm(forms.ModelForm):
    template_name = "fellchensammlung/forms/form_snippets.html"

    class Meta:
        model = Animal
        fields = ["name", "date_of_birth", "species", "sex", "description"]

        widgets = {
            'date_of_birth': DateInput(format=('%Y-%m-%d'))
        }


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
            submits = Div(Submit('submit', _('Speichern')),
                          Submit('save-and-add-another', _('Speichern und weiteres Foto hinzufügen')),
                          css_class="container-edit-buttons")
        else:
            submits = Fieldset(Submit('submit', _('Speichern')), css_class="container-edit-buttons")
        self.helper.layout = Layout(
            Div(
                'image',
                'alt_text',
                css_class="spaced",
            ),
            submits
        )

    class Meta:
        model = Image
        fields = ('image', 'alt_text')


class ReportAdoptionNoticeForm(forms.ModelForm):
    template_name = "fellchensammlung/forms/form_snippets.html"

    class Meta:
        model = ReportAdoptionNotice
        fields = ('reported_broken_rules', 'user_comment')


class ReportCommentForm(forms.ModelForm):
    template_name = "fellchensammlung/forms/form_snippets.html"

    class Meta:
        model = ReportComment
        fields = ('reported_broken_rules', 'user_comment')


class CommentForm(forms.ModelForm):
    class Meta:
        model = Comment
        fields = ('text',)


class SpeciesURLForm(forms.ModelForm):
    class Meta:
        model = SpeciesSpecificURL
        fields = ('species', 'url')


class ModerationActionForm(forms.ModelForm):
    class Meta:
        model = ModerationAction
        fields = ('action', 'public_comment', 'private_comment')


class CustomRegistrationForm(RegistrationForm):
    class Meta(RegistrationForm.Meta):
        model = User

    template_name = "fellchensammlung/forms/form_snippets.html"

    captcha = forms.CharField(validators=[animal_validator], label=_("Nenne eine bekannte Tierart"), help_text=_(
        "Bitte nenne hier eine bekannte Tierart (z.B. ein Tier das an der Leine geführt wird). Das Fragen wir dich um sicherzustellen, dass du kein Roboter bist."))


class AdoptionNoticeSearchForm(forms.Form):
    template_name = "fellchensammlung/forms/form_snippets.html"

    sex = forms.ChoiceField(choices=SexChoicesWithAll, label=_("Geschlecht"), required=False,
                            initial=SexChoicesWithAll.ALL)
    max_distance = forms.ChoiceField(choices=DistanceChoices, initial=DistanceChoices.ONE_HUNDRED,
                                     label=_("Suchradius"))
    location_string = forms.CharField(max_length=100, label=_("Stadt"), required=False)
