import { useState, useEffect } from "react";
import "./Evidence.css";
import { api } from "../services/api";
import { navigate } from "../App";

function Evidence() {
  const [evidence, setEvidence] = useState([]);
  const [loading, setLoading] = useState(true);
  const [extractingId, setExtractingId] = useState(null);

  useEffect(() => {
    loadEvidence();
  }, []);

  const loadEvidence = async () => {
    try {
      const data = await api.evidence.list();
      setEvidence(data);
    } catch (err) {
      console.error("Failed to load evidence:", err);
    } finally {
      setLoading(false);
    }
  };

  const handleExtract = async (evId) => {
    setExtractingId(evId);
    try {
      await api.evidence.extract(evId);
      await loadEvidence();
    } catch (err) {
      alert("Extraction failed: " + err.message);
    } finally {
      setExtractingId(null);
    }
  };

  return (
    <div className="evidence-page">

      <div className="evidence-header">
        <div>
          <p>EVIDENCE RECORD LEDGER</p>
          <h1>Evidence Management</h1>
          <span>
            Comprehensive repository of ingested case documents, telecommunication CDRs, and financial ledgers.
          </span>
        </div>

        <button onClick={() => navigate("/upload")}>
          + Ingest New Evidence
        </button>
      </div>

      <div className="evidence-table">
        <div className="evidence-table-header" style={{ display: "grid", gridTemplateColumns: "1fr 2fr 1fr 1.5fr 1fr 1.5fr", padding: "12px 16px", background: "#161d2d", fontWeight: "600", fontSize: "12px", color: "#94a3b8" }}>
          <span>ID</span>
          <span>DOCUMENT NAME</span>
          <span>TYPE</span>
          <span>STATUS</span>
          <span>ENTITIES</span>
          <span style={{ textAlign: "right" }}>ACTIONS</span>
        </div>

        {evidence.map((item) => (
          <div
            className="evidence-row"
            key={item.id}
            style={{ display: "grid", gridTemplateColumns: "1fr 2fr 1fr 1.5fr 1fr 1.5fr", alignItems: "center", padding: "14px 16px", borderBottom: "1px solid #1e293b", fontSize: "13px" }}
          >
            <span style={{ color: "#38bdf8", fontWeight: "600" }}>{item.id}</span>

            <div style={{ display: "flex", alignItems: "center", gap: "8px" }}>
              <span style={{ fontSize: "16px" }}>
                {item.file_type === "PDF" ? "📕" : item.file_type === "CSV" ? "📊" : item.file_type === "DOCX" ? "📘" : "📄"}
              </span>
              <div>
                <strong style={{ color: "#f8fafc", display: "block" }}>{item.name}</strong>
                <span style={{ fontSize: "11px", color: "#64748b" }}>{item.uploaded_at || "Uploaded recently"}</span>
              </div>
            </div>

            <span>
              <span style={{
                fontSize: "11px",
                fontWeight: "700",
                padding: "2px 6px",
                borderRadius: "4px",
                background:
                  item.file_type === "PDF" ? "rgba(239, 68, 68, 0.2)" :
                  item.file_type === "CSV" ? "rgba(34, 197, 94, 0.2)" :
                  item.file_type === "DOCX" ? "rgba(59, 130, 246, 0.2)" : "rgba(148, 163, 184, 0.2)",
                color:
                  item.file_type === "PDF" ? "#f87171" :
                  item.file_type === "CSV" ? "#4ade80" :
                  item.file_type === "DOCX" ? "#60a5fa" : "#cbd5e1"
              }}>
                {item.file_type}
              </span>
            </span>

            <span>
              <span
                className={
                  item.status === "Processed"
                    ? "evidence-status processed"
                    : "evidence-status pending"
                }
              >
                {item.status}
              </span>
            </span>

            <span style={{ color: "#cbd5e1", fontWeight: "600" }}>
              {item.extracted_entities ? `${item.extracted_entities} entities` : "—"}
            </span>

            <div style={{ display: "flex", justifyContent: "flex-end", gap: "6px" }}>
              <button
                onClick={() => handleExtract(item.id)}
                disabled={extractingId === item.id}
                style={{
                  padding: "4px 8px",
                  background: "#1e293b",
                  border: "1px solid #334155",
                  borderRadius: "4px",
                  color: "#38bdf8",
                  fontSize: "11px",
                  cursor: "pointer"
                }}
              >
                {extractingId === item.id ? "Extracting..." : "Re-Extract"}
              </button>

              <button
                onClick={() => navigate("/graph")}
                style={{
                  padding: "4px 8px",
                  background: "#1e293b",
                  border: "1px solid #334155",
                  borderRadius: "4px",
                  color: "#f8fafc",
                  fontSize: "11px",
                  cursor: "pointer"
                }}
              >
                Graph ➔
              </button>
            </div>
          </div>
        ))}
      </div>

    </div>
  );
}

export default Evidence;