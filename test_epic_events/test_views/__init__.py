from datetime import date

from django.test import Client
from django.urls import reverse
from pytest_django.asserts import assertTemplateUsed

from epic_events.models import Collaborator, Contract, Customer, Department


class CollaboratorMixin:
    client = Client()

    password = "00000000pW-"

    customer_data = {
        "first_name": "John",
        "last_name": "Doe",
        "email": "new_collaborator@gmail.com",
        "name": "entreprise",
    }

    contract_data = {
        "total_amount": 1000,
        "amount_paid": 0,
        "is_signed": False,
    }

    @classmethod
    def create_department(self, name: str) -> Department:
        department = Department(name=name)
        department.save()

        return department

    @classmethod
    def create_collaborator(self, role: str, number=""):
        collaborator = Collaborator(
            first_name="John",
            last_name="Doe",
            email=f"{role}{number}@gmail.com",
            department=self.create_department(name=role),
            birthdate=date(year=2000, month=1, day=1),
        )
        collaborator.save()
        collaborator.set_password(self.password)
        collaborator.save()

        return collaborator

    @classmethod
    def login(self, role: str, test=False, number="") -> Collaborator:
        # 0. logout
        self.logout()

        # 1. get or create collaborator
        qs = Collaborator.objects.filter(email=f"{role}{number}@gmail.com")
        if qs:
            collaborator = qs[0]
        else:
            collaborator = self.create_collaborator(role=role, number=number)

        # 2. post login
        data = {"email": collaborator.email, "password": self.password}
        response1 = self.client.post(reverse("login"), data)
        if test:
            assert response1.status_code == 302
            assert response1.url == reverse("home")

            # 3. get home
            response = self.client.get(reverse("home"))
            is_authenticated = response.context["request"].user.is_authenticated
            user_role = response.context["request"].user.role

            assertTemplateUsed(response, "collaborator/home.html")
            assert is_authenticated is True
            assert user_role == role

        return collaborator

    @classmethod
    def logout(self, test=False):
        # 1. get logout
        self.client.get(reverse("logout"))

        if test:
            # 2. get login to test template and user status
            response = self.client.get(reverse("login"))
            is_authenticated = response.context["request"].user.is_authenticated

            assert is_authenticated is False
            assertTemplateUsed(response, "collaborator/login.html")

    @classmethod
    def create_customer(self) -> Customer:
        self.login(role="Commercial")
        self.client.post(reverse("create_customer"), self.customer_data)

        return Customer.objects.get(email=self.customer_data["email"])

    @classmethod
    def create_contract(self) -> (Customer, Contract):
        customer = self.create_customer()

        self.login(role="Gestion")
        self.client.post(
            reverse("create_contract", args=[customer.id]), self.contract_data
        )
        contract = Contract.objects.get(customer=customer)

        return customer, contract
