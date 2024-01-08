from django.db import models
from django.utils.text import slugify

from .mixins import TimeFieldMixin
from .str_template import unfilled


class Location(TimeFieldMixin):
    STREET_TYPE = [
        ("", ""),
        ("rue", "rue"),
        ("impasse", "impasse"),
        ("avenue", "avenue"),
        ("boulevard", "boulevard"),
        ("allée", "allée"),
        ("chemin", "chemin"),
    ]

    name = models.CharField(
        max_length=128, verbose_name="Nom du lieu", blank=True, null=True
    )
    number = models.CharField(
        max_length=50, blank=True, null=True, verbose_name="Numéro de voie"
    )
    street_type = models.CharField(
        max_length=100,
        choices=STREET_TYPE,
        blank=True,
        null=True,
        verbose_name="Type de voie",
    )
    street_name = models.CharField(
        max_length=100,
        blank=True,
        null=True,
        verbose_name="Nom de voie",
    )
    city = models.CharField(
        max_length=100,
        verbose_name="Ville",
    )
    zip = models.CharField(
        max_length=6,
        verbose_name="Code postal",
    )
    slug_form = models.SlugField(null=True, max_length=255)

    def __str__(self, name=True) -> str:
        if self.name and name:
            name = f"{self.name.strip().title()} "
        else:
            name = ""

        if self.number:
            number = f"{self.number.strip().upper()} "
        else:
            number = ""

        if self.street_type:
            street_type = f"{self.street_type} "
        else:
            street_type = ""

        if self.street_name:
            street_name = f"{self.street_name.strip().title()}, "
        else:
            street_name = ""

        if self.zip:
            zip = f"{self.zip} "
        else:
            zip = ""

        if self.city:
            city = f"{self.city.strip().capitalize()}"
        else:
            city = ""

        return f"{name} {number} {street_type} {street_name} {zip} {city}"

    @property
    def formatted_name(self) -> str:
        if self.name:
            return self.name.strip().title()

        return unfilled

    @property
    def formatted_address(self) -> str:
        return self.__str__(name=False)

    @classmethod
    def french_name(self) -> str:
        """used in flash messages"""

        return "Lieu"

    @classmethod
    def french_plural_name(self) -> str:
        """used as title in template 'list'"""

        return f"{self.french_name()}x"

    def save(self, *args, **kwargs):
        self.slug_form = slugify(str(self))
        # get self.id
        super().save(*args, **kwargs)
        self.slug = f"{self.id} {slugify(str(self))}"
        super().save(*args, **kwargs)
