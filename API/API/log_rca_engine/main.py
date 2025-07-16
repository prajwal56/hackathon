import time
import yaml
from rule_engine import RuleEngine



if __name__ == "__main__":
    # config = load_config()
    engine = RuleEngine()
    while True:
        print("🔄 Running RCA Rule Engine...")
        engine.run()
        time.sleep(60)
