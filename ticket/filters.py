import django_filters

from ticket.models import Ticket


class TicketFilter(django_filters.FilterSet):
    chupiaohang = django_filters.CharFilter(lookup_expr='icontains')
    piaomianjiage = django_filters.NumberFilter()
    price__gt = django_filters.NumberFilter(name='piaomianjiage', lookup_expr='gt')
    price__lt = django_filters.NumberFilter(name='piaomianjiage', lookup_expr='lt')
    class Meta:
        model = Ticket
        fields = ['gongyingshang', 'chupiaohang', 'chupiaoriqi']