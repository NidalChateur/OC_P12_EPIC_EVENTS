from django.urls import path

from ..views.contract import (
    CreateView,
    DeleteView,
    DetailView,
    ListView,
    MyListView,
    SearchView,
    UpdateView,
    model,
)

urlpatterns = [
    path(
        f"collaborators/<int:id>/{model.my_list_url_name()}/",
        MyListView.as_view(),
        name=model.my_list_url_name(),
    ),
    path(f"{model.plural_name()}/", ListView.as_view(), name=model.plural_name()),
    path(
        f"{model.plural_name()}/<str:search>/search/",
        SearchView.as_view(),
        name=model.search_url_name(),
    ),
    path(
        f"{model.plural_name()}/<int:id>/",
        DetailView.as_view(),
        name=model.singular_name(),
    ),
    path(
        f"customers/<int:id>/{model.plural_name()}/create/",
        CreateView.as_view(),
        name=model.create_url_name(),
    ),
    path(
        f"{model.plural_name()}/<int:id>/update/",
        UpdateView.as_view(),
        name=model.update_url_name(),
    ),
    path(
        f"{model.plural_name()}/<int:id>/delete/",
        DeleteView.as_view(),
        name=model.delete_url_name(),
    ),
]
