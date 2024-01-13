from django.urls import path

from ..views.collaborator import (
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

urlpatterns = [
    path(
        "collaborators/first-connexion/",
        FirstConnexionView.as_view(),
        name="first_connexion",
    ),
    path("", LoginView.as_view(), name="login"),
    path("logout/", LogoutView.as_view(), name="logout"),
    path("home/", HomeView.as_view(), name="home"),
    path("collaborators/", ListView.as_view(), name="collaborators"),
    path("collaborators/<int:id>/", DetailView.as_view(), name="collaborator"),
    path(
        "collaborators/<str:search>/search/",
        SearchView.as_view(),
        name="search_collaborator",
    ),
    path(
        "collaborators/create/",
        CreateView.as_view(),
        name="create_collaborator",
    ),
    path(
        "collaborators/<int:id>/update/",
        UpdateView.as_view(),
        name="update_collaborator",
    ),
    path(
        "collaborators/<int:id>/delete/",
        DeleteView.as_view(),
        name="delete_collaborator",
    ),
    path(
        "collaborators/<int:id>/create-password/",
        CreatePasswordView.as_view(),
        name="create_password",
    ),
    path(
        "my-profile/change-password/",
        ChangePasswordView.as_view(),
        name="change_password",
    ),
]
