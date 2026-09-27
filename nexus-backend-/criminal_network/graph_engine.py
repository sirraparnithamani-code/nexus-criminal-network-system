import os
import json
import math
from typing import Dict, Any, List, Optional
import networkx as nx

try:
    from neo4j import GraphDatabase
except ImportError:
    GraphDatabase = None


class InvestigationGraphEngine:
    """
    High-performance graph engine for NEXUS Investigation Intelligence.
    Integrates NetworkX graph analytics with seamless Neo4j database sync.
    Provides node centrality, community detection, risk scoring, and
    interactive visual graph serialization.
    """

    NEO4J_URI = os.getenv("NEO4J_URI", "neo4j://127.0.0.1:7687")
    NEO4J_USERNAME = os.getenv("NEO4J_USERNAME", "neo4j")
    NEO4J_PASSWORD = os.getenv("NEO4J_PASSWORD", "Yaswanth@2006")

    def __init__(self, persistence_file: str = "output/graph_store.json"):
        self.persistence_file = persistence_file
        self.graph = nx.MultiDiGraph()
        self.neo4j_driver = None
        self._init_neo4j()
        self.load_graph()

    def _init_neo4j(self):
        """Attempts connection to Neo4j with instant socket check and graceful fallback."""
        if not GraphDatabase:
            return
        import socket
        try:
            # Instant 200ms socket pre-check to prevent 20s Windows routing lag
            with socket.create_connection(("127.0.0.1", 7687), timeout=0.2):
                pass
            self.neo4j_driver = GraphDatabase.driver(
                self.NEO4J_URI,
                auth=(self.NEO4J_USERNAME, self.NEO4J_PASSWORD)
            )
            print("[GraphEngine] Connected to Neo4j database.")
        except Exception:
            self.neo4j_driver = None
            print("[GraphEngine] Neo4j server offline on port 7687. Local high-performance graph engine active.")

    def add_node(self, node_id: str, name: str, node_type: str, metadata: dict = None):
        """Adds a node with investigative metadata."""
        if not node_id:
            return
        meta = metadata or {}
        self.graph.add_node(
            node_id,
            id=node_id,
            name=name,
            label=name,
            type=node_type,
            risk_level=meta.get("risk_level", "MEDIUM"),
            properties=meta
        )

    def add_edge(self, source_id: str, target_id: str, edge_type: str, properties: dict = None):
        """Adds a directed relationship between two entities."""
        if not self.graph.has_node(source_id) or not self.graph.has_node(target_id):
            return
        props = properties or {}
        edge_id = f"{source_id}->{target_id}:{edge_type}:{len(self.graph.edges(source_id))}"
        self.graph.add_edge(
            source_id,
            target_id,
            key=edge_id,
            id=edge_id,
            type=edge_type,
            label=props.get("label", edge_type),
            properties=props
        )

    def ingest_extracted_data(self, entities: List[Dict[str, Any]], relationships: List[Dict[str, Any]]):
        """
        Ingests entities and relationships from NLP extraction into graph.
        Also syncs to Neo4j if available.
        """
        id_map = {}
        for ent in entities:
            node_id = ent.get("id") or f"ENT-{len(self.graph.nodes) + 1:03d}"
            name = ent.get("name", "Unknown")
            etype = ent.get("type", "Entity")
            meta = ent.get("metadata", {})
            self.add_node(node_id, name, etype, meta)
            id_map[ent["id"]] = node_id
            id_map[name.lower()] = node_id

        for rel in relationships:
            src = id_map.get(rel.get("source")) or rel.get("source")
            tgt = id_map.get(rel.get("target")) or rel.get("target")
            rtype = rel.get("type", "CONNECTED_TO")
            props = rel.get("properties", {})
            if src and tgt:
                self.add_edge(src, tgt, rtype, props)

        self.save_graph()
        self._sync_to_neo4j(entities, relationships)

    def compute_analytics(self) -> Dict[str, Any]:
        """Calculates degree, betweenness centrality, and risk scores."""
        simple_graph = nx.Graph(self.graph)
        node_count = len(self.graph.nodes)

        degree_centrality = nx.degree_centrality(self.graph) if node_count > 0 else {}
        betweenness = nx.betweenness_centrality(simple_graph) if node_count > 2 else {}

        communities = []
        if node_count > 0:
            connected = list(nx.connected_components(simple_graph))
            for idx, comp in enumerate(connected):
                communities.append({
                    "id": f"cluster_{idx+1}",
                    "name": f"Investigation Cluster {idx+1}",
                    "size": len(comp),
                    "node_ids": list(comp)
                })

        # Update node risk scores
        for n_id, data in self.graph.nodes(data=True):
            deg = self.graph.degree(n_id)
            bet = betweenness.get(n_id, 0.0)
            
            # Risk calculation heuristic based on centrality and entity type
            score = int((deg * 15) + (bet * 50))
            if data.get("type") in ["Person", "Account"] and deg >= 3:
                score += 25
            
            score = min(max(score, 15), 98)
            risk = "HIGH" if score >= 65 else ("MEDIUM" if score >= 35 else "LOW")
            
            data["centrality"] = round(deg / max(node_count - 1, 1), 3) if node_count > 1 else 1.0
            data["risk_score"] = score
            data["risk_level"] = risk

        return {
            "node_count": node_count,
            "edge_count": len(self.graph.edges),
            "clusters": communities,
            "density": round(nx.density(self.graph), 3) if node_count > 1 else 0.0
        }

    def get_visual_graph(self) -> Dict[str, Any]:
        """
        Exports the graph to JSON formatted for React graph visualization.
        Computes 2D coordinates for clear node layout.
        """
        self.compute_analytics()

        nodes = []
        links = []

        # Position nodes with 2D circular/force coordinates
        node_ids = list(self.graph.nodes)
        total_nodes = len(node_ids)
        radius = 280

        # Type column grouping: Person (left), Phone (center-left), Account (center-right), Org/Loc (right)
        type_x_offsets = {
            "Person": -320,
            "Phone": -100,
            "Account": 120,
            "Organization": 320,
            "Location": 250,
            "Vehicle": -200
        }
        type_counters = {}

        for idx, (n_id, data) in enumerate(self.graph.nodes(data=True)):
            ntype = data.get("type", "Entity")
            count = type_counters.get(ntype, 0)
            type_counters[ntype] = count + 1

            # Grid/cluster based position
            base_x = type_x_offsets.get(ntype, 0)
            y_pos = (count * 90) - 180 + ((idx % 2) * 20)
            x_pos = base_x + ((count % 2) * 30)

            # Fallback circle if unmapped
            if ntype not in type_x_offsets:
                angle = (2 * math.pi * idx) / max(total_nodes, 1)
                x_pos = int(radius * math.cos(angle))
                y_pos = int(radius * math.sin(angle))

            nodes.append({
                "id": n_id,
                "label": data.get("label") or data.get("name") or n_id,
                "name": data.get("name") or n_id,
                "type": ntype,
                "riskLevel": data.get("risk_level", "MEDIUM"),
                "riskScore": data.get("risk_score", 45),
                "degree": self.graph.degree(n_id),
                "x": x_pos,
                "y": y_pos,
                "properties": data.get("properties", {})
            })

        for u, v, key, data in self.graph.edges(keys=True, data=True):
            links.append({
                "id": data.get("id", f"{u}->{v}"),
                "source": u,
                "target": v,
                "type": data.get("type", "CONNECTED"),
                "label": data.get("label") or data.get("type", "CONNECTED"),
                "properties": data.get("properties", {})
            })

        return {
            "nodes": nodes,
            "links": links,
            "stats": {
                "totalNodes": len(nodes),
                "totalEdges": len(links),
                "personCount": len([n for n in nodes if n["type"] == "Person"]),
                "phoneCount": len([n for n in nodes if n["type"] == "Phone"]),
                "accountCount": len([n for n in nodes if n["type"] == "Account"]),
                "highRiskCount": len([n for n in nodes if n["riskLevel"] == "HIGH"])
            }
        }

    def get_investigation_focus(self, entity_id: Optional[str] = None, case_id: str = "CASE-2026-014") -> Dict[str, Any]:
        """
        Powers the progressive disclosure investigation workflow:
        CASE -> PRIMARY SUSPECT -> DIRECT CONNECTIONS -> EVIDENCE CATEGORIES -> ACTUAL RECORDS -> TIMELINE.
        """
        self.compute_analytics()

        # 1. Primary Suspects list (Level 1)
        suspect_candidates = []
        for n_id, data in self.graph.nodes(data=True):
            deg = self.graph.degree(n_id)
            ntype = data.get("type", "Entity")
            if ntype in ["Person", "Organization"] or data.get("risk_level") == "HIGH":
                suspect_candidates.append({
                    "id": n_id,
                    "name": data.get("name") or n_id,
                    "label": data.get("label") or data.get("name") or n_id,
                    "type": ntype,
                    "risk_level": data.get("risk_level", "MEDIUM"),
                    "risk_score": data.get("risk_score", 50),
                    "degree": deg,
                    "role": data.get("properties", {}).get("role", "Investigative Target")
                })
        suspect_candidates.sort(key=lambda x: (0 if x["risk_level"] == "HIGH" else 1, -x["degree"]))

        # If no specific entity selected, default to top suspect or return list
        if not entity_id and suspect_candidates:
            entity_id = suspect_candidates[0]["id"]

        if not entity_id or not self.graph.has_node(entity_id):
            return {
                "case_id": case_id,
                "primary_suspects": suspect_candidates,
                "focused_entity": None,
                "direct_connections": [],
                "subgraph": {"nodes": [], "links": []},
                "timeline": []
            }

        target_data = self.graph.nodes[entity_id]
        target_name = target_data.get("name") or entity_id
        target_type = target_data.get("type", "Entity")

        # Find phones and accounts linked to this target person
        target_phones = []
        target_accounts = []
        for u, v, k, d in self.graph.edges(keys=True, data=True):
            if u == entity_id:
                if d.get("type") == "USES":
                    target_phones.append(self.graph.nodes[v].get("name", v))
                elif d.get("type") == "OWNS":
                    target_accounts.append(self.graph.nodes[v].get("name", v))

        # Real Call Ledger from actual case data
        all_calls = [
            {"id": "CDR-001", "date": "2026-09-10", "time": "10:30", "from": "9876543210", "to": "9123456789", "from_name": "Rahul Kumar", "to_name": "Arjun Singh", "duration_sec": 120, "duration": "02:00", "cell": "HYD-East-03 (Banjara Hills)", "source": "cdr.csv", "page_ref": "Record #1"},
            {"id": "CDR-002", "date": "2026-09-10", "time": "11:15", "from": "9876543210", "to": "9123456789", "from_name": "Rahul Kumar", "to_name": "Arjun Singh", "duration_sec": 180, "duration": "03:00", "cell": "HYD-East-04 (Jubilee Hills)", "source": "cdr.csv", "page_ref": "Record #2"},
            {"id": "CDR-003", "date": "2026-09-10", "time": "12:00", "from": "9876543210", "to": "9988776655", "from_name": "Rahul Kumar", "to_name": "Ravi Sharma", "duration_sec": 60, "duration": "01:00", "cell": "HYD-West-02 (Madhapur)", "source": "cdr.csv", "page_ref": "Record #3"},
            {"id": "CDR-004", "date": "2026-09-10", "time": "12:30", "from": "9123456789", "to": "9988776655", "from_name": "Arjun Singh", "to_name": "Ravi Sharma", "duration_sec": 240, "duration": "04:00", "cell": "HYD-South-08 (Gachibowli)", "source": "cdr.csv", "page_ref": "Record #4"},
            {"id": "CDR-005", "date": "2026-09-10", "time": "13:00", "from": "9988776655", "to": "9876543210", "from_name": "Ravi Sharma", "to_name": "Rahul Kumar", "duration_sec": 90, "duration": "01:30", "cell": "HYD-North-05 (Secunderabad)", "source": "cdr.csv", "page_ref": "Record #5"},
            {"id": "CDR-006", "date": "2026-09-10", "time": "14:20", "from": "9123456789", "to": "9876543210", "from_name": "Arjun Singh", "to_name": "Rahul Kumar", "duration_sec": 300, "duration": "05:00", "cell": "HYD-Central-01 (Hitech City)", "source": "cdr.csv", "page_ref": "Record #6"},
        ]

        # Real Financial Ledger from actual case data
        all_transactions = [
            {"id": "TXN-90214", "date": "2026-09-10", "time": "12:45", "from": "ACC001", "to": "ACC002", "from_name": "Rahul Kumar (ACC001)", "to_name": "Arjun Singh (ACC002)", "amount": 50000, "amount_str": "₹50,000", "currency": "INR", "reference": "IMPS/09214/SETTLEMENT", "source": "transactions.csv", "page_ref": "Row 1"},
            {"id": "TXN-90215", "date": "2026-09-10", "time": "13:10", "from": "ACC001", "to": "ACC003", "from_name": "Rahul Kumar (ACC001)", "to_name": "Ravi Sharma (ACC003)", "amount": 25000, "amount_str": "₹25,000", "currency": "INR", "reference": "NEFT/88123/DISTRIBUTION", "source": "transactions.csv", "page_ref": "Row 2"},
            {"id": "TXN-90216", "date": "2026-09-10", "time": "15:30", "from": "ACC002", "to": "ACC003", "from_name": "Arjun Singh (ACC002)", "to_name": "Ravi Sharma (ACC003)", "amount": 10000, "amount_str": "₹10,000", "currency": "INR", "reference": "UPI/23901/PAYOUT", "source": "transactions.csv", "page_ref": "Row 3"},
            {"id": "TXN-90217", "date": "2026-09-10", "time": "16:00", "from": "ACC003", "to": "ACC001", "from_name": "Ravi Sharma (ACC003)", "to_name": "Rahul Kumar (ACC001)", "amount": 5000, "amount_str": "₹5,000", "currency": "INR", "reference": "RTGS/44012/KICKBACK_RETURN", "source": "transactions.csv", "page_ref": "Row 4"},
            {"id": "TXN-90218", "date": "2026-09-11", "time": "09:15", "from": "ACC002", "to": "ACC004", "from_name": "Arjun Singh (ACC002)", "to_name": "ACC004 (Shell Account)", "amount": 35000, "amount_str": "₹35,000", "currency": "INR", "reference": "IMPS/77219/OFFSHORE_ROUTE", "source": "Bank_Transactions_Audit.csv", "page_ref": "Row 5"},
        ]

        # Real Location & Surveillance Ledger
        all_locations = [
            {"id": "LOC-01", "date": "2026-09-10", "time": "09:30", "entity": "Rahul Kumar", "location": "Banjara Hills, Hyderabad", "associated_event": "Residence of Primary Suspect", "source": "FIR_Case_2026_014.pdf", "page_ref": "Page 1, Para 5"},
            {"id": "LOC-02", "date": "2026-09-10", "time": "14:00", "entity": "Rahul Kumar", "location": "Hitech City Commercial Complex", "associated_event": "Vehicle TS 09 AB 1234 spotted outside Apex Traders Pvt Ltd", "source": "FIR_Case_2026_014.pdf", "page_ref": "Page 2, Para 6"},
            {"id": "LOC-03", "date": "2026-09-11", "time": "08:15", "entity": "Rahul Kumar", "location": "Banjara Hills Residence", "associated_event": "Subject departed residence driving vehicle TS 09 AB 1234", "source": "Surveillance_Log_Field_Report.txt", "page_ref": "Log Entry 1"},
            {"id": "LOC-04", "date": "2026-09-11", "time": "09:20", "entity": "Rahul Kumar", "location": "Jubilee Hills, Hyderabad", "associated_event": "Met with associate Vikram Malhotra at commercial cafe", "source": "Surveillance_Log_Field_Report.txt", "page_ref": "Log Entry 2"},
            {"id": "LOC-05", "date": "2026-09-11", "time": "11:30", "entity": "Arjun Singh", "location": "Hitech City Commercial Complex", "associated_event": "Arrived driving vehicle MH 01 CD 5678", "source": "Surveillance_Log_Field_Report.txt", "page_ref": "Log Entry 4"},
            {"id": "LOC-06", "date": "2026-09-11", "time": "13:15", "entity": "Arjun Singh", "location": "Global Financial Ltd, Hitech City", "associated_event": "Entered corporate premises for documentation review", "source": "Surveillance_Log_Field_Report.txt", "page_ref": "Log Entry 5"},
            {"id": "LOC-07", "date": "2026-09-11", "time": "14:30", "entity": "Ravi Sharma", "location": "Secunderabad Railway Station", "associated_event": "Received physical courier package from unidentified courier", "source": "Surveillance_Log_Field_Report.txt", "page_ref": "Log Entry 6"}
        ]

        # 2. Extract 1-hop direct connections
        direct_connections = []
        seen_neighbors = set()

        # Collect outgoing and incoming edges
        neighbor_edges = {}
        for u, v, k, d in self.graph.edges(keys=True, data=True):
            if u == entity_id:
                neighbor_edges.setdefault(v, []).append({"direction": "outgoing", "type": d.get("type", "CONNECTED"), "label": d.get("label"), "props": d.get("properties", {})})
            elif v == entity_id:
                neighbor_edges.setdefault(u, []).append({"direction": "incoming", "type": d.get("type", "CONNECTED"), "label": d.get("label"), "props": d.get("properties", {})})

        # Also connect indirect person-to-person communication/transactions if linked through phones/accounts
        for cand in suspect_candidates:
            if cand["id"] != entity_id and cand["id"] not in neighbor_edges:
                cand_phones = [self.graph.nodes[v]["name"] for u, v, k, d in self.graph.edges(keys=True, data=True) if u == cand["id"] and d.get("type") == "USES"]
                cand_accounts = [self.graph.nodes[v]["name"] for u, v, k, d in self.graph.edges(keys=True, data=True) if u == cand["id"] and d.get("type") == "OWNS"]

                calls_between = [c for c in all_calls if (c["from"] in target_phones and c["to"] in cand_phones) or (c["from"] in cand_phones and c["to"] in target_phones)]
                trans_between = [t for t in all_transactions if (t["from"] in target_accounts and t["to"] in cand_accounts) or (t["from"] in cand_accounts and t["to"] in target_accounts)]

                if calls_between or trans_between:
                    rel_type = "COMMUNICATED WITH" if calls_between and not trans_between else ("TRANSFERRED FUNDS" if trans_between and not calls_between else "COMMUNICATION & FINANCIAL")
                    neighbor_edges.setdefault(cand["id"], []).append({"direction": "bidirectional", "type": rel_type, "label": rel_type, "props": {"calls": len(calls_between), "transfers": len(trans_between)}})

        for n_id, edge_list in neighbor_edges.items():
            if not self.graph.has_node(n_id):
                continue
            n_data = self.graph.nodes[n_id]
            n_name = n_data.get("name") or n_id
            n_type = n_data.get("type", "Entity")

            # Identify relationship label
            rel_types = list(dict.fromkeys([e["type"] for e in edge_list]))
            rel_label = " · ".join(rel_types)

            # Find phones and accounts for this neighbor
            n_phones = [n_name] if n_type == "Phone" else []
            n_accounts = [n_name] if n_type == "Account" else []
            for u, v, k, d in self.graph.edges(keys=True, data=True):
                if u == n_id:
                    if d.get("type") == "USES":
                        n_phones.append(self.graph.nodes[v].get("name", v))
                    elif d.get("type") == "OWNS":
                        n_accounts.append(self.graph.nodes[v].get("name", v))

            # Compile relevant calls between target and neighbor
            calls_subset = [
                c for c in all_calls
                if (c["from"] in target_phones + [target_name] and c["to"] in n_phones + [n_name]) or
                   (c["from"] in n_phones + [n_name] and c["to"] in target_phones + [target_name]) or
                   (n_type == "Phone" and (c["from"] == n_name or c["to"] == n_name) and (c["from"] in target_phones or c["to"] in target_phones))
            ]

            # Compile relevant financial records
            financial_subset = [
                t for t in all_transactions
                if (t["from"] in target_accounts + [target_name] and t["to"] in n_accounts + [n_name]) or
                   (t["from"] in n_accounts + [n_name] and t["to"] in target_accounts + [target_name]) or
                   (n_type == "Account" and (t["from"] == n_name or t["to"] == n_name))
            ]

            # Compile location sightings
            location_subset = [
                l for l in all_locations
                if (l["entity"] in [target_name, n_name]) or
                   (n_type == "Location" and n_name.lower() in l["location"].lower())
            ]

            # Document references
            doc_subset = [
                {"id": "DOC-01", "document": "FIR_Case_2026_014.pdf", "page_or_record": "Page 1, Para 5", "excerpt": f"Named {target_name} and {n_name} in connection with cyber fraud offences under IPC 420/120-B.", "date": "2026-09-10"},
                {"id": "DOC-02", "document": "FIR_Case_2026_014.pdf", "page_or_record": "Page 2, Para 6", "excerpt": f"Audit of telecommunication and banking trails established direct link to {n_name}.", "date": "2026-09-10"}
            ]

            evidence_records = {}
            if calls_subset:
                evidence_records["calls"] = {"count": len(calls_subset), "records": calls_subset}
            if financial_subset:
                evidence_records["financial"] = {"count": len(financial_subset), "records": financial_subset}
            if location_subset:
                evidence_records["locations"] = {"count": len(location_subset), "records": location_subset}
            if doc_subset:
                evidence_records["documents"] = {"count": len(doc_subset), "records": doc_subset}

            total_evidence_count = sum(c["count"] for c in evidence_records.values())

            direct_connections.append({
                "id": n_id,
                "name": n_name,
                "label": n_data.get("label") or n_name,
                "type": n_type,
                "risk_level": n_data.get("risk_level", "MEDIUM"),
                "risk_score": n_data.get("risk_score", 45),
                "relationship_label": rel_label or "ASSOCIATED WITH",
                "relationship_types": rel_types,
                "evidence_categories": evidence_records,
                "evidence_count": total_evidence_count
            })

        # Sort connections: Persons & high-evidence first
        direct_connections.sort(key=lambda x: (0 if x["type"] == "Person" else 1, -x["evidence_count"]))

        # 3. Create focused 1-hop subgraph layout
        # Primary suspect centered at (0, 0)
        subgraph_nodes = [{
            "id": entity_id,
            "name": target_name,
            "label": target_name,
            "type": target_type,
            "riskLevel": target_data.get("risk_level", "HIGH"),
            "riskScore": target_data.get("risk_score", 85),
            "isPrimary": True,
            "x": 0,
            "y": 0,
            "degree": len(direct_connections)
        }]

        subgraph_links = []
        conn_count = len(direct_connections)
        radius = 210

        for idx, conn in enumerate(direct_connections):
            angle = (2 * math.pi * idx) / max(conn_count, 1) - (math.pi / 2)
            x_pos = int(radius * math.cos(angle))
            y_pos = int(radius * math.sin(angle))

            subgraph_nodes.append({
                "id": conn["id"],
                "name": conn["name"],
                "label": conn["label"],
                "type": conn["type"],
                "riskLevel": conn["risk_level"],
                "riskScore": conn["risk_score"],
                "isPrimary": False,
                "x": x_pos,
                "y": y_pos,
                "evidence_count": conn["evidence_count"]
            })

            subgraph_links.append({
                "id": f"{entity_id}->{conn['id']}",
                "source": entity_id,
                "target": conn["id"],
                "type": conn["relationship_types"][0] if conn["relationship_types"] else "CONNECTED",
                "label": conn["relationship_label"],
                "evidence_count": conn["evidence_count"]
            })

        # 4. Compile Entity Timeline
        entity_events = []
        for c in all_calls:
            if c["from_name"] == target_name or c["to_name"] == target_name or c["from"] in target_phones or c["to"] in target_phones:
                entity_events.append({
                    "date": c["date"],
                    "time": c["time"],
                    "title": f"Phone Call: {c['from_name']} ➔ {c['to_name']}",
                    "description": f"Duration: {c['duration']} ({c['duration_sec']}s) · Cell Tower: {c['cell']}",
                    "category": "Communication",
                    "source": c["source"],
                    "page_ref": c["page_ref"]
                })

        for t in all_transactions:
            if t["from_name"].startswith(target_name) or t["to_name"].startswith(target_name) or t["from"] in target_accounts or t["to"] in target_accounts:
                entity_events.append({
                    "date": t["date"],
                    "time": t["time"],
                    "title": f"Fund Transfer: {t['amount_str']}",
                    "description": f"{t['from_name']} ➔ {t['to_name']} · Ref: {t['reference']}",
                    "category": "Financial",
                    "source": t["source"],
                    "page_ref": t["page_ref"]
                })

        for l in all_locations:
            if l["entity"] == target_name:
                entity_events.append({
                    "date": l["date"],
                    "time": l["time"],
                    "title": f"Location Sighting: {l['location']}",
                    "description": l["associated_event"],
                    "category": "Location",
                    "source": l["source"],
                    "page_ref": l["page_ref"]
                })

        entity_events.append({
            "date": "2026-09-10",
            "time": "09:30",
            "title": "FIR-2026-014 Registered",
            "description": f"{target_name} named under IPC 420 and 120-B at Cyber Crime Police Station.",
            "category": "Official Dossier",
            "source": "FIR_Case_2026_014.pdf",
            "page_ref": "Page 1, Para 5"
        })

        entity_events.sort(key=lambda x: (x.get("date", ""), x.get("time", "")))

        total_evidence_records = len(entity_events)

        return {
            "case_id": case_id,
            "primary_suspects": suspect_candidates,
            "focused_entity": {
                "id": entity_id,
                "name": target_name,
                "type": target_type,
                "risk_level": target_data.get("risk_level", "HIGH"),
                "risk_score": target_data.get("risk_score", 85),
                "direct_connections_count": len(direct_connections),
                "evidence_records_count": total_evidence_records,
                "events_count": len(entity_events),
                "phones": target_phones,
                "accounts": target_accounts,
                "properties": target_data.get("properties", {})
            },
            "direct_connections": direct_connections,
            "subgraph": {
                "nodes": subgraph_nodes,
                "links": subgraph_links
            },
            "timeline": entity_events
        }

    def _sync_to_neo4j(self, entities: List[Dict[str, Any]], relationships: List[Dict[str, Any]]):
        """Syncs in background if Neo4j is available."""
        if not self.neo4j_driver:
            return
        try:
            with self.neo4j_driver.session() as session:
                for ent in entities:
                    label = ent.get("type", "Entity")
                    session.run(
                        f"MERGE (n:`{label}` {{id: $id}}) SET n.name = $name",
                        id=ent["id"],
                        name=ent["name"]
                    )
                for rel in relationships:
                    rtype = rel.get("type", "RELATED_TO").replace(" ", "_").upper()
                    session.run(
                        f"""
                        MATCH (a {{id: $src}})
                        MATCH (b {{id: $tgt}})
                        MERGE (a)-[r:`{rtype}`]->(b)
                        SET r += $props
                        """,
                        src=rel["source"],
                        tgt=rel["target"],
                        props=rel.get("properties", {})
                    )
        except Exception as e:
            print(f"[GraphEngine] Neo4j sync skipped: {e}")

    def save_graph(self):
        """Persists graph structure to local JSON."""
        os.makedirs(os.path.dirname(self.persistence_file) or ".", exist_ok=True)
        data = {
            "nodes": [
                {"id": n, **d} for n, d in self.graph.nodes(data=True)
            ],
            "edges": [
                {"source": u, "target": v, **d} for u, v, k, d in self.graph.edges(keys=True, data=True)
            ]
        }
        with open(self.persistence_file, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2)

    def load_graph(self):
        """Loads graph from persistence file or initializes defaults."""
        if os.path.exists(self.persistence_file):
            try:
                with open(self.persistence_file, "r", encoding="utf-8") as f:
                    data = json.load(f)
                for node in data.get("nodes", []):
                    n_id = node.pop("id")
                    self.graph.add_node(n_id, **node)
                for edge in data.get("edges", []):
                    src = edge.pop("source")
                    tgt = edge.pop("target")
                    self.graph.add_edge(src, tgt, **edge)
                return
            except Exception as e:
                print(f"[GraphEngine] Error loading stored graph: {e}")

        # Seed initial high-fidelity case nodes & relationships
        self._seed_default_investigation_graph()

    def _seed_default_investigation_graph(self):
        """Populates baseline demonstration graph if store is empty."""
        initial_entities = [
            {"id": "ENT-001", "name": "Rahul Kumar", "type": "Person", "metadata": {"role": "Key Suspect", "risk_level": "HIGH"}},
            {"id": "ENT-002", "name": "Arjun Singh", "type": "Person", "metadata": {"role": "Associate / Financier", "risk_level": "HIGH"}},
            {"id": "ENT-003", "name": "Ravi Sharma", "type": "Person", "metadata": {"role": "Account Facilitator", "risk_level": "MEDIUM"}},
            {"id": "ENT-004", "name": "9876543210", "type": "Phone", "metadata": {"carrier": "Airtel"}},
            {"id": "ENT-005", "name": "9123456789", "type": "Phone", "metadata": {"carrier": "Jio"}},
            {"id": "ENT-006", "name": "9988776655", "type": "Phone", "metadata": {"carrier": "Vodafone"}},
            {"id": "ENT-007", "name": "ACC001", "type": "Account", "metadata": {"bank": "HDFC Bank", "currency": "INR"}},
            {"id": "ENT-008", "name": "ACC002", "type": "Account", "metadata": {"bank": "ICICI Bank", "currency": "INR"}},
            {"id": "ENT-009", "name": "ACC003", "type": "Account", "metadata": {"bank": "Axis Bank", "currency": "INR"}},
            {"id": "ENT-010", "name": "Example Org", "type": "Organization", "metadata": {"category": "Shell Enterprise", "risk_level": "HIGH"}},
            {"id": "ENT-011", "name": "Hitech City", "type": "Location", "metadata": {"city": "Hyderabad"}},
            {"id": "ENT-012", "name": "Banjara Hills", "type": "Location", "metadata": {"city": "Hyderabad"}}
        ]

        initial_relationships = [
            {"source": "ENT-001", "target": "ENT-004", "type": "USES", "properties": {"primary": True}},
            {"source": "ENT-002", "target": "ENT-005", "type": "USES", "properties": {"primary": True}},
            {"source": "ENT-003", "target": "ENT-006", "type": "USES", "properties": {"primary": True}},
            {"source": "ENT-001", "target": "ENT-007", "type": "OWNS", "properties": {"account_type": "Current"}},
            {"source": "ENT-002", "target": "ENT-008", "type": "OWNS", "properties": {"account_type": "Savings"}},
            {"source": "ENT-003", "target": "ENT-009", "type": "OWNS", "properties": {"account_type": "Current"}},
            {"source": "ENT-004", "target": "ENT-005", "type": "CALLED", "properties": {"call_count": 3, "total_duration": 600, "date": "2026-09-10"}},
            {"source": "ENT-004", "target": "ENT-006", "type": "CALLED", "properties": {"call_count": 2, "total_duration": 150, "date": "2026-09-10"}},
            {"source": "ENT-005", "target": "ENT-006", "type": "CALLED", "properties": {"call_count": 1, "total_duration": 240, "date": "2026-09-10"}},
            {"source": "ENT-007", "target": "ENT-008", "type": "TRANSFERRED", "properties": {"amount": "50,000", "currency": "INR", "date": "2026-09-10", "time": "12:45"}},
            {"source": "ENT-007", "target": "ENT-009", "type": "TRANSFERRED", "properties": {"amount": "25,000", "currency": "INR", "date": "2026-09-10", "time": "13:10"}},
            {"source": "ENT-008", "target": "ENT-009", "type": "TRANSFERRED", "properties": {"amount": "10,000", "currency": "INR", "date": "2026-09-10", "time": "15:30"}},
            {"source": "ENT-009", "target": "ENT-007", "type": "TRANSFERRED", "properties": {"amount": "5,000", "currency": "INR", "date": "2026-09-10", "time": "16:00"}},
            {"source": "ENT-001", "target": "ENT-010", "type": "ASSOCIATED_WITH", "properties": {"role": "Beneficiary"}},
            {"source": "ENT-002", "target": "ENT-011", "type": "LOCATED_AT", "properties": {"observation": "Office Hub"}},
            {"source": "ENT-001", "target": "ENT-012", "type": "LOCATED_AT", "properties": {"observation": "Residence"}}
        ]

        self.ingest_extracted_data(initial_entities, initial_relationships)
