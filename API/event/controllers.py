from .serializers import EventSerializer
from .models import Event
from API.log_rca_engine.ai_engine import AIEngine
from datetime import datetime
from zoneinfo import ZoneInfo 
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
        Retrieves a list of all Event documents with created_at converted to IST and formatted.
        """
        events = Event.objects.all()
        data = EventSerializer(events, many=True).data

        for i in data:
            time = i.get("created_at")
            if time:
                # Parse string in UTC
                dt = datetime.strptime(time, '%Y-%m-%dT%H:%M:%S.%fZ')
                dt = dt.replace(tzinfo=ZoneInfo('UTC'))

                # Convert to IST
                ist_time = dt.astimezone(ZoneInfo('Asia/Kolkata'))

                # Format
                formatted = ist_time.strftime('%d-%m-%Y %I:%M:%S %p')
                i['created_at'] = formatted

        return data

    @staticmethod
    def get_event_rca(request):
        """
        Retrieves a list of all Event documents.
        """ 
        data = request.data
        RCA_data = EventController.ai_engine.generate_prompt(str(data))
        return RCA_data
    
        
        