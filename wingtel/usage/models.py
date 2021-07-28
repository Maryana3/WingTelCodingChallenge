from django.db import models
from model_utils import Choices
from wingtel.subscriptions.models import Subscription


class UsageRecord(models.Model):
    """Raw data usage record for a subscription"""
    subscriptions = models.ManyToManyField(Subscription)
    price = models.DecimalField(decimal_places=2, max_digits=5, default=0)
    usage_date = models.DateTimeField(null=True)
    used_metric_value = models.IntegerField(null=False)
    usage_type = models.CharField(max_length=20, default="")

    class Meta:
        ordering = ('usage_date', )
