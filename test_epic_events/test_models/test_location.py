from datetime import timedelta

import pytest
from django.db.utils import IntegrityError
from django.utils import timezone
from django.utils.text import slugify

from epic_events.models.location import Location
from epic_events.models.str_template import unfilled


class TestLocation:
    model = Location

    def location_instance(self) -> Location:
        return self.model(
            name="Tour Eiffel",
            number="5",
            street_type="avenue",
            street_name="Anatole France",
            city="Paris",
            zip="75007",
        )

    # testing TimeFieldMixin methods
    def test_singular_name(self):
        assert self.model.singular_name() == self.model.__name__.lower()

    def test_plural_name(self):
        assert self.model.plural_name() == self.model.__name__.lower() + "s"

    def test_template_name_list(self):
        assert (
            self.model.template_name_list()
            == f"{self.model.__name__.lower()}/list.html"
        )

    def test_template_name_detail(self):
        assert (
            self.model.template_name_detail()
            == f"{self.model.__name__.lower()}/detail.html"
        )

    def test_template_name_create(self):
        assert (
            self.model.template_name_create()
            == f"{self.model.__name__.lower()}/form.html"
        )

    def test_template_name_delete(self):
        assert (
            self.model.template_name_delete()
            == f"{self.model.__name__.lower()}/delete.html"
        )

    def test_my_list_url_name(self):
        assert self.model.my_list_url_name() == f"my_{self.model.__name__.lower()}s"

    def test_create_url_name(self):
        assert self.model.create_url_name() == f"create_{self.model.__name__.lower()}"

    def test_update_url_name(self):
        assert self.model.update_url_name() == f"update_{self.model.__name__.lower()}"

    def test_delete_url_name(self):
        assert self.model.delete_url_name() == f"delete_{self.model.__name__.lower()}"

    def test_search_url_name(self):
        assert self.model.search_url_name() == f"search_{self.model.__name__.lower()}"

    @pytest.mark.django_db
    def test_save_time(self):
        location = self.location_instance()
        location.save()

        timezone.now() - timedelta(
            minutes=5
        ) < location.creation_time < timezone.now() + timedelta(minutes=5)

        timezone.now() - timedelta(
            minutes=5
        ) < location.edition_time < timezone.now() + timedelta(minutes=5)

    # testing Location methods
    @pytest.mark.django_db
    def test_city_not_null_constraint(self):
        location = self.location_instance()
        with pytest.raises(expected_exception=IntegrityError):
            location.city = None
            location.save()

    @pytest.mark.django_db
    def test_zip_not_null_constraint(self):
        location = self.location_instance()
        with pytest.raises(expected_exception=IntegrityError):
            location.zip = None
            location.save()

    def test_STREET_TYPE(self):
        STREET_TYPE = [
            ("", ""),
            ("rue", "rue"),
            ("impasse", "impasse"),
            ("avenue", "avenue"),
            ("boulevard", "boulevard"),
            ("allée", "allée"),
            ("chemin", "chemin"),
        ]

        assert self.model.STREET_TYPE == STREET_TYPE

    def test_str_name_is_true(self):
        # test location with not None attributes
        location = self.location_instance()
        name = f"{location.name.title()}, "
        number = f"{location.number.upper()} "
        street_type = f"{location.street_type.capitalize()} "
        street_name = f"{location.street_name.title()}, "
        zip = f"{location.zip} "
        city = f"{location.city.title()}."

        assert (
            location.__str__(name=True)
            == f"{name}{number}{street_type}{street_name}{zip}{city}"
        )

        assert (
            location.__str__(name=False)
            == f"{number}{street_type}{street_name}{zip}{city}"
        )

        # test location with None attributes
        location.name = (
            location.number
        ) = location.street_type = location.street_name = None

        assert location.__str__(name=False) == f"{zip}{city}"
        assert location.__str__(name=True) == f"{zip}{city}"

    def test_formatted_name(self):
        # test location with not None attribute
        location = self.location_instance()
        assert location.formatted_name == location.name.title()

        # test location with None attribute
        location.name = None
        assert location.formatted_name == unfilled

    def test_formatted_address(self):
        # test location with not None attributes
        location = self.location_instance()

        assert location.__str__(name=False) == location.formatted_address

        # test location with None attributes
        location.name = (
            location.number
        ) = location.street_type = location.street_name = None

        assert location.__str__(name=False) == location.formatted_address

    def test_french_name(self):
        assert self.model.french_name() == "Lieu"

    def test_french_plural_name(self):
        assert self.model.french_plural_name() == "Lieux"

    @pytest.mark.django_db
    def test_save_slug(self):
        location = self.location_instance()
        location.save()

        assert location.slug == f"{location.id} {slugify(str(location))}"

    @pytest.mark.django_db
    def test_save_slug_form(self):
        location = self.location_instance()
        location.save()
        assert location.slug_form == slugify(str(location))
