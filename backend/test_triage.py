import sys
import os

sys.path.append(os.path.join(os.path.dirname(__file__), "src"))

from agents.triage_agent import TriageAgent

agent = TriageAgent()

payload = {
    "symptoms": ["chest_pain"],
    "vitals": {"bp": "180/100", "heart_rate": 120},
    "age": 65
}

print(agent.execute(payload))
