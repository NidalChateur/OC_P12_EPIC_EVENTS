from datetime import date

from django import forms
from django.contrib.auth import authenticate, get_user_model
from django.contrib.auth.forms import PasswordChangeForm, SetPasswordForm
from phonenumber_field.formfields import PhoneNumberField


class CreatePasswordForm(SetPasswordForm):
    class Meta:
        model = get_user_model()
        fields = ("password",)


class ChangePasswordForm(PasswordChangeForm):
    class Meta:
        model = get_user_model()
        fields = ("password",)


class FirstConnexionForm(forms.Form):
    id = forms.IntegerField(required=True, label="Identifiant")
    email = forms.EmailField(required=True)
    birthdate = forms.DateField(
        widget=forms.DateInput(attrs={"type": "date"}),
        required=True,
        label="Date de naissance",
    )

    def clean(self):
        cleaned_data = super().clean()
        if (
            not get_user_model()
            .objects.filter(
                id=cleaned_data.get("id"),
                email=cleaned_data.get("email"),
                birthdate=cleaned_data.get("birthdate"),
            )
            .exists()
        ):
            self.add_error("email", forms.ValidationError(""))
            self.add_error("id", forms.ValidationError(""))
            self.add_error("birthdate", forms.ValidationError(""))
            raise forms.ValidationError("Les informations entrées sont invalides.")

        try:
            collaborator = get_user_model().objects.get(
                email=cleaned_data.get("birthdate")
            )
            if collaborator.last_login:
                self.add_error("email", forms.ValidationError(""))
                self.add_error("id", forms.ValidationError(""))
                self.add_error("birthdate", forms.ValidationError(""))
                raise forms.ValidationError("Les informations entrées sont invalides.")
        except get_user_model().DoesNotExist:
            pass

        return cleaned_data


class LoginForm(forms.Form):
    email = forms.CharField(
        widget=forms.TextInput(attrs={"autofocus": True}), required=True
    )
    password = forms.CharField(
        label="Mot de passe", widget=forms.PasswordInput, required=True
    )

    def clean(self):
        cleaned_data = super().clean()
        cleaned_email = cleaned_data.get("email")
        cleaned_password = cleaned_data.get("password")

        collaborator = authenticate(email=cleaned_email, password=cleaned_password)

        if collaborator is None:
            self.add_error("email", forms.ValidationError(""))
            self.add_error("password", forms.ValidationError(""))
            raise forms.ValidationError(
                "Saisissez un email et un mot de passe valides."
            )

        return cleaned_data


class CollaboratorForm(forms.ModelForm):
    """used by a Manager to CRUD Collaborator()"""

    phone = PhoneNumberField(region="FR", label="Téléphone", required=False)

    class Meta:
        model = get_user_model()
        fields = (
            "first_name",
            "last_name",
            "birthdate",
            "email",
            "phone",
        )
        widgets = {"birthdate": forms.DateInput(attrs={"type": "date"})}

    def clean(self) -> dict:
        cleaned_data = super().clean()
        birthdate = cleaned_data.get("birthdate")

        AGE_LIMIT = 18
        today = date.today()
        age = (
            today.year
            - birthdate.year
            - ((today.month, today.day) < (birthdate.month, birthdate.day))
        )

        if age < AGE_LIMIT:
            self.add_error(
                "birthdate",
                forms.ValidationError("Le collaborateur doit avoir au moins 18 ans."),
            )

        return cleaned_data
