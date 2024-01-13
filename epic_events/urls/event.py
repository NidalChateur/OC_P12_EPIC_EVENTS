from django.urls import path

from ..views.event import (
    ChangeSupportView,
    CreateView,
    DeleteView,
    DetailView,
    ListEventsWithoutSupport,
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
        f"{model.plural_name()}/without_support/",
        ListEventsWithoutSupport.as_view(),
        name=f"{model.plural_name()}_without_support",
    ),
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
        f"contracts/<int:id>/{model.plural_name()}/create/",
        CreateView.as_view(),
        name=model.create_url_name(),
    ),
    path(
        f"{model.plural_name()}/<int:id>/update/",
        UpdateView.as_view(),
        name=model.update_url_name(),
    ),
    path(
        f"{model.plural_name()}/<int:id>/change_support/",
        ChangeSupportView.as_view(),
        name="change_support",
    ),
    path(
        f"{model.plural_name()}/<int:id>/delete/",
        DeleteView.as_view(),
        name=model.delete_url_name(),
    ),
]
