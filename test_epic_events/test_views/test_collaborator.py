""" info : after redirection(status_code==302), the context is lost : we have to
make another get method to be able to read response.context['request']"""


import pytest
from django.urls import reverse
from pytest_django.asserts import assertTemplateUsed

from . import Collaborator, CollaboratorMixin


@pytest.mark.django_db
class TestCollaborator(CollaboratorMixin):
    data = {
        "name": "Commercial",
        "first_name": "John",
        "last_name": "Doe",
        "birthdate": "01/01/2000",
        "email": "new_collaborator@gmail.com",
    }

    def test_wrong_login(self):
        data = {"email": "invalid", "password": "invalid"}
        response = self.client.post(reverse("login"), data)
        assert response.status_code == 200
        assert response.context["request"].user.is_authenticated is False

    @pytest.mark.parametrize("role", [("Gestion"), ("Commercial"), ("Support")])
    def test_valid_login(self, role: str):
        self.login(role=role, test=True)

    def test_logout(self):
        self.logout(test=True)

    """test if read permission is allowed or forbidden"""

    @pytest.mark.parametrize("role", [("Gestion"), ("Commercial"), ("Support")])
    def test_get_collaborators_as_collaborator(self, role: str):
        # 1. login
        self.login(role=role)

        # 2. get collaborators
        response = self.client.get(reverse("collaborators"))

        if role == "Gestion":
            # status_code == 200 : OK
            assert response.status_code == 200
            assertTemplateUsed(response, "collaborator/list.html")

        if role in ["Commercial", "Support"]:
            # status_code == 403 : forbidden permission
            assert response.status_code == 403

    def test_get_collaborators_as_visitor(self):
        # 0. logout
        self.logout()

        # 1. get collaborators as visitor
        response = self.client.get(reverse("collaborators"))
        # status_code == 302 : redirection
        assert response.status_code == 302
        # "/?next=/collaborators/" : redirected to login view
        assert response.url == "/?next=/collaborators/"

    """test if create permission is allowed or forbidden"""

    @pytest.mark.parametrize("role", [("Gestion"), ("Commercial"), ("Support")])
    def test_post_collaborator_as_collaborator(self, role: str):
        # 1. login
        self.login(role=role)

        # 2. test post collaborator

        response = self.client.post(reverse("create_collaborator"), self.data)

        if role == "Gestion":
            # status_code == 302 : redirection
            assert response.status_code == 302

            # 3. test get the created collaborator
            qs = Collaborator.objects.filter(email=self.data["email"])
            assert len(qs) == 1
            assert response.url == reverse("collaborator", args=[qs[0].id])

        if role in ["Commercial", "Support"]:
            # status_code == 403 : forbidden permission
            assert response.status_code == 403

        # 1. login as Support
        self.login(role="Support")

        # 2. test post collaborator
        data = {
            "name": "Commercial",
            "first_name": "John",
            "last_name": "Doe",
            "birthdate": "01/01/2000",
            "email": "new_collaborator@gmail.com",
        }

        response = self.client.post(reverse("create_collaborator"), data)
        # status_code == 403 : forbidden permission
        assert response.status_code == 403

    def test_post_collaborator_as_visitor(self):
        # 0. logout
        self.logout()

        # 1. test post collaborator as visitor
        response = self.client.post(reverse("create_collaborator"), self.data)
        # status_code == 302 : redirection
        assert response.status_code == 302
        # "/?next=/..." : redirected to login view
        assert response.url == "/?next=/collaborators/create/"

    """test if update permission is allowed or forbidden"""

    @pytest.mark.parametrize("role", [("Gestion"), ("Commercial"), ("Support")])
    def test_update_collaborator_as_collaborator(self, role: str):
        # 1. login
        self.login(role=role)

        if role == "Gestion":
            # 2. post collaborator (create)
            self.client.post(reverse("create_collaborator"), self.data)

            # 3. test update the collaborator department
            collaborator = Collaborator.objects.get(email=self.data["email"])

            self.data["name"] = "Support"
            response = self.client.post(
                reverse("update_collaborator", args=[collaborator.id]), self.data
            )
            # status_code == 302 : redirection
            assert response.status_code == 302

            # 4. test get the updated collaborator
            qs = Collaborator.objects.filter(email=self.data["email"])
            assert len(qs) == 1
            assert qs[0].department.name == "Support"
            assert response.url == reverse("collaborator", args=[qs[0].id])

        if role in ["Commercial", "Support"]:
            # 2. test update the collaborator
            response = self.client.post(
                reverse("update_collaborator", args=[1]), self.data
            )
            # status_code == 403 : forbidden permission
            assert response.status_code == 403

    def test_update_collaborator_as_visitor(self):
        # 0. logout
        self.logout()

        # 1. test update collaborator
        response = self.client.post(reverse("update_collaborator", args=[1]), self.data)
        # status_code == 302 : redirection
        assert response.status_code == 302
        # "/?next=/..." : redirected to login view
        assert response.url == "/?next=/collaborators/1/update/"

    """test if delete permission is allowed or forbidden"""

    @pytest.mark.parametrize("role", [("Gestion"), ("Commercial"), ("Support")])
    def test_delete_collaborator_as_collaborator(self, role: str):
        # 1. login
        self.login(role=role)

        if role == "Gestion":
            # 2. post collaborator (create)
            self.client.post(reverse("create_collaborator"), self.data)
            collaborator = Collaborator.objects.get(email=self.data["email"])

            # 3. test delete the collaborator
            response = self.client.post(
                reverse("delete_collaborator", args=[collaborator.id])
            )
            # status_code == 302 : redirection
            assert response.status_code == 302

            # 4. test get the deleted collaborator
            qs = Collaborator.objects.filter(email=self.data["email"])
            assert len(qs) == 0
            assert response.url == reverse("collaborators")

        if role in ["Commercial", "Support"]:
            # 2. test update the collaborator
            response = self.client.post(
                reverse("delete_collaborator", args=[1]), self.data
            )
            # status_code == 403 : forbidden permission
            assert response.status_code == 403

    def test_delete_collaborator_as_visitor(self):
        # 0. logout
        self.logout()

        # 1. test delete the collaborator
        response = self.client.post(reverse("delete_collaborator", args=[1]))
        # status_code == 302 : redirection
        assert response.status_code == 302
        # "/?next=/..." : redirected to login view
        assert response.url == "/?next=/collaborators/1/delete/"
