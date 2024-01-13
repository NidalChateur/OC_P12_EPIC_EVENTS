from django.urls import resolve, reverse

from epic_events.urls.department import (
    CreateView,
    DeleteView,
    DetailView,
    ListView,
    SearchView,
    UpdateView,
)


class TestDepartment:
    def test_list_url(self):
        # 1. path check
        assert reverse("departments") == "/departments/"

        # 2. view_name check
        assert resolve("/departments/").view_name == "departments"

        # 3. view_class check
        assert resolve("/departments/").func.view_class == ListView

    def test_detail_url(self):
        # 1. path check
        assert reverse("department", args=[1]) == "/departments/1/"

        # 2. view_name check
        assert resolve("/departments/1/").view_name == "department"

        # 3. view_class check
        assert resolve("/departments/1/").func.view_class == DetailView

    def test_search_url(self):
        # 1. path check
        assert reverse("search_department", args=[1]) == "/departments/1/search/"

        # 2. view_name check
        assert resolve("/departments/1/search/").view_name == "search_department"

        # 3. view_class check
        assert resolve("/departments/1/search/").func.view_class == SearchView

    def test_create_url(self):
        # 1. path check
        assert reverse("create_department") == "/departments/create/"

        # 2. view_name check
        assert resolve("/departments/create/").view_name == "create_department"

        # 3. view_class check
        assert resolve("/departments/create/").func.view_class == CreateView

    def test_update_url(self):
        # 1. path check
        assert reverse("update_department", args=[1]) == "/departments/1/update/"

        # 2. view_name check
        assert resolve("/departments/1/update/").view_name == "update_department"

        # 3. view_class check
        assert resolve("/departments/1/update/").func.view_class == UpdateView

    def test_delete_url(self):
        # 1. path check
        assert reverse("delete_department", args=[1]) == "/departments/1/delete/"

        # 2. view_name check
        assert resolve("/departments/1/delete/").view_name == "delete_department"

        # 3. view_class check
        assert resolve("/departments/1/delete/").func.view_class == DeleteView
