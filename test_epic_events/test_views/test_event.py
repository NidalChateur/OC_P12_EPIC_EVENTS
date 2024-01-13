import pytest
from django.urls import reverse
from pytest_django.asserts import assertTemplateUsed

from epic_events.models import Event

from . import CollaboratorMixin


@pytest.mark.django_db
class TestEvent(CollaboratorMixin):
    data = {
        "zip": "75000",
        "city": "Paris",
        "attendees": "0",
    }

    def _create_event(self) -> Event:
        customer, contract = self.create_contract()
        contract.is_signed = True
        contract.save()
        assert contract.is_ready_for_event

        self.login("Commercial")
        self.client.post(reverse("create_event", args=[contract.id]), self.data)
        qs = Event.objects.filter(contract=contract)
        assert len(qs) > 0

        return qs[0]

    def _create_and_assign_support_to_event(self) -> Event:
        # 1. post event and support
        event = self._create_event()
        support_1 = self.create_collaborator(role="Support", number="1")

        # 2. change event support
        self.login(role="Gestion")
        data = {"support": support_1.str_id}
        self.client.post(reverse("change_support", args=[event.id]), data)

        # check the event support
        events = Event.objects.filter(id=event.id)
        assert len(events) == 1
        assert events[0].support == support_1

        return events[0]

    """test if read permission is allowed or forbidden"""

    @pytest.mark.parametrize("role", [("Gestion"), ("Commercial"), ("Support")])
    def test_get_events_as_collaborator(self, role: str):
        # 1. login
        self.login(role=role)

        # 2. test get events
        response = self.client.get(reverse("events"))
        # status_code == 200 : valid permission
        assert response.status_code == 200
        assertTemplateUsed(response, "event/list.html")

    def test_get_events_as_visitor(self):
        # 0. logout
        self.logout()

        # 1. test get events as visitor
        response = self.client.get(reverse("events"))
        # status_code == 302 : redirection
        assert response.status_code == 302
        # "/?next=/customers/" : redirected to login view
        assert response.url == "/?next=/events/"

    """test if create permission is allowed or forbidden"""

    @pytest.mark.parametrize(
        "role, number",
        [
            ("Gestion", ""),
            ("Commercial", ""),
            ("Commercial", "2"),
            ("Support", ""),
            ("Support", "2"),
        ],
    )
    def test_post_event_as_collaborator(self, role: str, number: str):
        # 0. post contract
        customer, contract = self.create_contract()
        contract.is_signed = False
        contract.save()

        # 1. login
        collaborator = self.login(role=role, number=number)

        # 2. test post event
        response = self.client.post(
            reverse("create_event", args=[contract.id]), self.data
        )

        if collaborator == contract.customer.commercial:
            # test to post event with an unsigned contract
            assert contract.is_ready_for_event is False
            # 403 : forbidden
            assert response.status_code == 403

            # test to post event with a signed contract
            contract.is_signed = True
            contract.save()
            assert contract.is_ready_for_event is True

            response = self.client.post(
                reverse("create_event", args=[contract.id]), self.data
            )
            # 302 : event form is validated
            assert response.status_code == 302
            assert response.url == reverse("event", args=[1])
            # get the created event
            events = Event.objects.filter(contract=contract)
            assert len(events) == 1

        if collaborator != contract.customer.commercial:
            # 403 : forbidden
            assert response.status_code == 403

    def test_post_event_as_visitor(self):
        # 0. logout
        self.logout()

        # 1. test post event as visitor
        response = self.client.post(reverse("create_event", args=[1]), self.data)
        # status_code == 302 : redirection
        assert response.status_code == 302
        # "/?next=/..." : redirected to login view
        assert response.url == "/?next=/contracts/1/events/create/"

    """test if change_support permission is allowed or forbidden"""

    @pytest.mark.parametrize(
        "role",
        [("Gestion"), ("Commercial"), ("Support")],
    )
    def test_change_event_support_as_collaborator(self, role: str):
        # 0. post support and event (populating db)
        support_1 = self.create_collaborator(role="Support", number="1")
        event = self._create_event()

        # 1. login
        self.login(role=role)

        # 2. test post event
        data = {"support": support_1.str_id}
        response = self.client.post(reverse("change_support", args=[event.id]), data)

        if role == "Gestion":
            # 302 : change_event form is valid
            assert response.status_code == 302
            assert response.url == reverse("event", args=[event.id])

            # get the event were a support has been changed
            events = Event.objects.filter(id=event.id)
            assert len(events) == 1
            assert events[0].support == support_1

        if role == ["Commercial", ["Support"]]:
            # 403 : forbidden
            assert response.status_code == 403

    def test_change_event_support_as_visitor(self):
        # 0. logout
        self.logout()

        # 1. test change event support as visitor
        response = self.client.post(reverse("change_support", args=[1]), self.data)
        # status_code == 302 : redirection
        assert response.status_code == 302
        # "/?next=/..." : redirected to login view
        assert response.url == "/?next=/events/1/change_support/"

    """test if update permission is allowed or forbidden"""

    @pytest.mark.parametrize(
        "role, number",
        [
            ("Gestion", ""),
            ("Commercial", ""),
            ("Commercial", "2"),
            ("Support", ""),
            ("Support", "2"),
        ],
    )
    def test_update_event_as_collaborator(self, role: str, number: str):
        # 0. post event and assign support
        event = self._create_and_assign_support_to_event()
        commercial_event = event.contract.customer.commercial

        # 1. login
        collaborator = self.login(role=role, number=number)

        # 2. test update event
        self.data["attendees"] = "50"
        response = self.client.post(reverse("update_event", args=[event.id]), self.data)

        if collaborator == commercial_event or collaborator == event.support:
            # 302 : event form is validated
            assert response.status_code == 302
            assert response.url == reverse("event", args=[event.id])
            # get the updated event
            events = Event.objects.filter(id=event.id)
            assert len(events) == 1
            assert events[0].attendees == 50

        else:
            # 403 : forbidden
            assert response.status_code == 403

    def test_update_event_as_visitor(self):
        # 0. logout
        self.logout()

        # 1. test update event as visitor
        response = self.client.post(reverse("update_event", args=[1]), self.data)
        # status_code == 302 : redirection
        assert response.status_code == 302
        # "/?next=/..." : redirected to login view
        assert response.url == "/?next=/events/1/update/"

    """test if delete permission is allowed or forbidden"""

    @pytest.mark.parametrize(
        "role, number",
        [
            ("Gestion", ""),
            ("Commercial", ""),
            ("Support", ""),
            ("Commercial", "2"),
            ("Support", "2"),
        ],
    )
    def test_delete_event_as_collaborator(self, role: str, number: str):
        # 0. post event and assign support
        event = self._create_event()
        commercial_event = event.contract.customer.commercial

        # 1. login
        collaborator = self.login(role=role, number=number)

        # 2. test delete event

        if collaborator == commercial_event or collaborator == event.support:
            response = self.client.post(reverse("delete_event", args=[event.id]))
            # 302 : event form is validated
            assert response.status_code == 302
            assert response.url == reverse("events")
            # get the deleted event
            events = Event.objects.filter(id=event.id)
            assert len(events) == 0

        else:
            with pytest.raises(expected_exception=AttributeError):
                response = self.client.post(reverse("delete_event", args=[event.id]))

            # get the deleted event
            events = Event.objects.filter(id=event.id)
            assert len(events) == 1

    def test_delete_event_as_visitor(self):
        # 0. logout
        self.logout()

        # 1. test delete as visitor
        response = self.client.post(reverse("delete_event", args=[1]), self.data)
        # status_code == 302 : redirection
        assert response.status_code == 302
        # "/?next=/..." : redirected to login view
        assert response.url == "/?next=/events/1/delete/"
