import { useState, useEffect } from "react";
import "./cases.css";
import { api } from "../services/api";
import { navigate } from "../App";

function Cases() {
  const [cases, setCases] = useState([]);
  const [searchQuery, setSearchQuery] = useState("");
  const [statusFilter, setStatusFilter] = useState("all");
  const [showModal, setShowModal] = useState(false);
  const [newTitle, setNewTitle] = useState("");
  const [newDesc, setNewDesc] = useState("");
  const [newPriority, setNewPriority] = useState("MEDIUM");
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    loadCases();
  }, []);

  const loadCases = async () => {
    try {
      const data = await api.cases.list();
      setCases(data);
    } catch (err) {
      console.error("Failed to load cases:", err);
    } finally {
      setLoading(false);
    }
  };

  const handleCreateCase = async (e) => {
    e.preventDefault();
    if (!newTitle.trim()) return;

    try {
      await api.cases.create({
        title: newTitle,
        description: newDesc,
        priority: newPriority,
        assigned_officer: "Special Agent Roy"
      });
      setNewTitle("");
      setNewDesc("");
      setShowModal(false);
      loadCases();
    } catch (err) {
      alert("Failed to create case: " + err.message);
    }
  };

  const filteredCases = cases.filter((c) => {
    const matchesSearch =
      c.title.toLowerCase().includes(searchQuery.toLowerCase()) ||
      c.id.toLowerCase().includes(searchQuery.toLowerCase()) ||
      (c.description && c.description.toLowerCase().includes(searchQuery.toLowerCase()));

    const matchesStatus =
      statusFilter === "all" ||
      c.status.toLowerCase().replace(" ", "") === statusFilter.toLowerCase().replace(" ", "");

    return matchesSearch && matchesStatus;
  });

  return (
    <div className="cases-page">

      <div className="cases-header">
        <div>
          <p className="cases-eyebrow">INVESTIGATION DOSSIERS</p>
          <h1>Cases</h1>
          <p>Manage, inspect and create investigation dossiers.</p>
        </div>

        <button className="new-case-button" onClick={() => setShowModal(true)}>
          + New Case
        </button>
      </div>

      <div className="cases-toolbar">
        <input
          placeholder="Search cases by title, ID or description..."
          value={searchQuery}
          onChange={(e) => setSearchQuery(e.target.value)}
        />

        <select
          value={statusFilter}
          onChange={(e) => setStatusFilter(e.target.value)}
        >
          <option value="all">All Status</option>
          <option value="active">Active</option>
          <option value="underreview">Under Review</option>
          <option value="closed">Closed</option>
        </select>
      </div>

      <div className="cases-list">
        {filteredCases.map((item) => (
          <div className="case-card" key={item.id} style={{ cursor: "pointer" }} onClick={() => navigate("/graph")}>

            <div className="case-main">
              <div style={{ display: "flex", alignItems: "center", gap: "10px", marginBottom: "6px" }}>
                <span className="case-id">{item.id}</span>
                {item.priority && (
                  <span style={{
                    fontSize: "11px",
                    fontWeight: "600",
                    padding: "2px 6px",
                    borderRadius: "4px",
                    background: item.priority === "HIGH" ? "rgba(239, 68, 68, 0.2)" : "rgba(56, 189, 248, 0.2)",
                    color: item.priority === "HIGH" ? "#f87171" : "#38bdf8",
                    border: `1px solid ${item.priority === "HIGH" ? "#ef4444" : "#0284c7"}`
                  }}>
                    {item.priority} PRIORITY
                  </span>
                )}
              </div>

              <h2>{item.title}</h2>
              <p>{item.description}</p>

              <div style={{ display: "flex", gap: "12px", marginTop: "12px", fontSize: "12px", color: "#94a3b8" }}>
                <span>📁 Evidence: <strong>{item.evidence_count || 0}</strong></span>
                <span>👥 Entities: <strong>{item.entity_count || 0}</strong></span>
                <span>👮 Officer: <strong>{item.assigned_officer || "Roy"}</strong></span>
              </div>
            </div>

            <div className="case-details">
              <span
                className={`case-status ${
                  item.status === "Active"
                    ? "active"
                    : item.status === "Under Review"
                    ? "review"
                    : "closed"
                }`}
              >
                {item.status}
              </span>

              <span>{item.date || "Updated recently"}</span>

              <div style={{ display: "flex", gap: "6px", marginTop: "12px" }}>
                <button
                  onClick={(e) => { e.stopPropagation(); navigate("/graph"); }}
                  style={{ padding: "4px 8px", background: "#1e293b", border: "1px solid #475569", borderRadius: "4px", color: "#38bdf8", fontSize: "11px", cursor: "pointer" }}
                >
                  Graph
                </button>
                <button
                  onClick={(e) => { e.stopPropagation(); navigate("/upload"); }}
                  style={{ padding: "4px 8px", background: "#1e293b", border: "1px solid #475569", borderRadius: "4px", color: "#f1f5f9", fontSize: "11px", cursor: "pointer" }}
                >
                  + Evidence
                </button>
              </div>
            </div>

          </div>
        ))}
      </div>

      {/* CREATE NEW CASE MODAL */}
      {showModal && (
        <div style={{
          position: "fixed",
          inset: 0,
          background: "rgba(0, 0, 0, 0.75)",
          display: "flex",
          alignItems: "center",
          justifyContent: "center",
          zIndex: 1000,
          padding: "20px"
        }}>
          <div style={{
            background: "#161d2d",
            border: "1px solid #334155",
            borderRadius: "12px",
            width: "100%",
            maxWidth: "500px",
            padding: "24px",
            boxShadow: "0 20px 25px -5px rgba(0, 0, 0, 0.5)"
          }}>
            <h2 style={{ margin: "0 0 8px", color: "#f8fafc", fontSize: "20px" }}>Create New Investigation Case</h2>
            <p style={{ margin: "0 0 20px", color: "#94a3b8", fontSize: "13px" }}>
              Initialize an intelligence dossier to track evidence, entities, and network links.
            </p>

            <form onSubmit={handleCreateCase}>
              <div style={{ marginBottom: "16px" }}>
                <label style={{ display: "block", fontSize: "12px", fontWeight: "600", color: "#cbd5e1", marginBottom: "6px" }}>
                  Case Title
                </label>
                <input
                  type="text"
                  placeholder="e.g. Cyber Financial Fraud Syndicate"
                  value={newTitle}
                  onChange={(e) => setNewTitle(e.target.value)}
                  style={{ width: "100%", padding: "10px", background: "#0f172a", border: "1px solid #334155", borderRadius: "6px", color: "white", fontSize: "14px" }}
                  required
                />
              </div>

              <div style={{ marginBottom: "16px" }}>
                <label style={{ display: "block", fontSize: "12px", fontWeight: "600", color: "#cbd5e1", marginBottom: "6px" }}>
                  Description / Case Overview
                </label>
                <textarea
                  rows="3"
                  placeholder="Brief summary of allegations, suspects or known intelligence..."
                  value={newDesc}
                  onChange={(e) => setNewDesc(e.target.value)}
                  style={{ width: "100%", padding: "10px", background: "#0f172a", border: "1px solid #334155", borderRadius: "6px", color: "white", fontSize: "14px" }}
                />
              </div>

              <div style={{ marginBottom: "24px" }}>
                <label style={{ display: "block", fontSize: "12px", fontWeight: "600", color: "#cbd5e1", marginBottom: "6px" }}>
                  Priority Level
                </label>
                <select
                  value={newPriority}
                  onChange={(e) => setNewPriority(e.target.value)}
                  style={{ width: "100%", padding: "10px", background: "#0f172a", border: "1px solid #334155", borderRadius: "6px", color: "white", fontSize: "14px" }}
                >
                  <option value="HIGH">High Priority</option>
                  <option value="MEDIUM">Medium Priority</option>
                  <option value="LOW">Low Priority</option>
                </select>
              </div>

              <div style={{ display: "flex", justifyContent: "flex-end", gap: "10px" }}>
                <button
                  type="button"
                  onClick={() => setShowModal(false)}
                  style={{ padding: "9px 16px", background: "transparent", border: "1px solid #475569", borderRadius: "6px", color: "#cbd5e1", cursor: "pointer" }}
                >
                  Cancel
                </button>
                <button
                  type="submit"
                  style={{ padding: "9px 18px", background: "#38bdf8", border: "none", borderRadius: "6px", color: "#0f172a", fontWeight: "600", cursor: "pointer" }}
                >
                  Create Case Dossier
                </button>
              </div>
            </form>
          </div>
        </div>
      )}

    </div>
  );
}

export default Cases;