from django.urls import resolve, reverse

from epic_events.urls.company import (
    CreateView,
    DeleteView,
    DetailView,
    ListView,
    SearchView,
    UpdateView,
)


class TestCompany:
    def test_list_url(self):
        # 1. path check
        assert reverse("companies") == "/companies/"

        # 2. view_name check
        assert resolve("/companies/").view_name == "companies"

        # 3. view_class check
        assert resolve("/companies/").func.view_class == ListView

    def test_detail_url(self):
        # 1. path check
        assert reverse("company", args=[1]) == "/companies/1/"

        # 2. view_name check
        assert resolve("/companies/1/").view_name == "company"

        # 3. view_class check
        assert resolve("/companies/1/").func.view_class == DetailView

    def test_search_url(self):
        # 1. path check
        assert reverse("search_company", args=[1]) == "/companies/1/search/"

        # 2. view_name check
        assert resolve("/companies/1/search/").view_name == "search_company"

        # 3. view_class check
        assert resolve("/companies/1/search/").func.view_class == SearchView

    def test_create_url(self):
        # 1. path check
        assert reverse("create_company") == "/companies/create/"

        # 2. view_name check
        assert resolve("/companies/create/").view_name == "create_company"

        # 3. view_class check
        assert resolve("/companies/create/").func.view_class == CreateView

    def test_update_url(self):
        # 1. path check
        assert reverse("update_company", args=[1]) == "/companies/1/update/"

        # 2. view_name check
        assert resolve("/companies/1/update/").view_name == "update_company"

        # 3. view_class check
        assert resolve("/companies/1/update/").func.view_class == UpdateView

    def test_delete_url(self):
        # 1. path check
        assert reverse("delete_company", args=[1]) == "/companies/1/delete/"

        # 2. view_name check
        assert resolve("/companies/1/delete/").view_name == "delete_company"

        # 3. view_class check
        assert resolve("/companies/1/delete/").func.view_class == DeleteView
