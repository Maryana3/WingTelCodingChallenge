from rest_framework import viewsets

from wingtel.subscriptions.models import Subscription
from wingtel.subscriptions.serializers import SubscriptionSerializer


class SubscriptionViewSet(viewsets.ModelViewSet):
    """
    A viewset that provides `retrieve`, `create`, and `list` actions.
    """
    queryset = Subscription.objects.all()
    serializer_class = SubscriptionSerializer
