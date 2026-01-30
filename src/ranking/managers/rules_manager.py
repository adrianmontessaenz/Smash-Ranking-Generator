from pathlib import Path
import json
import os

class RulesManager:
    def __init__(self):
        # Initialize rules data (if any)
        if os.path.exists("data/rules.json"):
            with open("data/rules.json", "r") as rules_file:
                self._rules = json.load(rules_file)
        else:
            self._rules = {}
        
    def get_rules(self):
        return self._rules