from django.contrib.auth.models import AbstractUser
from django.db import models

from .department import Department
from .mixins import UserMixin
from .str_template import unfilled


class Collaborator(UserMixin, AbstractUser):
    """
    Permissions :

    Manager :  can CRUD Collaborator(), Contract() and update Event().support_id.
    Commercial : can CRUD Customer(), Company(), Event(), Location() and update Contract().
    Support : can update Event()"""

    department = models.ForeignKey(to=Department, on_delete=models.RESTRICT, null=True)

    birthdate = models.DateField(null=True, verbose_name="Date de naissance")

    REQUIRED_FIELDS = ["first_name", "last_name"]
    USERNAME_FIELD = "email"
    username = date_joined = None

    @property
    def str_id(self):
        if self.id:
            return str(self.id)

    @property
    def role(self) -> str:
        if self.department:
            return f"{self.department.name.capitalize()}"
        else:
            return unfilled

    @property
    def title(self) -> str:
        if self.first_name:
            return f"{self.role} {self.first_name.capitalize()}"
        else:
            return unfilled

    @classmethod
    def french_name(self) -> str:
        """used in flash messages"""

        return "Collaborateur"

    @classmethod
    def french_plural_name(self) -> str:
        """used as title in template 'list'"""

        return f"{self.french_name()}s"
