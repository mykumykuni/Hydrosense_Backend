# HydroSense React Frontend — Integration Guide

## Prerequisites

- Node.js 18+
- HydroSense backend running on port 8000 (Daphne)

---

## Step 1 — Create the React project

```powershell
# In a NEW folder (separate from the backend)
npm create vite@latest hydrosense-web -- --template react
cd hydrosense-web
npm install
npm install axios react-router-dom
```

---

## Step 2 — Environment variables

Create a `.env` file in the root of `hydrosense-web/`:

```env
VITE_API_BASE=http://localhost:8000/api
VITE_WS_BASE=ws://localhost:8000/ws/
```

> Vite requires the `VITE_` prefix for env vars to be accessible in the browser.

Also add your frontend's dev port to the backend `.env` so CORS allows it:

```env
# In Hydrosense_Backend/.env
CORS_ALLOWED_ORIGINS=http://localhost:3000,http://localhost:5173
```

Then restart Daphne.

---

## Step 3 — Axios instance (`src/api/axios.js`)

This is the core HTTP client. It automatically attaches the JWT token to every request and silently refreshes it when it expires.

```js
// src/api/axios.js
import axios from "axios";

const api = axios.create({
  baseURL: import.meta.env.VITE_API_BASE,
  headers: { "Content-Type": "application/json" },
});

// Attach access token to every request
api.interceptors.request.use((config) => {
  const token = localStorage.getItem("access");
  if (token) config.headers.Authorization = `Bearer ${token}`;
  return config;
});

// Auto-refresh on 401
api.interceptors.response.use(
  (res) => res,
  async (error) => {
    const original = error.config;
    if (error.response?.status === 401 && !original._retry) {
      original._retry = true;
      try {
        const refresh = localStorage.getItem("refresh");
        const { data } = await axios.post(
          `${import.meta.env.VITE_API_BASE}/users/token/refresh/`,
          { refresh }
        );
        localStorage.setItem("access", data.access);
        original.headers.Authorization = `Bearer ${data.access}`;
        return api(original);
      } catch {
        localStorage.clear();
        window.location.href = "/login";
      }
    }
    return Promise.reject(error);
  }
);

export default api;
```

---

## Step 4 — API service layer (`src/api/services.js`)

One function per endpoint — call these from anywhere in the app.

```js
// src/api/services.js
import api from "./axios";

// --- Auth ---
export const login = (email, password) =>
  api.post("/users/login/", { email, password });

export const register = (email, password) =>
  api.post("/users/register/", { email, password });

export const refreshToken = (refresh) =>
  api.post("/users/token/refresh/", { refresh });

// --- Users ---
export const getProfile = () => api.get("/users/profile/");
export const updateProfile = (data) => api.patch("/users/profile/", data);
export const changePassword = (old_password, new_password) =>
  api.post("/users/change-password/", { old_password, new_password });
export const listUsers = () => api.get("/users/");
export const approveUser = (id) => api.post(`/users/${id}/approve/`);
export const deactivateUser = (id) => api.post(`/users/${id}/deactivate/`);

// --- Sensors ---
export const listDevices = () => api.get("/sensors/");
export const listReadings = (params) => api.get("/sensors/readings/", { params });
export const getThresholds = () => api.get("/sensors/thresholds/");
export const updateThresholds = (data) => api.put("/sensors/thresholds/", data);

// --- Alerts ---
export const listAlerts = (params) => api.get("/alerts/", { params });

// --- Reports ---
export const listReports = () => api.get("/reports/");
export const submitReport = (data) => api.post("/reports/", data);

// --- Shifts ---
export const listShifts = () => api.get("/shifts/");
export const createShift = (note) => api.post("/shifts/", { note });

// --- Audit ---
export const listAuditLogs = () => api.get("/audit/");
```

---

## Step 5 — Auth context (`src/context/AuthContext.jsx`)

Provides `user`, `login`, `logout` to the whole app.

```jsx
// src/context/AuthContext.jsx
import { createContext, useContext, useState, useEffect } from "react";
import { login as apiLogin, getProfile } from "../api/services";

const AuthContext = createContext(null);

export function AuthProvider({ children }) {
  const [user, setUser] = useState(null);
  const [loading, setLoading] = useState(true);

  // On app load — restore session if tokens exist
  useEffect(() => {
    const access = localStorage.getItem("access");
    if (access) {
      getProfile()
        .then(({ data }) => setUser(data))
        .catch(() => localStorage.clear())
        .finally(() => setLoading(false));
    } else {
      setLoading(false);
    }
  }, []);

  const login = async (email, password) => {
    const { data } = await apiLogin(email, password);
    localStorage.setItem("access", data.access);
    localStorage.setItem("refresh", data.refresh);
    const profile = await getProfile();
    setUser(profile.data);
  };

  const logout = () => {
    localStorage.clear();
    setUser(null);
  };

  return (
    <AuthContext.Provider value={{ user, login, logout, loading }}>
      {children}
    </AuthContext.Provider>
  );
}

export const useAuth = () => useContext(AuthContext);
```

---

## Step 6 — WebSocket hook (`src/hooks/useHydroSocket.js`)

```js
// src/hooks/useHydroSocket.js
import { useEffect, useRef } from "react";

export function useHydroSocket({ onReading, onAlertNew, onAlertResolved }) {
  const ws = useRef(null);
  const pingInterval = useRef(null);

  useEffect(() => {
    const token = localStorage.getItem("access");
    if (!token) return;

    ws.current = new WebSocket(`${import.meta.env.VITE_WS_BASE}?token=${token}`);

    ws.current.onopen = () => {
      console.log("[WS] Connected");
      // Keep-alive ping every 30s
      pingInterval.current = setInterval(() => {
        if (ws.current?.readyState === WebSocket.OPEN) {
          ws.current.send(JSON.stringify({ type: "ping" }));
        }
      }, 30000);
    };

    ws.current.onmessage = (event) => {
      const data = JSON.parse(event.data);
      if (data.type === "sensor.reading") onReading?.(data.payload);
      if (data.type === "alert.new") onAlertNew?.(data.payload);
      if (data.type === "alert.resolved") onAlertResolved?.(data.payload);
    };

    ws.current.onclose = () => {
      console.log("[WS] Disconnected");
      clearInterval(pingInterval.current);
    };

    return () => {
      clearInterval(pingInterval.current);
      ws.current?.close();
    };
  }, []);
}
```

---

## Step 7 — Protected route (`src/components/ProtectedRoute.jsx`)

```jsx
// src/components/ProtectedRoute.jsx
import { Navigate } from "react-router-dom";
import { useAuth } from "../context/AuthContext";

export default function ProtectedRoute({ children, adminOnly = false }) {
  const { user, loading } = useAuth();

  if (loading) return <div>Loading...</div>;
  if (!user) return <Navigate to="/login" replace />;
  if (adminOnly && user.role !== "admin") return <Navigate to="/dashboard" replace />;

  return children;
}
```

---

## Step 8 — Login page (`src/pages/Login.jsx`)

```jsx
// src/pages/Login.jsx
import { useState } from "react";
import { useNavigate } from "react-router-dom";
import { useAuth } from "../context/AuthContext";

export default function Login() {
  const { login } = useAuth();
  const navigate = useNavigate();
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [error, setError] = useState("");

  const handleSubmit = async (e) => {
    e.preventDefault();
    setError("");
    try {
      await login(email, password);
      navigate("/dashboard");
    } catch (err) {
      setError(err.response?.data?.detail || "Login failed");
    }
  };

  return (
    <form onSubmit={handleSubmit}>
      <h1>HydroSense</h1>
      {error && <p style={{ color: "red" }}>{error}</p>}
      <input
        type="email"
        placeholder="Email"
        value={email}
        onChange={(e) => setEmail(e.target.value)}
        required
      />
      <input
        type="password"
        placeholder="Password"
        value={password}
        onChange={(e) => setPassword(e.target.value)}
        required
      />
      <button type="submit">Login</button>
    </form>
  );
}
```

---

## Step 9 — Dashboard page (`src/pages/Dashboard.jsx`)

```jsx
// src/pages/Dashboard.jsx
import { useEffect, useState } from "react";
import { listReadings, listAlerts } from "../api/services";
import { useHydroSocket } from "../hooks/useHydroSocket";
import { useAuth } from "../context/AuthContext";

export default function Dashboard() {
  const { user, logout } = useAuth();
  const [latestReading, setLatestReading] = useState(null);
  const [alerts, setAlerts] = useState([]);

  // Load initial data
  useEffect(() => {
    listReadings({ limit: 1 }).then(({ data }) => {
      if (data.results?.length) setLatestReading(data.results[0]);
    });
    listAlerts({ resolved: false }).then(({ data }) => {
      setAlerts(data.results || data);
    });
  }, []);

  // Real-time updates via WebSocket
  useHydroSocket({
    onReading: (payload) => setLatestReading(payload),
    onAlertNew: (payload) => setAlerts((prev) => [payload, ...prev]),
    onAlertResolved: (payload) =>
      setAlerts((prev) => prev.filter((a) => a.uid !== payload.uid)),
  });

  return (
    <div>
      <h1>HydroSense Dashboard</h1>
      <p>Welcome, {user?.email}</p>
      <button onClick={logout}>Logout</button>

      <section>
        <h2>Latest Reading</h2>
        {latestReading ? (
          <ul>
            <li>DO: {latestReading.dissolved_oxygen} mg/L</li>
            <li>pH: {latestReading.ph}</li>
            <li>Temperature: {latestReading.temperature} °C</li>
            <li>Salinity: {latestReading.salinity} ppt</li>
            <li>Severity: {latestReading.severity}</li>
          </ul>
        ) : (
          <p>No readings yet</p>
        )}
      </section>

      <section>
        <h2>Active Alerts ({alerts.length})</h2>
        {alerts.map((a) => (
          <div
            key={a.uid}
            style={{
              borderLeft: `4px solid ${a.severity === "critical" ? "red" : "orange"}`,
              padding: "8px",
              marginBottom: "8px",
            }}
          >
            <strong>[{a.severity.toUpperCase()}]</strong> {a.title} — {a.message}
          </div>
        ))}
      </section>
    </div>
  );
}
```

---

## Step 10 — Wire everything up

**`src/main.jsx`**

```jsx
import React from "react";
import ReactDOM from "react-dom/client";
import { BrowserRouter } from "react-router-dom";
import { AuthProvider } from "./context/AuthContext";
import App from "./App";

ReactDOM.createRoot(document.getElementById("root")).render(
  <BrowserRouter>
    <AuthProvider>
      <App />
    </AuthProvider>
  </BrowserRouter>
);
```

**`src/App.jsx`**

```jsx
import { Routes, Route, Navigate } from "react-router-dom";
import Login from "./pages/Login";
import Dashboard from "./pages/Dashboard";
import ProtectedRoute from "./components/ProtectedRoute";

export default function App() {
  return (
    <Routes>
      <Route path="/login" element={<Login />} />
      <Route
        path="/dashboard"
        element={
          <ProtectedRoute>
            <Dashboard />
          </ProtectedRoute>
        }
      />
      <Route path="*" element={<Navigate to="/dashboard" replace />} />
    </Routes>
  );
}
```

---

## Final folder structure

```
hydrosense-web/
├── .env
├── src/
│   ├── api/
│   │   ├── axios.js              ← HTTP client + auto-refresh interceptors
│   │   └── services.js           ← All API calls
│   ├── context/
│   │   └── AuthContext.jsx       ← Auth state, login, logout
│   ├── hooks/
│   │   └── useHydroSocket.js     ← WebSocket real-time updates
│   ├── components/
│   │   └── ProtectedRoute.jsx    ← Route guard
│   ├── pages/
│   │   ├── Login.jsx
│   │   └── Dashboard.jsx
│   ├── App.jsx
│   └── main.jsx
```

---

## Run it

```powershell
npm run dev
```

Open `http://localhost:5173` and log in with your superuser credentials.

---

## Available API Endpoints Reference

| Method | Endpoint | Auth Required | Description |
|--------|----------|---------------|-------------|
| `POST` | `/api/users/login/` | No | Get JWT access + refresh tokens |
| `POST` | `/api/users/register/` | No | Register new user |
| `POST` | `/api/users/token/refresh/` | No | Refresh access token |
| `GET/PATCH` | `/api/users/profile/` | Yes | Get / update own profile |
| `POST` | `/api/users/change-password/` | Yes | Change password |
| `GET` | `/api/users/` | Admin | List all users |
| `POST` | `/api/users/<id>/approve/` | Admin | Approve a pending user |
| `POST` | `/api/users/<id>/deactivate/` | Admin | Deactivate a user |
| `GET` | `/api/sensors/` | Yes | List sensor devices |
| `GET` | `/api/sensors/readings/` | Yes | List sensor readings |
| `GET/PUT` | `/api/sensors/thresholds/` | Admin | Get / update alert thresholds |
| `GET` | `/api/alerts/` | Yes | List alerts |
| `GET/POST` | `/api/reports/` | Yes | List / submit reports |
| `GET/POST` | `/api/shifts/` | Yes | List / create shift logs |
| `GET` | `/api/audit/` | Admin | View audit log |

## WebSocket Events Reference

Connect: `ws://localhost:8000/ws/?token=<access_token>`

| Event type | Payload fields | Trigger |
|------------|----------------|---------|
| `sensor.reading` | `device_id`, `dissolved_oxygen`, `ph`, `temperature`, `salinity`, `severity`, `timestamp` | New sensor reading received |
| `alert.new` | `uid`, `severity`, `title`, `message` | Alert created |
| `alert.resolved` | `uid` | Alert marked as resolved |

Send `{ "type": "ping" }` every 30s — server replies with `{ "type": "pong" }` to keep the connection alive.
