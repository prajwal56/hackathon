from rest_framework_mongoengine.serializers import DocumentSerializer
from .models import Rules  # Your MongoEngine model

class RulesSerializer(DocumentSerializer):
    class Meta:
        model = Rules
        fields = '__all__'
