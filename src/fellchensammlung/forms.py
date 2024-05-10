import datetime

from django import forms
from .models import AdoptionNotice, Animal, Image, Report, ModerationAction, User, Species
from django_registration.forms import RegistrationForm
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Submit, Layout, Fieldset, HTML, Row, Column, Field
from django.utils.translation import gettext_lazy as _
from notfellchen.settings import MEDIA_URL


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


class AnimalForm(forms.Form):

    def __init__(self, animal_id, *args, **kwargs):

        photo_rows = []

        super().__init__(*args, **kwargs)

        # Get the animal instance
        animal = Animal.objects.get(pk=animal_id)

        # Define Django form fields for later use
        self.fields["name"] = forms.CharField(initial=animal.name)
        self.fields["species"] = forms.ChoiceField(
            label=_("Tierart"),
            choices=[(x.id, x.name) for x in Species.objects.all()],
            initial=animal.species.pk
        )

        photos = animal.get_photos()

        for photo in photos:
            alt_field_name = f"image_alt_{photo.pk}"
            self.fields[alt_field_name] = forms.CharField()
            self.fields[alt_field_name].initial = photo.alt_text

            title_field_name = f"image_title_{photo.pk}"
            self.fields[title_field_name] = forms.CharField(max_length=200)
            self.fields[title_field_name].initial = photo.title

            delete_btn = f"delete_photo_{photo.pk}"
            save_btn = f"save_photo_{photo.pk}"

            current_row = Row(
                Column(title_field_name, css_class="form-group col-md-2 mb-0"),
                Column(
                    HTML(photo.as_html),
                    css_class="form-group col-md-4 mb-0"),
                Column(alt_field_name, css_class="form-group col-md-2 mb-0"),
                Column(
                    Submit(delete_btn, _("Löschen")),
                    css_class="form-group col-md-auto mb-0 needs_manual",
                ),
                Column(
                    Submit(save_btn, _("Bearbeiten")),
                    css_class="form-group col-md-auto mb-0 needs_manual",
                ),
                css_class="form-row",
            )

            photo_rows.append(current_row)

        self.helper = FormHelper()
        self.helper.form_class = 'card'

        submit_form_btn = f"submit_form_{animal.pk}"

        self.helper.layout = Layout(
            Fieldset(
                animal.name,
                Row(
                    Field("name", selected="", css_class="form-group col-md-6 mb-0"),
                    Field("species", css_class="form-group col-md-6 mb-0"),
                    Submit(submit_form_btn, _("Submit"),
                           css_class="form-group col-md-2 mb-0 needs_manual",
                           ),
                    css_class="form-row",
                )
            )
        )

        self.helper.layout.append(Fieldset(_("Fotos"), css_class="fieldsets"))
        for photo_row in photo_rows:
            self.helper.layout[-1].append(photo_row)

        current_row = Row(
            HTML(
                "<hr style='border: 0; clear:both; display:block; width: 96%; background-color:black; height: 1px;'>"
            )
        )
        self.helper.layout.append(current_row)

        # self.helper.layout.append('i_want_to_add_a_new_column')

        self.fields["add_image"] = forms.ImageField()
        self.fields["add_image_alt"] = forms.CharField()
        self.fields["add_image_title"] = forms.CharField(max_length=200, )

        current_row = Row(
            Column("add_image", css_class="form-group col-md-6 mb-0"),
            Column("add_image_alt", css_class="form-group col-md-2 mb-0"),
            Column("add_image_title", css_class="form-group col-md-2 mb-0"),
            css_class="form-row",
        )
        #self.helper.layout.append(current_row)

        #add_photo_btn = f"add_photo_btn_{animal.pk}"
        #self.helper.layout.append(Submit(add_photo_btn, _("Bild hinzufügen")))


class AnimalForm2(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.form_id = 'form-animal'
        self.helper.form_class = 'card'
        self.helper.form_method = 'post'

        self.helper.add_input(Submit('submit', _('Submit')))

    class Meta:
        model = Animal
        picture = forms.ImageField(label='Image', required=False)
        fields = ['name', "species", "sex", "date_of_birth", "description"]
        widgets = {
            'date_of_birth': DateInput(),
        }


class ImageForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.form_id = 'form-animal-photo'
        self.helper.form_class = 'card'
        self.helper.form_method = 'post'

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
