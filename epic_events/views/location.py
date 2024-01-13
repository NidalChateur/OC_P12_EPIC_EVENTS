from django.contrib import messages
from django.shortcuts import get_object_or_404, redirect, render
from django.utils.text import slugify
from django.views import View

from ..forms.location import LocationForm
from ..forms.search import SearchForm
from ..models.location import Location
from ..permissions import CommercialRequiredMixin, LoginRequiredMixin
from .paginator import paginator

model = Location
model_form = LocationForm

search_form = SearchForm

permission1 = LoginRequiredMixin
permission2 = CommercialRequiredMixin

context = {
    "title": model.french_plural_name(),
    "detail_url_name": model.singular_name(),
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


class ListView(permission1, SearchPostMixin):
    def get(self, request, *args, **kwargs):
        qs = model.objects.all().order_by("-edition_time")
        context["page_obj"] = paginator(request, qs)

        return render(request, model.template_name_list(), context)


class SearchView(permission1, SearchPostMixin):
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


class DetailView(permission1, View):
    def get(self, request, id, *args, **kwargs):
        obj = get_object_or_404(model, id=id)
        context["obj"] = obj

        return render(request, model.template_name_detail(), context)


class CreateView(permission2, View):
    def get(self, request, *args, **kwargs):
        return render(
            request,
            model.template_name_create(),
            {"form": model_form(), "title": model.french_name().lower()},
        )

    def post(self, request, *args, **kwargs):
        form = model_form(request.POST)

        if form.is_valid():
            qs = model.objects.filter(slug_form=form.cleaned_data["slug_form"])
            if qs:
                obj = qs[0]
                messages.info(
                    request,
                    f" ℹ️ {model.french_name()} identifiant n°{obj.id} existe déjà.",
                )

            else:
                obj = form.save()
                obj.save()

                messages.success(
                    request,
                    f" ✅ {model.french_name()} identifiant n°{obj.id} a été créé avec succès !",
                )

            return redirect(f"{model.singular_name()}", id=obj.id)

        return render(
            request,
            model.template_name_create(),
            {"form": form, "title": model.french_name().lower()},
        )


class UpdateView(permission2, View):
    def get(self, request, id, *args, **kwargs):
        obj = get_object_or_404(model, id=id)

        return render(
            request,
            model.template_name_create(),
            {
                "form": model_form(instance=obj),
                "obj": obj,
                "title": model.french_name().lower(),
            },
        )

    def post(self, request, id, *args, **kwargs):
        obj = get_object_or_404(model, id=id)

        form = model_form(request.POST, instance=obj)

        if form.is_valid():
            qs = model.objects.filter(slug_form=form.cleaned_data["slug_form"])
            if qs:
                obj = qs[0]
                messages.info(
                    request,
                    f" ℹ️ {model.french_name()} identifiant n°{obj.id} existe déjà.",
                )

            else:
                obj = form.save()
                obj.save()
                messages.success(
                    request,
                    f" ✅ {model.french_name()} identifiant n°{obj.id} a été modifié avec succès !",
                )

            return redirect(f"{model.singular_name()}", id=obj.id)

        return render(
            request,
            model.template_name_create(),
            {"form": form, "title": model.french_name().lower()},
        )


class DeleteView(permission2, View):
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
