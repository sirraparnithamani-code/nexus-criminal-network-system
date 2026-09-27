import "./SidebarStyles.css";
import { navigate } from "../App";

function Sidebar({ activePath }) {
  const currentPath = activePath || window.location.pathname;

  const goTo = (path) => {
    navigate(path);
  };

  return (
    <aside className="sidebar">

      {/* BRAND */}
      <div className="sidebar-brand" onClick={() => goTo("/dashboard")} style={{ cursor: "pointer" }}>
        <div className="sidebar-logo">N</div>

        <div>
          <strong>NEXUS</strong>
          <span>Investigation Intelligence</span>
        </div>
      </div>

      {/* NAVIGATION */}
      <nav className="sidebar-nav">

        <p className="nav-title">WORKSPACE</p>

        {/* DASHBOARD */}
        <button
          className={`nav-item ${
            currentPath === "/dashboard" ? "active" : ""
          }`}
          onClick={() => goTo("/dashboard")}
        >
          <span>⌂</span>
          Dashboard
        </button>

        {/* CASES */}
        <button
          className={`nav-item ${
            currentPath === "/cases" ? "active" : ""
          }`}
          onClick={() => goTo("/cases")}
        >
          <span>▣</span>
          Cases
        </button>

        {/* UPLOAD EVIDENCE */}
        <button
          className={`nav-item ${
            currentPath === "/upload" ? "active" : ""
          }`}
          onClick={() => goTo("/upload")}
        >
          <span>↑</span>
          Upload Evidence
        </button>

        {/* SEARCH */}
        <button
          className={`nav-item ${
            currentPath === "/search" ? "active" : ""
          }`}
          onClick={() => goTo("/search")}
        >
          <span>⌕</span>
          Search
        </button>

        <p className="nav-title">ANALYSIS & INTEL</p>

        {/* INVESTIGATION */}
        <button
          className={`nav-item ${
            currentPath === "/investigation" ? "active" : ""
          }`}
          onClick={() => goTo("/investigation")}
        >
          <span>◎</span>
          Investigation
        </button>

        {/* NETWORK GRAPH */}
        <button
          className={`nav-item ${
            currentPath === "/graph" ? "active" : ""
          }`}
          onClick={() => goTo("/graph")}
        >
          <span>⌘</span>
          Network Graph
        </button>

        {/* TIMELINE */}
        <button
          className={`nav-item ${
            currentPath === "/timeline" ? "active" : ""
          }`}
          onClick={() => goTo("/timeline")}
        >
          <span>⏱</span>
          Timeline
        </button>

        {/* EVIDENCE */}
        <button
          className={`nav-item ${
            currentPath === "/evidence" ? "active" : ""
          }`}
          onClick={() => goTo("/evidence")}
        >
          <span>▤</span>
          Evidence
        </button>

      </nav>

      {/* BOTTOM */}
      <div className="sidebar-bottom">

        <div className="user-badge-mini" style={{ padding: "8px 12px", fontSize: "12px", color: "#8e9bb0", display: "flex", alignItems: "center", gap: "8px" }}>
          <span style={{ width: "8px", height: "8px", borderRadius: "50%", background: "#10b981", display: "inline-block" }}></span>
          <span>Agent Roy · Active</span>
        </div>

        <button
          className="logout-button"
          onClick={() => goTo("/")}
        >
          Sign Out
        </button>

      </div>

    </aside>
  );
}

export default Sidebar;