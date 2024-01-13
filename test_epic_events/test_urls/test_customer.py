import pytest
from django.urls import resolve, reverse
from django.views import View

from epic_events.urls.customer import (
    CreateView,
    DeleteView,
    DetailView,
    ListView,
    MyListView,
    SearchView,
    UpdateView,
)


class TestCustomer:
    @pytest.mark.parametrize(
        "url_path, url_name, id, ViewClass",
        [
            ("/customers/", "customers", None, ListView),
            ("/collaborators/1/my_customers/", "my_customers", 1, MyListView),
            ("/customers/1/", "customer", 1, DetailView),
            ("/customers/1/search/", "search_customer", 1, SearchView),
            ("/customers/create/", "create_customer", None, CreateView),
            ("/customers/1/update/", "update_customer", 1, UpdateView),
            ("/customers/1/delete/", "delete_customer", 1, DeleteView),
        ],
    )
    def test_url(self, url_path: str, url_name: str, id: int, ViewClass: View):
        # 1. path check
        if id:
            assert reverse(url_name, args=[id]) == url_path
        else:
            assert reverse(url_name) == url_path

        # 2. view_name check
        assert resolve(url_path).view_name == url_name

        # 3. view_class check
        assert resolve(url_path).func.view_class == ViewClass
