from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from .controllers import EventController
from .serializers import EventSerializer

class EventViewSet(viewsets.ViewSet):
    """
    ViewSet for managing Event operations.
    """

    @action(detail=False, methods=['post'], url_path='create_event')
    def create_event(self, request):
        """
        Create a new event.
        """
        try:
            data = EventController.create_event(request)
            return Response(data, status=status.HTTP_201_CREATED)
        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)
