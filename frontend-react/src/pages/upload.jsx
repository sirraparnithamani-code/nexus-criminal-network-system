import { useState } from "react";
import "./Upload.css";
import { api } from "../services/api";
import { navigate } from "../App";

function Upload() {
  const [selectedFiles, setSelectedFiles] = useState([]);
  const [caseId, setCaseId] = useState("CASE-2026-014");
  const [isProcessing, setIsProcessing] = useState(false);
  const [progressStep, setProgressStep] = useState(0); // 0: Idle, 1: Reading, 2: NLP, 3: Graph, 4: Done
  const [extractionResult, setExtractionResult] = useState(null);
  const [errorMessage, setErrorMessage] = useState("");

  const handleFileChange = (e) => {
    if (e.target.files && e.target.files.length > 0) {
      setSelectedFiles(Array.from(e.target.files));
      setExtractionResult(null);
      setErrorMessage("");
    }
  };

  const handleProcessUpload = async () => {
    if (selectedFiles.length === 0) {
      setErrorMessage("Please select at least one raw case document or PDF to process.");
      return;
    }

    setIsProcessing(true);
    setErrorMessage("");
    setProgressStep(1);

    try {
      // Animated stepper progression
      const stepTimer1 = setTimeout(() => setProgressStep(2), 700);
      const stepTimer2 = setTimeout(() => setProgressStep(3), 1400);

      const res = await api.evidence.upload(selectedFiles, caseId);

      clearTimeout(stepTimer1);
      clearTimeout(stepTimer2);
      setProgressStep(4);
      setExtractionResult(res);
    } catch (err) {
      console.error("Upload error:", err);
      setErrorMessage("Extraction failed: " + err.message);
      setProgressStep(0);
    } finally {
      setIsProcessing(false);
    }
  };

  // Helper to load sample FIR demo PDF
  const handleLoadSampleFIR = async () => {
    setIsProcessing(true);
    setProgressStep(1);
    setErrorMessage("");

    try {
      // Simulate raw FIR text ingestion if browser cannot read local disk path directly
      const sampleText = `DISTRICT: Hyderabad City Commissionerate
POLICE STATION: Cyber Crime PS, Cyberabad
FIR NO: FIR-2026-014 | DATE: 2026-09-10 | TIME: 09:30 hrs
SUSPECTS:
- Accused 1: Rahul Kumar, Banjara Hills, Hyderabad. Phone: 9876543210. Account: ACC001 (HDFC Bank).
- Accused 2: Arjun Singh, Hitech City, Hyderabad. Phone: 9123456789. Account: ACC002 (ICICI Bank).
- Accused 3: Ravi Sharma, Hyderabad. Phone: 9988776655. Account: ACC003 (Axis Bank).
- Organization: Apex Traders Pvt Ltd, Hitech City.
STATEMENT OF FACTS:
On 2026-09-10 at 10:30 hrs, telecommunication intercepted call between 9876543210 (Rahul Kumar) and 9123456789 (Arjun Singh) for 120 seconds.
At 12:00 hrs, Rahul Kumar called Ravi Sharma on 9988776655 for 60 seconds.
At 12:45 hrs, electronic fund transfer of INR 50,000 sent from account ACC001 (Rahul Kumar) to account ACC002 (Arjun Singh).
At 13:10 hrs, transfer of INR 25,000 sent from account ACC001 to account ACC003 (Ravi Sharma).
At 15:30 hrs, account ACC002 transferred INR 10,000 into account ACC003.
At 16:00 hrs, account ACC003 returned kickback of INR 5,000 into account ACC001.
Vehicle TS 09 AB 1234 driven by Rahul Kumar spotted at Hitech City outside Apex Traders Pvt Ltd.`;

      const blob = new Blob([sampleText], { type: "text/plain" });
      const sampleFile = new File([blob], "FIR_Case_2026_014_Raw.txt", { type: "text/plain" });

      setProgressStep(2);
      const res = await api.evidence.upload([sampleFile], caseId);
      setProgressStep(4);
      setExtractionResult(res);
    } catch (e) {
      setErrorMessage("Sample upload error: " + e.message);
      setProgressStep(0);
    } finally {
      setIsProcessing(false);
    }
  };

  return (
    <div className="upload-page">

      <div className="upload-header">
        <p className="upload-eyebrow">RAW DOCUMENT INGESTION & NLP EXTRACTION</p>
        <h1>Upload Evidence</h1>
        <p>
          Ingest raw, unannotated police FIRs, interrogation transcripts, bank logs, and call detail records.
          NEXUS automatically extracts entities, relationships, and chronological timelines.
        </p>
      </div>

      <div className="upload-container">

        {/* LEFT UPLOAD BOX */}
        <div className="upload-box" style={{ flex: "1.2" }}>

          <div className="upload-icon">↑</div>

          <h2>Select Raw Investigation Files</h2>

          <p>
            Accepts unannotated PDF dossiers, DOCX reports, text logs, or CSV spreadsheets.
          </p>

          <div style={{ marginBottom: "16px", width: "100%", maxWidth: "320px" }}>
            <label style={{ display: "block", fontSize: "12px", color: "#94a3b8", marginBottom: "4px", textAlign: "left" }}>
              Assign to Case Dossier:
            </label>
            <select
              value={caseId}
              onChange={(e) => setCaseId(e.target.value)}
              style={{ width: "100%", padding: "8px 12px", background: "#0f172a", border: "1px solid #334155", borderRadius: "6px", color: "#f8fafc", fontSize: "13px" }}
            >
              <option value="CASE-2026-014">CASE-2026-014 (Financial Network Investigation)</option>
              <option value="CASE-2026-011">CASE-2026-011 (Organized Crime Analysis)</option>
              <option value="CASE-2026-008">CASE-2026-008 (Missing Person Investigation)</option>
            </select>
          </div>

          <input
            type="file"
            id="evidence-file"
            hidden
            multiple
            accept=".pdf,.docx,.txt,.csv,.log"
            onChange={handleFileChange}
          />

          <div style={{ display: "flex", gap: "10px", flexWrap: "wrap", justifyContent: "center" }}>
            <label
              htmlFor="evidence-file"
              className="upload-button"
              style={{ cursor: "pointer", display: "inline-block" }}
            >
              {selectedFiles.length > 0 ? "Change Files" : "Select Raw Document / PDF"}
            </label>

            <button
              type="button"
              onClick={handleLoadSampleFIR}
              style={{ padding: "10px 16px", background: "rgba(56, 189, 248, 0.15)", border: "1px solid #0284c7", borderRadius: "6px", color: "#38bdf8", fontSize: "14px", fontWeight: "500", cursor: "pointer" }}
            >
              Quick Ingest Sample Raw FIR
            </button>
          </div>

          {selectedFiles.length > 0 && (
            <div style={{ marginTop: "16px", padding: "12px", background: "#0f172a", borderRadius: "8px", border: "1px solid #1e293b", width: "100%", maxWidth: "420px" }}>
              <p style={{ margin: "0 0 6px", fontSize: "12px", color: "#94a3b8", fontWeight: "600" }}>Selected Documents:</p>
              {selectedFiles.map((f, i) => (
                <div key={i} style={{ fontSize: "13px", color: "#e2e8f0", display: "flex", justifyContent: "space-between", padding: "3px 0" }}>
                  <span>📄 {f.name}</span>
                  <span style={{ color: "#64748b" }}>{(f.size / 1024).toFixed(1)} KB</span>
                </div>
              ))}

              <button
                onClick={handleProcessUpload}
                disabled={isProcessing}
                style={{
                  width: "100%",
                  marginTop: "12px",
                  padding: "10px",
                  background: isProcessing ? "#475569" : "#38bdf8",
                  color: "#0f172a",
                  fontWeight: "600",
                  fontSize: "14px",
                  border: "none",
                  borderRadius: "6px",
                  cursor: isProcessing ? "wait" : "pointer"
                }}
              >
                {isProcessing ? "Processing Evidence..." : "⚡ Run NLP Extraction & Ingest"}
              </button>
            </div>
          )}

          {errorMessage && (
            <p style={{ color: "#f87171", fontSize: "13px", marginTop: "12px" }}>{errorMessage}</p>
          )}

          <span className="upload-formats" style={{ marginTop: "16px" }}>
            Supported Formats: PDF · TXT · DOCX · CSV · LOG
          </span>

        </div>

        {/* RIGHT PROCESSING PIPELINE STEPPER */}
        <div className="processing-panel" style={{ flex: "1" }}>

          <p className="panel-label">
            AUTONOMOUS EXTRACTION PIPELINE
          </p>

          <h2>Automated Intelligence Extraction</h2>

          <div className="pipeline-step" style={{ opacity: progressStep >= 1 || progressStep === 0 ? 1 : 0.4 }}>
            <span style={{ background: progressStep >= 1 ? "#38bdf8" : "#1e293b", color: progressStep >= 1 ? "#0f172a" : "#94a3b8" }}>01</span>
            <div>
              <strong>Raw Document Text Extraction</strong>
              <p>Extract unannotated text and tabular records via PDFPlumber & DOCX engine.</p>
            </div>
          </div>

          <div className="pipeline-step" style={{ opacity: progressStep >= 2 || progressStep === 0 ? 1 : 0.4 }}>
            <span style={{ background: progressStep >= 2 ? "#38bdf8" : "#1e293b", color: progressStep >= 2 ? "#0f172a" : "#94a3b8" }}>02</span>
            <div>
              <strong>NLP Entity Extraction</strong>
              <p>Detect Persons, Phone numbers, Bank accounts, Organizations, and Locations.</p>
            </div>
          </div>

          <div className="pipeline-step" style={{ opacity: progressStep >= 3 || progressStep === 0 ? 1 : 0.4 }}>
            <span style={{ background: progressStep >= 3 ? "#38bdf8" : "#1e293b", color: progressStep >= 3 ? "#0f172a" : "#94a3b8" }}>03</span>
            <div>
              <strong>Cross-Domain Relationship Mapping</strong>
              <p>Link caller-receiver calls, account money transfers, and entity associations.</p>
            </div>
          </div>

          <div className="pipeline-step" style={{ opacity: progressStep >= 4 || progressStep === 0 ? 1 : 0.4 }}>
            <span style={{ background: progressStep >= 4 ? "#10b981" : "#1e293b", color: progressStep >= 4 ? "white" : "#94a3b8" }}>04</span>
            <div>
              <strong>Investigation Graph & Chronology</strong>
              <p>Sync to Graph Engine, calculate risk scores, and populate investigation timeline.</p>
            </div>
          </div>

        </div>

      </div>

      {/* EXTRACTION RESULTS DISPLAY */}
      {extractionResult && (
        <div style={{
          marginTop: "30px",
          padding: "24px",
          background: "#161d2d",
          border: "1px solid #334155",
          borderRadius: "12px"
        }}>
          <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center", marginBottom: "16px" }}>
            <div>
              <span style={{ background: "rgba(16, 185, 129, 0.2)", color: "#34d399", padding: "3px 8px", borderRadius: "4px", fontSize: "11px", fontWeight: "700" }}>
                EXTRACTION SUCCESSFUL
              </span>
              <h2 style={{ margin: "8px 0 0", color: "#f8fafc", fontSize: "20px" }}>
                Intelligence Findings Extracted
              </h2>
            </div>

            <div style={{ display: "flex", gap: "10px" }}>
              <button
                onClick={() => navigate("/graph")}
                style={{ padding: "8px 16px", background: "#38bdf8", color: "#0f172a", border: "none", borderRadius: "6px", fontWeight: "600", cursor: "pointer" }}
              >
                View in Network Graph ➔
              </button>
              <button
                onClick={() => navigate("/timeline")}
                style={{ padding: "8px 16px", background: "#1e293b", color: "#f1f5f9", border: "1px solid #475569", borderRadius: "6px", cursor: "pointer" }}
              >
                View Timeline ➔
              </button>
            </div>
          </div>

          {extractionResult.processed_files && extractionResult.processed_files.map((file, idx) => (
            <div key={idx} style={{ marginBottom: "16px" }}>
              <p style={{ margin: "0 0 10px", fontSize: "14px", color: "#cbd5e1" }}>
                Document: <strong>{file.file_name}</strong> · Found <strong>{file.extracted_entities_count}</strong> entities, <strong>{file.extracted_relationships_count}</strong> relationships, and <strong>{file.timeline_events_count}</strong> timeline events.
              </p>

              {/* ENTITY PILLS */}
              <div style={{ display: "flex", flexWrap: "wrap", gap: "8px", marginBottom: "14px" }}>
                {file.entities && file.entities.map((ent, i) => (
                  <span
                    key={i}
                    style={{
                      display: "inline-flex",
                      alignItems: "center",
                      gap: "6px",
                      padding: "4px 10px",
                      borderRadius: "6px",
                      fontSize: "12px",
                      background:
                        ent.type === "Person" ? "rgba(56, 189, 248, 0.15)" :
                        ent.type === "Phone" ? "rgba(34, 197, 94, 0.15)" :
                        ent.type === "Account" ? "rgba(234, 179, 8, 0.15)" :
                        ent.type === "Organization" ? "rgba(168, 85, 247, 0.15)" :
                        ent.type === "Location" ? "rgba(249, 115, 22, 0.15)" : "rgba(100, 116, 139, 0.2)",
                      color:
                        ent.type === "Person" ? "#38bdf8" :
                        ent.type === "Phone" ? "#4ade80" :
                        ent.type === "Account" ? "#facc15" :
                        ent.type === "Organization" ? "#c084fc" :
                        ent.type === "Location" ? "#fb923c" : "#cbd5e1",
                      border: `1px solid ${
                        ent.type === "Person" ? "rgba(56, 189, 248, 0.3)" :
                        ent.type === "Phone" ? "rgba(34, 197, 94, 0.3)" :
                        ent.type === "Account" ? "rgba(234, 179, 8, 0.3)" :
                        ent.type === "Organization" ? "rgba(168, 85, 247, 0.3)" :
                        ent.type === "Location" ? "rgba(249, 115, 22, 0.3)" : "rgba(100, 116, 139, 0.3)"
                      }`
                    }}
                  >
                    <small style={{ fontWeight: "700", opacity: 0.8 }}>{ent.type}:</small>
                    <strong>{ent.name}</strong>
                  </span>
                ))}
              </div>

              {/* RELATIONSHIP CHIPS */}
              {file.relationships && file.relationships.length > 0 && (
                <div style={{ background: "#0f172a", padding: "12px", borderRadius: "8px", border: "1px solid #1e293b", marginBottom: "12px" }}>
                  <p style={{ margin: "0 0 8px", fontSize: "12px", color: "#94a3b8", fontWeight: "600" }}>Detected Connections & Financial Trails:</p>
                  <div style={{ display: "grid", gridTemplateColumns: "repeat(auto-fill, minmax(280px, 1fr))", gap: "8px" }}>
                    {file.relationships.slice(0, 6).map((rel, rIdx) => (
                      <div key={rIdx} style={{ fontSize: "12px", color: "#cbd5e1", padding: "6px 8px", background: "#161d2d", borderRadius: "4px" }}>
                        <strong>{rel.source_name || rel.source}</strong>
                        <span style={{ color: "#38bdf8", margin: "0 6px" }}>➔ [{rel.type}] ➔</span>
                        <strong>{rel.target_name || rel.target}</strong>
                        {rel.properties?.amount && <span style={{ color: "#facc15", marginLeft: "6px" }}>(₹{rel.properties.amount})</span>}
                      </div>
                    ))}
                  </div>
                </div>
              )}
            </div>
          ))}
        </div>
      )}

    </div>
  );
}

export default Upload;