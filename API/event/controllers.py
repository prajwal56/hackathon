from .serializers import EventSerializer
from .models import Event
from API.log_rca_engine.ai_engine import AIEngine
class EventController:
    """
    Handles business logic for Event operations.
    """
    ai_engine = AIEngine()
    @staticmethod
    def create_event(request):
        """
        Validates and creates a new Event document.
        """
        serializer = EventSerializer(data=request.data)
        if serializer.is_valid(raise_exception=True):
            event = serializer.save()
            return EventSerializer(event).data
        
    @staticmethod
    def get_event_list(request):
        """
        Retrieves a list of all Event documents.
        """
        events = Event.objects.all()
        return EventSerializer(events, many=True).data

    @staticmethod
    def get_event_rca(request):
        """
        Retrieves a list of all Event documents.
        """ 
        data = request.data
        RCA_data = EventController.ai_engine.generate_prompt(str(data))
        return RCA_data
    
        
        