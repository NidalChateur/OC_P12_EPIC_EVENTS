import pytest
from django.urls import resolve, reverse
from django.views import View

from epic_events.urls.event import (
    CreateView,
    DeleteView,
    DetailView,
    ListView,
    MyListView,
    SearchView,
    UpdateView,
    ChangeSupportView,
    ListEventsWithoutSupport,
)


class TestEvent:
    @pytest.mark.parametrize(
        "url_path, url_name, id, ViewClass",
        [
            ("/events/without_support/", "events_without_support", None, ListEventsWithoutSupport),
            ("/events/", "events", None, ListView),
            ("/collaborators/1/my_events/", "my_events", 1, MyListView),
            ("/events/1/", "event", 1, DetailView),
            ("/events/1/search/", "search_event", 1, SearchView),
            ("/contracts/1/events/create/", "create_event", 1, CreateView),
            ("/events/1/update/", "update_event", 1, UpdateView),
            ("/events/1/delete/", "delete_event", 1, DeleteView),
            ("/events/1/change_support/", "change_support", 1, ChangeSupportView),
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
