from datetime import date, timedelta

import pytest
from django.db.utils import IntegrityError
from django.utils import timezone
from django.utils.text import slugify
from phonenumbers import parse
from phonenumbers.phonenumberutil import NumberParseException

from epic_events.models.collaborator import Collaborator, Department
from epic_events.models.customer import Company, Customer
from epic_events.models.str_template import unfilled


class TestCustomer:
    model = Customer

    def department_instance(self) -> Department:
        return Department(name="Commercial")

    def collaborator_instance(self) -> Collaborator:
        return Collaborator(
            first_name="John",
            last_name="Doe",
            email="johndoe@gmail.com",
            phone=parse("+33605040302", None),
            birthdate=date(year=2000, month=1, day=1),
            department=self.department_instance(),
        )

    def company_instance(self) -> Company:
        return Company(name="Entreprise")

    def customer_instance(self) -> Customer:
        return self.model(
            first_name="Jean",
            last_name="Dupont",
            email="JeanDupont@gmail.com",
            phone=parse("+33605040302", None),
            company=self.company_instance(),
            commercial=self.collaborator_instance(),
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
        customer = self.customer_instance()
        customer.commercial = None
        customer.company = None
        customer.save()

        timezone.now() - timedelta(
            minutes=5
        ) < customer.creation_time < timezone.now() + timedelta(minutes=5)

        timezone.now() - timedelta(
            minutes=5
        ) < customer.edition_time < timezone.now() + timedelta(minutes=5)

    # testing UserMixin methods
    @pytest.mark.django_db
    def test_first_name_not_null_constraint(self):
        customer = self.customer_instance()
        customer.commercial = customer.company = None

        with pytest.raises(expected_exception=IntegrityError):
            customer.first_name = None
            customer.save()

    @pytest.mark.django_db
    def test_last_name_not_null_constraint(self):
        customer = self.customer_instance()
        customer.commercial = customer.company = None

        with pytest.raises(expected_exception=IntegrityError):
            customer.last_name = None
            customer.save()

    @pytest.mark.django_db
    def test_email_not_null_constraint(self):
        customer = self.customer_instance()
        customer.commercial = customer.company = None

        with pytest.raises(expected_exception=IntegrityError):
            customer.email = None
            customer.save()

    @pytest.mark.django_db
    def test_email_unique_constraint(self):
        customer = self.customer_instance()
        customer.commercial = customer.company = None
        customer.save()

        with pytest.raises(expected_exception=IntegrityError):
            customer2 = self.customer_instance()
            customer2.commercial = customer2.company = None
            customer2.save()

    def test_str(self):
        # test a Customer with not None attributes
        customer = self.customer_instance()
        first_name = customer.first_name.capitalize()
        last_name = customer.last_name.capitalize()
        assert str(customer) == f"{first_name} {last_name}"

        # test a Customer with None attributes
        customer.first_name = customer.last_name = None
        assert str(customer) == f"{unfilled} {unfilled}"

    def test_name(self):
        # test a Customer with not None attributes
        customer = self.customer_instance()
        assert customer.name == str(customer)

        # test a Customer with None attributes
        customer.first_name = customer.last_name = None
        assert customer.name == str(customer)

    def test_formatted_phone(self):
        # test a Customer with a valid phone number
        customer = self.customer_instance()
        assert customer.formatted_phone == "+33 6 05 04 03 02"

        # test a Customer with a None phone number
        customer.phone = None
        assert customer.formatted_phone == unfilled

        # test a Customer with an invalid phone number
        with pytest.raises(expected_exception=NumberParseException):
            customer.phone = parse("1234", None)

    @pytest.mark.django_db
    def test_save_slug(self):
        # test Customer with not None foreign keys
        customer = self.customer_instance()
        customer.company.save()
        customer.commercial.department.save()
        customer.commercial.save()
        customer.save()

        slug_first_name = slugify(customer.first_name)
        slug_last_name = slugify(customer.last_name)
        slug_email = slugify(customer.email)
        slug_foreign_key = (
            f"{slugify(customer.company_name)} {slugify(customer.commercial_name)}"
        )

        assert (
            customer.slug
            == f"{customer.id} {slug_first_name} {slug_last_name} {slug_email} {slug_foreign_key}"
        )

        # test Customer with None foreign keys
        customer.commercial = customer.company = None
        customer.save()
        slug_foreign_key = f"{slugify(unfilled)} {slugify(unfilled)}"

        assert (
            customer.slug
            == f"{customer.id} {slug_first_name} {slug_last_name} {slug_email} {slug_foreign_key}"
        )

    # testing Customer methods
    @pytest.mark.django_db
    def test_company_name(self):
        # test Customer with a not None company
        customer = self.customer_instance()
        customer.company.save()
        customer.commercial = None
        customer.save()

        assert customer.company_name == customer.company.name.capitalize()

        # test Customer with a None company
        customer.company = None
        customer.save()

        assert customer.company_name == unfilled

    @pytest.mark.django_db
    def test_commercial_name(self):
        # test Customer with a not None commercial
        customer = self.customer_instance()
        customer.company = None
        customer.commercial.department.save()
        customer.commercial.save()
        customer.save()

        assert customer.commercial_name == customer.commercial.name

        # test Customer with a None commercial
        customer.commercial = None
        customer.save()

        assert customer.company_name == unfilled

    def test_french_name(self):
        assert self.model.french_name() == "Client"

    def test_french_plural_name(self):
        assert self.model.french_plural_name() == "Clients"
