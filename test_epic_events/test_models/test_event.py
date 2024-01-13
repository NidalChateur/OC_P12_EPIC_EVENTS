from datetime import date, timedelta

import pytest
from django.utils import timezone
from django.utils.text import slugify
from phonenumbers import parse

from epic_events.models.collaborator import Collaborator, Department
from epic_events.models.contract_event import (
    Contract,
    Event,
    Location,
    events,
    events_without_support,
)
from epic_events.models.customer import Customer
from epic_events.models.str_template import unfilled


class TestEvent:
    model = Event

    def department_instance(self, role: str) -> Department:
        return Department(name=role)

    def collaborator_instance(
        self, role: str = "Commercial", number: int = 1
    ) -> Collaborator:
        return Collaborator(
            first_name=f"{number}_John",
            last_name=f"{number}_Doe",
            email=f"{number}_johndoe@gmail.com",
            phone=parse(f"+3360504030{number}", None),
            birthdate=date(year=2000, month=1, day=1),
            department=self.department_instance(role),
        )

    def customer_instance(self) -> Customer:
        return Customer(
            first_name="Jean",
            last_name="Dupont",
            email="JeanDupont@gmail.com",
            phone=parse("+33605040302", None),
            commercial=self.collaborator_instance(),
        )

    def contract_instance(self) -> Contract:
        return Contract(
            customer=self.customer_instance(),
            total_amount=5000,
        )

    def location_instance(self) -> Location:
        return Location(
            name="Tour Eiffel",
            number="5",
            street_type="avenue",
            street_name="Anatole France",
            zip="75007",
            city="Paris",
        )

    def event_instance(self) -> Event:
        return Event(
            contract=self.contract_instance(),
            location=self.location_instance(),
            support=self.collaborator_instance("Support", 2),
        )

    """ testing TimeFieldMixin methods """

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
        event = self.event_instance()
        event.contract = event.location = event.support = None
        event.save()

        timezone.now() - timedelta(
            minutes=5
        ) < event.creation_time < timezone.now() + timedelta(minutes=5)

        timezone.now() - timedelta(
            minutes=5
        ) < event.edition_time < timezone.now() + timedelta(minutes=5)

    """ testing Event methods """

    def test_address(self):
        # with not None attribute
        event = self.event_instance()
        assert event.location is not None
        assert event.address == str(event.location)

        # with None attribute
        event.location = None
        assert event.location is None
        assert event.address == unfilled

    def test_customer_name(self):
        # with not None attribute
        event = self.event_instance()
        assert event.contract is not None
        assert event.customer_name == event.contract.customer.name

        # with None attribute
        event.contract = None
        assert event.contract is None
        assert event.customer_name == unfilled

    def test_customer_email(self):
        # with not None attribute
        event = self.event_instance()
        assert event.contract is not None
        assert event.customer_email == event.contract.customer.email

        # with None attribute
        event.contract = None
        assert event.contract is None
        assert event.customer_email == unfilled

    def test_customer_phone(self):
        # with not None attribute
        event = self.event_instance()
        assert event.contract is not None
        assert event.customer_phone == event.contract.customer.formatted_phone

        # with None attribute
        event.contract = None
        assert event.contract is None
        assert event.customer_phone == unfilled

    def test_commercial_id(self):
        # with not None attribute
        event = self.event_instance()
        assert event.contract is not None
        assert event.commercial_id == event.contract.commercial_id

        # with None attribute
        event.contract = None
        assert event.contract is None
        assert event.commercial_id == unfilled

    def test_commercial_name(self):
        # with not None attribute
        event = self.event_instance()
        assert event.contract is not None
        assert event.commercial_name == event.contract.commercial_name

        # with None attribute
        event.contract = None
        assert event.contract is None
        assert event.commercial_name == unfilled

    def test_commercial_email(self):
        # with not None attribute
        event = self.event_instance()
        assert event.contract is not None
        assert event.commercial_email == event.contract.commercial_email

        # with None attribute
        event.contract = None
        assert event.contract is None
        assert event.commercial_email == unfilled

    def test_commercial_phone(self):
        # with not None attribute
        event = self.event_instance()
        assert event.contract is not None
        assert event.commercial_phone == event.contract.commercial_phone

        # with None attribute
        event.contract = None
        assert event.contract is None
        assert event.commercial_phone == unfilled

    def test_support_name(self):
        # with not None attribute
        event = self.event_instance()
        assert event.support is not None
        assert event.support_name == event.support.name

        # with None attribute
        event.support = None
        assert event.support is None
        assert event.support_name == unfilled

    def test_support_email(self):
        # with not None attribute
        event = self.event_instance()
        assert event.support is not None
        assert event.support_email == event.support.email

        # with None attribute
        event.support = None
        assert event.support is None
        assert event.support_email == unfilled

    def test_support_phone(self):
        # with not None attribute
        event = self.event_instance()
        assert event.support is not None
        assert event.support_phone == event.support.formatted_phone

        # with None attribute
        event.support = None
        assert event.support is None
        assert event.support_phone == unfilled

    def test_french_name(self):
        assert self.model.french_name() == "Événement"

    def test_french_plural_name(self):
        assert self.model.french_plural_name() == "Événements"

    @pytest.mark.django_db
    def test_save_slug(self):
        event = self.event_instance()
        event.support.department.save()
        event.support.save()
        event.location.save()
        event.contract.customer.commercial.department.save()
        event.contract.customer.commercial.save()
        event.contract.customer.save()
        event.contract.save()
        event.save()

        # test with not None attribute
        slug_commercial = slugify(event.commercial_name)
        slug_support = slugify(event.support_name)
        slug_customer = slugify(event.customer_name)
        contract_id = event.contract.id
        slug = (
            f"{event.id} {contract_id} {slug_customer} {slug_commercial} {slug_support}"
        )
        assert event.contract is not None
        assert event.support is not None
        assert event.slug == slug

        # test with None attribute
        event.contract = event.support = None
        event.save()
        slug_commercial = slugify(event.commercial_name)
        slug_support = slugify(event.support_name)
        slug_customer = slugify(event.customer_name)
        contract_id = ""
        slug = (
            f"{event.id} {contract_id} {slug_customer} {slug_commercial} {slug_support}"
        )
        assert event.contract is None
        assert event.support is None
        assert event.slug == slug

    """ test event filters """

    @pytest.mark.django_db
    def test_events(self):
        event1 = self.event_instance()
        event1.support = event1.location = event1.contract = None
        event1.save()

        event2 = self.event_instance()
        event2.location = event2.contract = None
        event2.support.department.save()
        event2.support.save()
        event2.save()

        qs1 = events()
        qs2 = Event.objects.all().order_by("-edition_time")

        assert list(qs1) == list(qs2)

        qs3 = events(support=event2.support)
        qs4 = Event.objects.filter(support=event2.support).order_by("-edition_time")

        assert list(qs3) == list(qs4)

    @pytest.mark.django_db
    def test_events_without_support(self):
        event1 = self.event_instance()
        event1.support = event1.location = event1.contract = None
        event1.save()

        event2 = self.event_instance()
        event2.location = event2.contract = event2.support = None
        event2.save()

        qs1 = events_without_support()
        qs2 = Event.objects.filter(support__isnull=True).order_by("-edition_time")

        assert list(qs1) == list(qs2)
