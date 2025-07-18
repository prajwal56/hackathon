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
from collections import defaultdict

class RuleEngine:
    def __init__(self):
        dotenv_path = os.path.join("/opt/Hackathon/hackathon/API/API/settings/", '.env')
        # print(dotenv_path)
        load_dotenv(dotenv_path)
        # print(os.getenv("ES_HOST"))
        self.es = Elasticsearch(
            hosts=os.getenv("ES_HOST", "http://localhost:9200"),
            basic_auth=(os.getenv("ES_USERNAME","elastic"), os.getenv("ES_PASSWORD","hanTZ123$")),
        )
        self.ai_engine = AIEngine()
        self.interval = int(os.getenv("RULE_ENGINE_INTERVAL", 60))
        self.client = MongoClient(os.getenv("MONGO_URL"))
        self.db = self.client[os.getenv("MONGO_DB")]
            # Directly access the collection
        self.collection = self.db["rules"]

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
        # rules = self.load_rules()
        query = {
            "is_deleted": False,
            "is_active": True,
        }
        rules = list(self.collection.find(query))
        # rules = [ru.get("condition",{}) for ru in rule]
        for rule in rules:
            print(f"\n🔍 Evaluating rule: {rule.get('name','')}")
            start_time = now - timedelta(seconds=rule.get("duration", 60))
            self.evaluate_rule(rule, start_time, now)

    def evaluate_rule(self, rule, start_time, end_time):
        hits = self.generate_event(rule, start_time, end_time)
        if hits:
            if rule.get('linked_rules',[]):
                for linked_rule in rule.get('linked_rules',[]):
                    query = {
                        "is_deleted": False,
                        "rule_id": linked_rule
                    }
                    l_rule= self.collection.find_one(query)
                    if l_rule:
                        l_hits = self.generate_event(l_rule, start_time, end_time)
                        if l_hits:
                            hits.extend(l_hits)
            # self.generate_alert(rule, hits)
            # self.generate_rca(rule, hits)
            classify_obj = self.group_messages_by_ip(hits)
            unique_messages = set()
            for hit in hits:
                data ={
                    'msg' : hit["_source"].get("message"),
                    "ip_address": hit["_source"].get("host",{}).get("ip","0.0.0.0")
                }
            print(f"🚨 Rule triggered: {rule['name']} ({len(data.get('msg',[]))} unique hits)")

            if data:
                unique_messages = set(data.get('msg',[]))
                # ai_output = self.ai_engine.generate_prompt(str(unique_messages))
                # rca = ai_output.get('rca', "")
                # solution = ai_output.get('solution', "")
                solution = ''
                rca = ''

                try:
                    self.create_event(rule, classify_obj, rca, solution)
                except Exception as e:
                    print(f"❌ Error calling event API: {e}")

                # print("RCA:-------------------------", rca)
                # print("Solution:--------------------", solution)
        else:
            print("✅ No issues detected.")
            
    def generate_event(self, rule, start_time, end_time):
        """
        Sends a POST request to create an event with provided details.
        """
        try:
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
                for hit in hits:
                    hit['rule_name'] = rule.get("name", "")
            return hits
        except Exception as e:
            print(f"❌ Error calling event API: {e}")
            return []
    
            
    def create_event(self, rule, classify_obj, rca, solution):
        """
        Sends a POST request to create an event with provided details.
        """
        listed_messages = []
        for message in classify_obj:
            listed_messages.extend(message.get('msg',[]))
        event_data = {
            "title": f"Rule triggered: {rule['name']}",
            "description": f"{len(listed_messages)} unique messages found.\n\nRCA: {rca}\n\nSolution: {solution}",
            "logs": classify_obj,
            "rule_name": rule.get('name', ""),
            "severity": rule.get('alert', {}).get("severity", ""),
        }

        api_response = requests.post(
            "http://10.0.4.203:9090/event/create_event/",
            json=event_data,
            headers={"Content-Type": "application/json"}
        )

        if api_response.status_code == 201:
            print("✅ Event created successfully.")
        else:
            print(f"❌ Failed to create event: {api_response.status_code} - {api_response.text}")
            
    def group_messages_by_ip(self,hits):
        ip_map = defaultdict(list)

        # for hit in hits:
        #     ip =  hit["_source"].get("host",{}).get("ip","0.0.0.0")
        #     message =  hit["_source"].get("message")
        #     if ip:
        #         ip_map[ip].append(message)
        result_map = {}

        for entry in hits:
            source = entry["_source"]
            ip = source.get("host", {}).get("ip", "0.0.0.0")
            rule_name = entry.get("rule_name", "Unknown Rule")
            messages = source.get("message", [])
            if isinstance(messages, str):
                messages = [messages]

            if ip not in result_map:
                result_map[ip] = {}

            if rule_name not in result_map[ip]:
                result_map[ip][rule_name] = []

            result_map[ip][rule_name].extend(messages)

        # Convert to desired format
        result = [
            {
                "ip": ip,
                "rules": [{"rule_name": rule, "msg": msgs} for rule, msgs in rule_map.items()]
            }
            for ip, rule_map in result_map.items()
        ]
        return result


if __name__ == "__main__":
    engine = RuleEngine()
    while True:
        print("\n⏱️  Running RCA Rule Engine...")
        engine.run()
        time.sleep(engine.interval)
