import time
import yaml
from rule_engine import RuleEngine

def load_config():
    with open("config.yml") as f:
        return yaml.safe_load(f)

if __name__ == "__main__":
    config = load_config()
    engine = RuleEngine(config)
    while True:
        print("🔄 Running RCA Rule Engine...")
        engine.run()
        time.sleep(60)
