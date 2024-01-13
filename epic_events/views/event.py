from django.contrib import messages
from django.contrib.auth import get_user_model
from django.shortcuts import get_object_or_404, redirect, render
from django.utils.text import slugify
from django.views import View

from ..forms.contract import ContractForm
from ..forms.event import ChangeSupportForm, EventForm
from ..forms.location import LocationForm
from ..forms.search import SearchForm
from ..models.contract_event import Contract, Event, events, events_without_support
from ..models.location import Location
from ..permissions import (
    CommercialEventRequiredMixin,
    CommercialOrSupportEventRequiredMixin,
    LoginRequiredMixin,
    ManagerRequiredMixin,
)
from .paginator import paginator

model = Event
model_form = EventForm
model_form2 = ChangeSupportForm

relation1_model = Contract
relation1_form = ContractForm

relation2_model = Location
relation2_form = LocationForm

search_form = SearchForm

read_permission = LoginRequiredMixin
create_permission = CommercialEventRequiredMixin
change_support_permission = ManagerRequiredMixin
update_permission = CommercialOrSupportEventRequiredMixin
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
        qs = events(support=obj)
        context["page_obj"] = paginator(request, qs)

        return render(request, model.template_name_list(), context)


class ListEventsWithoutSupport(read_permission, SearchPostMixin):
    def get(self, request, *args, **kwargs):
        qs = events_without_support()
        context["page_obj"] = paginator(request, qs)

        return render(request, model.template_name_list(), context)


class ListView(read_permission, SearchPostMixin):
    def get(self, request, *args, **kwargs):
        qs = events()
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

        return render(request, model.template_name_detail(), context)


class CreateView(create_permission, View):
    def get(self, request, id, *args, **kwargs):
        obj = get_object_or_404(relation1_model, id=id)

        return render(
            request,
            model.template_name_create(),
            {
                "model_form": model_form(),
                "relation2_form": relation2_form(),
                "title": model.french_name().lower(),
                "obj": obj,
            },
        )

    def post(self, request, id, *args, **kwargs):
        form1 = model_form(request.POST)
        form2 = relation2_form(request.POST)

        if all([form1.is_valid(), form2.is_valid()]):
            obj1 = form1.save(commit=False)
            obj1.contract = get_object_or_404(relation1_model, id=id)

            # check if location exists
            qs = relation2_model.objects.filter(
                slug_form=form2.cleaned_data["slug_form"]
            )
            if qs:
                obj2 = qs[0]
                obj1.location = obj2
            else:
                obj2 = form2.save()
                obj1.location = obj2

            obj1.save()
            obj2.save()

            messages.success(
                request,
                f" ✅ {model.french_name()} identifiant n°{obj1.id} a été créé avec succès !",
            )

            return redirect(f"{model.singular_name()}", id=obj1.id)

        return render(
            request,
            model.template_name_create(),
            {
                "model_form": form1,
                "relation2_form": form2,
                "title": model.french_name().lower(),
            },
        )


class UpdateView(update_permission, View):
    def get(self, request, id, *args, **kwargs):
        obj = get_object_or_404(model, id=id)

        return render(
            request,
            model.template_name_create(),
            {
                "model_form": model_form(instance=obj),
                "relation2_form": relation2_form(instance=obj.location),
                "title": model.french_name().lower(),
                "obj": obj,
            },
        )

    def post(self, request, id, *args, **kwargs):
        obj = get_object_or_404(model, id=id)
        form1 = model_form(request.POST, instance=obj)
        form2 = relation2_form(request.POST, instance=obj.location)

        if all([form1.is_valid(), form2.is_valid()]):
            form1.save()

            # check if location exists
            qs = relation2_model.objects.filter(
                slug_form=form2.cleaned_data["slug_form"]
            )
            if qs:
                obj.location = qs[0]
            else:
                new_location = Location(
                    name=form2.cleaned_data["name"],
                    number=form2.cleaned_data["number"],
                    street_type=form2.cleaned_data["street_type"],
                    street_name=form2.cleaned_data["street_name"],
                    city=form2.cleaned_data["city"],
                    zip=form2.cleaned_data["zip"],
                )
                new_location.save()
                obj.location = new_location

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
                "model_form": form1,
                "relation2_form": form2,
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


class ChangeSupportView(change_support_permission, View):
    def get(self, request, id, *args, **kwargs):
        obj = get_object_or_404(model, id=id)

        return render(
            request,
            model.template_name_create(),
            {
                "model_form": model_form2(instance=obj),
                "title": model.french_name().lower(),
                "obj": obj,
            },
        )

    def post(self, request, id, *args, **kwargs):
        obj = get_object_or_404(model, id=id)
        form = model_form2(request.POST, instance=obj)

        if form.is_valid():
            form.save()

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
