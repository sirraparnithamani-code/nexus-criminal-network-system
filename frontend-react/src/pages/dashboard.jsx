import { useState, useEffect } from "react";
import "./Dashboard.css";
import { api } from "../services/api";
import { navigate } from "../App";

function Dashboard() {
  const [stats, setStats] = useState({
    activeCases: 12,
    totalCases: 14,
    evidenceItems: 248,
    keyEntities: 20,
    relationships: 24,
    alerts: 8,
    recentCases: []
  });
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    async function loadStats() {
      try {
        const data = await api.dashboard.getStats();
        if (data) {
          setStats(data);
        }
      } catch (err) {
        console.error("Failed to load dashboard stats:", err);
      } finally {
        setLoading(false);
      }
    }
    loadStats();
  }, []);

  return (
    <div className="dashboard-page">

      <header className="dashboard-header">

        <div>
          <p className="dashboard-eyebrow">
            INVESTIGATION COMMAND CENTER · HYDERABAD CYBER CELL
          </p>

          <h1>Dashboard</h1>

          <p>
            Real-time overview of active criminal intelligence, cross-domain entities and network graphs.
          </p>
        </div>

        <div className="user-area" style={{ display: "flex", alignItems: "center", gap: "12px" }}>
          <div style={{ textAlign: "right" }}>
            <span style={{ display: "block", fontSize: "14px", fontWeight: "600", color: "#e2e8f0" }}>Special Agent Roy</span>
            <span style={{ display: "block", fontSize: "12px", color: "#94a3b8" }}>NEXUS-047 · Lead Investigator</span>
          </div>
          <button onClick={() => navigate("/")} style={{ padding: "8px 14px", borderRadius: "6px", border: "1px solid #334155", background: "#1e293b", color: "#f1f5f9", cursor: "pointer" }}>
            Sign Out
          </button>
        </div>

      </header>

      {/* ACTIVE CASE HIGHLIGHT BANNER */}
      <div style={{
        background: "linear-gradient(135deg, rgba(30, 41, 59, 0.7), rgba(15, 23, 42, 0.9))",
        border: "1px solid rgba(56, 189, 248, 0.3)",
        borderRadius: "10px",
        padding: "16px 20px",
        marginBottom: "24px",
        display: "flex",
        justifyContent: "space-between",
        alignItems: "center",
        flexWrap: "wrap",
        gap: "12px"
      }}>
        <div>
          <div style={{ display: "flex", alignItems: "center", gap: "8px", marginBottom: "4px" }}>
            <span style={{ background: "#ef4444", color: "white", fontSize: "11px", fontWeight: "bold", padding: "2px 8px", borderRadius: "4px" }}>ACTIVE TARGET</span>
            <span style={{ color: "#38bdf8", fontWeight: "600", fontSize: "14px" }}>CASE-2026-014</span>
            <span style={{ color: "#94a3b8", fontSize: "13px" }}>· Cyber Financial Fraud & Money Mule Network</span>
          </div>
          <p style={{ margin: 0, fontSize: "13px", color: "#cbd5e1" }}>
            Primary suspects: <strong>Rahul Kumar</strong> (9876543210), <strong>Arjun Singh</strong> (9123456789), <strong>Ravi Sharma</strong> (9988776655). Total money trail: INR 90,000.
          </p>
        </div>
        <div style={{ display: "flex", gap: "8px" }}>
          <button onClick={() => navigate("/graph")} style={{ padding: "8px 14px", background: "#38bdf8", color: "#0f172a", border: "none", borderRadius: "6px", fontWeight: "600", fontSize: "13px", cursor: "pointer" }}>
            Open Network Graph
          </button>
          <button onClick={() => navigate("/upload")} style={{ padding: "8px 14px", background: "transparent", color: "#e2e8f0", border: "1px solid #475569", borderRadius: "6px", fontWeight: "500", fontSize: "13px", cursor: "pointer" }}>
            + Upload Evidence
          </button>
        </div>
      </div>

      <section className="dashboard-stats">

        <div className="stat-card">
          <span>ACTIVE CASES</span>
          <strong>{stats.activeCases}</strong>
          <p>Investigations currently open</p>
        </div>

        <div className="stat-card">
          <span>EVIDENCE ITEMS</span>
          <strong>{stats.evidenceItems}</strong>
          <p>Raw documents, CDRs & statements</p>
        </div>

        <div className="stat-card">
          <span>KEY ENTITIES</span>
          <strong>{stats.keyEntities}</strong>
          <p>People, phones, accounts, locations</p>
        </div>

        <div className="stat-card">
          <span>SYSTEM ALERTS</span>
          <strong style={{ color: "#f87171" }}>0{stats.alerts}</strong>
          <p>Circular transfers & mule patterns</p>
        </div>

      </section>

      <section className="dashboard-grid">

        <div className="dashboard-panel">

          <div className="panel-heading">
            <div>
              <span>CASE ACTIVITY</span>
              <h2>Recent Investigations</h2>
            </div>

            <button onClick={() => navigate("/cases")}>
              View all
            </button>
          </div>

          <div className="case-row" onClick={() => navigate("/graph")} style={{ cursor: "pointer" }}>
            <div>
              <strong>CASE-2026-014</strong>
              <p>Financial Network Investigation · Banjara Hills & Hitech City</p>
            </div>
            <span className="status active">Active</span>
          </div>

          <div className="case-row" onClick={() => navigate("/cases")} style={{ cursor: "pointer" }}>
            <div>
              <strong>CASE-2026-011</strong>
              <p>Organized Crime Analysis · Cross-District Logistics</p>
            </div>
            <span className="status review">Review</span>
          </div>

          <div className="case-row" onClick={() => navigate("/cases")} style={{ cursor: "pointer" }}>
            <div>
              <strong>CASE-2026-008</strong>
              <p>Missing Person Investigation · Transit Hub Tracking</p>
            </div>
            <span className="status active">Active</span>
          </div>

        </div>

        <div className="dashboard-panel">

          <div className="panel-heading">
            <div>
              <span>INTELLIGENCE WORKSPACE</span>
              <h2>Quick Actions</h2>
            </div>
          </div>

          <div className="quick-actions">

            <button onClick={() => navigate("/cases")}>
              <span>▣</span> View Cases
            </button>

            <button onClick={() => navigate("/upload")}>
              <span>↑</span> Upload Raw Evidence
            </button>

            <button onClick={() => navigate("/search")}>
              <span>⌕</span> Search Intelligence
            </button>

            <button onClick={() => navigate("/graph")}>
              <span>⌘</span> Open Network Graph
            </button>

            <button onClick={() => navigate("/timeline")}>
              <span>⏱</span> Investigation Timeline
            </button>

            <button onClick={() => navigate("/investigation")}>
              <span>◎</span> Intelligence Analysis
            </button>

          </div>

        </div>

      </section>

    </div>
  );
}

export default Dashboard;