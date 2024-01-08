from django import forms

from ..models.company import Company


class CompanyForm(forms.ModelForm):
    """used by a Commercial to CRUD a customer Company()"""

    name = forms.CharField(label="Nom de l'entreprise", required=True)

    class Meta:
        model = Company
        fields = ["name"]
