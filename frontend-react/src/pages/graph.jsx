import { useState, useEffect, useRef } from "react";
import "./graph.css";
import { api } from "../services/api";

function Graph() {
  const [graphData, setGraphData] = useState({ nodes: [], links: [] });
  const [selectedEntity, setSelectedEntity] = useState(null);
  const [filterType, setFilterType] = useState("All");
  const [searchFilter, setSearchFilter] = useState("");
  const [loading, setLoading] = useState(true);
  const [zoomLevel, setZoomLevel] = useState(1);

  // Dragging state
  const [draggingNodeId, setDraggingNodeId] = useState(null);
  const svgRef = useRef(null);

  /**
   * Arranges nodes into 4 clear, well-spaced investigation columns:
   * Suspects (Person) -> Communications (Phone) -> Financials (Account) -> Destinations (Org / Loc)
   */
  const applyStructuredLayout = (data) => {
    if (!data || !data.nodes) return data;

    const stageBuckets = {
      Person: [],
      Phone: [],
      Account: [],
      Destinations: [],
    };

    data.nodes.forEach((node) => {
      if (node.type === "Person") {
        stageBuckets.Person.push(node);
      } else if (node.type === "Phone") {
        stageBuckets.Phone.push(node);
      } else if (node.type === "Account") {
        stageBuckets.Account.push(node);
      } else {
        stageBuckets.Destinations.push(node);
      }
    });

    // Clear column spacing: 250px intervals across width
    const stageX = {
      Person: -370,
      Phone: -120,
      Account: 130,
      Destinations: 370,
    };

    const positionedNodes = [];

    Object.entries(stageBuckets).forEach(([colKey, nodesInCol]) => {
      const total = nodesInCol.length;
      const spacing = total > 4 ? 90 : 120;
      const startY = total <= 1 ? 0 : -((total - 1) * spacing) / 2;

      nodesInCol.forEach((node, idx) => {
        positionedNodes.push({
          ...node,
          x: stageX[colKey],
          y: Math.round(startY + idx * spacing),
        });
      });
    });

    return {
      ...data,
      nodes: positionedNodes,
    };
  };

  const reloadGraph = async () => {
    setLoading(true);
    try {
      const data = await api.graph.getData();
      if (data && data.nodes) {
        setGraphData(applyStructuredLayout(data));
      }
    } catch (err) {
      console.error("Failed to load graph data:", err);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    let isMounted = true;

    api.graph.getData()
      .then((data) => {
        if (isMounted && data && data.nodes) {
          setGraphData(applyStructuredLayout(data));
        }
      })
      .catch((err) => {
        console.error("Failed to load graph data:", err);
      })
      .finally(() => {
        if (isMounted) setLoading(false);
      });

    return () => {
      isMounted = false;
    };
  }, []);

  const handleResetLayout = () => {
    reloadGraph();
    setSelectedEntity(null);
    setSearchFilter("");
    setFilterType("All");
    setZoomLevel(1);
  };

  // Node Color mapping by type
  const getNodeColor = (type) => {
    switch (type) {
      case "Person":
        return "#38bdf8"; // Cyan
      case "Phone":
        return "#4ade80"; // Green
      case "Account":
        return "#facc15"; // Yellow
      case "Organization":
        return "#c084fc"; // Purple
      case "Location":
        return "#fb923c"; // Orange
      case "Vehicle":
        return "#f87171"; // Red
      default:
        return "#94a3b8"; // Slate
    }
  };

  // Node Icon mapping
  const getNodeIcon = (type) => {
    switch (type) {
      case "Person":
        return "👤";
      case "Phone":
        return "📱";
      case "Account":
        return "💳";
      case "Organization":
        return "🏢";
      case "Location":
        return "📍";
      case "Vehicle":
        return "🚗";
      default:
        return "◎";
    }
  };

  // Filtering nodes
  const filteredNodes = graphData.nodes.filter((node) => {
    const matchesSearch =
      node.name.toLowerCase().includes(searchFilter.toLowerCase()) ||
      node.type.toLowerCase().includes(searchFilter.toLowerCase());

    const matchesType =
      filterType === "All" ? true :
      filterType === "High Risk" ? node.riskLevel === "HIGH" :
      node.type === filterType;

    return matchesSearch && matchesType;
  });

  const visibleNodeIds = new Set(filteredNodes.map((n) => n.id));

  const filteredLinks = graphData.links.filter(
    (link) => visibleNodeIds.has(link.source) && visibleNodeIds.has(link.target)
  );

  // Mouse interaction for node dragging
  const handleMouseDown = (e, nodeId) => {
    e.stopPropagation();
    setDraggingNodeId(nodeId);
  };

  const handleMouseMove = (e) => {
    if (!draggingNodeId || !svgRef.current) return;
    const rect = svgRef.current.getBoundingClientRect();
    const x = (e.clientX - rect.left - rect.width / 2) / zoomLevel;
    const y = (e.clientY - rect.top - rect.height / 2) / zoomLevel;

    setGraphData((prev) => ({
      ...prev,
      nodes: prev.nodes.map((n) =>
        n.id === draggingNodeId ? { ...n, x: Math.round(x), y: Math.round(y) } : n
      ),
    }));
  };

  const handleMouseUp = () => {
    setDraggingNodeId(null);
  };

  // Entity Details selection
  const handleSelectNode = (node) => {
    const connections = graphData.links
      .filter((l) => l.source === node.id || l.target === node.id)
      .map((l) => {
        const otherId = l.source === node.id ? l.target : l.source;
        const otherNode = graphData.nodes.find((n) => n.id === otherId);
        return {
          id: l.id,
          type: l.type,
          label: l.label,
          targetId: otherId,
          targetName: otherNode ? otherNode.name : otherId,
          targetType: otherNode ? otherNode.type : "Entity",
          direction: l.source === node.id ? "Outgoing" : "Incoming",
          properties: l.properties || {}
        };
      });

    setSelectedEntity({
      ...node,
      connectionsList: connections,
      connectionsCount: connections.length,
      timeline: [
        {
          date: "10 SEP 2026",
          time: "10:30",
          title: "Telecommunication Intercept",
          description: `${node.name} linked via telecommunication surveillance log.`
        },
        {
          date: "10 SEP 2026",
          time: "12:45",
          title: "Financial Transfer Activity",
          description: `Transaction node connection confirmed in Case CASE-2026-014.`
        },
        {
          date: "11 SEP 2026",
          time: "14:00",
          title: "Location Proximity Sighting",
          description: `Entity associated with Hitech City and Banjara Hills clusters.`
        }
      ]
    });
  };

  // Node position map for fast link calculation
  const nodePos = {};
  filteredNodes.forEach((n) => {
    nodePos[n.id] = { x: n.x || 0, y: n.y || 0 };
  });

  // Track connected nodes for focal spotlighting
  const connectedNodeIds = new Set();
  if (selectedEntity) {
    graphData.links.forEach((l) => {
      if (l.source === selectedEntity.id) connectedNodeIds.add(l.target);
      if (l.target === selectedEntity.id) connectedNodeIds.add(l.source);
    });
  }

  /**
   * Computes clean, collision-free paths:
   * 1. Intra-column links (Phone-to-Phone, Account-to-Account) arc outward instead of crossing vertically through nodes
   * 2. Multi-hop links arch gracefully over intermediate stages
   * 3. Adjacent stage links use smooth horizontal cubic Bezier curves
   */
  const computeLinkPath = (src, tgt) => {
    const dx = tgt.x - src.x;
    const dy = tgt.y - src.y;
    const isSameColumn = Math.abs(dx) < 50;
    const isLongJump = Math.abs(dx) > 300 && Math.abs(dy) < 60;

    if (isSameColumn) {
      const bendSide = src.x < 0 ? -1 : 1;
      const arcWidth = Math.min(Math.abs(dy) * 0.45, 55) * bendSide;
      const reverseMod = dy < 0 ? -0.8 : 1;
      const actualArc = arcWidth * reverseMod;

      const midX = src.x + actualArc * 0.85;
      const midY = (src.y + tgt.y) / 2;

      return {
        path: `M ${src.x} ${src.y} Q ${src.x + actualArc * 1.6} ${midY} ${tgt.x} ${tgt.y}`,
        midX,
        midY,
      };
    }

    if (isLongJump) {
      const archY = src.y < 0 ? -50 : 50;
      const midX = (src.x + tgt.x) / 2;
      const midY = (src.y + tgt.y) / 2 + archY;

      return {
        path: `M ${src.x} ${src.y} C ${src.x + dx * 0.3} ${src.y + archY * 1.3}, ${src.x + dx * 0.7} ${tgt.y + archY * 1.3}, ${tgt.x} ${tgt.y}`,
        midX,
        midY: midY * 0.95,
      };
    }

    const midX = (src.x + tgt.x) / 2;
    const midY = (src.y + tgt.y) / 2;

    return {
      path: `M ${src.x} ${src.y} C ${src.x + dx * 0.45} ${src.y}, ${src.x + dx * 0.55} ${tgt.y}, ${tgt.x} ${tgt.y}`,
      midX,
      midY,
    };
  };

  return (
    <div className="graph-page">

      {/* HEADER */}
      <div className="graph-header">
        <div>
          <p>INTERACTIVE INVESTIGATION GRAPH · CLEAN INVESTIGATION FLOW</p>
          <h1>Investigation Network Graph</h1>
          <span>
            Structured cross-domain intelligence: Suspects → Communications → Financials → Corporate / Location Fronts
          </span>
        </div>

        <div style={{ display: "flex", gap: "10px", alignItems: "center", flexWrap: "wrap" }}>
          <input
            type="text"
            placeholder="Search entities in graph..."
            value={searchFilter}
            onChange={(e) => setSearchFilter(e.target.value)}
            style={{
              padding: "7px 14px",
              background: "#0f172a",
              border: "1px solid #334155",
              borderRadius: "6px",
              color: "white",
              fontSize: "13px",
              minWidth: "220px",
            }}
          />

          <button
            onClick={handleResetLayout}
            title="Reset layout to clean structured view"
            style={{
              padding: "7px 14px",
              background: "#1e293b",
              border: "1px solid #334155",
              borderRadius: "6px",
              color: "#e2e8f0",
              fontSize: "12px",
              fontWeight: "600",
              cursor: "pointer",
            }}
          >
            ⟲ Reset Clean Layout
          </button>
        </div>
      </div>

      {/* FILTER BAR & STAGE OVERVIEW */}
      <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center", flexWrap: "wrap", gap: "12px", margin: "14px 0" }}>
        <div style={{ display: "flex", gap: "6px", flexWrap: "wrap" }}>
          {["All", "Person", "Phone", "Account", "Organization", "Location", "High Risk"].map((t) => (
            <button
              key={t}
              onClick={() => setFilterType(t)}
              style={{
                padding: "6px 12px",
                borderRadius: "6px",
                fontSize: "12px",
                cursor: "pointer",
                border: "1px solid",
                background: filterType === t ? "#38bdf8" : "#131b26",
                color: filterType === t ? "#0f172a" : "#cbd5e1",
                borderColor: filterType === t ? "#38bdf8" : "#263548",
                fontWeight: filterType === t ? "700" : "500",
                transition: "all 0.15s ease",
              }}
            >
              {t}
            </button>
          ))}
        </div>

        {/* Legend */}
        <div style={{ display: "flex", gap: "14px", fontSize: "12px", color: "#94a3b8", background: "#101622", padding: "6px 14px", borderRadius: "6px", border: "1px solid #1e293b" }}>
          <span><span style={{ color: "#38bdf8" }}>●</span> Person</span>
          <span><span style={{ color: "#4ade80" }}>●</span> Phone</span>
          <span><span style={{ color: "#facc15" }}>●</span> Account</span>
          <span><span style={{ color: "#c084fc" }}>●</span> Organization</span>
          <span><span style={{ color: "#fb923c" }}>●</span> Location</span>
          <span><span style={{ color: "#ef4444" }}>⚠</span> High Risk</span>
        </div>
      </div>

      {/* MAIN GRAPH WORKSPACE */}
      <div className="graph-layout">

        {/* SVG INTERACTIVE GRAPH CANVAS */}
        <div
          className="graph-workspace"
          style={{
            position: "relative",
            overflow: "hidden",
            background: "#080c14",
            border: "1px solid #1e293b",
            borderRadius: "10px",
            minHeight: "580px",
            cursor: draggingNodeId ? "grabbing" : "default",
          }}
          onClick={() => setSelectedEntity(null)}
          onMouseMove={handleMouseMove}
          onMouseUp={handleMouseUp}
        >
          {loading && (
            <div style={{ position: "absolute", top: "14px", left: "14px", fontSize: "12px", color: "#38bdf8", zIndex: 10 }}>
              ⚡ Loading Intelligence Graph...
            </div>
          )}

          {/* Zoom controls */}
          <div style={{ position: "absolute", top: "14px", right: "14px", display: "flex", gap: "6px", zIndex: 10 }}>
            <button
              onClick={(e) => { e.stopPropagation(); setZoomLevel((z) => Math.min(z + 0.15, 1.6)); }}
              style={{ padding: "4px 10px", background: "#16202e", border: "1px solid #334155", borderRadius: "4px", color: "white", cursor: "pointer", fontSize: "13px" }}
              title="Zoom In"
            >
              +
            </button>
            <button
              onClick={(e) => { e.stopPropagation(); setZoomLevel(1); }}
              style={{ padding: "4px 8px", background: "#16202e", border: "1px solid #334155", borderRadius: "4px", color: "#94a3b8", cursor: "pointer", fontSize: "11px" }}
              title="Reset Zoom"
            >
              {Math.round(zoomLevel * 100)}%
            </button>
            <button
              onClick={(e) => { e.stopPropagation(); setZoomLevel((z) => Math.max(z - 0.15, 0.7)); }}
              style={{ padding: "4px 10px", background: "#16202e", border: "1px solid #334155", borderRadius: "4px", color: "white", cursor: "pointer", fontSize: "13px" }}
              title="Zoom Out"
            >
              -
            </button>
          </div>

          <svg
            ref={svgRef}
            width="100%"
            height="100%"
            viewBox="-500 -330 1000 660"
            style={{ width: "100%", height: "100%", minHeight: "580px" }}
          >
            {/* SVG DEFS */}
            <defs>
              <marker
                id="arrowhead-clean"
                markerWidth="8"
                markerHeight="8"
                refX="28"
                refY="4"
                orient="auto"
              >
                <polygon points="0 1, 7 4, 0 7" fill="#475569" />
              </marker>
              <marker
                id="arrowhead-highlight"
                markerWidth="9"
                markerHeight="9"
                refX="28"
                refY="4.5"
                orient="auto"
              >
                <polygon points="0 1, 8 4.5, 0 8" fill="#38bdf8" />
              </marker>
            </defs>

            {/* STAGE LANES / SWIMLANES (PERSON -> PHONE -> ACCOUNT -> DESTINATION) */}
            <g opacity="0.6" style={{ pointerEvents: "none" }}>
              {/* Lane 1: Suspects */}
              <text x="-370" y="-285" fill="#38bdf8" fontSize="11" fontWeight="700" textAnchor="middle" letterSpacing="1px">
                1. SUSPECTS (PERSON)
              </text>
              <line x1="-370" y1="-270" x2="-370" y2="280" stroke="#1e293b" strokeDasharray="3 3" strokeWidth="1" />

              {/* Lane 2: Phones */}
              <text x="-120" y="-285" fill="#4ade80" fontSize="11" fontWeight="700" textAnchor="middle" letterSpacing="1px">
                2. PHONES (CDR)
              </text>
              <line x1="-120" y1="-270" x2="-120" y2="280" stroke="#1e293b" strokeDasharray="3 3" strokeWidth="1" />

              {/* Lane 3: Accounts */}
              <text x="130" y="-285" fill="#facc15" fontSize="11" fontWeight="700" textAnchor="middle" letterSpacing="1px">
                3. BANK ACCOUNTS
              </text>
              <line x1="130" y1="-270" x2="130" y2="280" stroke="#1e293b" strokeDasharray="3 3" strokeWidth="1" />

              {/* Lane 4: Destinations */}
              <text x="370" y="-285" fill="#c084fc" fontSize="11" fontWeight="700" textAnchor="middle" letterSpacing="1px">
                4. ORG / LOCATIONS
              </text>
              <line x1="370" y1="-270" x2="370" y2="280" stroke="#1e293b" strokeDasharray="3 3" strokeWidth="1" />
            </g>

            {/* TRANSFORMED GRAPH GROUP */}
            <g transform={`scale(${zoomLevel})`}>

              {/* CLEAN CURVED LINKS */}
              {filteredLinks.map((link) => {
                const src = nodePos[link.source];
                const tgt = nodePos[link.target];
                if (!src || !tgt) return null;

                const isLinkSelected =
                  selectedEntity &&
                  (selectedEntity.id === link.source || selectedEntity.id === link.target);
                const isDimmed = selectedEntity && !isLinkSelected;

                const { path, midX, midY } = computeLinkPath(src, tgt);

                const labelText = link.label || link.type;
                const badgeWidth = Math.max(labelText.length * 6.5 + 14, 46);

                return (
                  <g
                    key={link.id}
                    opacity={isDimmed ? 0.15 : 1}
                    style={{ transition: "opacity 0.2s ease" }}
                  >
                    {/* Link Path */}
                    <path
                      d={path}
                      fill="none"
                      stroke={isLinkSelected ? "#38bdf8" : "rgba(71, 85, 105, 0.55)"}
                      strokeWidth={isLinkSelected ? "2.5" : "1.6"}
                      strokeDasharray={link.type === "CALLED" ? "4 4" : "none"}
                      markerEnd={isLinkSelected ? "url(#arrowhead-highlight)" : "url(#arrowhead-clean)"}
                    />

                    {/* Non-overlapping Label Badge with Dark Solid Backdrop */}
                    <g transform={`translate(${midX}, ${midY})`}>
                      <rect
                        x={-badgeWidth / 2}
                        y="-9"
                        width={badgeWidth}
                        height="18"
                        rx="5"
                        fill="#0b1019"
                        stroke={isLinkSelected ? "#38bdf8" : "#263548"}
                        strokeWidth={isLinkSelected ? "1.5" : "1"}
                      />
                      <text
                        x="0"
                        y="3"
                        textAnchor="middle"
                        dominantBaseline="central"
                        fill={isLinkSelected ? "#38bdf8" : "#94a3b8"}
                        fontSize="9.5"
                        fontWeight="600"
                        style={{ pointerEvents: "none", userSelect: "none" }}
                      >
                        {labelText}
                      </text>
                    </g>
                  </g>
                );
              })}

              {/* NODES */}
              {filteredNodes.map((node) => {
                const isSelected = selectedEntity?.id === node.id;
                const isConnected = selectedEntity && (isSelected || connectedNodeIds.has(node.id));
                const isDimmed = selectedEntity && !isConnected;

                const color = getNodeColor(node.type);
                const icon = getNodeIcon(node.type);
                const isHighRisk = node.riskLevel === "HIGH";

                const labelWidth = Math.max(node.name.length * 7.5 + 20, 84);

                return (
                  <g
                    key={node.id}
                    transform={`translate(${node.x || 0}, ${node.y || 0})`}
                    onClick={(e) => {
                      e.stopPropagation();
                      handleSelectNode(node);
                    }}
                    onMouseDown={(e) => handleMouseDown(e, node.id)}
                    opacity={isDimmed ? 0.25 : 1}
                    style={{ cursor: "pointer", transition: "opacity 0.2s ease" }}
                  >
                    {/* High Risk pulsing ring */}
                    {isHighRisk && (
                      <circle
                        r="28"
                        fill="none"
                        stroke="#ef4444"
                        strokeWidth="1.8"
                        opacity="0.45"
                        strokeDasharray="4 2"
                      />
                    )}

                    {/* Selected glow ring */}
                    {isSelected && (
                      <circle
                        r="32"
                        fill="none"
                        stroke="#38bdf8"
                        strokeWidth="2.5"
                        opacity="0.9"
                      />
                    )}

                    {/* Node Main Circle */}
                    <circle
                      r="22"
                      fill="#101726"
                      stroke={isSelected ? "#38bdf8" : color}
                      strokeWidth={isSelected ? "3" : "2.2"}
                    />

                    {/* Node Center Icon */}
                    <text
                      textAnchor="middle"
                      dominantBaseline="central"
                      fontSize="14"
                      style={{ pointerEvents: "none", userSelect: "none" }}
                    >
                      {icon}
                    </text>

                    {/* Clear Label Container Pill (Prevents any line overlapping) */}
                    <g transform="translate(0, 27)">
                      <rect
                        x={-labelWidth / 2}
                        y="0"
                        width={labelWidth}
                        height="20"
                        rx="5"
                        fill="#0c121e"
                        stroke={isSelected ? "#38bdf8" : "#243245"}
                        strokeWidth={isSelected ? "1.5" : "1"}
                      />
                      <text
                        x="0"
                        y="14"
                        textAnchor="middle"
                        fill="#f8fafc"
                        fontSize="11"
                        fontWeight="600"
                        style={{ pointerEvents: "none", userSelect: "none" }}
                      >
                        {node.name}
                      </text>
                    </g>

                    {/* Sub-label Type and Risk */}
                    <text
                      y="58"
                      textAnchor="middle"
                      fill={color}
                      fontSize="9"
                      fontWeight="700"
                      letterSpacing="0.4px"
                      style={{ pointerEvents: "none", userSelect: "none" }}
                    >
                      {node.type.toUpperCase()}{isHighRisk ? " · HIGH RISK" : ""}
                    </text>
                  </g>
                );
              })}

            </g>
          </svg>

          {/* Bottom Help Indicator */}
          <div style={{ position: "absolute", bottom: "12px", left: "16px", fontSize: "12px", color: "#64748b", pointerEvents: "none", display: "flex", gap: "16px" }}>
            <span>💡 Click any node to focus & view full intelligence dossier</span>
            <span>🖐 Drag nodes to customize spacing</span>
            <span>⟲ Click canvas background to unselect</span>
          </div>
        </div>

        {/* RIGHT ENTITY INTEL DRAWER (PRESERVED & ENHANCED) */}
        <aside className="entity-panel" style={{ width: "360px" }}>

          {!selectedEntity ? (
            <div className="entity-empty">
              <div className="entity-empty-icon">◎</div>
              <h2>Select an entity</h2>
              <p>
                Click any person, phone number, bank account, or organization in the graph
                to inspect its dossier, risk score, connections, and timeline.
              </p>
            </div>
          ) : (
            <div style={{ padding: "8px" }}>

              {/* ENTITY HEADER */}
              <div className="entity-header">
                <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center", marginBottom: "8px" }}>
                  <span
                    className="entity-type"
                    style={{
                      background: `${getNodeColor(selectedEntity.type)}22`,
                      color: getNodeColor(selectedEntity.type),
                      borderColor: `${getNodeColor(selectedEntity.type)}66`,
                      padding: "3px 8px",
                      borderRadius: "4px",
                      border: "1px solid",
                      fontSize: "11px",
                      fontWeight: "700"
                    }}
                  >
                    {selectedEntity.type}
                  </span>

                  <span style={{
                    fontSize: "11px",
                    fontWeight: "700",
                    padding: "3px 8px",
                    borderRadius: "4px",
                    background: selectedEntity.riskLevel === "HIGH" ? "rgba(239, 68, 68, 0.2)" : "rgba(34, 197, 94, 0.2)",
                    color: selectedEntity.riskLevel === "HIGH" ? "#f87171" : "#4ade80",
                    border: `1px solid ${selectedEntity.riskLevel === "HIGH" ? "#ef4444" : "#22c55e"}`
                  }}>
                    {selectedEntity.riskLevel} RISK
                  </span>
                </div>

                <h2>{selectedEntity.name}</h2>
                <p style={{ fontSize: "12px", color: "#94a3b8" }}>
                  Entity ID: <strong>{selectedEntity.id}</strong> · Detected in CASE-2026-014
                </p>
              </div>

              {/* RISK METER */}
              <div style={{ margin: "14px 0", background: "#0f172a", padding: "12px", borderRadius: "8px", border: "1px solid #1e293b" }}>
                <div style={{ display: "flex", justifyContent: "space-between", fontSize: "11px", marginBottom: "6px" }}>
                  <span style={{ color: "#94a3b8", fontWeight: "600" }}>INVESTIGATION RISK SCORE</span>
                  <strong style={{ color: selectedEntity.riskLevel === "HIGH" ? "#f87171" : "#38bdf8" }}>
                    {selectedEntity.riskScore || 65}%
                  </strong>
                </div>
                <div style={{ height: "6px", background: "#1e293b", borderRadius: "3px", overflow: "hidden" }}>
                  <div style={{
                    width: `${selectedEntity.riskScore || 65}%`,
                    height: "100%",
                    background: selectedEntity.riskLevel === "HIGH" ? "linear-gradient(90deg, #f59e0b, #ef4444)" : "linear-gradient(90deg, #10b981, #38bdf8)"
                  }} />
                </div>
              </div>

              {/* DIRECT CONNECTIONS LIST */}
              <div style={{ marginBottom: "18px" }}>
                <p style={{ fontSize: "12px", fontWeight: "700", color: "#94a3b8", textTransform: "uppercase", margin: "0 0 8px" }}>
                  Direct Connections ({selectedEntity.connectionsCount})
                </p>

                <div style={{ maxHeight: "160px", overflowY: "auto", display: "flex", flexDirection: "column", gap: "6px" }}>
                  {selectedEntity.connectionsList && selectedEntity.connectionsList.map((conn, idx) => (
                    <div
                      key={idx}
                      onClick={() => {
                        const targetNode = graphData.nodes.find((n) => n.id === conn.targetId);
                        if (targetNode) handleSelectNode(targetNode);
                      }}
                      style={{
                        padding: "8px 10px",
                        background: "#0f172a",
                        borderRadius: "6px",
                        border: "1px solid #1e293b",
                        fontSize: "12px",
                        display: "flex",
                        justifyContent: "space-between",
                        alignItems: "center",
                        cursor: "pointer",
                        transition: "background 0.15s ease",
                      }}
                      onMouseEnter={(e) => (e.currentTarget.style.background = "#162235")}
                      onMouseLeave={(e) => (e.currentTarget.style.background = "#0f172a")}
                    >
                      <div>
                        <strong style={{ color: "#f8fafc" }}>{conn.targetName}</strong>
                        <span style={{ display: "block", fontSize: "10px", color: getNodeColor(conn.targetType) }}>
                          {conn.targetType}
                        </span>
                      </div>
                      <span style={{
                        fontSize: "10px",
                        fontWeight: "600",
                        padding: "2px 8px",
                        borderRadius: "4px",
                        background: "#161d2d",
                        color: "#38bdf8",
                        border: "1px solid #334155"
                      }}>
                        {conn.label || conn.type}
                      </span>
                    </div>
                  ))}
                </div>
              </div>

              {/* ACTIVITY TRAIL */}
              <div className="entity-timeline">
                <div className="timeline-heading">
                  <span>CHRONOLOGY</span>
                  <strong>Activity Trail</strong>
                </div>

                {selectedEntity.timeline.map((event, index) => (
                  <div className="entity-event" key={index}>
                    <div className="entity-event-date">
                      <strong>{event.date}</strong>
                      <span>{event.time}</span>
                    </div>

                    <div className="entity-event-marker">
                      <div className="timeline-dot" />
                      {index !== selectedEntity.timeline.length - 1 && <div className="timeline-connector" />}
                    </div>

                    <div className="entity-event-content">
                      <h3>{event.title}</h3>
                      <p>{event.description}</p>
                    </div>
                  </div>
                ))}
              </div>

            </div>
          )}

        </aside>

      </div>

    </div>
  );
}

export default Graph;