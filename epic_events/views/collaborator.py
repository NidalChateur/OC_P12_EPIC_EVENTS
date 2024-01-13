from django.contrib import messages
from django.contrib.auth import get_user_model, login, logout
from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import get_object_or_404, redirect, render
from django.utils.text import slugify
from django.views import View

from ..forms.collaborator import (
    ChangePasswordForm,
    CollaboratorForm,
    CreatePasswordForm,
    FirstConnexionForm,
    LoginForm,
)
from ..forms.department import DepartmentForm
from ..forms.search import SearchForm
from ..models.contract_event import (
    contracts,
    contracts_ready_for_event,
    events,
    events_without_support,
    unpaid_contracts,
    unsigned_contracts,
)
from ..models.customer import Customer
from ..models.department import Department
from ..permissions import ManagerRequiredMixin
from .paginator import paginator

login_permission = LoginRequiredMixin
change_password_permission = login_permission
crud_permission = ManagerRequiredMixin


class FirstConnexionView(View):
    template_name = "collaborator/first_connexion.html"
    form = FirstConnexionForm

    def get(self, request, *args, **kwargs):
        if request.user.is_authenticated:
            return redirect("home")

        return render(request, self.template_name, {"form": self.form})

    def post(self, request, *args, **kwargs):
        form = self.form(request.POST)

        if form.is_valid():
            return redirect("create_password", id=form.cleaned_data["id"])

        return render(request, self.template_name, {"form": form})


class CreatePasswordView(View):
    template_name = "collaborator/password.html"
    form = CreatePasswordForm

    def get(self, request, id, *args, **kwargs):
        if request.user.is_authenticated:
            return redirect("home")
        collaborator = get_object_or_404(get_user_model(), id=id)

        return render(request, self.template_name, {"form": self.form(collaborator)})

    def post(self, request, id, *args, **kwargs):
        collaborator = get_object_or_404(get_user_model(), id=id)
        form = self.form(collaborator, request.POST)

        if form.is_valid():
            form.save()
            messages.success(
                request,
                f" ✅ {collaborator.name}, votre mot de passe a été créé avec succès !",
            )
            messages.info(request, " ℹ️ Connectez vous avec vos identifiants.")
            return redirect("login")

        return render(request, self.template_name, {"form": form})


class ChangePasswordView(change_password_permission, View):
    template_name = "collaborator/password.html"
    form = ChangePasswordForm

    def get(self, request, *args, **kwargs):
        collaborator = get_object_or_404(get_user_model(), id=request.user.id)

        return render(request, self.template_name, {"form": self.form(collaborator)})

    def post(self, request, *args, **kwargs):
        collaborator = get_object_or_404(get_user_model(), id=request.user.id)
        form = self.form(collaborator, request.POST)

        if form.is_valid():
            form.save()
            messages.success(
                request,
                f" ✅ {collaborator.name}, votre mot de passe a été modifié avec succès !",
            )
            messages.info(request, " ℹ️ Connectez vous avec vos identifiants.")

            return redirect("login")

        return render(request, self.template_name, {"form": form})


class LoginView(View):
    template_name = "collaborator/login.html"
    form = LoginForm

    def get(self, request, *args, **kwargs):
        if request.user.is_authenticated:
            return redirect("home")

        return render(request, self.template_name, {"form": self.form})

    def post(self, request, *args, **kwargs):
        form = self.form(request.POST)

        if form.is_valid():
            collaborator = get_object_or_404(
                get_user_model(), email=form.cleaned_data["email"]
            )
            login(request, collaborator)
            messages.success(request, " ✅ Connexion réussie !")

            return redirect("home")

        return render(request, self.template_name, {"form": form})


class LogoutView(View):
    def get(self, request, *args, **kwargs):
        logout(request)
        messages.info(request, " ℹ️ Vous êtes déconnecté.")

        return redirect("login")


class HomeView(login_permission, View):
    template_name = "collaborator/home.html"

    def get(self, request, *args, **kwargs):
        context = {
            "all_customers": Customer.objects.all().count(),
            "all_contracts": len(contracts()),
            "all_events": len(events()),
        }

        if request.user.role == "Commercial":
            my_unsigned_contracts = len(unsigned_contracts(request.user))
            my_unpaid_contracts = len(unpaid_contracts(request.user))
            my_events_to_create = len(contracts_ready_for_event(request.user))

            context["my_unsigned_contracts"] = my_unsigned_contracts
            context["my_unpaid_contracts"] = my_unpaid_contracts
            context["my_events_to_create"] = my_events_to_create

        if request.user.role == "Gestion":
            context["events_without_support"] = len(events_without_support())

        if request.user.role == "Support":
            context["my_events"] = len(events(support=request.user))

        return render(request, self.template_name, context)


class ListView(crud_permission, View):
    template_name = "collaborator/list.html"
    form = SearchForm

    def get(self, request, *args, **kwargs):
        collaborators = get_user_model().objects.all().order_by("-edition_time")
        page_obj = paginator(request, collaborators)

        return render(
            request,
            self.template_name,
            {
                "page_obj": page_obj,
                "form": self.form(placeholder="Rechercher collaborateur"),
            },
        )

    def post(self, request, *args, **kwargs):
        """search"""

        form = self.form(request.POST)
        if form.is_valid():
            return redirect("search_collaborator", search=form.cleaned_data["search"])


class SearchView(crud_permission, View):
    template_name = "collaborator/list.html"
    form = SearchForm

    def get(self, request, search, *args, **kwargs):
        collaborators = (
            get_user_model()
            .objects.filter(slug__contains=slugify(search))
            .order_by("-edition_time")
        )

        if len(collaborators) < 2:
            messages.info(request, f" ℹ️ {len(collaborators)} résultat trouvé.")
        else:
            messages.info(request, f" ℹ️ {len(collaborators)} résultats trouvés.")

        page_obj = paginator(request, collaborators)

        return render(
            request,
            self.template_name,
            {
                "page_obj": page_obj,
                "form": self.form(placeholder="Rechercher collaborateur"),
            },
        )

    def post(self, request, *args, **kwargs):
        """search"""

        form = self.form(request.POST)
        if form.is_valid():
            return redirect("search_collaborator", search=form.cleaned_data["search"])


class DetailView(login_permission, View):
    template_name = "collaborator/detail.html"

    def get(self, request, id, *args, **kwargs):
        collaborator = get_object_or_404(get_user_model(), id=id)
        my_customers = Customer.objects.filter(commercial=collaborator)
        my_events = events(support=collaborator)

        return render(
            request,
            self.template_name,
            {
                "collaborator": collaborator,
                "customers": my_customers,
                "events": my_events,
            },
        )


class CreateView(crud_permission, View):
    template_name = "collaborator/form.html"
    collaborator_form = CollaboratorForm
    department_form = DepartmentForm

    def get(self, request, *args, **kwargs):
        return render(
            request,
            self.template_name,
            {
                "collaborator_form": self.collaborator_form(),
                "department_form": self.department_form(),
            },
        )

    def post(self, request, *args, **kwargs):
        collaborator_form = self.collaborator_form(request.POST)
        department_form = self.department_form(request.POST)

        if all([collaborator_form.is_valid(), department_form.is_valid()]):
            collaborator = collaborator_form.save(commit=False)

            # check if department exists
            qs = Department.objects.filter(name=department_form.cleaned_data["name"])
            if qs:
                department = qs[0]
            else:
                department = department_form.save()
                department.save()

            collaborator.department = department
            collaborator.save()

            messages.success(
                request,
                f" ✅ Le profil collaborateur identifiant n°{collaborator.id} a été créé avec succès !",
            )

            return redirect("collaborator", id=collaborator.id)

        return render(
            request,
            self.template_name,
            {
                "collaborator_form": collaborator_form,
                "department_form": department_form,
            },
        )


class UpdateView(crud_permission, View):
    template_name = "collaborator/form.html"
    collaborator_form = CollaboratorForm
    department_form = DepartmentForm

    def get(self, request, id, *args, **kwargs):
        collaborator = get_object_or_404(get_user_model(), id=id)

        return render(
            request,
            self.template_name,
            {
                "collaborator_form": self.collaborator_form(instance=collaborator),
                "department_form": self.department_form(
                    instance=collaborator.department
                ),
                "collaborator": collaborator,
            },
        )

    def post(self, request, id, *args, **kwargs):
        collaborator = get_object_or_404(get_user_model(), id=id)

        collaborator_form = self.collaborator_form(request.POST, instance=collaborator)

        department_form = self.department_form(
            request.POST, instance=collaborator.department
        )

        if all([collaborator_form.is_valid(), department_form.is_valid()]):
            collaborator = collaborator_form.save(commit=False)

            # check if department exists
            qs = Department.objects.filter(name=department_form.cleaned_data["name"])
            if qs:
                department = qs[0]
            else:
                department = Department(name=department_form.cleaned_data["name"])
                department.save()

            collaborator.department = department
            collaborator.save()

            messages.success(
                request,
                f" ✅ Le profil collaborateur identifiant n°{collaborator.id} a été modifié avec succès !",
            )

            return redirect("collaborator", id=collaborator.id)

        return render(
            request,
            self.template_name,
            {
                "collaborator_form": collaborator_form,
                "department_form": department_form,
            },
        )


class DeleteView(crud_permission, View):
    template_name = "collaborator/delete.html"

    def get(self, request, id, *args, **kwargs):
        """delete confirmation"""

        collaborator = get_object_or_404(get_user_model(), id=id)

        return render(request, self.template_name, {"collaborator": collaborator})

    def post(self, request, id, *args, **kwargs):
        "delete"

        collaborator = get_object_or_404(get_user_model(), id=id)
        collaborator_id = collaborator.id
        collaborator.delete()
        messages.success(
            request,
            f" ✅ Le profil collaborateur identifiant n°{collaborator_id} a été supprimé avec succès !",
        )

        return redirect("collaborators")
