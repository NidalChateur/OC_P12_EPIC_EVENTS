from django.contrib import messages
from django.contrib.auth import get_user_model
from django.shortcuts import get_object_or_404, redirect, render
from django.utils.text import slugify
from django.views import View

from ..forms.contract import ContractForm
from ..forms.customer import CustomerForm
from ..forms.search import SearchForm
from ..models.contract_event import Contract, Event, contracts
from ..models.customer import Customer
from ..permissions import (
    LoginRequiredMixin,
    ManagerOrCommercialContractRequiredMixin,
    ManagerRequiredMixin,
)
from .paginator import paginator

model = Contract
model_form = ContractForm

relation_model = Customer
relation_form = CustomerForm

search_form = SearchForm

read_permission = LoginRequiredMixin
create_permission = ManagerRequiredMixin
update_permission = ManagerOrCommercialContractRequiredMixin
delete_permission = update_permission

context = {
    "title": model.french_plural_name(),
    "detail_url_name": model.singular_name(),
    "list_url_name": model.plural_name(),
    "my_list_url_name": model.my_list_url_name(),
    "create_url_name": model.create_url_name(),
    "update_url_name": model.update_url_name(),
    "delete_url_name": model.delete_url_name(),
    "form": search_form(placeholder=f"Rechercher {model.french_name().lower()}"),
}


class SearchPostMixin(View):
    def post(self, request, *args, **kwargs):
        """search"""

        form = search_form(request.POST)
        if form.is_valid():
            return redirect(model.search_url_name(), search=form.cleaned_data["search"])


class MyListView(read_permission, SearchPostMixin):
    def get(self, request, id, *args, **kwargs):
        obj = get_object_or_404(get_user_model(), id=id)
        qs = contracts(commercial=obj)
        context["page_obj"] = paginator(request, qs)

        return render(request, model.template_name_list(), context)


class ListView(read_permission, SearchPostMixin):
    def get(self, request, *args, **kwargs):
        qs = contracts()
        context["page_obj"] = paginator(request, qs)

        return render(request, model.template_name_list(), context)


class SearchView(read_permission, SearchPostMixin):
    def get(self, request, search, *args, **kwargs):
        qs = model.objects.filter(slug__contains=slugify(search)).order_by(
            "-edition_time"
        )

        if len(qs) < 2:
            messages.info(request, f" ℹ️ {len(qs)} résultat trouvé.")
        else:
            messages.info(request, f" ℹ️ {len(qs)} résultats trouvés.")

        context["page_obj"] = paginator(request, qs)

        return render(request, model.template_name_list(), context)


class DetailView(read_permission, View):
    def get(self, request, id, *args, **kwargs):
        context["obj"] = get_object_or_404(model, id=id)
        qs = Event.objects.filter(contract=context["obj"])

        if qs:
            context["event"] = qs[0]

        return render(request, model.template_name_detail(), context)


class CreateView(create_permission, View):
    def get(self, request, id, *args, **kwargs):
        obj = get_object_or_404(relation_model, id=id)

        return render(
            request,
            model.template_name_create(),
            {
                "model_form": model_form(),
                "title": model.french_name().lower(),
                "obj": obj,
            },
        )

    def post(self, request, id, *args, **kwargs):
        form = model_form(request.POST)

        if form.is_valid():
            obj = form.save(commit=False)
            obj.customer = get_object_or_404(relation_model, id=id)

            obj.save()
            messages.success(
                request,
                f" ✅ {model.french_name()} identifiant n°{obj.id} a été créé avec succès !",
            )

            return redirect(f"{model.singular_name()}", id=obj.id)

        return render(
            request,
            model.template_name_create(),
            {"model_form": form, "title": model.french_name().lower()},
        )


class UpdateView(update_permission, View):
    def get(self, request, id, *args, **kwargs):
        obj = get_object_or_404(model, id=id)

        return render(
            request,
            model.template_name_create(),
            {
                "model_form": model_form(instance=obj),
                "title": model.french_name().lower(),
                "obj": obj,
            },
        )

    def post(self, request, id, *args, **kwargs):
        obj = get_object_or_404(model, id=id)
        form = model_form(request.POST, instance=obj)

        if form.is_valid():
            obj.save()
            messages.success(
                request,
                f" ✅ {model.french_name()} identifiant n°{obj.id} a été modifié avec succès !",
            )

            return redirect(f"{model.singular_name()}", id=obj.id)

        return render(
            request,
            model.template_name_create(),
            {
                "model_form": form,
                "title": model.french_name().lower(),
                "obj": obj,
            },
        )


class DeleteView(delete_permission, View):
    def get(self, request, id, *args, **kwargs):
        """delete confirmation"""

        obj = get_object_or_404(model, id=id)

        return render(
            request,
            model.template_name_delete(),
            {"title": model.french_name().lower(), "obj": obj},
        )

    def post(self, request, id, *args, **kwargs):
        "delete"

        obj = get_object_or_404(model, id=id)
        obj_id = obj.id
        obj.delete()
        messages.success(
            request,
            f" ✅ {model.french_name()} identifiant n°{obj_id} a été supprimé avec succès !",
        )

        return redirect(f"{model.plural_name()}")
