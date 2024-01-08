from .mixins import NameFieldMixin


class Company(NameFieldMixin):
    """customers companies CRUD by commercials"""

    @classmethod
    def french_name(self) -> str:
        """used in flash messages"""

        return "Entreprise"

    @classmethod
    def french_plural_name(self) -> str:
        """used as title in template 'list'"""

        return f"{self.french_name()}s"
