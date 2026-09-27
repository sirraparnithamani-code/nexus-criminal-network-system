import { useState, useEffect } from "react";
import Login from "./pages/Login";
import Dashboard from "./pages/dashboard";
import Cases from "./pages/cases";
import Upload from "./pages/upload";
import Search from "./pages/search";
import Investigation from "./pages/investigation";
import Graph from "./pages/graph";
import Evidence from "./pages/Evidence";
import Timeline from "./pages/timeline";
import DashboardLayout from "./layouts/DashboardLayout";

// Custom event for instant client-side route transitions
export const navigate = (path) => {
  window.history.pushState({}, "", path);
  window.dispatchEvent(new CustomEvent("nexus-navigate", { detail: path }));
};

function App() {
  const [currentPath, setCurrentPath] = useState(window.location.pathname || "/");

  useEffect(() => {
    const handlePopState = () => {
      setCurrentPath(window.location.pathname);
    };

    const handleCustomNav = (e) => {
      setCurrentPath(e.detail);
    };

    window.addEventListener("popstate", handlePopState);
    window.addEventListener("nexus-navigate", handleCustomNav);

    return () => {
      window.removeEventListener("popstate", handlePopState);
      window.removeEventListener("nexus-navigate", handleCustomNav);
    };
  }, []);

  const renderPage = () => {
    switch (currentPath) {
      case "/dashboard":
        return <Dashboard />;
      case "/cases":
        return <Cases />;
      case "/upload":
        return <Upload />;
      case "/search":
        return <Search />;
      case "/investigation":
        return <Investigation />;
      case "/graph":
        return <Graph />;
      case "/evidence":
        return <Evidence />;
      case "/timeline":
        return <Timeline />;
      default:
        // Default to login on root, or dashboard if already authenticated
        if (currentPath === "/" || currentPath === "/login") {
          return <Login />;
        }
        return <Dashboard />;
    }
  };

  if (currentPath === "/" || currentPath === "/login") {
    return <Login />;
  }

  return (
    <DashboardLayout currentPath={currentPath}>
      {renderPage()}
    </DashboardLayout>
  );
}

export default App;