from django import forms

from ..models.contract_event import Contract


class ContractForm(forms.ModelForm):
    """used by a Manager to CRUD a customer Contract()
    used by a Commercial to update a customer Contract()"""

    class Meta:
        model = Contract
        fields = (
            "total_amount",
            "amount_paid",
            "is_signed",
        )

    def clean(self):
        cleaned_data = super().clean()
        total_amount = cleaned_data.get("total_amount")
        amount_paid = cleaned_data.get("amount_paid")

        if amount_paid > total_amount:
            self.add_error(
                "amount_paid",
                forms.ValidationError(
                    "Le montant payé par le client ne peut pas excéder le montant total."
                ),
            )

        return cleaned_data
