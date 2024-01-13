from django.core.paginator import Paginator


def paginator(request, qs: list) -> Paginator:
    """split the qs into 10 instances per page"""

    paginator = Paginator(qs, 10)
    page_number = request.GET.get("page")

    return paginator.get_page(page_number)
