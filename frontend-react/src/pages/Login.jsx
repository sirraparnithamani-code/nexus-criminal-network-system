import { useState } from "react";
import "./Login.css";
import { api } from "../services/api";
import { navigate } from "../App";

function Login() {
  const [username, setUsername] = useState("investigator");
  const [password, setPassword] = useState("password123");
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");

  const handleSubmit = async (e) => {
    e.preventDefault();
    if (!username.trim() || !password.trim()) {
      setError("Please enter your username and password.");
      return;
    }

    setLoading(true);
    setError("");

    try {
      const res = await api.auth.login(username, password);
      if (res.user) {
        localStorage.setItem("nexus_user", JSON.stringify(res.user));
      }
      navigate("/dashboard");
    } catch (err) {
      setError("Authentication failed. Please verify credentials.");
    } finally {
      setLoading(false);
    }
  };

  const handleDemoLogin = () => {
    setUsername("investigator");
    setPassword("password123");
    navigate("/dashboard");
  };

  return (
    <main className="login-page">

      <section className="login-card">

        <div className="brand">
          <div className="brand-mark">N</div>

          <div>
            <h1>NEXUS</h1>
            <p>Investigation Intelligence System</p>
          </div>
        </div>

        <div className="login-heading">
          <p className="login-eyebrow">SECURE INVESTIGATION WORKSPACE</p>
          <h2>Welcome back</h2>
          <p>
            Sign in to access your intelligence workspace and active cases.
          </p>
        </div>

        {error && (
          <div style={{ padding: "10px", background: "rgba(239, 68, 68, 0.15)", border: "1px solid #ef4444", borderRadius: "6px", color: "#fca5a5", fontSize: "13px", marginBottom: "16px" }}>
            {error}
          </div>
        )}

        <form onSubmit={handleSubmit}>

          <div className="form-group">
            <label htmlFor="username">
              Username or Badge ID
            </label>

            <input
              id="username"
              name="username"
              type="text"
              value={username}
              onChange={(e) => setUsername(e.target.value)}
              placeholder="e.g. investigator or NEXUS-047"
              required
            />
          </div>

          <div className="form-group">
            <label htmlFor="password">
              Password / Authorization Token
            </label>

            <input
              id="password"
              name="password"
              type="password"
              value={password}
              onChange={(e) => setPassword(e.target.value)}
              placeholder="Enter your security token"
              required
            />
          </div>

          <div className="form-options">
            <label className="remember">
              <input type="checkbox" defaultChecked />
              <span>Remember session</span>
            </label>

            <button
              type="button"
              className="forgot-password"
              onClick={handleDemoLogin}
              style={{ color: "#38bdf8", background: "none", border: "none", cursor: "pointer", fontSize: "13px" }}
            >
              Use Demo Credentials
            </button>
          </div>

          <button
            type="submit"
            className="sign-in-button"
            disabled={loading}
          >
            {loading ? "Authenticating..." : "Sign In to Workspace"}
          </button>

        </form>

        <p className="login-note">
          Authorized law enforcement & intelligence personnel only · NEXUS v2.0
        </p>

      </section>

      <footer className="login-footer">
        NEXUS · Investigation Intelligence System · Sovereign Crime & Telecom Analytics
      </footer>

    </main>
  );
}

export default Login;