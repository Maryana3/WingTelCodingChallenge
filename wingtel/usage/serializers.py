from rest_framework import serializers
import decimal
from wingtel.usage.models import AggregatedUsageRecord


class SubscriptionsPriceLimitSerializer(serializers.ModelSerializer):
    limit_subscriptions = serializers.SerializerMethodField()

    def get_limit_subscriptions(self, obj):
        exceeded_price_subscriptions = []
        price_limit = float(self.context['request'].query_params.get("price_limit", None))
        price_limit = decimal.Decimal(price_limit)
        att_plan = obj.att_subscription_id.plan
        sprint_plan = obj.sprint_subscription_id.plan
        if price_limit and price_limit < att_plan.price:
            exceeded_price_subscriptions.append({"att_subscription_id": obj.att_subscription_id.id,
                                                 "plan_price": att_plan.price,
                                                  "price_exceeded":  att_plan.price - price_limit})
        if price_limit and price_limit < sprint_plan.price:
            exceeded_price_subscriptions.append({"sprint_subscription_id": obj.sprint_subscription_id.id,
                                                 "plan_price": sprint_plan.price,
                                                  "price_exceeded": sprint_plan.price - price_limit})
        return exceeded_price_subscriptions

    class Meta:
        model = AggregatedUsageRecord
        fields = ["id", "usage_type", "limit_subscriptions"]