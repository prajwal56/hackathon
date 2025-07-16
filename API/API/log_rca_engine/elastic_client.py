from elasticsearch import Elasticsearch
import yaml
from rest_framework.exceptions import ValidationError
from dotenv import load_dotenv
import os
import re
class ElasticClient:
    def __init__(self):
        dotenv_path = os.path.join("D:\hackathon\hackathon\API\settings", '.env')
        # print(dotenv_path)
        load_dotenv(dotenv_path)
        print(os.getenv("ES_HOST"))
        self.es = Elasticsearch(
            hosts=os.getenv("ES_HOST", "http://localhost:9200"),
            basic_auth=(os.getenv("ES_USERNAME","elastic"), os.getenv("ES_PASSWORD","hanTZ123$")),
        )

    def search(self, index, query, size=50):
        return self.es.search(index=index, body=query, size=size)

    def get_all_fields(self, index_name="*"):
        """
        Get all available fields from the Elasticsearch index mapping,
        across all indices by default (index_name='*').
        """
        try:
            if index_name != "*" and  isinstance(index_name, list):
                index_name = [i+'*' for i in index_name]
            mapping = self.es.indices.get_mapping(index=index_name)
            fields = set()
            for index_data in mapping.values():
                properties = index_data.get("mappings", {}).get("properties", {})
                fields.update(ElasticClient.extract_leaf_fields(self,properties))

            return sorted(fields)
        except Exception as e:
            raise ValidationError(f"Failed to get fields: {str(e)}")
        
        
    def _extract_leaf_fields(self, properties, parent=""):
        """
        Recursively extract only leaf fields from properties.
        A field is a leaf if it has no nested 'properties' key.
        """
        fields = []

        for field, value in properties.items():
            full_field = f"{parent}.{field}" if parent else field

            # If the field has nested properties, go deeper
            if "properties" in value:
                fields.extend(self.extract_leaf_fields(value["properties"], full_field))
            else:
                fields.append(full_field)

        return fields


    def extract_leaf_fields(self, properties, parent_field=""):
        """
        Recursively extract only the leaf (bottom-level) field names from nested mappings.
        """
        field_list = []

        for field, value in properties.items():
            full_field = f"{parent_field}.{field}" if parent_field else field

            # If field has nested properties, recurse
            if "properties" in value:
                field_list.extend(self.extract_leaf_fields(value["properties"], full_field))
            else:
                # Only add if it doesn't have nested 'properties'
                field_list.append(full_field)

        return field_list


    def get_all_index_options(self):
        """
        Fetch all index names from Elasticsearch, remove date suffixes,
        and return a list of unique base index names.
        """
        try:
            # Get all index names from Elasticsearch
            index_metadata = self.es.indices.get_alias()
            all_indices = list(index_metadata.keys())

            unique = set()
            date_pattern = re.compile(r"(-\d{4}[\.-]\d{2}[\.-]\d{2})$")  # Matches -2025.07.15 or -2025-07-15

            for index_name in all_indices:
                base_name = date_pattern.sub('', index_name)
                if not base_name.startswith('.'):
                    unique.add(base_name)

            return sorted(unique)

        except Exception as e:
            raise ValidationError(f"Failed to fetch unique index prefixes: {str(e)}")