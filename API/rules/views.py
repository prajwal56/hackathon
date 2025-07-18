from rest_framework import viewsets, status
from rest_framework.response import Response
from rest_framework.decorators import action
from drf_yasg.utils import swagger_auto_schema
from .controllers import RulesController
from .serializers import RulesSerializer
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework import status
from drf_yasg.utils import swagger_auto_schema
from .serializers import RulesSerializer
from .controllers import RulesController  # adjust if needed
from django.core.exceptions import ObjectDoesNotExist, ValidationError

class RulesViewSet(viewsets.ViewSet):
    """
    A ViewSet for managing Rules. Delegates logic to controllers.py.
    """
    
    @swagger_auto_schema(
        operation_description="List all rules",
        responses={200: RulesSerializer(many=True)}
    )
    @action(detail=False, methods=['get'], url_path='list')
    def list_rules(self, request):
        """
        List all rules.
        """
        return Response(RulesController.list_rules(self,request))

    @swagger_auto_schema(
        operation_description="Retrieve a rule by ID",
        responses={200: RulesSerializer(), 404: "Rule not found"}
    )
    @action(detail=False, methods=['get'], url_path='edit/(?P<pk>[^/.]+)')
    def retrieve_rule(self, request, pk=None):
        """
        Retrieve a single rule via: /api/rules/edit/<pk>/
        """
        try:
            data = RulesController.get_rule(self,request, pk)
            return Response(data)
        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_404_NOT_FOUND)

    @swagger_auto_schema(
        operation_description="Create a new rule",
        request_body=RulesSerializer,
        responses={201: RulesSerializer(), 400: "Validation error"}
    )
    @action(detail=False, methods=['post'], url_path='create')
    def create_rule(self, request):
        """
        Create a rule.
        """
        try:
            data = RulesController.create_rule(self,request, request.data)
            return Response(data, status=status.HTTP_201_CREATED)
        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)

    @swagger_auto_schema(
        operation_description="Update an existing rule",
        request_body=RulesSerializer,
        responses={
            200: RulesSerializer(),
            400: "Validation error",
            404: "Rule not found"
        }
    )
    @action(detail=False, methods=['put'], url_path='update/(?P<pk>[^/.]+)')
    def update_rule(self, request, pk=None):
        """
        PUT /api/rules/update/<pk>/

        Update an existing rule using its primary key.
        """
        try:
            updated_data = RulesController.update_rule(self, request, pk, request.data)
            return Response(updated_data, status=status.HTTP_200_OK)

        except ObjectDoesNotExist:
            return Response({"error": "Rule not found"}, status=status.HTTP_404_NOT_FOUND)

        except ValidationError as ve:
            return Response({"error": str(ve)}, status=status.HTTP_400_BAD_REQUEST)

        except Exception as e:
            status_code = status.HTTP_404_NOT_FOUND if "not found" in str(e).lower() else status.HTTP_400_BAD_REQUEST
            return Response({"error": str(e)}, status=status_code)
        
        
    @action(detail=False, methods=['put'], url_path='update_status/(?P<pk>[^/.]+)')
    def update_rule_status(self, request, pk=None):
        """
        PUT /api/rules/update_status/<pk>/

        Update an existing rule using its primary key.
        """
        try:
            updated_data = RulesController.update_rule_status(self, request, pk, request.data)
            return Response(updated_data, status=status.HTTP_200_OK)

        except ObjectDoesNotExist:
            return Response({"error": "Rule not found"}, status=status.HTTP_404_NOT_FOUND)

        except ValidationError as ve:
            return Response({"error": str(ve)}, status=status.HTTP_400_BAD_REQUEST)

        except Exception as e:
            status_code = status.HTTP_404_NOT_FOUND if "not found" in str(e).lower() else status.HTTP_400_BAD_REQUEST
            return Response({"error": str(e)}, status=status_code)

        
        
    @swagger_auto_schema(
        operation_description="Delete a rule by ID",
        responses={204: "Deleted", 404: "Rule not found"}
    )
    @action(detail=False, methods=['delete'], url_path='delete/(?P<pk>[^/.]+)')
    def delete_rule(self, request, pk=None):
        """
        Delete a rule.
        """
        try:
            RulesController.delete_rule(self,request, pk)
            return Response(status=status.HTTP_204_NO_CONTENT)
        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_404_NOT_FOUND)
        
    @action(detail=False, methods=['post'], url_path='options')
    def get_options(self, request, *args, **kwargs):
        """
        Handle OPTIONS requests for the RulesViewSet.
        """
        try:
            # Call the list_rules method to get the options
            options = RulesController.get_options(self, request)
            return Response(options, status=status.HTTP_200_OK)
        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)
        
    @action(detail=False, methods=['post'], url_path='resource_list')
    def get_resource_list(self, request):
        """
        Retrieve a list of resources.
        """
        try:
            data = RulesController.get_resource_list(self, request)
            return Response(data)
        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)
