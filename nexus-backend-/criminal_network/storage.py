import os
import json
import time
from typing import Dict, Any, List, Optional

class CaseStorage:
    """
    Manages persistent state for Cases, Evidence, Extracted Entities,
    Timeline Events, and Investigation Reports.
    """

    def __init__(self, data_file: str = "output/nexus_db.json"):
        self.data_file = data_file
        self.state = {
            "cases": [],
            "evidence": [],
            "timeline": [],
            "reports": {},
            "users": [
                {
                    "username": "investigator",
                    "password": "password123",
                    "name": "Special Agent Roy",
                    "role": "Lead Investigator",
                    "badge": "NEXUS-047"
                }
            ]
        }
        self.load()

    def load(self):
        """Loads database from disk or seeds initial cases and evidence."""
        if os.path.exists(self.data_file):
            try:
                with open(self.data_file, "r", encoding="utf-8") as f:
                    self.state = json.load(f)
                return
            except Exception as e:
                print(f"[Storage] Failed to read database: {e}")

        self._seed_default_state()
        self.save()

    def save(self):
        """Saves current state to JSON file."""
        os.makedirs(os.path.dirname(self.data_file) or ".", exist_ok=True)
        with open(self.data_file, "w", encoding="utf-8") as f:
            json.dump(self.state, f, indent=2)

    def _seed_default_state(self):
        """Seeds initial realistic investigation cases and evidence."""
        self.state["cases"] = [
            {
                "id": "CASE-2026-014",
                "title": "Financial Network Investigation",
                "description": "Analysis of financial transactions, circular money transfers and communication ties between identified entities.",
                "status": "Active",
                "priority": "HIGH",
                "created_at": "2026-09-10T09:00:00Z",
                "assigned_officer": "Special Agent Roy",
                "evidence_count": 4,
                "entity_count": 12
            },
            {
                "id": "CASE-2026-011",
                "title": "Organized Crime Analysis",
                "description": "Investigation of relationships between syndicate suspects, front companies, logistics hubs and contraband movements.",
                "status": "Under Review",
                "priority": "HIGH",
                "created_at": "2026-09-08T14:30:00Z",
                "assigned_officer": "Inspector V. Rao",
                "evidence_count": 2,
                "entity_count": 8
            },
            {
                "id": "CASE-2026-008",
                "title": "Missing Person Investigation",
                "description": "Timeline and entity analysis related to a missing person last seen near Hitech City transit terminal.",
                "status": "Active",
                "priority": "MEDIUM",
                "created_at": "2026-09-05T11:15:00Z",
                "assigned_officer": "Sub-Inspector Anjali",
                "evidence_count": 1,
                "entity_count": 4
            },
            {
                "id": "CASE-2026-003",
                "title": "Property Fraud Investigation",
                "description": "Evidence and relationship analysis concerning suspected property document forgery and forged deeds.",
                "status": "Closed",
                "priority": "LOW",
                "created_at": "2026-08-20T16:00:00Z",
                "assigned_officer": "Special Agent Roy",
                "evidence_count": 3,
                "entity_count": 6
            }
        ]

        self.state["evidence"] = [
            {
                "id": "EV-001",
                "case_id": "CASE-2026-014",
                "name": "FIR_2026_014.pdf",
                "file_type": "PDF",
                "size_kb": 248,
                "status": "Processed",
                "uploaded_at": "2026-09-10 09:30",
                "extracted_entities": 8
            },
            {
                "id": "EV-002",
                "case_id": "CASE-2026-014",
                "name": "Financial_Report.docx",
                "file_type": "DOCX",
                "size_kb": 182,
                "status": "Processed",
                "uploaded_at": "2026-09-10 10:15",
                "extracted_entities": 6
            },
            {
                "id": "EV-003",
                "case_id": "CASE-2026-014",
                "name": "cdr.csv",
                "file_type": "CSV",
                "size_kb": 45,
                "status": "Processed",
                "uploaded_at": "2026-09-10 10:45",
                "extracted_entities": 6
            },
            {
                "id": "EV-004",
                "case_id": "CASE-2026-014",
                "name": "transactions.csv",
                "file_type": "CSV",
                "size_kb": 38,
                "status": "Processed",
                "uploaded_at": "2026-09-10 11:00",
                "extracted_entities": 6
            }
        ]

        self.state["timeline"] = [
            {
                "id": "EVT-001",
                "case_id": "CASE-2026-014",
                "date": "2026-09-10",
                "time": "10:30",
                "title": "First Phone Communication Detected",
                "description": "Phone call recorded between 9876543210 (Rahul Kumar) and 9123456789 (Arjun Singh) for 120 seconds.",
                "category": "Communication",
                "source_doc": "cdr.csv",
                "entities": [{"name": "Rahul Kumar", "type": "Person"}, {"name": "Arjun Singh", "type": "Person"}]
            },
            {
                "id": "EVT-002",
                "case_id": "CASE-2026-014",
                "date": "2026-09-10",
                "time": "12:00",
                "title": "Secondary Communication Outlier",
                "description": "Rahul Kumar contacted Ravi Sharma on phone 9988776655 for 60 seconds.",
                "category": "Communication",
                "source_doc": "cdr.csv",
                "entities": [{"name": "Rahul Kumar", "type": "Person"}, {"name": "Ravi Sharma", "type": "Person"}]
            },
            {
                "id": "EVT-003",
                "case_id": "CASE-2026-014",
                "date": "2026-09-10",
                "time": "12:45",
                "title": "Large Fund Transfer Dispatched",
                "description": "INR 50,000 transferred from ACC001 (Rahul Kumar) to ACC002 (Arjun Singh).",
                "category": "Financial Transaction",
                "source_doc": "transactions.csv",
                "entities": [{"name": "ACC001", "type": "Account"}, {"name": "ACC002", "type": "Account"}]
            },
            {
                "id": "EVT-004",
                "case_id": "CASE-2026-014",
                "date": "2026-09-10",
                "time": "13:10",
                "title": "Secondary Fund Distribution",
                "description": "INR 25,000 transferred from ACC001 (Rahul Kumar) to ACC003 (Ravi Sharma).",
                "category": "Financial Transaction",
                "source_doc": "transactions.csv",
                "entities": [{"name": "ACC001", "type": "Account"}, {"name": "ACC003", "type": "Account"}]
            },
            {
                "id": "EVT-005",
                "case_id": "CASE-2026-014",
                "date": "2026-09-10",
                "time": "16:00",
                "title": "Return / Kickback Transfer Identified",
                "description": "Reverse transaction of INR 5,000 sent from ACC003 (Ravi Sharma) back to ACC001 (Rahul Kumar).",
                "category": "Financial Transaction",
                "source_doc": "transactions.csv",
                "entities": [{"name": "ACC003", "type": "Account"}, {"name": "ACC001", "type": "Account"}]
            }
        ]

    # =========================================================================
    # CASES
    # =========================================================================

    def get_cases(self) -> List[Dict[str, Any]]:
        return self.state.get("cases", [])

    def get_case(self, case_id: str) -> Optional[Dict[str, Any]]:
        for c in self.state.get("cases", []):
            if c["id"] == case_id:
                return c
        return None

    def add_case(self, case_data: Dict[str, Any]) -> Dict[str, Any]:
        case_id = case_data.get("id") or f"CASE-2026-{len(self.state['cases']) + 1:03d}"
        new_case = {
            "id": case_id,
            "title": case_data.get("title", "Untitled Investigation"),
            "description": case_data.get("description", ""),
            "status": case_data.get("status", "Active"),
            "priority": case_data.get("priority", "MEDIUM"),
            "created_at": case_data.get("created_at", time.strftime("%Y-%m-%dT%H:%M:%SZ")),
            "assigned_officer": case_data.get("assigned_officer", "Investigator"),
            "evidence_count": 0,
            "entity_count": 0
        }
        self.state["cases"].insert(0, new_case)
        self.save()
        return new_case

    # =========================================================================
    # EVIDENCE
    # =========================================================================

    def get_evidence(self, case_id: Optional[str] = None) -> List[Dict[str, Any]]:
        ev_list = self.state.get("evidence", [])
        if case_id:
            return [e for e in ev_list if e.get("case_id") == case_id]
        return ev_list

    def add_evidence(self, ev_data: Dict[str, Any]) -> Dict[str, Any]:
        ev_id = f"EV-{len(self.state['evidence']) + 1:03d}"
        item = {
            "id": ev_id,
            "case_id": ev_data.get("case_id", "CASE-2026-014"),
            "name": ev_data.get("name", "Document"),
            "file_type": ev_data.get("file_type", "RAW"),
            "size_kb": ev_data.get("size_kb", 10),
            "status": ev_data.get("status", "Pending"),
            "uploaded_at": time.strftime("%Y-%m-%d %H:%M"),
            "extracted_entities": ev_data.get("extracted_entities", 0),
            "file_path": ev_data.get("file_path", "")
        }
        self.state["evidence"].insert(0, item)
        # Update case evidence count
        for c in self.state["cases"]:
            if c["id"] == item["case_id"]:
                c["evidence_count"] = len(self.get_evidence(c["id"]))
        self.save()
        return item

    def update_evidence_status(self, ev_id: str, status: str, entities_count: int = 0):
        for e in self.state["evidence"]:
            if e["id"] == ev_id:
                e["status"] = status
                if entities_count:
                    e["extracted_entities"] = entities_count
        self.save()

    # =========================================================================
    # TIMELINE
    # =========================================================================

    def get_timeline(self, case_id: Optional[str] = None) -> List[Dict[str, Any]]:
        events = self.state.get("timeline", [])
        if case_id:
            return [e for e in events if e.get("case_id") == case_id or not e.get("case_id")]
        return events

    def add_timeline_events(self, case_id: str, new_events: List[Dict[str, Any]]):
        for evt in new_events:
            evt["case_id"] = case_id
            self.state["timeline"].append(evt)
        self.save()

    # =========================================================================
    # SEARCH
    # =========================================================================

    def search(self, query: str, category: str = "All") -> List[Dict[str, Any]]:
        """Multi-domain search across cases, evidence, timeline, and entities."""
        q = query.lower().strip()
        results = []

        # 1. Search Cases
        if category in ["All", "Cases"]:
            for c in self.state["cases"]:
                if q in c["title"].lower() or q in c["description"].lower() or q in c["id"].lower():
                    results.append({
                        "category": "CASE",
                        "id": c["id"],
                        "title": f"{c['id']} · {c['title']}",
                        "description": c["description"],
                        "badge": c["status"]
                    })

        # 2. Search Evidence
        if category in ["All", "Evidence"]:
            for ev in self.state["evidence"]:
                if q in ev["name"].lower() or q in ev["id"].lower():
                    results.append({
                        "category": "EVIDENCE",
                        "id": ev["id"],
                        "title": ev["name"],
                        "description": f"Evidence {ev['id']} in case {ev.get('case_id')} ({ev['file_type']})",
                        "badge": ev["status"]
                    })

        # 3. Search Timeline
        if category in ["All", "Events"]:
            for evt in self.state["timeline"]:
                if q in evt["title"].lower() or q in evt["description"].lower() or q in evt.get("date", "").lower():
                    results.append({
                        "category": "TIMELINE",
                        "id": evt["id"],
                        "title": f"{evt.get('date')} {evt.get('time', '')} - {evt['title']}",
                        "description": evt["description"],
                        "badge": evt.get("category", "Event")
                    })

        return results
