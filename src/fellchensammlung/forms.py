from django import forms
from .models import AdoptionNotice, Animal, Image


class DateInput(forms.DateInput):
    input_type = 'date'


class AdoptionNoticeForm(forms.ModelForm):
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
