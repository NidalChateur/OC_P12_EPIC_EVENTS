from django.urls import resolve, reverse

from epic_events.urls.collaborator import (
    ChangePasswordView,
    CreatePasswordView,
    CreateView,
    DeleteView,
    DetailView,
    FirstConnexionView,
    HomeView,
    ListView,
    LoginView,
    LogoutView,
    SearchView,
    UpdateView,
)


class TestCollaborator:
    def test_first_connexion_url(self):
        # 1. path check
        assert reverse("first_connexion") == "/collaborators/first-connexion/"

        # 2. view_name check
        assert resolve("/collaborators/first-connexion/").view_name == "first_connexion"

        # 3. view_class check
        assert (
            resolve("/collaborators/first-connexion/").func.view_class
            == FirstConnexionView
        )

    def test_login_url(self):
        # 1. path check
        assert reverse("login") == "/"

        # 2. view_name check
        assert resolve("/").view_name == "login"

        # 3. view_class check
        assert resolve("/").func.view_class == LoginView

    def test_logout_url(self):
        # 1. path check
        assert reverse("logout") == "/logout/"

        # 2. view_name check
        assert resolve("/logout/").view_name == "logout"

        # 3. view_class check
        assert resolve("/logout/").func.view_class == LogoutView

    def test_home_url(self):
        # 1. path check
        assert reverse("home") == "/home/"

        # 2. view_name check
        assert resolve("/home/").view_name == "home"

        # 3. view_class check
        assert resolve("/home/").func.view_class == HomeView

    def test_list_url(self):
        # 1. path check
        assert reverse("collaborators") == "/collaborators/"

        # 2. view_name check
        assert resolve("/collaborators/").view_name == "collaborators"

        # 3. view_class check
        assert resolve("/collaborators/").func.view_class == ListView

    def test_detail_url(self):
        # 1. path check
        assert reverse("collaborator", args=[1]) == "/collaborators/1/"

        # 2. view_name check
        assert resolve("/collaborators/1/").view_name == "collaborator"

        # 3. view_class check
        assert resolve("/collaborators/1/").func.view_class == DetailView

    def test_search_url(self):
        # 1. path check
        assert reverse("search_collaborator", args=[1]) == "/collaborators/1/search/"

        # 2. view_name check
        assert resolve("/collaborators/1/search/").view_name == "search_collaborator"

        # 3. view_class check
        assert resolve("/collaborators/1/search/").func.view_class == SearchView

    def test_create_url(self):
        # 1. path check
        assert reverse("create_collaborator") == "/collaborators/create/"

        # 2. view_name check
        assert resolve("/collaborators/create/").view_name == "create_collaborator"

        # 3. view_class check
        assert resolve("/collaborators/create/").func.view_class == CreateView

    def test_update_url(self):
        # 1. path check
        assert reverse("update_collaborator", args=[1]) == "/collaborators/1/update/"

        # 2. view_name check
        assert resolve("/collaborators/1/update/").view_name == "update_collaborator"

        # 3. view_class check
        assert resolve("/collaborators/1/update/").func.view_class == UpdateView

    def test_delete_url(self):
        # 1. path check
        assert reverse("delete_collaborator", args=[1]) == "/collaborators/1/delete/"

        # 2. view_name check
        assert resolve("/collaborators/1/delete/").view_name == "delete_collaborator"

        # 3. view_class check
        assert resolve("/collaborators/1/delete/").func.view_class == DeleteView

    def test_create_password_url(self):
        # 1. path check
        assert (
            reverse("create_password", args=[1]) == "/collaborators/1/create-password/"
        )

        # 2. view_name check
        assert (
            resolve("/collaborators/1/create-password/").view_name == "create_password"
        )

        # 3. view_class check
        assert (
            resolve("/collaborators/1/create-password/").func.view_class
            == CreatePasswordView
        )

    def test_change_password_url(self):
        # 1. path check
        assert reverse("change_password") == "/my-profile/change-password/"

        # 2. view_name check
        assert resolve("/my-profile/change-password/").view_name == "change_password"

        # 3. view_class check
        assert (
            resolve("/my-profile/change-password/").func.view_class
            == ChangePasswordView
        )
