"""Sandbox personnel roster. In-memory only; never written to CSV."""
from dataclasses import dataclass, replace

AVAILABLE = "AVAILABLE"
UNAVAILABLE = "UNAVAILABLE"
STATES = (AVAILABLE, UNAVAILABLE)

@dataclass(frozen=True)
class Agent:
    agent_id: str
    display_name: str
    qualifications: tuple
    availability: str = AVAILABLE

FIXED_AGENTS = (
    Agent("AGENT_001", "Mara Voss", ("SIGNALS_ANALYSIS", "DATA_SYSTEMS")),
    Agent("AGENT_002", "Jonas Reed", ("FIELD_RESPONSE",)),
    Agent("AGENT_003", "Ilse Quill", ("OCCULT_RESPONSE", "FIELD_RESPONSE")),
    Agent("AGENT_004", "Tobin Hale", ("DATA_SYSTEMS",), UNAVAILABLE),
)

def is_active(row):
    return str(row.get("active", "")).strip().upper() == "TRUE"

class SandboxRoster:
    def __init__(self, tables, agents=FIXED_AGENTS):
        self.tables = tables
        self._initial = {a.agent_id: a for a in agents}
        if len(self._initial) != len(tuple(agents)):
            raise ValueError("Duplicate agent_id in roster.")
        self._current = dict(self._initial)

    def agents(self):
        return sorted(self._current.values(), key=lambda a: a.agent_id)

    def get(self, agent_id):
        return self._current.get(agent_id)

    def set_availability(self, agent_id, availability):
        if agent_id not in self._current:
            raise KeyError("Unknown agent: " + agent_id)
        if availability not in STATES:
            raise ValueError("Invalid availability: " + str(availability))
        self._current[agent_id] = replace(
            self._current[agent_id], availability=availability
        )

    def reset(self):
        self._current = dict(self._initial)

    def audit(self):
        catalog = {}
        for row in self.tables.get("qualification_catalog", []):
            catalog.setdefault(row.get("qualification_id", ""), []).append(row)
        issues = []
        for agent in self.agents():
            for qid in agent.qualifications:
                rows = catalog.get(qid, [])
                if len(rows) != 1:
                    issues.append(agent.agent_id + ": " + qid + " MISSING OR DUPLICATE")
                elif not is_active(rows[0]):
                    issues.append(agent.agent_id + ": " + qid + " INACTIVE")
        return issues

    def available_with(self, qualification_id):
        return [
            a for a in self.agents()
            if a.availability == AVAILABLE and qualification_id in a.qualifications
        ]
