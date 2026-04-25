from django.contrib import messages
from django.shortcuts import redirect, render

from apps.core.exceptions import RepositoryError
from apps.deals.dtos import DealCreateDTO
from apps.deals.forms import DealCreateForm
from apps.deals.services import DealService


deal_service = DealService()


def deal_list(request):
    try:
        deals = deal_service.list_deals()
    except RepositoryError as e:
        deals = []
        messages.error(request, str(e))

    return render(
        request,
        "deals/deal_list.html",
        {
            "deals": deals,
        },
    )


def deal_create(request):
    if request.method == "POST":
        form = DealCreateForm(request.POST)

        if form.is_valid():
            dto = DealCreateDTO(**form.cleaned_data)

            try:
                deal_id = deal_service.create_deal(dto)
                messages.success(request, f"案件を登録しました: {deal_id}")
                return redirect("deals:list")
            except RepositoryError as e:
                messages.error(request, str(e))
    else:
        form = DealCreateForm()

    return render(
        request,
        "deals/deal_create.html",
        {
            "form": form,
        },
    )

# Create your views here.
