from django import forms
from django.forms.widgets import HiddenInput
from django.utils.text import slugify

from ..models.location import Location


class LocationForm(forms.ModelForm):
    """used by a Commercial to CRUD an Event().location"""

    slug_form = forms.SlugField(max_length=255, required=False, widget=HiddenInput)

    class Meta:
        model = Location
        fields = ["name", "number", "street_type", "street_name", "zip", "city"]

    def clean(self) -> dict:
        cleaned_data = super().clean()

        if cleaned_data["name"]:
            name = cleaned_data["name"]
        else:
            name = ""

        if cleaned_data["number"]:
            number = cleaned_data["number"]
        else:
            number = ""

        if cleaned_data["street_type"]:
            street_type = cleaned_data["street_type"]
        else:
            street_type = ""

        if cleaned_data["street_name"]:
            street_name = cleaned_data["street_name"]
        else:
            street_name = ""

        city = cleaned_data["city"]
        zip = cleaned_data["zip"]

        if not zip.isdigit() and len(zip) < 5:
            self.add_error(
                "zip",
                forms.ValidationError("Le code postal est composé de cinq chiffres."),
            )

        cleaned_data["slug_form"] = slugify(
            f"{name} {number} {street_type} {street_name} {zip} {city}"
        )

        return cleaned_data
