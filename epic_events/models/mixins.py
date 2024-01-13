import phonenumbers
from django.db import models
from django.utils import timezone
from django.utils.text import slugify
from phonenumber_field.modelfields import PhoneNumberField

from .str_template import unfilled


class TimeFieldMixin(models.Model):
    slug = models.SlugField(max_length=255, null=True)
    creation_time = models.DateTimeField(auto_now_add=True, null=True)
    edition_time = models.DateTimeField(auto_now_add=True, null=True)

    class Meta:
        abstract = True

    @classmethod
    def singular_name(self) -> str:
        return self.__name__.lower()

    @classmethod
    def plural_name(self) -> str:
        if self.singular_name() == "company":
            return "companies"
        return f"{self.singular_name()}s"

    @classmethod
    def template_name_list(self) -> str:
        return f"{self.singular_name()}/list.html"

    @classmethod
    def template_name_detail(self) -> str:
        return f"{self.singular_name()}/detail.html"

    @classmethod
    def template_name_create(self) -> str:
        return f"{self.singular_name()}/form.html"

    @classmethod
    def template_name_delete(self) -> str:
        return f"{self.singular_name()}/delete.html"

    @classmethod
    def my_list_url_name(self) -> str:
        return f"my_{self.plural_name()}"

    @classmethod
    def create_url_name(self) -> str:
        return f"create_{self.singular_name()}"

    @classmethod
    def update_url_name(self) -> str:
        return f"update_{self.singular_name()}"

    @classmethod
    def delete_url_name(self) -> str:
        return f"delete_{self.singular_name()}"

    @classmethod
    def search_url_name(self) -> str:
        return f"search_{self.singular_name()}"

    def save(self, *args, **kwargs):
        self.edition_time = timezone.now()
        super().save(*args, **kwargs)


class NameFieldMixin(TimeFieldMixin):
    name = models.CharField(max_length=128)

    class Meta:
        abstract = True

    def __str__(self) -> str:
        if self.name:
            return f"{self.name.capitalize()}"
        return unfilled

    def save(self, *args, **kwargs):
        # first save to generate self.id
        super().save(*args, **kwargs)

        self.slug = f"{self.id} {slugify(self.name)}"

        super().save(*args, **kwargs)


class UserMixin(TimeFieldMixin):
    first_name = models.CharField(max_length=150, verbose_name="Prénom")
    last_name = models.CharField(max_length=150, verbose_name="Nom")
    email = models.EmailField(unique=True)
    phone = PhoneNumberField(null=True, blank=True)

    class Meta:
        abstract = True

    def __str__(self) -> str:
        if self.first_name:
            first_name = self.first_name.capitalize()
        else:
            first_name = unfilled

        if self.last_name:
            last_name = self.last_name.capitalize()
        else:
            last_name = unfilled

        return f"{first_name} {last_name}"

    @property
    def name(self) -> str:
        return str(self)

    @property
    def formatted_phone(self):
        if self.phone:
            return phonenumbers.format_number(
                self.phone, phonenumbers.PhoneNumberFormat.INTERNATIONAL
            )
        return unfilled

    def save(self, *args, **kwargs):
        # first save to generate self.id
        super().save(*args, **kwargs)

        # building the slug field
        slug_first_name = slugify(self.first_name)
        slug_last_name = slugify(self.last_name)
        slug_email = slugify(self.email)

        if self.singular_name() == "collaborator":
            slug_foreign_key = slugify(self.role)

        if self.singular_name() == "customer":
            slug_foreign_key = (
                f"{slugify(self.company_name)} {slugify(self.commercial_name)}"
            )

        self.slug = f"{self.id} {slug_first_name} {slug_last_name} {slug_email} {slug_foreign_key}"
        super().save(*args, **kwargs)
