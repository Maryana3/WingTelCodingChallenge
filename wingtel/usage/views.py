from rest_framework import viewsets
from wingtel.usage.models import AggregatedUsageRecord
from wingtel.usage.serializers import SubscriptionsPriceLimitSerializer
from django.db.models import Q
from rest_framework.response import Response
from django.db.models import Count, Sum
from django.db import transaction


class UsageMetricsBySubscriptionUsageTypeViewSet(viewsets.ViewSet):
    """
    A viewset that provides `retrieve`, `create`, and `list` actions.
    """

    def list(self, request):
        queryset = AggregatedUsageRecord.objects.all()
        subscription_id = self.request.query_params.get("subscription_id", None)
        start_date = self.request.query_params.get("start_date", None)
        end_date = self.request.query_params.get("end_date", None)
        usage_type = self.request.query_params.get("usage_type", None)
        if subscription_id:
            queryset = queryset.filter(Q(att_subscription_id__id=subscription_id)
                                       | Q(sprint_subscription_id__id=subscription_id))
        if usage_type:
            queryset = queryset.filter(usage_type=usage_type)
        if start_date and end_date:
            queryset = queryset.filter(usage_date__range=[start_date, end_date])
        result = queryset.aggregate(att_subscription_count=Count("att_subscription_id"),
                                    sprint_subscription_count=Count("sprint_subscription_id"),
                                    total_price_usage=Sum("att_subscription_id__plan__price") +
                                                      Sum("sprint_subscription_id__plan__price"),
                                    att_subscription_id__plan__price=Sum("att_subscription_id__plan__price"),
                                    sprint_subscription_id__plan__price=Sum("sprint_subscription_id__plan__price"))
        result["att_subscription_id"] = subscription_id
        result["sprint_subscription_id"] = subscription_id
        return Response(result)


class SubscriptionsExceedingUsagePriceLimitViewSet(viewsets.ModelViewSet):
    """
    A viewset that provides `retrieve`, `create`, and `list` actions.
    """
    queryset = AggregatedUsageRecord.objects.all()
    serializer_class = SubscriptionsPriceLimitSerializer

    @transaction.atomic
    def get_queryset(self):

        price_limit = self.request.query_params.get("price_limit", None)

        if price_limit:
            return self.queryset.filter((Q(att_subscription_id__plan__price__gt=price_limit) |
                                         Q(sprint_subscription_id__plan__price__gt=price_limit)))
        return self.queryset
        """

        from django.db import transaction
        from datetime import datetime
        from django.test import TestCase
        from wingtel.att_subscriptions.models import ATTSubscription
        from wingtel.sprint_subscriptions.models import SprintSubscription
        from wingtel.plans.models import Plan
        from django.contrib.auth.models import User
        from wingtel.usage.models import AggregatedUsageRecord
        print(ATTSubscription.objects.all().count(),SprintSubscription.objects.all().count(),
              AggregatedUsageRecord.objects.all().count(),User.objects.all().count(),sep=" ")
        try:
            AggregatedUsageRecord.objects.all().delete()
            ATTSubscription.objects.all().delete()
            SprintSubscription.objects.all().delete()
            User.objects.all().delete()
        except Exception as e:
            print(e)
        print(ATTSubscription.objects.all().count(), SprintSubscription.objects.all().count(),
              AggregatedUsageRecord.objects.all().count(), User.objects.all().count(), sep=" ")
        print("ATTSubscription.objects.all().count() ",ATTSubscription.objects.all().count(),
              "SprintSubscription.objects.all().count() ",SprintSubscription.objects.all().count())

        user1 = User.objects.create_user('john', 'lennon@thebeatles.com', 'johnpassword')
        tmp1 = Plan.objects.create(name="tmp1",price=5)
        tmp2 = Plan.objects.create(name="tmp2", price=10)
        tmp3 = Plan.objects.create(name="tmp3", price=15)
        tmp4 = Plan.objects.create(name="tmp4", price=20)
        i = ATTSubscription.objects.create(user=user1,plan=tmp1,status="new")
        print("id i",i.id)
        ATTSubscription.objects.create(user=user1,plan=tmp2, status="active")
        ATTSubscription.objects.create(user=user1,plan=tmp3, status="expired")
        ATTSubscription.objects.create(user=user1,plan=tmp4, status="active")

        SprintSubscription.objects.create(user=user1,plan=tmp4, status="new")
        SprintSubscription.objects.create(user=user1,plan=tmp3, status="active")
        SprintSubscription.objects.create(user=user1,plan=tmp2, status="expired")
        SprintSubscription.objects.create(user=user1,plan=tmp1, status="active")

        import json
        # Opening JSON file
        f = open('wingtel/usage/fixtures.json',"rb" )
        data = json.load(f)
        try:
            for item in data:
                item_ = item['fields']
                import pytz
                if item["model"] == "usage.datausagerecord":
                    AggregatedUsageRecord.objects.create(
                        att_subscription_id_id=item_["subscription"],
                        sprint_subscription_id_id=item_["subscription"],
                        price=item_["price"],
                        usage_date= datetime.strptime(item_["usage_date"],"%Y-%m-%dT%H:%M:%S.%fZ"),
                        usage_type="data",
                        used_metric_value=item_["kilobytes_used"]
                    )
                if item["model"] == "usage.voiceusagerecord":
                    AggregatedUsageRecord.objects.create(
                        att_subscription_id_id=item_["subscription"],
                        sprint_subscription_id_id=item_["subscription"],
                        price=item_["price"],
                        usage_date=datetime.strptime(item_["usage_date"],"%Y-%m-%dT%H:%M:%S.%fZ"),
                        usage_type="voice",
                        used_metric_value=item_["seconds_used"]
                    )
        except Exception as e:
            print("Exception ",e)
        """
