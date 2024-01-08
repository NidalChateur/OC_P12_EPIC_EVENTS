from django.db import models

from .collaborator import Collaborator
from .company import Company
from .mixins import UserMixin
from .str_template import unfilled


class Customer(UserMixin):
    company = models.ForeignKey(to=Company, on_delete=models.SET_NULL, null=True)
    commercial = models.ForeignKey(
        to=Collaborator, on_delete=models.SET_NULL, null=True, related_name="commercial"
    )

    @property
    def company_name(self):
        if self.company:
            return self.company.name.capitalize()
        return unfilled

    @property
    def commercial_name(self):
        if self.commercial:
            return self.commercial.name
        return unfilled

    @classmethod
    def french_name(self) -> str:
        """used in flash messages"""

        return "Client"

    @classmethod
    def french_plural_name(self) -> str:
        """used as title in template 'list'"""

        return f"{self.french_name()}s"
