import django_filters
from django_filters.widgets import RangeWidget

from ticket.models import Ticket


class TicketFilter(django_filters.FilterSet):
    chupiaohang = django_filters.CharFilter(lookup_expr='icontains')
    piaomianjiage = django_filters.NumberFilter(label='票面价格')
    chupiaoriqi = django_filters.DateFromToRangeFilter(label='出票日期',widget=RangeWidget(attrs={'placeholder': 'YYYY/MM/DD'}))
    price__gt = django_filters.NumberFilter(label='票面价格da',name='piaomianjiage', lookup_expr='gt')
    price__lt = django_filters.NumberFilter(label='票面价格xiao', name='piaomianjiage', lookup_expr='lt')
    class Meta:
        model = Ticket
        fields = {
            'gourujiage',
            'goumairiqi',
            'chupiaoriqi',
        }