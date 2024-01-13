from datetime import timedelta

import pytest
from django.db.utils import IntegrityError
from django.utils import timezone
from django.utils.text import slugify

from epic_events.models.collaborator import Department
from epic_events.models.str_template import unfilled


class TestDepartment:
    model = Department

    def department_instance(self) -> Department:
        return self.model(name="Commercial")

    # testing TimeFieldMixin methods
    def test_singular_name(self):
        assert self.model.singular_name() == self.model.__name__.lower()

    def test_plural_name(self):
        assert self.model.plural_name() == self.model.__name__.lower() + "s"

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
        assert self.model.my_list_url_name() == f"my_{self.model.__name__.lower()}s"

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
        department = self.department_instance()
        department.save()

        timezone.now() - timedelta(
            minutes=5
        ) < department.creation_time < timezone.now() + timedelta(minutes=5)

        timezone.now() - timedelta(
            minutes=5
        ) < department.edition_time < timezone.now() + timedelta(minutes=5)

    # testing NameFieldMixin methods
    @pytest.mark.django_db
    def test_name_not_null_constraint(self):
        department = self.department_instance()
        department.save()

        with pytest.raises(expected_exception=IntegrityError):
            department.name = None
            department.save()

    def test_str(self):
        # test a Department with a not None attribute
        department = self.department_instance()
        assert str(department) == department.name.capitalize()

        # test a Department with a None attributes
        department.name = None
        assert str(department) == unfilled

    @pytest.mark.django_db
    def test_save_slug(self):
        department = self.department_instance()
        department.save()
        slug_name = slugify(department.name)
        assert department.slug == f"{department.id} {slug_name}"

    # testing Department methods
    def test_french_name(self):
        assert self.model.french_name() == "Département"

    def test_french_plural_name(self):
        assert self.model.french_plural_name() == "Départements"
