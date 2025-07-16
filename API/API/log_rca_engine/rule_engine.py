import time
import yaml
import os
from elasticsearch import Elasticsearch
from datetime import datetime, timedelta
from ai_engine import AIEngine
from dotenv import load_dotenv
from pymongo import MongoClient
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
        # must_clauses = [{"match_phrase": {c["field"]: c["contains"]}} for c in rule["condition"].get("must", [])]
        # must_not_clauses = [{"match": {c["field"]: c["match"]}} for c in rule["condition"].get("must_not", [])]

        
        rule['condition']["query"]['bool']['filter']={
                    "range": {
                        "@timestamp": {
                            "gte": start_time.isoformat(),
                            "lte": end_time.isoformat()
                        }
                    }
                }
        rule['index'] = [i+"*" for i in rule.get("index","*")]
        query = rule.get("condition",{}).get("query",{})
        response = self.es.search(index=rule.get("index","*"), query=query, size=10)
        hits = response.get("hits", {}).get("hits", [])
        if hits:
            unique_messages = set()
            for hit in hits:
                msg = hit["_source"].get("message")
                if msg:
                    unique_messages.add(msg[0])

            print(f"🚨 Rule triggered: {rule['name']} ({len(unique_messages)} unique hits)")
            if unique_messages:
                ai_output = self.ai_engine.generate_prompt(str(unique_messages))
                print("RCA:-------------------------",ai_output.get('rca',""))
                print("solution:---------------------",ai_output.get('solution',""))
        else:
            print("✅ No issues detected.")


if __name__ == "__main__":
    engine = RuleEngine()
    while True:
        print("\n⏱️  Running RCA Rule Engine...")
        engine.run()
        time.sleep(engine.interval)
