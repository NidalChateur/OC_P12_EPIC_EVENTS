import pytest
from django.urls import resolve, reverse
from django.views import View

from epic_events.urls.contract_filter import (
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
)


class TestContractFilter:
    @pytest.mark.parametrize(
        "url_path, url_name, id, ViewClass",
        [
            (
                "/contracts/signed_paid/",
                "signed_paid_contracts",
                None,
                SignedPaidContracts,
            ),
            (
                "/contracts/signed_unpaid/",
                "signed_unpaid_contracts",
                None,
                SignedUnpaidContracts,
            ),
            (
                "/contracts/unsigned_paid/",
                "unsigned_paid_contracts",
                None,
                UnsignedPaidContracts,
            ),
            (
                "/contracts/unsigned_unpaid/",
                "unsigned_unpaid_contracts",
                None,
                UnsignedUnpaidContracts,
            ),
            (
                "/contracts/ready_for_event/",
                "ready_for_event_contracts",
                None,
                ReadyForEventContracts,
            ),
            (
                "/collaborators/1/my_contracts/signed_paid/",
                "my_signed_paid_contracts",
                1,
                MySignedPaidContracts,
            ),
            (
                "/collaborators/1/my_contracts/signed_unpaid/",
                "my_signed_unpaid_contracts",
                1,
                MySignedUnpaidContracts,
            ),
            (
                "/collaborators/1/my_contracts/unsigned_paid/",
                "my_unsigned_paid_contracts",
                1,
                MyUnsignedPaidContracts,
            ),
            (
                "/collaborators/1/my_contracts/unsigned_unpaid/",
                "my_unsigned_unpaid_contracts",
                1,
                MyUnsignedUnpaidContracts,
            ),
            (
                "/collaborators/1/my_contracts/ready_for_event/",
                "my_ready_for_event_contracts",
                1,
                MyReadyForEventContracts,
            ),
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
