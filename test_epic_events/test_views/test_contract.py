# # test read contracts (visitor(no), commercial(yes), support(yes), gestion(yes))
# # test create contract (visitor(no), commercial(no), support(no), gestion(yes))

import pytest
from django.urls import reverse
from pytest_django.asserts import assertTemplateUsed

from epic_events.models import Contract

from . import CollaboratorMixin


@pytest.mark.django_db
class TestContract(CollaboratorMixin):

    """test read permission"""

    @pytest.mark.parametrize("role", [("Gestion"), ("Commercial"), ("Support")])
    def test_get_contracts_as_collaborator(self, role: str):
        # 1. login
        self.login(role=role)

        # 2. test get contracts
        response = self.client.get(reverse("contracts"))
        # status_code == 200 : valid permission
        assert response.status_code == 200
        assertTemplateUsed(response, "contract/list.html")

    def test_get_contracts_as_visitor(self):
        # 0. logout
        self.logout()

        # 1. test get contracts as visitor
        response = self.client.get(reverse("contracts"))
        # status_code == 302 : redirection
        assert response.status_code == 302
        # "/?next=/customers/" : redirected to login view
        assert response.url == "/?next=/contracts/"

    """test if create permission is allowed or forbidden"""

    @pytest.mark.parametrize("role", [("Gestion"), ("Commercial"), ("Support")])
    def test_post_contract_as_collaborator(self, role: str):
        # 0. post customer
        customer = self.create_customer()

        # 1. login
        self.login(role=role)

        # 2. test post contract
        response = self.client.post(
            reverse("create_contract", args=[customer.id]), self.contract_data
        )

        if role == "Gestion":
            # 302 : redirection
            assert response.status_code == 302
            assert response.url == reverse("contract", args=[1])
            contract = Contract.objects.get(customer=customer)
            assert contract

        if role in ["Commercial", "Support"]:
            # 403 : forbidden
            assert response.status_code == 403

    def test_post_contract_as_visitor(self):
        # 0. logout
        self.logout()

        # 1. test post contract as visitor
        response = self.client.post(
            reverse("create_contract", args=[1]), self.contract_data
        )
        # status_code == 302 : redirection
        assert response.status_code == 302
        # "/?next=/..." : redirected to login view
        assert response.url == "/?next=/customers/1/contracts/create/"

    """test if update permission is allowed or forbidden"""

    @pytest.mark.parametrize(
        "role, number",
        [("Gestion", ""), ("Commercial", ""), ("Support", ""), ("Commercial", "2")],
    )
    def test_update_contract_as_collaborator(self, role: str, number: str):
        # 0. post customer
        customer, contract = self.create_contract()

        # 1. login
        collaborator = self.login(role=role, number=number)

        # 2. test update contract
        self.contract_data["is_signed"] = True
        response = self.client.post(
            reverse("update_contract", args=[contract.id]), self.contract_data
        )

        if role == "Gestion" or collaborator == contract.customer.commercial:
            # 302 : redirection
            assert response.status_code == 302
            assert response.url == reverse("contract", args=[contract.id])
            # get the updated contract
            updated_contract = Contract.objects.get(id=contract.id)
            assert updated_contract.is_signed is True

        if (
            role in ["Support", "Commercial"]
            and collaborator != contract.customer.commercial
        ):
            # 403 : forbidden
            assert response.status_code == 403

    def test_update_contract_as_visitor(self):
        # 0. logout
        self.logout()

        # 1. test update contract as visitor
        response = self.client.post(
            reverse("update_contract", args=[1]), self.contract_data
        )
        # status_code == 302 : redirection
        assert response.status_code == 302
        # "/?next=/..." : redirected to login view
        assert response.url == "/?next=/contracts/1/update/"

    """test if delete permission is allowed or forbidden"""

    @pytest.mark.parametrize(
        "role, number",
        [("Gestion", ""), ("Commercial", ""), ("Support", ""), ("Commercial", "2")],
    )
    def test_delete_contract_as_collaborator(self, role: str, number: str):
        # 0. post customer
        customer, contract = self.create_contract()

        # 1. login
        collaborator = self.login(role=role, number=number)

        # 2. test delete contract
        response = self.client.post(reverse("delete_contract", args=[contract.id]))

        if role == "Gestion" or collaborator == contract.customer.commercial:
            # 302 : redirection
            assert response.status_code == 302
            assert response.url == reverse("contracts")
            # get the deleted contract
            deleted_contract = Contract.objects.filter(id=contract.id)
            assert len(deleted_contract) == 0

        if (
            role in ["Support", "Commercial"]
            and collaborator != contract.customer.commercial
        ):
            # 403 : forbidden
            assert response.status_code == 403

    def test_delete_contract_as_visitor(self):
        # 0. logout
        self.logout()

        # 1. test delete contract as visitor
        response = self.client.post(
            reverse("delete_contract", args=[1]), self.contract_data
        )
        # status_code == 302 : redirection
        assert response.status_code == 302
        # "/?next=/..." : redirected to login view
        assert response.url == "/?next=/contracts/1/delete/"
