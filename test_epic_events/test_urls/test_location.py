from django.urls import resolve, reverse

from epic_events.urls.location import (
    CreateView,
    DeleteView,
    DetailView,
    ListView,
    SearchView,
    UpdateView,
)


class TestLocation:
    def test_list_url(self):
        # 1. path check
        assert reverse("locations") == "/locations/"

        # 2. view_name check
        assert resolve("/locations/").view_name == "locations"

        # 3. view_class check
        assert resolve("/locations/").func.view_class == ListView

    def test_detail_url(self):
        # 1. path check
        assert reverse("location", args=[1]) == "/locations/1/"

        # 2. view_name check
        assert resolve("/locations/1/").view_name == "location"

        # 3. view_class check
        assert resolve("/locations/1/").func.view_class == DetailView

    def test_search_url(self):
        # 1. path check
        assert reverse("search_location", args=[1]) == "/locations/1/search/"

        # 2. view_name check
        assert resolve("/locations/1/search/").view_name == "search_location"

        # 3. view_class check
        assert resolve("/locations/1/search/").func.view_class == SearchView

    def test_create_url(self):
        # 1. path check
        assert reverse("create_location") == "/locations/create/"

        # 2. view_name check
        assert resolve("/locations/create/").view_name == "create_location"

        # 3. view_class check
        assert resolve("/locations/create/").func.view_class == CreateView

    def test_update_url(self):
        # 1. path check
        assert reverse("update_location", args=[1]) == "/locations/1/update/"

        # 2. view_name check
        assert resolve("/locations/1/update/").view_name == "update_location"

        # 3. view_class check
        assert resolve("/locations/1/update/").func.view_class == UpdateView

    def test_delete_url(self):
        # 1. path check
        assert reverse("delete_location", args=[1]) == "/locations/1/delete/"

        # 2. view_name check
        assert resolve("/locations/1/delete/").view_name == "delete_location"

        # 3. view_class check
        assert resolve("/locations/1/delete/").func.view_class == DeleteView
