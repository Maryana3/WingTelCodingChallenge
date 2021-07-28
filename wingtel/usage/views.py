from rest_framework import viewsets
from wingtel.usage.models import UsageRecord
from wingtel.usage.serializers import SubscriptionsPriceLimitSerializer
from django.db.models import Q
from rest_framework.response import Response
from django.db.models import Count, Sum, Case, When, IntegerField
from django.db import transaction
from django_filters.rest_framework import DjangoFilterBackend


class UsageMetricsBySubscriptionUsageTypeViewSet(viewsets.ViewSet):
    """
    A viewset that provides `retrieve`, `create`, and `list` actions.
    """

    def list(self, request):
        queryset = UsageRecord.objects.all()
        subscription_id = self.request.query_params.get("subscription_id", None)
        start_date = self.request.query_params.get("start_date", None)
        end_date = self.request.query_params.get("end_date", None)
        usage_type = self.request.query_params.get("usage_type", None)
        if subscription_id:
            queryset = queryset.filter(subscription_id__in=subscription_id)
        if usage_type:
            queryset = queryset.filter(usage_type=usage_type)
        if start_date and end_date:
            queryset = queryset.filter(usage_date__range=[start_date, end_date])
        result = queryset.aggregate(subscription_count=Count("subscription__id"),
                                    total_price_usage=Sum("subscription__plan__price"),
                                    att_subscription__count=Count(Case(When(subscriptions__subscription_type="att",
                                                                                then=1),
                                                                           output_field=IntegerField())),
                                    sprint_subscription__count=Sum(
                                        Case(When(subscriptions__subscription_type="sprint",
                                                  then=subscriptions___plan__price),
                                             output_field=IntegerField()),
                                    att_subscription__plan__price_sum=Sum(Case(When(subscriptions__subscription_type="att",
                                                                            then=subscriptions___plan__price),
                                                                       output_field=IntegerField())),
                                    sprint_subscription__plan__price_sum=Sum(Case(When(subscriptions__subscription_type="sprint",
                                                                            then=subscriptions___plan__price),
                                                                       output_field=IntegerField()))))
        result["subscription_id"] = [subscription_id] if subscription_id else []

        return Response(result)


class SubscriptionsExceedingUsagePriceLimitViewSet(viewsets.ModelViewSet):
    """
    A viewset that provides `retrieve`, `create`, and `list` actions.
    """
    queryset = UsageRecord.objects.all()
    serializer_class = SubscriptionsPriceLimitSerializer

    @transaction.atomic
    def get_queryset(self):

        price_limit = self.request.query_params.get("price_limit", 0)
        return self.queryset.filter(subscriptions__plan__price__gt=price_limit)
        """


        from django.db import transaction
        from datetime import datetime
        from django.test import TestCase
        from wingtel.subscriptions.models import Subscription
        from wingtel.plans.models import Plan
        from django.contrib.auth.models import User
        from wingtel.usage.models import UsageRecord

        print("User.objects ",User.objects.all().count())
        user1 = User.objects.create_user('john', 'lennon@thebeatles.com', 'johnpassword')
        tmp1 = Plan.objects.create(name="tmp1",price=5)
        tmp2 = Plan.objects.create(name="tmp2", price=10)
        tmp3 = Plan.objects.create(name="tmp3", price=15)
        tmp4 = Plan.objects.create(name="tmp4", price=20)
        from decimal import Decimal

        Subscription.objects.create(user=user1,plan=tmp4, status="new",subscription_type="att",ONE_KILOBYTE_PRICE = Decimal('0.001'),ONE_SECOND_PRICE = Decimal('0.001'))
        Subscription.objects.create(user=user1,plan=tmp3, status="active",subscription_type="sprint")
        Subscription.objects.create(user=user1,plan=tmp2, status="expired",subscription_type="att",ONE_KILOBYTE_PRICE = Decimal('0.001'),ONE_SECOND_PRICE = Decimal('0.001'))
        Subscription.objects.create(user=user1,plan=tmp1, status="active",subscription_type="sprint")

        import json
        # Opening JSON file
        f = open('wingtel/usage/fixtures.json',"rb" )
        data = json.load(f)
        try:
            for item in data:
                item_ = item['fields']
                import pytz
                if item["model"] == "usage.datausagerecord":
                    obj = UsageRecord.objects.create(
                        price=item_["price"],
                        usage_date= datetime.strptime(item_["usage_date"],"%Y-%m-%dT%H:%M:%S.%fZ"),
                        usage_type="data",
                        used_metric_value=item_["kilobytes_used"]
                    )
                    print("obj",obj.subscriptions)
                    obj.subscriptions.add(Subscription.objects.get(id=item_["subscription"]))
                    print("obj",obj.subscriptions)
                    obj.save()
                    print("obj",obj.subscriptions)
                if item["model"] == "usage.voiceusagerecord":
                    obj = UsageRecord.objects.create(
                        price=item_["price"],
                        usage_date=datetime.strptime(item_["usage_date"],"%Y-%m-%dT%H:%M:%S.%fZ"),
                        usage_type="voice",
                        used_metric_value=item_["seconds_used"]
                    )
                    print("obj",obj.subscriptions)
                    print(Subscription.objects.get(id=item_["subscription"]))
                    obj.subscriptions.add(Subscription.objects.get(id=item_["subscription"]))
                    print("obj",obj.subscriptions)
                    obj.save()
                    print("obj",obj.subscriptions)
        except Exception as e:
            print("Exception ",e)
        """

