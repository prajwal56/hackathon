from elasticsearch import Elasticsearch
import yaml

class ElasticClient:
    def __init__(self, config):
        self.es = Elasticsearch(
            config["es_host"],
            basic_auth=(config["es_username"], config["es_password"])
            )

    def search(self, index, query, size=50):
        return self.es.search(index=index, body=query, size=size)
