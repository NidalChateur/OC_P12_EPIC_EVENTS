from .mixins import NameFieldMixin


class Department(NameFieldMixin):
    @classmethod
    def french_name(self) -> str:
        """used in flash messages"""

        return "Département"

    @classmethod
    def french_plural_name(self) -> str:
        """used as title in template 'list'"""

        return f"{self.french_name()}s"
