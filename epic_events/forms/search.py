from django import forms


class SearchForm(forms.Form):
    search = forms.CharField(
        widget=forms.TextInput(attrs={"class": "form-control me-2"}),
        required=True,
    )

    def __init__(self, *args, **kwargs):
        """allow to change the search.placeholder in view"""

        placeholder = kwargs.pop("placeholder", "Rechercher")
        super(SearchForm, self).__init__(*args, **kwargs)
        self.fields["search"].widget.attrs["placeholder"] = placeholder
