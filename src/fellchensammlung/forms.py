from django import forms
from .models import AdoptionNotice, Animal, Image, Report, ModerationAction, User
from django_registration.forms import RegistrationForm
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Submit
from django.utils.translation import gettext_lazy as _

class DateInput(forms.DateInput):
    input_type = 'date'


class AdoptionNoticeForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = FormHelper()

        self.helper.form_id = 'form-adoption-notice'
        self.helper.form_class = 'card'
        self.helper.form_method = 'post'

        self.helper.layout = Layout(
            Fieldset(
                _('Vermittlungsdetails'),
                'name',
                'group_only',
                'searching_since',
                'description',
                'further_information',
            ),
            Submit('submit', _('Submit'))
        )

    class Meta:
        model = AdoptionNotice
        fields = ['name', "group_only", "further_information", "description", "searching_since"]
        widgets = {
            'searching_since': DateInput(),
        }


class AnimalForm(forms.ModelForm):
    class Meta:
        model = Animal
        picture = forms.ImageField(label='Image', required=False)
        fields = ['name', "species", "sex", "date_of_birth", "description"]
        widgets = {
            'date_of_birth': DateInput(),
        }


class ImageForm(forms.ModelForm):
    class Meta:
        model = Image
        fields = ('title', 'image', 'alt_text')


class ReportForm(forms.ModelForm):
    class Meta:
        model = Report
        fields = ('reported_broken_rules', 'comment')


class ModerationActionForm(forms.ModelForm):
    class Meta:
        model = ModerationAction
        fields = ('action', 'public_comment', 'private_comment')


class CustomRegistrationForm(RegistrationForm):
    class Meta(RegistrationForm.Meta):
        model = User
