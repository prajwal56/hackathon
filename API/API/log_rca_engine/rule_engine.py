import time
import yaml
import os
from elasticsearch import Elasticsearch
from datetime import datetime, timedelta
from ai_engine import AIEngine
from dotenv import load_dotenv
from pymongo import MongoClient
import requests
from datetime import datetime
from ssh_interface import SSHInterface
class RuleEngine:
    def __init__(self):
        dotenv_path = os.path.join("D:\hackathon\hackathon\API\settings", '.env')
        # print(dotenv_path)
        load_dotenv(dotenv_path)
        # print(os.getenv("ES_HOST"))
        self.es = Elasticsearch(
            hosts=os.getenv("ES_HOST", "http://localhost:9200"),
            basic_auth=(os.getenv("ES_USERNAME","elastic"), os.getenv("ES_PASSWORD","hanTZ123$")),
        )
        self.ai_engine = AIEngine()
        self.interval = int(os.getenv("RULE_ENGINE_INTERVAL", 60))

    # def load_rules(self):
    #     rules = []
    #     for filename in os.listdir(self.rules_dir):
    #         if filename.endswith(".yml") or filename.endswith(".yaml"):
    #             with open(os.path.join(self.rules_dir, filename), "r") as f:
    #                 rule = yaml.safe_load(f)
    #                 rules.append(rule)
    #     return rules

    def run(self):
        now = datetime.utcnow()
        start_time = now - timedelta(seconds=self.interval)
        # rules = self.load_rules()
        client = MongoClient(os.getenv("MONGO_URL"))
        db = client[os.getenv("MONGO_DB")]
            # Directly access the collection
        collection = db["rules"]
        query = {
            "is_deleted": False,
        }
        rules = list(collection.find(query))
        # rules = [ru.get("condition",{}) for ru in rule]
        for rule in rules:
            print(f"\n🔍 Evaluating rule: {rule.get('name','')}")
            self.evaluate_rule(rule, start_time, now)

    def evaluate_rule(self, rule, start_time, end_time):
        rule['condition']["query"]['bool']['filter'] = {
            "range": {
                "@timestamp": {
                    "gte": start_time.isoformat(),
                    "lte": end_time.isoformat()
                }
            }
        }
        if isinstance(rule.get("index"), list):
            rule['index'] = [i + "*" for i in rule.get("index", "*")]
        elif rule.get("index") != "*" and not isinstance(rule.get("index"), list):
            rule['index'] = [rule.get("index", "*")+"*"]
        else:
            rule['index'] = "*"
        # rule['index'] = [i + "*" for i in rule.get("index", "*")]
        query = rule.get("condition", {}).get("query", {})

        response = self.es.search(index=rule.get("index", "*"), query=query, size=10)
        hits = response.get("hits", {}).get("hits", [])

        if hits:
            unique_messages = set()
            for hit in hits:
                msg = hit["_source"].get("message")
                if msg:
                    if isinstance(msg, list):
                        unique_messages.update(msg)
                    else:
                        unique_messages.add(msg)

            print(f"🚨 Rule triggered: {rule['name']} ({len(unique_messages)} unique hits)")

            if unique_messages:
                ai_output = self.ai_engine.generate_prompt(str(unique_messages))
                rca = ai_output.get('rca', "")
                solution = ai_output.get('solution', "")

                try:
                    self.create_event(rule, unique_messages, rca, solution)
                except Exception as e:
                    print(f"❌ Error calling event API: {e}")

                print("RCA:-------------------------", rca)
                print("Solution:--------------------", solution)
        else:
            print("✅ No issues detected.")
            
    def create_event(self, rule, unique_messages, rca, solution):
        """
        Sends a POST request to create an event with provided details.
        """
        event_data = {
            "title": f"Rule triggered: {rule['name']}",
            "description": f"{len(unique_messages)} unique messages found.\n\nRCA: {rca}\n\nSolution: {solution}",
            "logs": list(unique_messages),
            "rule_name": rule.get('name', ""),
            "severity": rule.get('alert', {}).get("severity", ""),
        }

        api_response = requests.post(
            "http://localhost:9090/event/create_event/",
            json=event_data,
            headers={"Content-Type": "application/json"}
        )

        if api_response.status_code == 201:
            print("✅ Event created successfully.")
        else:
            print(f"❌ Failed to create event: {api_response.status_code} - {api_response.text}")


if __name__ == "__main__":
    engine = RuleEngine()
    while True:
        print("\n⏱️  Running RCA Rule Engine...")
        engine.run()
        time.sleep(engine.interval)
