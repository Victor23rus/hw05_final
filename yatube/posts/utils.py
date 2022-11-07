from django.core.paginator import Paginator

NUM = 10


def paginate_page(queryset, request):
    paginator = Paginator(queryset, NUM)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    return page_obj
