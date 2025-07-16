from .serializers import EventSerializer

class EventController:
    """
    Handles business logic for Event operations.
    """

    @staticmethod
    def create_event(request):
        """
        Validates and creates a new Event document.
        """
        serializer = EventSerializer(data=request.data)
        if serializer.is_valid(raise_exception=True):
            event = serializer.save()
            return EventSerializer(event).data
