from datetime import timedelta

import pytest
from django.db.utils import IntegrityError
from django.utils import timezone
from django.utils.text import slugify

from epic_events.models.company import Company
from epic_events.models.str_template import unfilled


class TestCompany:
    model = Company

    def company_instance(self) -> Company:
        return self.model(name="entreprise")

    # testing TimeFieldMixin methods
    def test_singular_name(self):
        assert self.model.singular_name() == self.model.__name__.lower()

    def test_plural_name(self):
        assert self.model.plural_name() == "companies"

    def test_template_name_list(self):
        assert (
            self.model.template_name_list()
            == f"{self.model.__name__.lower()}/list.html"
        )

    def test_template_name_detail(self):
        assert (
            self.model.template_name_detail()
            == f"{self.model.__name__.lower()}/detail.html"
        )

    def test_template_name_create(self):
        assert (
            self.model.template_name_create()
            == f"{self.model.__name__.lower()}/form.html"
        )

    def test_template_name_delete(self):
        assert (
            self.model.template_name_delete()
            == f"{self.model.__name__.lower()}/delete.html"
        )

    def test_my_list_url_name(self):
        assert self.model.my_list_url_name() == "my_companies"

    def test_create_url_name(self):
        assert self.model.create_url_name() == f"create_{self.model.__name__.lower()}"

    def test_update_url_name(self):
        assert self.model.update_url_name() == f"update_{self.model.__name__.lower()}"

    def test_delete_url_name(self):
        assert self.model.delete_url_name() == f"delete_{self.model.__name__.lower()}"

    def test_search_url_name(self):
        assert self.model.search_url_name() == f"search_{self.model.__name__.lower()}"

    @pytest.mark.django_db
    def test_save_time(self):
        company = self.company_instance()
        company.save()

        timezone.now() - timedelta(
            minutes=5
        ) < company.creation_time < timezone.now() + timedelta(minutes=5)

        timezone.now() - timedelta(
            minutes=5
        ) < company.edition_time < timezone.now() + timedelta(minutes=5)

    # testing NameFieldMixin methods
    def test_str(self):
        # test a Department with a not None attribute
        company = self.company_instance()
        assert str(company) == company.name.capitalize()

        # test a Department with a None attributes
        company.name = None
        assert str(company) == unfilled

    @pytest.mark.django_db
    def test_save_slug(self):
        company = self.company_instance()
        company.save()
        slug_name = slugify(company.name)
        assert company.slug == f"{company.id} {slug_name}"

    @pytest.mark.django_db
    def test_name_not_null_constraint(self):
        company = self.company_instance()
        company.save()

        with pytest.raises(expected_exception=IntegrityError):
            company.name = None
            company.save()

    # testing Company methods
    def test_french_name(self):
        assert self.model.french_name() == "Entreprise"

    def test_french_plural_name(self):
        assert self.model.french_plural_name() == "Entreprises"
