from django.contrib.auth import get_user_model
from django.shortcuts import get_object_or_404, render

from ..models.contract_event import (
    contracts_ready_for_event,
    signed_paid_contracts,
    signed_unpaid_contracts,
    unsigned_paid_contracts,
    unsigned_unpaid_contracts,
)
from .contract import SearchPostMixin, context, model, read_permission
from .paginator import paginator


# filter in all contracts
class SignedPaidContracts(read_permission, SearchPostMixin):
    def get(self, request, *args, **kwargs):
        qs = signed_paid_contracts()
        context["page_obj"] = paginator(request, qs)

        return render(request, model.template_name_list(), context)


class SignedUnpaidContracts(read_permission, SearchPostMixin):
    def get(self, request, *args, **kwargs):
        qs = signed_unpaid_contracts()
        context["page_obj"] = paginator(request, qs)

        return render(request, model.template_name_list(), context)


class UnsignedPaidContracts(read_permission, SearchPostMixin):
    def get(self, request, *args, **kwargs):
        qs = unsigned_paid_contracts()
        context["page_obj"] = paginator(request, qs)

        return render(request, model.template_name_list(), context)


class UnsignedUnpaidContracts(read_permission, SearchPostMixin):
    def get(self, request, *args, **kwargs):
        qs = unsigned_unpaid_contracts()
        context["page_obj"] = paginator(request, qs)

        return render(request, model.template_name_list(), context)


class ReadyForEventContracts(read_permission, SearchPostMixin):
    def get(self, request, *args, **kwargs):
        qs = contracts_ready_for_event()
        context["page_obj"] = paginator(request, qs)

        return render(request, model.template_name_list(), context)


# filter in commercial contracts
class MySignedPaidContracts(read_permission, SearchPostMixin):
    def get(self, request, id, *args, **kwargs):
        obj = get_object_or_404(get_user_model(), id=id)
        qs = signed_paid_contracts(commercial=obj)
        context["page_obj"] = paginator(request, qs)

        return render(request, model.template_name_list(), context)


class MySignedUnpaidContracts(read_permission, SearchPostMixin):
    def get(self, request, id, *args, **kwargs):
        obj = get_object_or_404(get_user_model(), id=id)
        qs = signed_unpaid_contracts(commercial=obj)
        context["page_obj"] = paginator(request, qs)

        return render(request, model.template_name_list(), context)


class MyUnsignedPaidContracts(read_permission, SearchPostMixin):
    def get(self, request, id, *args, **kwargs):
        obj = get_object_or_404(get_user_model(), id=id)
        qs = unsigned_paid_contracts(commercial=obj)
        context["page_obj"] = paginator(request, qs)

        return render(request, model.template_name_list(), context)


class MyUnsignedUnpaidContracts(read_permission, SearchPostMixin):
    def get(self, request, id, *args, **kwargs):
        obj = get_object_or_404(get_user_model(), id=id)
        qs = unsigned_unpaid_contracts(commercial=obj)
        context["page_obj"] = paginator(request, qs)

        return render(request, model.template_name_list(), context)


class MyReadyForEventContracts(read_permission, SearchPostMixin):
    def get(self, request, id, *args, **kwargs):
        obj = get_object_or_404(get_user_model(), id=id)
        qs = contracts_ready_for_event(commercial=obj)
        context["page_obj"] = paginator(request, qs)

        return render(request, model.template_name_list(), context)
