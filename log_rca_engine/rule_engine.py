import time
import yaml
import os
from elasticsearch import Elasticsearch
from datetime import datetime, timedelta
from ai_engine import AIEngine

class RuleEngine:
    def __init__(self, config):
        self.ai_engine = AIEngine(config)
        self.config = config
        self.es = Elasticsearch(
            config["es_host"],
            basic_auth=(config["es_username"], config["es_password"])
        )
        self.interval = int(config.get("interval", 60))
        self.rules_dir = config["rules_path"]

    def load_rules(self):
        rules = []
        for filename in os.listdir(self.rules_dir):
            if filename.endswith(".yml") or filename.endswith(".yaml"):
                with open(os.path.join(self.rules_dir, filename), "r") as f:
                    rule = yaml.safe_load(f)
                    rules.append(rule)
        return rules

    def run(self):
        now = datetime.utcnow()
        start_time = now - timedelta(seconds=self.interval)
        rules = self.load_rules()

        for rule in rules:
            print(f"\n🔍 Evaluating rule: {rule['name']}")
            self.evaluate_rule(rule, start_time, now)

    def evaluate_rule(self, rule, start_time, end_time):
        must_clauses = [{"match_phrase": {c["field"]: c["contains"]}} for c in rule["condition"].get("must", [])]
        must_not_clauses = [{"match": {c["field"]: c["match"]}} for c in rule["condition"].get("must_not", [])]

        query = {
            "bool": {
                "must": must_clauses,
                "must_not": must_not_clauses,
                "filter": {
                    "range": {
                        "@timestamp": {
                            "gte": start_time.isoformat(),
                            "lte": end_time.isoformat()
                        }
                    }
                }
            }
        }

        response = self.es.search(index=rule["index"], query=query, size=10)
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


def load_config():
    with open("config.yml", "r") as f:
        return yaml.safe_load(f)

if __name__ == "__main__":
    config = load_config()
    engine = RuleEngine(config)
    while True:
        print("\n⏱️  Running RCA Rule Engine...")
        engine.run()
        time.sleep(engine.interval)
