from datetime import date, timedelta

import pytest
from django.db.models import F, Q
from django.db.utils import IntegrityError
from django.utils import timezone
from django.utils.text import slugify
from phonenumbers import parse

from epic_events.models.collaborator import Collaborator
from epic_events.models.contract_event import (
    Contract,
    Event,
    contracts,
    contracts_ready_for_event,
    paid_contracts,
    signed_contracts,
    signed_paid_contracts,
    signed_unpaid_contracts,
    unpaid_contracts,
    unsigned_contracts,
    unsigned_paid_contracts,
    unsigned_unpaid_contracts,
)
from epic_events.models.customer import Customer
from epic_events.models.str_template import no, unfilled, yes


class TestContract:
    model = Contract

    def collaborator_instance(self) -> Collaborator:
        return Collaborator(
            first_name="John",
            last_name="Doe",
            email="johndoe@gmail.com",
            phone=parse("+33605040302", None),
            birthdate=date(year=2000, month=1, day=1),
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
        return Contract(customer=self.customer_instance(), total_amount=5000)

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
        contract = self.contract_instance()
        contract.customer.commercial.save()
        contract.customer.save()
        contract.save()

        timezone.now() - timedelta(
            minutes=5
        ) < contract.creation_time < timezone.now() + timedelta(minutes=5)

        timezone.now() - timedelta(
            minutes=5
        ) < contract.edition_time < timezone.now() + timedelta(minutes=5)

    # # testing Contract methods
    @pytest.mark.django_db
    def test_total_amount_not_null_constraint(self):
        contract = self.contract_instance()
        contract.customer.commercial.save()
        contract.customer.save()

        with pytest.raises(expected_exception=IntegrityError):
            contract.total_amount = None
            contract.save()

    @pytest.mark.django_db
    def test_amount_paid_not_null_constraint(self):
        contract = self.contract_instance()
        contract.customer.commercial.save()
        contract.customer.save()

        with pytest.raises(expected_exception=IntegrityError):
            contract.amount_paid = None
            contract.save()

    @pytest.mark.django_db
    def test_amount_is_signed_null_constraint(self):
        contract = self.contract_instance()
        contract.customer.commercial.save()
        contract.customer.save()

        with pytest.raises(expected_exception=IntegrityError):
            contract.is_signed = None
            contract.save()

    def test_is_paid(self):
        contract = self.contract_instance()

        assert contract.is_paid == (contract.total_amount - contract.amount_paid == 0)

    def test_formatted_is_signed(self):
        contract = self.contract_instance()

        assert contract.is_signed is False
        assert contract.formatted_is_signed == no

        contract.is_signed = True

        assert contract.is_signed is True
        assert contract.formatted_is_signed == yes

    def test_formatted_is_paid(self):
        contract = self.contract_instance()
        if contract.total_amount - contract.amount_paid == 0:
            is_paid = yes
        else:
            is_paid = no

        assert contract.formatted_is_paid == is_paid

    def test_remaining_amount(self):
        contract = self.contract_instance()

        assert contract.remaining_amount == contract.total_amount - contract.amount_paid

    def test_formatted_amount_paid(self):
        # test with not None attribute
        contract = self.contract_instance()
        contract.amount_paid = 1000
        formatted_amount_paid = "{:,}".format(contract.amount_paid).replace(",", " ")

        assert contract.formatted_amount_paid == formatted_amount_paid

        # test with None attribute
        contract.amount_paid = None
        assert contract.formatted_amount_paid == unfilled

    def test_formatted_total_amount(self):
        # test with not None attribute
        contract = self.contract_instance()
        formatted_total_amount = "{:,}".format(contract.total_amount).replace(",", " ")

        assert contract.formatted_total_amount == formatted_total_amount

        # test with None attribute
        contract.total_amount = None
        assert contract.formatted_total_amount == unfilled

    def test_formatted_remaining_amount(self):
        contract = self.contract_instance()

        formatted_remaining_amount = "{:,}".format(contract.remaining_amount).replace(
            ",", " "
        )

        assert contract.formatted_remaining_amount == formatted_remaining_amount

    def test_customer_name(self):
        # test with no None attribute
        contract = self.contract_instance()
        assert contract.customer_name == contract.customer.name

        # test with None attribute
        contract.customer = None
        assert contract.customer_name == unfilled

    def test_customer_email(self):
        # test with no None attribute
        contract = self.contract_instance()
        assert contract.customer_email == contract.customer.email

        # test with None attribute
        contract.customer = None
        assert contract.customer_email == unfilled

    def test_customer_phone(self):
        # test with no None attribute
        contract = self.contract_instance()
        assert contract.customer_phone == contract.customer.formatted_phone

        # test with None attribute
        contract.customer = None
        assert contract.customer_phone == unfilled

    def test_customer_has_commercial(self):
        # test with no None attribute
        contract = self.contract_instance()

        if contract.customer.commercial:
            customer_has_commercial = True
        else:
            customer_has_commercial = False

        assert contract.customer_has_commercial == customer_has_commercial

        # test with None attribute
        contract.customer.commercial = None
        assert contract.customer_has_commercial is False

        contract.customer = None
        assert contract.customer_has_commercial is False

    @pytest.mark.django_db
    def test_commercial_id(self):
        # test with no None attribute
        contract = self.contract_instance()
        contract.customer.commercial.save()
        contract.customer.save()
        assert contract.commercial_id == str(contract.customer.commercial.id)

        # test with None attribute
        contract.customer.commercial = None
        assert contract.commercial_id == unfilled

    def test_commercial_name(self):
        # test with no None attribute
        contract = self.contract_instance()
        assert contract.commercial_name == contract.customer.commercial.name

        # test with None attribute
        contract.customer.commercial = None
        assert contract.commercial_name == unfilled

    def test_commercial_email(self):
        # test with no None attribute
        contract = self.contract_instance()
        assert contract.commercial_email == contract.customer.commercial.email

        # test with None attribute
        contract.customer.commercial = None
        assert contract.commercial_email == unfilled

    def test_commercial_phone(self):
        # test with no None attribute
        contract = self.contract_instance()
        assert contract.commercial_phone == contract.customer.commercial.formatted_phone

        # test with None attribute
        contract.customer.commercial = None
        assert contract.commercial_phone == unfilled

    @pytest.mark.django_db
    def test_is_ready_for_event(self):
        # test with is_signed==False and no event
        contract = self.contract_instance()
        contract.customer.commercial.save()
        contract.customer.save()
        contract.save()

        qs = Event.objects.filter(contract=contract)
        assert contract.is_signed is False
        assert len(qs) == 0
        assert contract.is_ready_for_event is False

        # test with is_signed==True and no event
        contract.is_signed = True
        qs = Event.objects.filter(contract=contract)
        assert contract.is_signed is True
        assert len(qs) == 0
        assert contract.is_ready_for_event is True

        # test with is_signed==True and with event created
        event = Event(contract=contract)
        event.save()
        contract.is_signed = True
        qs = Event.objects.filter(contract=contract)
        assert contract.is_signed is True
        assert len(qs) > 0
        assert contract.is_ready_for_event is False

    def test_french_name(self):
        assert self.model.french_name() == "Contrat"

    def test_french_plural_name(self):
        assert self.model.french_plural_name() == "Contrats"

    @pytest.mark.django_db
    def test_save_slug(self):
        # test with no None attributes
        contract = self.contract_instance()
        contract.customer.commercial.save()
        contract.customer.save()
        contract.save()
        slug_customer = slugify(contract.customer_name)
        slug_commercial = slugify(contract.commercial_name)
        assert (
            contract.slug
            == f"{contract.id}{slug_customer}{slug_commercial}{contract.total_amount}"
        )

        contract.customer = None
        contract.save()
        assert contract.slug == f"{contract.id}{contract.total_amount}"

    # test contract filters
    @pytest.mark.django_db
    def test_contracts(self):
        contract1 = self.contract_instance()
        contract1.customer.commercial.save()
        contract1.customer.save()
        contract1.save()

        contract2 = self.contract_instance()
        contract2.customer = contract1.customer
        contract2.save()

        commercial1 = contract1.customer.commercial
        commercial2 = Collaborator(
            first_name="Paul",
            last_name="Petit",
            email="paulpetit@gmail.com",
            birthdate=date(year=2000, month=1, day=1),
        )

        commercial2.save()

        # test getting all contracts
        qs1 = contracts()
        qs2 = Contract.objects.all().order_by("-edition_time")

        assert list(qs1) == list(qs2)

        # test getting all commercial1 contract
        qs3 = contracts(commercial=commercial1)
        qs4 = Contract.objects.filter(customer__commercial=commercial1).order_by(
            "-edition_time"
        )

        assert list(qs3) == list(qs4)

        # test getting all commercial2 contract
        qs5 = contracts(commercial=commercial2)
        qs6 = Contract.objects.filter(customer__commercial=commercial2).order_by(
            "-edition_time"
        )

        assert list(qs5) == list(qs6)

    @pytest.mark.django_db
    def test_signed_contracts(self):
        contract1 = self.contract_instance()
        contract1.customer.commercial.save()
        contract1.customer.save()
        contract1.save()

        contract2 = self.contract_instance()
        contract2.customer = contract1.customer
        contract2.is_signed = True
        contract2.save()

        commercial1 = contract1.customer.commercial

        # test getting all signed contracts
        qs1 = signed_contracts()
        qs2 = Contract.objects.filter(is_signed=True).order_by("-edition_time")

        assert list(qs1) == list(qs2)

        # test getting all commercial signed contract
        qs3 = signed_contracts(commercial=commercial1)
        qs4 = qs1.filter(customer__commercial=commercial1)

        assert list(qs3) == list(qs4)

    @pytest.mark.django_db
    def test_unsigned_contracts(self):
        contract1 = self.contract_instance()
        contract1.customer.commercial.save()
        contract1.customer.save()
        contract1.save()

        contract2 = self.contract_instance()
        contract2.customer = contract1.customer
        contract2.is_signed = True
        contract2.save()

        # test getting all signed contracts
        qs1 = unsigned_contracts()
        qs2 = Contract.objects.filter(is_signed=False).order_by("-edition_time")

        assert list(qs1) == list(qs2)

    @pytest.mark.django_db
    def test_contracts_ready_for_event(self):
        contract1 = self.contract_instance()
        contract1.customer.commercial.save()
        contract1.customer.save()
        contract1.save()

        contract2 = self.contract_instance()
        contract2.customer = contract1.customer
        contract2.is_signed = True
        contract2.save()

        # test getting all contracts ready for event
        qs1 = contracts_ready_for_event()

        qs2 = Contract.objects.filter(is_signed=True).order_by("-edition_time")
        qs3 = qs2.exclude(Q(id__in=Event.objects.values("contract__id")))

        assert list(qs1) == list(qs3)
        assert contract1.is_ready_for_event is False
        assert contract2.is_ready_for_event is True
        assert len(qs1) == len(qs3) == 1

    @pytest.mark.django_db
    def test_unpaid_contracts(self):
        contract1 = self.contract_instance()
        contract1.customer.commercial.save()
        contract1.customer.save()
        contract1.save()

        contract2 = self.contract_instance()
        contract2.customer = contract1.customer
        contract2.is_signed = True
        contract2.save()

        qs1 = unpaid_contracts()
        qs2 = Contract.objects.filter(amount_paid__lt=F("total_amount")).order_by(
            "-edition_time"
        )

        assert list(qs1) == list(qs2)

    @pytest.mark.django_db
    def test_paid_contracts(self):
        contract1 = self.contract_instance()
        contract1.customer.commercial.save()
        contract1.customer.save()
        contract1.save()

        contract2 = self.contract_instance()
        contract2.customer = contract1.customer
        contract2.is_signed = True
        contract2.amount_paid = contract2.total_amount
        contract2.save()

        qs1 = paid_contracts()
        qs2 = Contract.objects.filter(amount_paid=F("total_amount")).order_by(
            "-edition_time"
        )

        assert list(qs1) == list(qs2)

    @pytest.mark.django_db
    def test_signed_unpaid_contracts(self):
        contract1 = self.contract_instance()
        contract1.customer.commercial.save()
        contract1.customer.save()
        contract1.save()

        contract2 = self.contract_instance()
        contract2.customer = contract1.customer
        contract2.is_signed = True
        contract2.save()

        qs1 = signed_unpaid_contracts()
        qs2 = Contract.objects.filter(
            is_signed=True, amount_paid__lt=F("total_amount")
        ).order_by("-edition_time")

        assert list(qs1) == list(qs2)

    @pytest.mark.django_db
    def test_signed_paid_contracts(self):
        contract1 = self.contract_instance()
        contract1.customer.commercial.save()
        contract1.customer.save()
        contract1.save()

        contract2 = self.contract_instance()
        contract2.customer = contract1.customer
        contract2.is_signed = True
        contract2.amount_paid = contract2.total_amount
        contract2.save()

        qs1 = signed_paid_contracts()
        qs2 = Contract.objects.filter(
            is_signed=True, amount_paid=F("total_amount")
        ).order_by("-edition_time")

        assert list(qs1) == list(qs2)

    @pytest.mark.django_db
    def test_unsigned_unpaid_contracts(self):
        contract1 = self.contract_instance()
        contract1.customer.commercial.save()
        contract1.customer.save()
        contract1.save()

        contract2 = self.contract_instance()
        contract2.customer = contract1.customer
        contract2.is_signed = True
        contract2.amount_paid = contract2.total_amount
        contract2.save()

        qs1 = unsigned_unpaid_contracts()
        qs2 = Contract.objects.filter(
            is_signed=False, amount_paid__lt=F("total_amount")
        ).order_by("-edition_time")

        assert list(qs1) == list(qs2)

    @pytest.mark.django_db
    def test_unsigned_paid_contracts(self):
        contract1 = self.contract_instance()
        contract1.customer.commercial.save()
        contract1.customer.save()
        contract1.save()

        contract2 = self.contract_instance()
        contract2.customer = contract1.customer
        contract2.is_signed = True
        contract2.amount_paid = contract2.total_amount
        contract2.save()

        qs1 = unsigned_paid_contracts()
        qs2 = Contract.objects.filter(
            is_signed=False, amount_paid=F("total_amount")
        ).order_by("-edition_time")

        assert list(qs1) == list(qs2)
