import os
import yaml
from django.conf import settings
from django.utils.text import slugify
import uuid
from rest_framework.exceptions import NotFound, ValidationError
from .models import Rules
from .serializers import RulesSerializer
from rest_framework.request import Request
from rest_framework.exceptions import ParseError
from mongoengine.base.datastructures import BaseDict, BaseList
from bson import ObjectId
import sys
# Add project root to path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
from API.log_rca_engine.elastic_client import ElasticClient
from pymongo import MongoClient
class RulesController:
    elastic = ElasticClient()
    def __init__(self):
        self.rules_dir = os.path.join(settings.BASE_DIR, "rules")

    def list_rules(self, request):
        """
        Return paginated and serialized list of all rules for mongoengine.
        Accepts query params: ?page=1&limit=10
        """
        result = {}
        try:
            page = int(request.GET.get('page', 1))
            limit = int(request.GET.get('limit', 10))
            offset = (page - 1) * limit

            total_rules = Rules.objects.count()
            rules = Rules.objects.filter(is_deleted=False).skip(offset).limit(limit)

            serializer = RulesSerializer(rules, many=True)

            result["data"] = serializer.data
            result["pagination"] = {
                "page": page,
                "limit": limit,
                "total": total_rules,
                "has_next": offset + limit < total_rules,
                "has_previous": page > 1
            }

            return result

        except Exception as e:
            raise ValidationError(f"Failed to list rules: {str(e)}")



    def get_rule(self, request, pk):
        """
        Return one rule by ID.
        """
        try:
            rule = Rules.objects.get(pk=pk)
            # data = RulesSerializer(rule).data
            # data['condition'] = {'must': data.get("condition_must",{}),"must_not":data.get("condition_must_not",{}) }
            condition = RulesController.parse_es_query_to_ui(self,rule.condition)
            data= RulesSerializer(rule).data
            data['condition'] = condition
            return data
        except Rules.DoesNotExist:
            raise NotFound("Rule not found")
        except Exception as e:
            raise ValidationError(f"Failed to retrieve rule: {str(e)}")

    def create_rule(self, request, data):
        """
        Create a new rule and save it directly to MongoDB.
        """
        try:
            # Extract fields manually from data
            name = data.get("name")
            index = data.get("index")
            description = data.get("description")
            condition = data.get("condition",{})
            alert = data.get("alert", {})
            business_service_details = data.get("business_service_details",{})
            duration = data.get("duration",0)
            ssh_commands = data.get("ssh_commands",[])
            # Optional: Basic manual validation
            if not name or not index:
                raise ValidationError("Missing required fields: 'name' or 'index'.")

            # Save using the model directly
            rule = Rules.objects.create(
                rule_id=RulesController.get_ID(self),
                name=name,
                index=index,
                description=description,
                condition = condition,
                business_service_details = business_service_details,
                alert=alert,
                is_deleted=False,
                duration=duration,
                ssh_commands=ssh_commands
            )
            rule={
                "id": rule.id,
                "name": rule.name,
                "index": rule.index,
                "description": rule.description,
                "condition": rule.condition,
                "alert": rule.alert
            }
            # RulesController.save_rule_to_yaml(self,rule)
            return {
                "message": "Rule created successfully",
                "status": "success",
            }

        except Exception as e:
            raise ValidationError(f"Failed to create rule: {str(e)}")

    def update_rule(self, request, pk, data):
        """
        Update an existing rule.
        """
        try:
            rule = Rules.objects.get(pk=pk)
        except Rules.DoesNotExist:
            raise NotFound("Rule not found")

        try:
            rule.name = data.get("name","")
            rule.index = data.get("index","")
            rule.description = data.get("description","")
            rule.condition = data.get("condition",{})
            rule.alert = data.get("alert",{})
            rule.is_deleted = False
            rule.business_service_details = data.get("business_service_details",{})
            rule.duration = data.get("duration",0)
            rule.ssh_commands = data.get("ssh_commands",[])
            rule.save()
            rule={
                "id": rule.id,
                "name": rule.name,
                "index": rule.index,
                "description": rule.description,
                "condition": rule.condition,
                "alert": rule.alert
            }
            return {
                "message": "Rule updated successfully",
                "status": "success",
            }
        except ValidationError as e:
            raise e
        except Exception as e:
            raise ValidationError(f"Failed to update rule: {str(e)}")

    def delete_rule(self, request, pk):
        """
        Delete a rule.
        """
        try:
            rule = Rules.objects.get(pk=pk)
            rule.is_deleted = True
            rule.save()
        except Rules.DoesNotExist:
            raise NotFound("Rule not found")
        except Exception as e:
            raise ValidationError(f"Failed to delete rule: {str(e)}")

    def convert_to_native(obj):
        """
        Recursively convert MongoEngine-specific data structures to native Python types.
        """
        if isinstance(obj, BaseDict):
            return {k: RulesController.convert_to_native(v) for k, v in obj.items()}
        elif isinstance(obj, BaseList):
            return [RulesController.convert_to_native(item) for item in obj]
        elif isinstance(obj, ObjectId):
            return str(obj)
        elif isinstance(obj, bytes):  # for !!binary types
            return obj.decode(errors="ignore")
        elif isinstance(obj, dict):
            return {k: RulesController.convert_to_native(v) for k, v in obj.items()}
        elif isinstance(obj, list):
            return [RulesController.convert_to_native(item) for item in obj]
        return obj

    def save_clean_yaml(self,rule_dict: dict) -> str:
        """
        Convert a MongoEngine rule dict to clean YAML and save it under BASE_DIR/log_rca_engine/rules/.
        """
        if "name" not in rule_dict:
            raise ValueError("Missing 'name' in rule_dict")

        # Convert all MongoEngine fields to native Python types
        clean_dict = RulesController.convert_to_native(rule_dict)

        # Safe filename from rule name
        safe_name = slugify(clean_dict["name"]) + ".yml"
        rules_dir = os.path.join(settings.BASE_DIR, "log_rca_engine", "rules")
        os.makedirs(rules_dir, exist_ok=True)
        file_path = os.path.join(rules_dir, safe_name)

        # Dump YAML in readable format
        with open(file_path, "w", encoding="utf-8") as f:
            yaml.dump(
                clean_dict,
                f,
                allow_unicode=True,
                default_flow_style=False,
                sort_keys=False
            )

        return file_path

    def extract_request_data(request: Request) -> dict:
        """
        Extract and return data from a Django Rest Framework request.

        Handles both JSON and form data depending on request method and content type.

        Args:
            request (Request): DRF request object.

        Returns:
            dict: Parsed request data.

        Raises:
            ParseError: If data could not be parsed.
        """
        try:
            if request.method in ["POST", "PUT", "PATCH"]:
                return request.data  # Handles JSON, multipart, form, etc.
            elif request.method == "GET":
                return request.query_params  # For GET params like ?key=value
            else:
                return {}
        except Exception as e:
            raise ParseError(f"Failed to parse request data: {str(e)}")
        
    def get_options(self, request):
        """
        Return all available fields from Elasticsearch mappings.
        """
        options = {}
        try:
            client = MongoClient("mongodb://infraondns:InfraonMongodb321@10.0.4.247:27017/infraondns_mongodb?retryWrites=false&authSource=infraondns_mongodb&authMechanism=SCRAM-SHA-1")
            # Access the database
            db = client["infraondns_mongodb"]
            # Directly access the collection
            collection = db["business_service"]
            query = {
                "is_deleted": False,
                "organization" : "136761188499418255360"
            }
            service_data = collection.find(query)
            service_list = [{"value":service["name"],"key":service["business_service_id"]} for service in service_data]
            collection = db["correlation_rules"]
            rule_list=Rules.objects.filter(is_deleted=False).only("name","rule_id")
            rules = [{"key":rule.rule_id,"value":rule.name} for rule in rule_list]
            data = RulesController.extract_request_data(request)
            indexOptions = RulesController.elastic.get_all_index_options()
            if data.get("index"):
                fields = RulesController.elastic.get_all_fields(index_name=[data.get("index")])
            else:
                fields = RulesController.elastic.get_all_fields()
                
            options={
                "fields":fields,
                "service_list":service_list,
                "rule_list":rules,
                "indexOptions":indexOptions,
            }
        except Exception as e:
            raise ValidationError(f"Failed to get fields: {str(e)}")
        return options
    
    def get_resource_list(self, request):
        """
        Return a list of resources from Elasticsearch.
        """
        fields = []
        try:
            data = RulesController.extract_request_data(request)
            client = MongoClient("mongodb://infraondns:InfraonMongodb321@10.0.4.247:27017/infraondns_mongodb?retryWrites=false&authSource=infraondns_mongodb&authMechanism=SCRAM-SHA-1")
            # Access the database
            db = client["infraondns_mongodb"]
            # Directly access the collection
            collection = db["business_service"]
            query = {
                "is_deleted": False,
                "organization" : "136761188499418255360",
                "business_service_id":data.get("service_id")
            }
            service_data = list(collection.find(query))
            nodes_list=service_data[0].get("style_property",{}).get("nodes",[])
            
            # nodes_list.extend( for service_data in service_datas)
            ci_ids=[]
            for item in nodes_list:
                stat_list=item.get("asset_config",{}).get("stat",[])
                if "p_avail" in stat_list:
                    ci_ids.append(item.get("asset_config",{}).get("ci_id"))
            collection = db["cmdb_ci"]
            query = {
                "is_deleted": False,
                "ci_id": {"$in": ci_ids}
            }
            ci_data = collection.find(query)
            fields = [{"value":ci.get("ci_name"),"key":{"ci_id":ci.get("ci_id"),"ip_address":ci.get("ip_address")}} for ci in ci_data]
        except Exception as e:
            raise ValidationError(f"Failed to get fields: {str(e)}")
        return fields
        
        
    def parse_es_query_to_ui(self, dsl):
        condition_groups = []
        must_groups = dsl.get('query', {}).get('bool', {}).get('must', [])

        for group in must_groups:
            bool_group = group.get('bool', {})
            if 'should' in bool_group:
                group_logic = 'OR'
                filters = bool_group.get('should', [])
            else:
                group_logic = 'AND'
                filters = bool_group.get('must', [])

            parsed_filters = []
            for f in filters:
                operator = 'is'
                field = ''
                value = ''
                
                if 'term' in f:
                    field = list(f['term'].keys())[0]
                    value = f['term'][field]
                    operator = 'is'

                elif 'match' in f:
                    field = list(f['match'].keys())[0]
                    value = f['match'][field].get('query', '')
                    operator = 'match'

                elif 'match_phrase' in f:
                    field = list(f['match_phrase'].keys())[0]
                    raw_val = f['match_phrase'][field]
                    value = raw_val
                    val_lower = raw_val.lower()

                    if val_lower.startswith('*') and val_lower.endswith('*'):
                        operator = 'contains'
                        value = raw_val.strip('*')
                    elif val_lower.startswith('*'):
                        operator = 'ends with'
                        value = raw_val.lstrip('*')
                    elif val_lower.endswith('*'):
                        operator = 'starts with'
                        value = raw_val.rstrip('*')
                    else:
                        operator = 'match phrase'
                        value = raw_val

                elif 'terms' in f:
                    field = list(f['terms'].keys())[0]
                    value = f['terms'][field]
                    operator = 'is one of'

                elif 'wildcard' in f:
                    field = list(f['wildcard'].keys())[0]
                    wildcard_val = f['wildcard'][field].get('value', '')
                    value = wildcard_val.replace('*', '')
                    val_lower = wildcard_val.lower()

                    if val_lower.startswith('*') and val_lower.endswith('*'):
                        operator = 'contains'
                    elif val_lower.startswith('*'):
                        operator = 'ends with'
                    elif val_lower.endswith('*'):
                        operator = 'starts with'

                elif 'exists' in f:
                    field = f['exists']['field']
                    operator = 'exists'

                elif f.get('bool', {}).get('must_not', {}).get('exists'):
                    field = f['bool']['must_not']['exists']['field']
                    operator = 'does not exist'

                elif f.get('bool', {}).get('must_not', {}).get('term'):
                    field = list(f['bool']['must_not']['term'].keys())[0]
                    value = f['bool']['must_not']['term'][field]
                    operator = 'is not'

                elif f.get('bool', {}).get('must_not', {}).get('terms'):
                    field = list(f['bool']['must_not']['terms'].keys())[0]
                    value = f['bool']['must_not']['terms'][field]
                    operator = 'is not one of'

                parsed_filters.append({
                    'field': field,
                    'operator': operator,
                    'value': value,
                    'logicWithNext': 'AND'
                })

            condition_groups.append({
                'logic': group_logic,
                'filters': parsed_filters
            })

        return condition_groups



    def get_ID(self):
        return str(uuid.uuid4().int % (10**20))  # 