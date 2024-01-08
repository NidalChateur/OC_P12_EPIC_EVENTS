from django.db import models
from django.db.models import F, Q
from django.utils.text import slugify

from .collaborator import Collaborator
from .customer import Customer
from .location import Location
from .mixins import TimeFieldMixin
from .str_template import no, unfilled, yes


class Contract(TimeFieldMixin):
    customer = models.ForeignKey(to=Customer, on_delete=models.CASCADE, null=True)
    total_amount = models.PositiveIntegerField(
        default=0, verbose_name="Montant total €"
    )
    amount_paid = models.PositiveIntegerField(default=0, verbose_name="Montant payé €")
    is_signed = models.BooleanField(default=False, verbose_name="Signé")

    @property
    def is_paid(self) -> bool:
        return self.total_amount - self.amount_paid == 0

    def _formatted_bool(self, bool: bool) -> str:
        if bool:
            return yes
        return no

    @property
    def formatted_is_signed(self) -> str:
        return self._formatted_bool(self.is_signed)

    @property
    def formatted_is_paid(self) -> str:
        return self._formatted_bool(self.is_paid)

    @property
    def remaining_amount(self) -> float:
        return self.total_amount - self.amount_paid

    def _number_formatter(self, number: float) -> str:
        if number or number == 0:
            return "{:,}".format(number).replace(",", " ")
        return unfilled

    @property
    def formatted_amount_paid(self) -> str:
        return self._number_formatter(self.amount_paid)

    @property
    def formatted_total_amount(self) -> str:
        return self._number_formatter(self.total_amount)

    @property
    def formatted_remaining_amount(self) -> str:
        return self._number_formatter(self.remaining_amount)

    @property
    def customer_name(self) -> str:
        if self.customer:
            return self.customer.name
        return unfilled

    @property
    def customer_email(self) -> str:
        if self.customer:
            return self.customer.email
        return unfilled

    @property
    def customer_phone(self) -> str:
        if self.customer:
            return self.customer.formatted_phone
        return unfilled

    @property
    def customer_has_commercial(self) -> bool:
        if self.customer.commercial:
            return True
        return False

    @property
    def commercial_id(self) -> str:
        if self.customer_has_commercial:
            return self.customer.commercial.str_id
        return unfilled

    @property
    def commercial_name(self) -> str:
        if self.customer_has_commercial:
            return self.customer.commercial.name
        return unfilled

    @property
    def commercial_email(self) -> str:
        if self.customer_has_commercial:
            return self.customer.commercial.email
        return unfilled

    @property
    def commercial_phone(self) -> str:
        if self.customer_has_commercial:
            return self.customer.commercial.formatted_phone
        return unfilled

    @property
    def is_ready_for_event(self) -> bool:
        qs = Event.objects.filter(contract=self)
        if self.is_signed and len(qs) == 0:
            return True
        return False

    @classmethod
    def french_name(self) -> str:
        """used in flash messages"""

        return "Contrat"

    @classmethod
    def french_plural_name(self) -> str:
        """used as title in template 'list'"""

        return f"{self.french_name()}s"

    def save(self, *args, **kwargs):
        # first save to generate self.id
        super().save(*args, **kwargs)

        # building slug field
        if self.customer:
            slug_customer = f"{slugify(self.customer_name)}"
        else:
            slug_customer = ""

        if self.customer.commercial:
            slug_commercial = f"{slugify(self.commercial_name)}"
        else:
            slug_commercial = ""

        self.slug = f"{self.id} {slug_customer} {slug_commercial} {self.total_amount}"

        super().save(*args, **kwargs)


class Event(TimeFieldMixin):
    contract = models.ForeignKey(to=Contract, on_delete=models.RESTRICT, null=True)
    location = models.ForeignKey(to=Location, on_delete=models.SET_NULL, null=True)
    support = models.ForeignKey(
        to=Collaborator, on_delete=models.SET_NULL, null=True, blank=True
    )

    attendees = models.PositiveIntegerField(
        default=0, verbose_name="Nombre de participants"
    )
    start_date = models.DateTimeField(
        verbose_name="Date de début", null=True, blank=True
    )
    end_date = models.DateTimeField(verbose_name="Date de fin", null=True, blank=True)
    note = models.TextField(max_length=2048, null=True, blank=True)

    @property
    def address(self):
        if self.location:
            return f"{self.location.formatted_name}, {self.location.formatted_address}"
        return unfilled

    @property
    def customer_name(self):
        if self.contract:
            return self.contract.customer_name
        return unfilled

    @property
    def customer_email(self):
        if self.contract:
            return self.contract.customer_email
        return unfilled

    @property
    def customer_phone(self):
        if self.contract:
            return self.contract.customer_phone
        return unfilled

    @property
    def commercial_id(self):
        if self.contract:
            return self.contract.commercial_id
        return unfilled

    @property
    def commercial_name(self):
        if self.contract:
            return self.contract.commercial_name
        return unfilled

    @property
    def commercial_email(self):
        if self.contract:
            return self.contract.commercial_email
        return unfilled

    @property
    def commercial_phone(self):
        if self.contract:
            return self.contract.commercial_phone
        return unfilled

    @property
    def support_id(self):
        if self.support:
            return self.support.str_id
        return unfilled

    @property
    def support_name(self):
        if self.support:
            return self.support.name
        return unfilled

    @property
    def support_email(self):
        if self.support:
            return self.support.email
        return unfilled

    @property
    def support_phone(self):
        if self.support:
            return self.support.formatted_phone
        return unfilled

    @classmethod
    def french_name(self) -> str:
        """used in flash messages"""

        return "Événement"

    @classmethod
    def french_plural_name(self) -> str:
        """used as title in template 'list'"""

        return f"{self.french_name()}s"

    def save(self, *args, **kwargs):
        # first save to generate self.id
        super().save(*args, **kwargs)
        # building the slug field
        customer_name = slugify(self.customer_name)
        commercial_name = slugify(self.commercial_name)
        support_name = slugify(self.support_name)

        if self.contract:
            contract_id = self.contract.id
        else:
            contract_id = ""

        self.slug = (
            f"{self.id} {contract_id} {customer_name} {commercial_name} {support_name}"
        )
        super().save(*args, **kwargs)


""" Event filter """


def events(support: Collaborator = None) -> list[Event]:
    if support:
        return Event.objects.filter(support=support).order_by("-edition_time")

    return Event.objects.all().order_by("-edition_time")


def events_without_support() -> list[Event]:
    return events().filter(support__isnull=True)


""" Contract filter """


def contracts(commercial: Collaborator = None) -> list[Contract]:
    if commercial:
        return Contract.objects.filter(customer__commercial=commercial).order_by(
            "-edition_time"
        )

    return Contract.objects.all().order_by("-edition_time")


def signed_contracts(commercial: Collaborator = None) -> list[Contract]:
    return contracts(commercial).filter(is_signed=True)


def unsigned_contracts(commercial: Collaborator = None) -> list[Contract]:
    return contracts(commercial).filter(is_signed=False)


def contracts_ready_for_event(commercial: Collaborator = None) -> list[Contract]:
    return signed_contracts(commercial).exclude(
        Q(id__in=Event.objects.values("contract__id"))
    )


def unpaid_contracts(commercial: Collaborator = None) -> list[Contract]:
    return contracts(commercial).filter(amount_paid__lt=F("total_amount"))


def paid_contracts(commercial: Collaborator = None) -> list[Contract]:
    return contracts(commercial).filter(amount_paid=F("total_amount"))


def signed_unpaid_contracts(commercial: Collaborator = None) -> list[Contract]:
    return signed_contracts(commercial).filter(amount_paid__lt=F("total_amount"))


def signed_paid_contracts(commercial: Collaborator = None) -> list[Contract]:
    return signed_contracts(commercial).filter(amount_paid=F("total_amount"))


def unsigned_unpaid_contracts(commercial: Collaborator = None) -> list[Contract]:
    return unsigned_contracts(commercial).filter(amount_paid__lt=F("total_amount"))


def unsigned_paid_contracts(commercial: Collaborator = None) -> list[Contract]:
    return unsigned_contracts(commercial).filter(amount_paid=F("total_amount"))
