from django import forms
from phonenumber_field.formfields import PhoneNumberField

from ..models.customer import Customer


class CustomerForm(forms.ModelForm):
    """used by a Manager to CRUD a Customer()"""

    phone = PhoneNumberField(region="FR", label="Téléphone", required=False)

    class Meta:
        model = Customer
        fields = ("first_name", "last_name", "email", "phone")
