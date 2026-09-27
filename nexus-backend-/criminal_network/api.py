import os
import shutil
import time
from typing import List, Optional
from fastapi import FastAPI, UploadFile, File, Form, Query, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from pydantic import BaseModel

from document_processor import DocumentProcessor
from nlp_engine import NLPExtractionEngine
from graph_engine import InvestigationGraphEngine
from storage import CaseStorage

app = FastAPI(
    title="NEXUS Investigation Intelligence API",
    description="Backend API powering NEXUS investigation intelligence, raw document NLP extraction, graph analytics, and case timelines.",
    version="2.0.0"
)

# Enable CORS for React Frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

RAW_DATA_DIR = os.path.join(os.path.dirname(__file__), "raw_data")
OUTPUT_DIR = os.path.join(os.path.dirname(__file__), "output")

os.makedirs(RAW_DATA_DIR, exist_ok=True)
os.makedirs(OUTPUT_DIR, exist_ok=True)

# Initialize Core Services
storage = CaseStorage()
graph_engine = InvestigationGraphEngine()
nlp_engine = NLPExtractionEngine()

# =============================================================================
# DATA MODELS
# =============================================================================

class LoginRequest(BaseModel):
    username: str
    password: str

class CaseCreateRequest(BaseModel):
    title: str
    description: str
    priority: Optional[str] = "MEDIUM"
    assigned_officer: Optional[str] = "Lead Investigator"

# =============================================================================
# ROOT & SYSTEM HEALTH
# =============================================================================

@app.get("/")
def root():
    return {
        "status": "online",
        "system": "NEXUS Investigation Intelligence System",
        "version": "2.0.0",
        "active_cases": len(storage.get_cases()),
        "total_evidence": len(storage.get_evidence()),
        "graph_nodes": len(graph_engine.graph.nodes),
        "graph_edges": len(graph_engine.graph.edges),
        "neo4j_connected": bool(graph_engine.neo4j_driver is not None)
    }

@app.get("/api/health")
def health():
    return {
        "status": "healthy",
        "services": {
            "document_processor": "ready",
            "nlp_extraction_engine": "ready",
            "graph_engine": "ready",
            "neo4j_connected": bool(graph_engine.neo4j_driver is not None),
            "storage": "ready"
        },
        "timestamp": time.time()
    }

# =============================================================================
# AUTHENTICATION
# =============================================================================

@app.post("/api/auth/login")
def login(creds: LoginRequest):
    username = creds.username.strip()
    password = creds.password.strip()

    if not username or not password:
        raise HTTPException(status_code=400, detail="Username and password required")

    # Match user or accept demo investigator credentials
    user = None
    for u in storage.state.get("users", []):
        if u["username"].lower() == username.lower():
            user = u
            break

    if not user:
        # Provide demo investigator profile for testing
        user = {
            "username": username,
            "name": username.capitalize(),
            "role": "Investigator",
            "badge": "NEXUS-089"
        }

    return {
        "status": "success",
        "token": f"nexus-token-{int(time.time())}",
        "user": user
    }

# =============================================================================
# DASHBOARD STATS
# =============================================================================

@app.get("/api/dashboard/stats")
def get_dashboard_stats():
    cases = storage.get_cases()
    evidence = storage.get_evidence()
    analytics = graph_engine.compute_analytics()

    high_risk_entities = [
        n for n, d in graph_engine.graph.nodes(data=True)
        if d.get("risk_level") == "HIGH"
    ]

    return {
        "activeCases": len([c for c in cases if c.get("status") == "Active"]),
        "totalCases": len(cases),
        "evidenceItems": len(evidence),
        "keyEntities": len(graph_engine.graph.nodes),
        "relationships": len(graph_engine.graph.edges),
        "alerts": len(high_risk_entities) + len(analytics.get("clusters", [])),
        "recentCases": cases[:4],
        "clusters": analytics.get("clusters", [])
    }

# =============================================================================
# CASES API
# =============================================================================

@app.get("/api/cases")
def list_cases():
    return {"cases": storage.get_cases()}

@app.get("/api/cases/{case_id}")
def get_case_detail(case_id: str):
    case = storage.get_case(case_id)
    if not case:
        raise HTTPException(status_code=404, detail="Case not found")
    case_evidence = storage.get_evidence(case_id)
    case_timeline = storage.get_timeline(case_id)
    return {
        "case": case,
        "evidence": case_evidence,
        "timeline": case_timeline
    }

@app.post("/api/cases")
def create_case(data: CaseCreateRequest):
    new_case = storage.add_case(data.dict())
    return {"status": "success", "case": new_case}

# =============================================================================
# EVIDENCE & RAW DOCUMENT UPLOAD WITH NLP EXTRACTION
# =============================================================================

@app.get("/api/evidence")
def list_evidence(case_id: Optional[str] = None):
    return {"evidence": storage.get_evidence(case_id)}

@app.post("/api/evidence/upload")
async def upload_evidence(
    files: List[UploadFile] = File(...),
    case_id: str = Form("CASE-2026-014")
):
    """
    Accepts RAW investigation documents (PDF, DOCX, TXT, CSV).
    Saves the files, extracts plain text, executes NLP entity/relationship
    extraction, inserts results into the Graph, and builds the case timeline.
    """
    results = []

    for file in files:
        safe_name = os.path.basename(file.filename)
        dest_path = os.path.join(RAW_DATA_DIR, safe_name)

        # 1. Save uploaded raw file
        with open(dest_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)

        size_kb = max(int(os.path.getsize(dest_path) / 1024), 1)
        ext = os.path.splitext(safe_name)[1].replace(".", "").upper()

        # 2. Register evidence item in storage
        ev_item = storage.add_evidence({
            "case_id": case_id,
            "name": safe_name,
            "file_type": ext or "RAW",
            "size_kb": size_kb,
            "status": "Extracting Text",
            "file_path": dest_path
        })

        try:
            # 3. Extract text from RAW document
            doc_data = DocumentProcessor.extract_text_from_file(dest_path)
            extracted_text = doc_data.get("text", "")

            # 4. Perform NLP Entity, Relationship and Timeline Extraction
            storage.update_evidence_status(ev_item["id"], "Extracting Entities")
            nlp_result = nlp_engine.extract_all(extracted_text, source_id=safe_name)

            new_entities = nlp_result.get("entities", [])
            new_relationships = nlp_result.get("relationships", [])
            new_timeline = nlp_result.get("timeline", [])

            # 5. Ingest into Investigation Graph
            graph_engine.ingest_extracted_data(new_entities, new_relationships)

            # 6. Save Timeline events
            storage.add_timeline_events(case_id, new_timeline)

            # 7. Update status to Processed
            storage.update_evidence_status(ev_item["id"], "Processed", len(new_entities))

            results.append({
                "evidence_id": ev_item["id"],
                "file_name": safe_name,
                "file_type": ext,
                "status": "Processed",
                "extracted_entities_count": len(new_entities),
                "extracted_relationships_count": len(new_relationships),
                "timeline_events_count": len(new_timeline),
                "entities": new_entities,
                "relationships": new_relationships,
                "timeline": new_timeline
            })

        except Exception as e:
            storage.update_evidence_status(ev_item["id"], f"Failed: {str(e)}")
            results.append({
                "evidence_id": ev_item["id"],
                "file_name": safe_name,
                "status": "Error",
                "error": str(e)
            })

    # Update case entity count
    case = storage.get_case(case_id)
    if case:
        case["entity_count"] = len(graph_engine.graph.nodes)
        storage.save()

    return {
        "status": "success",
        "message": f"Successfully processed {len(files)} document(s)",
        "processed_files": results
    }

@app.post("/api/evidence/{evidence_id}/extract")
def extract_single_evidence(evidence_id: str):
    """Re-runs extraction on an existing evidence record."""
    target = None
    for ev in storage.get_evidence():
        if ev["id"] == evidence_id:
            target = ev
            break

    if not target:
        raise HTTPException(status_code=404, detail="Evidence item not found")

    file_path = target.get("file_path") or os.path.join(RAW_DATA_DIR, target["name"])
    if not os.path.exists(file_path):
        raise HTTPException(status_code=404, detail="Underlying document file not found on server")

    doc_data = DocumentProcessor.extract_text_from_file(file_path)
    nlp_result = nlp_engine.extract_all(doc_data.get("text", ""), source_id=target["name"])

    graph_engine.ingest_extracted_data(nlp_result["entities"], nlp_result["relationships"])
    storage.add_timeline_events(target.get("case_id", "CASE-2026-014"), nlp_result["timeline"])
    storage.update_evidence_status(evidence_id, "Processed", len(nlp_result["entities"]))

    return {
        "status": "success",
        "evidence_id": evidence_id,
        "extracted_entities": nlp_result["entities"],
        "extracted_relationships": nlp_result["relationships"],
        "timeline": nlp_result["timeline"]
    }

# =============================================================================
# ENTITIES API
# =============================================================================

@app.get("/api/entities")
@app.get("/api/cases/{case_id}/entities")
def get_entities(case_id: Optional[str] = None):
    """Returns all extracted entities formatted with risk metrics and properties."""
    graph_engine.compute_analytics()
    entities = []

    for n_id, data in graph_engine.graph.nodes(data=True):
        entities.append({
            "id": n_id,
            "name": data.get("name") or n_id,
            "label": data.get("label") or data.get("name") or n_id,
            "type": data.get("type", "Entity"),
            "riskLevel": data.get("risk_level", "MEDIUM"),
            "riskScore": data.get("risk_score", 45),
            "centrality": data.get("centrality", 0.1),
            "degree": graph_engine.graph.degree(n_id),
            "properties": data.get("properties", {})
        })

    return {
        "entities": entities,
        "total": len(entities),
        "by_type": {
            "Person": len([e for e in entities if e["type"] == "Person"]),
            "Phone": len([e for e in entities if e["type"] == "Phone"]),
            "Account": len([e for e in entities if e["type"] == "Account"]),
            "Organization": len([e for e in entities if e["type"] == "Organization"]),
            "Location": len([e for e in entities if e["type"] == "Location"]),
            "Vehicle": len([e for e in entities if e["type"] == "Vehicle"])
        }
    }

# =============================================================================
# GRAPH API
# =============================================================================

@app.get("/api/graph")
@app.get("/api/cases/{case_id}/graph")
def get_investigation_graph(case_id: Optional[str] = None):
    """Returns nodes and edges formatted for React graph visualization."""
    return graph_engine.get_visual_graph()

@app.get("/api/graph/investigate")
@app.get("/api/cases/{case_id}/graph/investigate")
def get_focused_investigation(
    case_id: Optional[str] = "CASE-2026-014",
    entity_id: Optional[str] = None
):
    """
    Returns the focused 1-hop investigation view for progressive disclosure:
    Primary Suspect -> Direct Connections -> Categorized Evidence Records -> Timeline.
    """
    return graph_engine.get_investigation_focus(entity_id=entity_id, case_id=case_id or "CASE-2026-014")

# =============================================================================
# TIMELINE API
# =============================================================================

@app.get("/api/timeline")
@app.get("/api/cases/{case_id}/timeline")
def get_case_timeline(case_id: Optional[str] = None):
    return {"timeline": storage.get_timeline(case_id)}

# =============================================================================
# SEARCH API
# =============================================================================

@app.get("/api/search")
def search_intelligence(
    q: str = Query(..., min_length=1),
    category: str = Query("All")
):
    """Unified full-text and faceted search across entities, cases, evidence, and timeline."""
    results = storage.search(q, category)

    # Search extracted graph entities
    if category in ["All", "People", "Locations", "Organizations"]:
        type_filter = {
            "People": "Person",
            "Locations": "Location",
            "Organizations": "Organization"
        }.get(category)

        for n_id, data in graph_engine.graph.nodes(data=True):
            ent_type = data.get("type", "Entity")
            name = data.get("name", "")

            if type_filter and ent_type != type_filter:
                continue

            if q.lower() in name.lower() or q.lower() in n_id.lower() or q.lower() in ent_type.lower():
                results.append({
                    "category": ent_type.upper(),
                    "id": n_id,
                    "title": name,
                    "description": f"{ent_type} linked to {graph_engine.graph.degree(n_id)} connection(s) in investigation network",
                    "badge": data.get("risk_level", "MEDIUM")
                })

    return {"query": q, "category": category, "results": results, "count": len(results)}

# =============================================================================
# INVESTIGATION & AI SUMMARY API
# =============================================================================

@app.get("/api/investigation/summary")
def get_investigation_summary():
    analytics = graph_engine.compute_analytics()
    nodes = list(graph_engine.graph.nodes(data=True))
    
    # Read AI report if generated
    report_file = os.path.join(OUTPUT_DIR, "final_report.txt")
    report_text = ""
    if os.path.exists(report_file):
        with open(report_file, "r", encoding="utf-8", errors="replace") as f:
            report_text = f.read()
    else:
        report_text = (
            "### AI Investigation Summary\n"
            "Entities and financial relationships have been cross-referenced across Call Detail Records "
            "and Bank Transaction Ledgers. High-centrality entities require investigator verification."
        )

    return {
        "status": "Analysis Complete",
        "keyEntitiesCount": len(nodes),
        "relationshipsCount": len(graph_engine.graph.edges),
        "clustersCount": len(analytics.get("clusters", [])),
        "suspiciousPatternsCount": len([n for n, d in nodes if d.get("risk_level") == "HIGH"]),
        "analytics": analytics,
        "aiReport": report_text
    }

# =============================================================================
# LEGACY POST /analyze ENDPOINT
# =============================================================================

@app.post("/analyze")
async def legacy_analyze(files: List[UploadFile] = File(...)):
    """Legacy backward compatibility endpoint."""
    return await upload_evidence(files=files, case_id="CASE-2026-014")