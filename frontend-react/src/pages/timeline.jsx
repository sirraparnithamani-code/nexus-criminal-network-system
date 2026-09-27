import { useState, useEffect } from "react";
import "./Timeline.css";
import { api } from "../services/api";

function Timeline() {
  const [events, setEvents] = useState([]);
  const [categoryFilter, setCategoryFilter] = useState("All");
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    async function loadTimeline() {
      try {
        const data = await api.timeline.get();
        setEvents(data);
      } catch (err) {
        console.error("Failed to load timeline:", err);
      } finally {
        setLoading(false);
      }
    }
    loadTimeline();
  }, []);

  const categories = ["All", "Communication", "Financial Transaction", "Surveillance / Movement", "Official Filing"];

  const filteredEvents = events.filter((evt) => {
    if (categoryFilter === "All") return true;
    return evt.category && evt.category.toLowerCase().includes(categoryFilter.toLowerCase());
  });

  return (
    <div className="timeline-page">

      <div className="timeline-header">
        <div>
          <p>CASE CHRONOLOGY & AUDIT TRAIL</p>
          <h1>Investigation Timeline</h1>
          <span>
            Chronological milestone sequence extracted from communication intercepts, financial transfers, and surveillance records.
          </span>
        </div>
      </div>

      {/* FILTER BUTTONS */}
      <div style={{ display: "flex", gap: "8px", flexWrap: "wrap", margin: "20px 0" }}>
        {categories.map((cat) => (
          <button
            key={cat}
            onClick={() => setCategoryFilter(cat)}
            style={{
              padding: "6px 12px",
              borderRadius: "6px",
              fontSize: "12px",
              fontWeight: "500",
              cursor: "pointer",
              border: "1px solid",
              background: categoryFilter === cat ? "#38bdf8" : "#161d2d",
              color: categoryFilter === cat ? "#0f172a" : "#cbd5e1",
              borderColor: categoryFilter === cat ? "#38bdf8" : "#334155"
            }}
          >
            {cat}
          </button>
        ))}
      </div>

      <div className="timeline">
        {filteredEvents.map((event, index) => (
          <div className="timeline-event" key={event.id || index}>

            <div className="timeline-date">
              <strong>{event.date}</strong>
              <span>{event.time}</span>
            </div>

            <div className="timeline-dot" style={{
              background:
                event.category === "Communication" ? "#4ade80" :
                event.category === "Financial Transaction" ? "#facc15" :
                event.category === "Official Filing" ? "#f87171" : "#38bdf8"
            }} />

            <div className="timeline-content">
              <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center", marginBottom: "4px" }}>
                <span style={{
                  fontSize: "10px",
                  fontWeight: "700",
                  textTransform: "uppercase",
                  padding: "2px 6px",
                  borderRadius: "4px",
                  background:
                    event.category === "Communication" ? "rgba(34, 197, 94, 0.2)" :
                    event.category === "Financial Transaction" ? "rgba(234, 179, 8, 0.2)" : "rgba(56, 189, 248, 0.2)",
                  color:
                    event.category === "Communication" ? "#4ade80" :
                    event.category === "Financial Transaction" ? "#facc15" : "#38bdf8"
                }}>
                  {event.category || "Milestone"}
                </span>

                {event.source_doc && (
                  <span style={{ fontSize: "11px", color: "#64748b" }}>
                    Source: {event.source_doc}
                  </span>
                )}
              </div>

              <h2>{event.title}</h2>
              <p>{event.description}</p>

              {/* INVOLVED ENTITIES */}
              {event.entities && event.entities.length > 0 && (
                <div style={{ display: "flex", flexWrap: "wrap", gap: "6px", marginTop: "8px" }}>
                  {event.entities.map((ent, i) => (
                    <span
                      key={i}
                      style={{
                        fontSize: "11px",
                        padding: "2px 6px",
                        borderRadius: "4px",
                        background: "#0f172a",
                        color: "#94a3b8",
                        border: "1px solid #1e293b"
                      }}
                    >
                      {ent.name || ent}
                    </span>
                  ))}
                </div>
              )}
            </div>

          </div>
        ))}
      </div>

    </div>
  );
}

export default Timeline;