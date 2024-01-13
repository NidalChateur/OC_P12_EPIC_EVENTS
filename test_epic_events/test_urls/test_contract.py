import pytest
from django.urls import resolve, reverse
from django.views import View

from epic_events.urls.contract import (
    CreateView,
    DeleteView,
    DetailView,
    ListView,
    MyListView,
    SearchView,
    UpdateView,
)


class TestContract:
    @pytest.mark.parametrize(
        "url_path, url_name, id, ViewClass",
        [
            ("/contracts/", "contracts", None, ListView),
            ("/collaborators/1/my_contracts/", "my_contracts", 1, MyListView),
            ("/contracts/1/", "contract", 1, DetailView),
            ("/contracts/1/search/", "search_contract", 1, SearchView),
            ("/customers/1/contracts/create/", "create_contract", 1, CreateView),
            ("/contracts/1/update/", "update_contract", 1, UpdateView),
            ("/contracts/1/delete/", "delete_contract", 1, DeleteView),
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
