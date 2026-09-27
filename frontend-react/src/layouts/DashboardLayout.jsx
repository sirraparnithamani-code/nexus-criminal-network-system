import Sidebar from "../components/Sidebar";

function DashboardLayout({ children, currentPath }) {
  return (
    <div className="dashboard-layout">
      <Sidebar activePath={currentPath} />

      <main className="dashboard-main">
        {children}
      </main>
    </div>
  );
}

export default DashboardLayout;