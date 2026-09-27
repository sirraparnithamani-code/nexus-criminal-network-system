import { useState } from "react";
import "./Search.css";
import { api } from "../services/api";
import { navigate } from "../App";

function Search() {
  const [query, setQuery] = useState("");
  const [activeCategory, setActiveCategory] = useState("All");
  const [results, setResults] = useState([
    {
      category: "PERSON",
      id: "ENT-001",
      title: "Rahul Kumar",
      description: "Primary suspect connected to 4 phone calls, 2 accounts, and front entity Apex Traders.",
      badge: "HIGH RISK"
    },
    {
      category: "LOCATION",
      id: "ENT-011",
      title: "Hitech City, Hyderabad",
      description: "Identified location for commercial offices and meetings between suspects.",
      badge: "SURVEILLANCE"
    },
    {
      category: "CASE",
      id: "CASE-2026-014",
      title: "CASE-2026-014 · Financial Network Investigation",
      description: "Comprehensive financial fraud & money mule network dossier.",
      badge: "ACTIVE"
    }
  ]);
  const [searching, setSearching] = useState(false);

  const categories = ["All", "People", "Locations", "Organizations", "Evidence", "Cases"];

  const handleSearch = async (e) => {
    if (e) e.preventDefault();
    if (!query.trim()) return;

    setSearching(true);
    try {
      const data = await api.search.query(query, activeCategory);
      setResults(data);
    } catch (err) {
      console.error("Search error:", err);
    } finally {
      setSearching(false);
    }
  };

  const handleCategorySelect = (cat) => {
    setActiveCategory(cat);
    if (query.trim()) {
      api.search.query(query, cat).then((data) => setResults(data));
    }
  };

  const handleResultClick = (res) => {
    if (res.category === "CASE") {
      navigate("/cases");
    } else if (res.category === "EVIDENCE") {
      navigate("/evidence");
    } else {
      navigate("/graph");
    }
  };

  return (
    <div className="search-page">

      <div className="search-header">
        <p>INTELLIGENCE QUERY ENGINE</p>
        <h1>Intelligence Search</h1>
        <span>
          Search across cases, evidence documents, phone numbers, bank accounts, and extracted entities.
        </span>
      </div>

      <form className="search-box" onSubmit={handleSearch}>
        <input
          placeholder="Search suspects, phones (+91...), account numbers (ACC...), locations, or cases..."
          value={query}
          onChange={(e) => setQuery(e.target.value)}
        />
        <button type="submit" disabled={searching}>
          {searching ? "Searching..." : "Search"}
        </button>
      </form>

      <div className="search-filters">
        {categories.map((cat) => (
          <button
            key={cat}
            type="button"
            className={activeCategory === cat ? "filter-active" : ""}
            onClick={() => handleCategorySelect(cat)}
          >
            {cat}
          </button>
        ))}
      </div>

      <div className="search-results">
        {results.length === 0 ? (
          <div style={{ padding: "40px 20px", textAlign: "center", color: "#64748b" }}>
            <p style={{ fontSize: "16px", margin: "0 0 6px" }}>No matching intelligence records found.</p>
            <span style={{ fontSize: "13px" }}>Try searching for "Rahul", "9876543210", "ACC001", "Hitech City", or "CASE".</span>
          </div>
        ) : (
          results.map((item, idx) => (
            <div
              className="result-card"
              key={idx}
              onClick={() => handleResultClick(item)}
              style={{ cursor: "pointer" }}
            >
              <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center", marginBottom: "6px" }}>
                <span>{item.category}</span>
                {item.badge && (
                  <strong style={{
                    fontSize: "11px",
                    padding: "2px 6px",
                    borderRadius: "4px",
                    background: item.badge.includes("HIGH") ? "rgba(239, 68, 68, 0.2)" : "rgba(56, 189, 248, 0.2)",
                    color: item.badge.includes("HIGH") ? "#f87171" : "#38bdf8"
                  }}>
                    {item.badge}
                  </strong>
                )}
              </div>

              <h2>{item.title}</h2>
              <p>{item.description}</p>
            </div>
          ))
        )}
      </div>

    </div>
  );
}

export default Search;