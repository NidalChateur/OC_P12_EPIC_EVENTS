from datetime import date, timedelta

import pytest
from django.db.utils import IntegrityError
from django.utils import timezone
from django.utils.text import slugify
from phonenumbers import parse
from phonenumbers.phonenumberutil import NumberParseException

from epic_events.models.collaborator import Collaborator, Department
from epic_events.models.str_template import unfilled


class TestCollaborator:
    model = Collaborator

    def department_instance(self) -> Department:
        return Department(name="Commercial")

    def collaborator_instance(self) -> Collaborator:
        return self.model(
            first_name="John",
            last_name="Doe",
            email="johndoe@gmail.com",
            phone=parse("+33605040302", None),
            birthdate=date(year=2000, month=1, day=1),
            department=self.department_instance(),
        )

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
        collaborator = self.collaborator_instance()
        collaborator.department = None
        collaborator.save()

        timezone.now() - timedelta(
            minutes=5
        ) < collaborator.creation_time < timezone.now() + timedelta(minutes=5)

        timezone.now() - timedelta(
            minutes=5
        ) < collaborator.edition_time < timezone.now() + timedelta(minutes=5)

    # testing UserMixin methods
    @pytest.mark.django_db
    def test_first_name_not_null_constraint(self):
        collaborator = self.collaborator_instance()
        collaborator.department.save()
        collaborator.save()

        with pytest.raises(expected_exception=IntegrityError):
            collaborator.first_name = None
            collaborator.save()

    @pytest.mark.django_db
    def test_last_name_not_null_constraint(self):
        collaborator = self.collaborator_instance()
        collaborator.department.save()
        collaborator.save()

        with pytest.raises(expected_exception=IntegrityError):
            collaborator.last_name = None
            collaborator.save()

    @pytest.mark.django_db
    def test_email_not_null_constraint(self):
        collaborator = self.collaborator_instance()
        collaborator.department.save()
        collaborator.save()

        with pytest.raises(expected_exception=IntegrityError):
            collaborator.email = None
            collaborator.save()

    @pytest.mark.django_db
    def test_email_unique_constraint(self):
        collaborator = self.collaborator_instance()
        collaborator.department.save()
        collaborator.save()

        with pytest.raises(expected_exception=IntegrityError):
            collaborator2 = self.collaborator_instance()
            collaborator2.department = None
            collaborator2.save()

    def test_str(self):
        # test a Collaborator with not None attributes
        collaborator = self.collaborator_instance()
        first_name = collaborator.first_name.capitalize()
        last_name = collaborator.last_name.capitalize()
        assert str(collaborator) == f"{first_name} {last_name}"

        # test a Collaborator with None attributes
        collaborator.first_name = collaborator.last_name = None
        assert str(collaborator) == f"{unfilled} {unfilled}"

    def test_name(self):
        # test a Collaborator with not None attributes
        collaborator = self.collaborator_instance()
        assert str(collaborator) == collaborator.name

        # test a Collaborator with None attributes
        collaborator.first_name = collaborator.last_name = None
        assert str(collaborator) == collaborator.name

    def test_formatted_phone(self):
        # test a Collaborator with a valid phone number
        collaborator = self.collaborator_instance()
        assert collaborator.formatted_phone == "+33 6 05 04 03 02"

        # test a Collaborator with a None phone number
        collaborator.phone = None
        assert collaborator.formatted_phone == unfilled

        # test a Collaborator with an invalid phone number
        with pytest.raises(expected_exception=NumberParseException):
            collaborator.phone = parse("1234", None)

    @pytest.mark.django_db
    def test_save_slug(self):
        collaborator = self.collaborator_instance()
        collaborator.department.save()
        collaborator.save()

        slug_first_name = slugify(collaborator.first_name)
        slug_last_name = slugify(collaborator.last_name)
        slug_email = slugify(collaborator.email)
        slug_role = slugify(collaborator.role)

        assert (
            collaborator.slug
            == f"{collaborator.id} {slug_first_name} {slug_last_name} {slug_email} {slug_role}"
        )

    # testing Collaborator methods
    @pytest.mark.django_db
    def test_first_birthdate_not_null_constraint(self):
        collaborator = self.collaborator_instance()
        collaborator.department.save()
        collaborator.save()

        with pytest.raises(expected_exception=IntegrityError):
            collaborator.birthdate = None
            collaborator.save()

    @pytest.mark.django_db
    def test_str_id(self):
        department = self.department_instance()
        department.save()

        collaborator = self.collaborator_instance()
        collaborator.department = department
        collaborator.save()

        assert collaborator.str_id == str(collaborator.id)

    def test_role(self):
        # test with a not None department
        collaborator = self.collaborator_instance()
        assert collaborator.role == collaborator.department.name

        # test with a None department
        collaborator.department = None
        assert collaborator.role == unfilled

    def test_title(self):
        # test with a not None first_name
        collaborator = self.collaborator_instance()
        first_name = collaborator.first_name.capitalize()
        assert collaborator.title == f"{collaborator.role} {first_name}"

        # test with a None first_name
        collaborator.first_name = None
        assert collaborator.title == f"{collaborator.role} {unfilled}"

    def test_french_name(self):
        assert self.model.french_name() == "Collaborateur"

    def test_french_plural_name(self):
        assert self.model.french_plural_name() == "Collaborateurs"
