from django import forms
from django.forms import DateTimeInput, Textarea

from ..models.collaborator import Collaborator
from ..models.contract_event import Event


class ChangeSupportForm(forms.ModelForm):
    """used by a Manager to change the event support"""

    class Meta:
        model = Event
        fields = ("support",)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        supports = Collaborator.objects.filter(department__name="Support")

        self.fields["support"].queryset = supports


class EventForm(forms.ModelForm):
    """used by a Manager to CRUD a customer Contract()
    used by a Commercial to update a customer Contract()"""

    # note = forms.CharField(widget=forms.Textarea(attrs={"rows": 5}))

    class Meta:
        model = Event
        fields = ("start_date", "end_date", "attendees", "note")

        widgets = {
            "start_date": DateTimeInput(attrs={"type": "datetime-local"}),
            "end_date": DateTimeInput(attrs={"type": "datetime-local"}),
            "note": Textarea(attrs={"rows": 5}),
        }

    def clean(self):
        cleaned_data = super().clean()
        start_date = cleaned_data.get("start_date")
        end_date = cleaned_data.get("end_date")

        if start_date and end_date and start_date > end_date:
            self.add_error(
                "end_date",
                forms.ValidationError(
                    "La date de fin doit avoir lieu après la date début."
                ),
            )

        return cleaned_data
