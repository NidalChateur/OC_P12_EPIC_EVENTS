""" info : after redirection(status_code==302), the context is lost : we have to
make another get method to be able to read response.context['request']"""


import pytest
from django.urls import reverse
from pytest_django.asserts import assertTemplateUsed

from epic_events.models.customer import Customer

from . import CollaboratorMixin


@pytest.mark.django_db
class TestCustomer(CollaboratorMixin):
    data = {
        "first_name": "John",
        "last_name": "Doe",
        "email": "new_collaborator@gmail.com",
        "name": "entreprise",
    }

    """test if read permission is allowed or forbidden"""

    @pytest.mark.parametrize("role", [("Gestion"), ("Commercial"), ("Support")])
    def test_get_customers_as_collaborator(self, role: str):
        # 1. login
        self.login(role=role)

        # 2. test get customers
        response = self.client.get(reverse("customers"))
        # status_code == 200 : valid permission
        assert response.status_code == 200
        assertTemplateUsed(response, "customer/list.html")

    def test_get_customers_as_visitor(self):
        # 0. logout
        self.logout()

        # 1. test get customers as visitor
        response = self.client.get(reverse("customers"))
        # status_code == 302 : redirection
        assert response.status_code == 302
        # "/?next=/customers/" : redirected to login view
        assert response.url == "/?next=/customers/"

    """test if create permission is allowed or forbidden"""

    @pytest.mark.parametrize("role", [("Gestion"), ("Commercial"), ("Support")])
    def test_post_customer_as_collaborator(self, role: str):
        # 1. login
        collaborator = self.login(role=role)

        # 2. test post customer
        response = self.client.post(reverse("create_customer"), self.data)

        if role == "Commercial":
            # 302 : redirection
            assert response.status_code == 302
            assert response.url == reverse("customer", args=[1])

            # test get the customer created and check the customer commercial
            customer = Customer.objects.get(email=self.data["email"])
            assert customer
            assert customer.commercial == collaborator

        if role in ["Gestion", "Support"]:
            # 403 : forbidden permission
            assert response.status_code == 403

    def test_post_customer_as_visitor(self):
        # 0. logout
        self.logout()

        # 1. test post customer as visitor
        response = self.client.post(reverse("create_customer"), self.data)
        # status_code == 302 : redirection
        assert response.status_code == 302
        # "/?next=/..." : redirected to login view
        assert response.url == "/?next=/customers/create/"

    """test if update permission is allowed or forbidden"""

    @pytest.mark.parametrize("role", [("Gestion"), ("Commercial"), ("Support")])
    def test_update_customer_as_collaborator(self, role: str):
        # 1. login
        collaborator = self.login(role=role)

        if role == "Commercial":
            # 2. post customer (create)
            self.client.post(reverse("create_customer"), self.data)
            customer = Customer.objects.get(email=self.data["email"])

            # 3. test update the customer
            self.data["first_name"] = "Paul"
            response = self.client.post(
                reverse("update_customer", args=[customer.id]), self.data
            )

            # 302 : redirection
            assert response.status_code == 302
            assert response.url == reverse("customer", args=[customer.id])

            # test get the updated customer
            customer = Customer.objects.get(email=self.data["email"])
            assert customer.first_name == self.data["first_name"]
            assert customer.commercial == collaborator

        if role in ["Gestion", "Support"]:
            response = self.client.post(reverse("update_customer", args=[1]), self.data)
            # 403 : forbidden permission
            assert response.status_code == 403

    def test_update_customer_as_visitor(self):
        # 0. logout
        self.logout()

        # 1. test update as visitor
        response = self.client.post(reverse("update_customer", args=[1]), self.data)
        # status_code == 302 : redirection
        assert response.status_code == 302
        # "/?next=/..." : redirected to login view
        assert response.url == "/?next=/customers/1/update/"

    """test if delete permission is allowed or forbidden"""

    @pytest.mark.parametrize("role", [("Gestion"), ("Commercial"), ("Support")])
    def test_delete_customer_as_collaborator(self, role: str):
        # 1. login
        self.login(role=role)

        if role == "Commercial":
            # 2. post customer (create)
            self.client.post(reverse("create_customer"), self.data)
            customer = Customer.objects.get(email=self.data["email"])

            # 3. test delete the customer
            response = self.client.post(reverse("delete_customer", args=[customer.id]))

            # 302 : redirection
            assert response.status_code == 302
            assert response.url == reverse("customers")

            # test get the deleted customer
            customer = Customer.objects.filter(email=self.data["email"])
            assert len(customer) == 0

        if role in ["Gestion", "Support"]:
            response = self.client.post(reverse("delete_customer", args=[1]))
            # 403 : forbidden permission
            assert response.status_code == 403

    def test_delete_customer_as_visitor(self):
        # 0. logout
        self.logout()

        # 1. delete customer as visitor
        response = self.client.post(reverse("delete_customer", args=[1]), self.data)
        # status_code == 302 : redirection
        assert response.status_code == 302
        # "/?next=/..." : redirected to login view
        assert response.url == "/?next=/customers/1/delete/"
