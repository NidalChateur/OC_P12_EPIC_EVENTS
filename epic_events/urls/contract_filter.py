from django.urls import path

from ..views.contract_filter import (
    MyReadyForEventContracts,
    MySignedPaidContracts,
    MySignedUnpaidContracts,
    MyUnsignedPaidContracts,
    MyUnsignedUnpaidContracts,
    ReadyForEventContracts,
    SignedPaidContracts,
    SignedUnpaidContracts,
    UnsignedPaidContracts,
    UnsignedUnpaidContracts,
    model,
)

urlpatterns = [
    # all contracts
    path(
        f"{model.plural_name()}/signed_paid/",
        SignedPaidContracts.as_view(),
        name=f"signed_paid_{model.plural_name()}",
    ),
    path(
        f"{model.plural_name()}/signed_unpaid/",
        SignedUnpaidContracts.as_view(),
        name=f"signed_unpaid_{model.plural_name()}",
    ),
    path(
        f"{model.plural_name()}/unsigned_paid/",
        UnsignedPaidContracts.as_view(),
        name=f"unsigned_paid_{model.plural_name()}",
    ),
    path(
        f"{model.plural_name()}/unsigned_unpaid/",
        UnsignedUnpaidContracts.as_view(),
        name=f"unsigned_unpaid_{model.plural_name()}",
    ),
    path(
        f"{model.plural_name()}/ready_for_event/",
        ReadyForEventContracts.as_view(),
        name=f"ready_for_event_{model.plural_name()}",
    ),
    # commercial contracts
    path(
        f"collaborators/<int:id>/{model.my_list_url_name()}/signed_paid/",
        MySignedPaidContracts.as_view(),
        name=f"my_signed_paid_{model.plural_name()}",
    ),
    path(
        f"collaborators/<int:id>/{model.my_list_url_name()}/signed_unpaid/",
        MySignedUnpaidContracts.as_view(),
        name=f"my_signed_unpaid_{model.plural_name()}",
    ),
    path(
        f"collaborators/<int:id>/{model.my_list_url_name()}/unsigned_paid/",
        MyUnsignedPaidContracts.as_view(),
        name=f"my_unsigned_paid_{model.plural_name()}",
    ),
    path(
        f"collaborators/<int:id>/{model.my_list_url_name()}/unsigned_unpaid/",
        MyUnsignedUnpaidContracts.as_view(),
        name=f"my_unsigned_unpaid_{model.plural_name()}",
    ),
    path(
        f"collaborators/<int:id>/{model.my_list_url_name()}/ready_for_event/",
        MyReadyForEventContracts.as_view(),
        name=f"my_ready_for_event_{model.plural_name()}",
    ),
]
