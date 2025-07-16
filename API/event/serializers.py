from rest_framework_mongoengine.serializers import DocumentSerializer
from .models import Event

class EventSerializer(DocumentSerializer):
    class Meta:
        model = Event
        fields = '__all__'
