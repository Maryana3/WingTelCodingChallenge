from rest_framework import viewsets
from wingtel.usage.models import UsageRecord
from wingtel.usage.serializers import SubscriptionsPriceLimitSerializer
from wingtel.subscriptions.serializers import Subscription
from django.db.models import Q
from rest_framework.response import Response
from django.db.models import Count, Sum, Case, When, IntegerField
from django_filters.rest_framework import DjangoFilterBackend


class UsageMetricsBySubscriptionUsageTypeViewSet(viewsets.ViewSet):
    """
    A viewset that provides `retrieve`, `create`, and `list` actions.
    """

    def list(self, request):
        start_date = self.request.query_params.get("start_date", None)
        end_date = self.request.query_params.get("end_date", None)
        usage_type = self.request.query_params.get("usage_type", None)
        queryset = UsageRecord.objects.all()
        if usage_type:
            queryset = queryset.filter(usage_type=usage_type)
        if start_date or end_date:
            queryset = queryset.filter(
                usage_date__range=[start_date, end_date],
            )
        result = queryset.values(
            'subscriptions__id'
        ).annotate(
            total_sum=Sum('price'),
            total_usage=Count('price'),
        ).order_by('subscriptions__id')
        return Response(result)


class SubscriptionsExceedingUsagePriceLimitViewSet(viewsets.ModelViewSet):
    """
    A viewset that provides `retrieve`, `create`, and `list` actions.
    """
    queryset = UsageRecord.objects.all()
    serializer_class = SubscriptionsPriceLimitSerializer

    def get_queryset(self):

        price_limit = self.request.query_params.get("price_limit", 0)
        return self.queryset.filter(subscriptions__plan__price__gt=price_limit)