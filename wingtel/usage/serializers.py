from rest_framework import serializers
import decimal
from wingtel.usage.models import UsageRecord
from django.db.models import Count, Sum, Case, When, IntegerField


class SubscriptionsPriceLimitSerializer(serializers.ModelSerializer):
    limit_subscriptions = serializers.SerializerMethodField()

    def get_limit_subscriptions(self, obj):
        exceeded_price_subscriptions = []
        try:
            price_limit = float(self.context['request'].query_params.get("price_limit", None))
            price_limit = decimal.Decimal(price_limit)
            exceeded_price_subscriptions = obj.subscriptions.values('id').annotate(plan_price=Sum('plan__price'),
                                                                    price_exceeded=Sum('plan__price')-price_limit).\
                    order_by('id')

            """
            subscriptions = obj.subscriptions.all()
            for subscription in subscriptions:
                if price_limit and subscription.plan.price:
                    exceeded_price_subscriptions.append({"subscription_id": subscription.id,
                                                         "plan_price": subscription.plan.price,
                                                         "price_exceeded": subscription.plan.price
                                                                           - price_limit})
            """
        except:
            pass

        return exceeded_price_subscriptions

    class Meta:
        model = UsageRecord
        fields = ["id", "usage_type", "limit_subscriptions"]