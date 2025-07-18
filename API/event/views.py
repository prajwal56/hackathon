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
        
    @action(detail=False, methods=['get'], url_path='event_list')
    def get_event_list(self, request):
        """
        Get a list of events.
        """
        try:
            data = EventController.get_event_list(request)
            return Response(data, status=status.HTTP_200_OK)
        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)

    @action(detail=False, methods=['post'], url_path='get_event_rca')
    def get_event_rca(self, request):
        """
        Get RCA for an event.
        """
        try:
            data = EventController.get_event_rca(request)
            return Response(data, status=status.HTTP_200_OK)
        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)
    
    @action(detail=False, methods=['get'], url_path='get_event_chart')
    def get_event_chart(self, request):
        """
        Get chart data for an event.
        """
        try:
            data = EventController.transform_events_to_5min_summary(request)
            return Response(data, status=status.HTTP_200_OK)
        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)
        
    @action(detail=False, methods=['get'], url_path='get_rule_donut_chart')
    def get_rule_donut_chart(self, request):
        """
        Get donut chart data for rules.
        """
        try:
            data = EventController.get_rule_donut_chart(request)
            return Response(data, status=status.HTTP_200_OK)
        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)
        
    @action(detail=False, methods=['post'], url_path='execute_custom_commands')
    def execute_commands(self, request):
        """
        Get RCA for an event.
        """
        try:
            data = EventController.executeCommands(request)
            return Response(data, status=status.HTTP_200_OK)
        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)
        
    @action(detail=False, methods=['post'], url_path='generate_event')
    def generate_event(self, request):
        """
        Generate event and run corresponding script based on event name.
        """
        try:
            data = EventController.generate_event(request)
            return Response(data, status=status.HTTP_200_OK)
        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)
        
    @action(detail=False, methods=['post'], url_path='mark_resolved')
    def mark_resolved(self, request):
        """
        Mark an event as resolved.
        """
        try:
            eveny_id = request.data.get('event_id',"")
            data = EventController.mark_resolved(request,eveny_id)
            EventController.clear_ai_memory()
            return Response(data, status=status.HTTP_200_OK)
        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)
        
    @action(detail=False, methods=['post'], url_path='clear_ai_memory')
    def clear_ai_memory(self, request):
        """
        Generate event and run corresponding script based on event name.
        """
        try:
            data = EventController.clear_ai_memory()
            return Response(data, status=status.HTTP_200_OK)
        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)
        
    @action(detail=False, methods=['get'], url_path='get_success_rate')
    def get_success_rate(self, request):
        """
        Get success rate for an event.
        """
        try:
            data = EventController.get_success_rate(request)
            return Response(data, status=status.HTTP_200_OK)
        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)