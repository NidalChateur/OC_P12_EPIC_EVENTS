from django import forms

from ..models.department import Department


class DepartmentForm(forms.ModelForm):
    """used by a Manager to CRUD a Department()"""

    name = forms.CharField(
        label="Nom du département",
        required=True,
        widget=forms.Select(
            choices=[
                ("Commercial", "Commercial"),
                ("Support", "Support"),
                ("Gestion", "Gestion"),
            ]
        ),
    )

    class Meta:
        model = Department
        fields = ["name"]
