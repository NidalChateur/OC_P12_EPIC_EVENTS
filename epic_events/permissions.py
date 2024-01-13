from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.shortcuts import get_object_or_404

from .models.contract_event import Contract, Event


class CommercialRequiredMixin(LoginRequiredMixin, UserPassesTestMixin):
    """used in customer, company and location views (CRUD)"""

    def test_func(self):
        """permission"""

        return self.request.user.role == "Commercial"


class ManagerRequiredMixin(LoginRequiredMixin, UserPassesTestMixin):
    """used in contract views (CRUD) or in event view (change event support)"""

    def test_func(self):
        """permission"""

        return self.request.user.role == "Gestion"


class ManagerOrCommercialContractRequiredMixin(LoginRequiredMixin, UserPassesTestMixin):
    """used in contract views (update or delete contract)"""

    def test_func(self):
        """permission"""

        id = (
            self.request.path.replace("/contracts/", "")
            .replace("/update/", "")
            .replace("/delete/", "")
        )
        contract = get_object_or_404(Contract, id=int(id))

        return (
            self.request.user.str_id == contract.commercial_id
            or self.request.user.role == "Gestion"
        )


class CommercialEventRequiredMixin(LoginRequiredMixin, UserPassesTestMixin):
    """used in event view (create event)"""

    def test_func(self):
        """permission"""

        id = self.request.path.replace("/contracts/", "").replace("/events/create/", "")
        contract = get_object_or_404(Contract, id=int(id))

        return (
            contract.is_ready_for_event
            and self.request.user.str_id == contract.commercial_id
        )


class CommercialOrSupportEventRequiredMixin(LoginRequiredMixin, UserPassesTestMixin):
    """used in event views (update or delete event)"""

    def test_func(self):
        """permission"""

        id = (
            self.request.path.replace("/events/", "")
            .replace("/update/", "")
            .replace("/delete/", "")
        )
        event = get_object_or_404(Event, id=int(id))

        return (
            self.request.user.str_id == event.commercial_id
            or self.request.user.id == event.support.id
        )
