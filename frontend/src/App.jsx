import { Routes, Route, NavLink, useLocation } from "react-router-dom";
import "./App.css";
import Home from "./pages/Home";
import Dashboard from "./pages/Dashboard";
import History from "./pages/History";

function NavBar() {
  const location = useLocation();
  // Hide the top nav on home — it has its own header
  if (location.pathname === "/") return null;

  return (
    <header className="sticky top-0 z-10 bg-white border-b border-gray-200 px-6 py-3 flex items-center justify-between shadow-sm">
      <NavLink
        to="/"
        className="text-lg font-bold text-gray-900 hover:text-blue-600 transition-colors"
      >
        ParticleSight
      </NavLink>
      <nav className="flex items-center gap-6 text-sm">
        <NavLink
          to="/"
          className={({ isActive }) =>
            isActive
              ? "text-blue-600 font-medium"
              : "text-gray-500 hover:text-gray-900 transition-colors"
          }
        >
          Datasets
        </NavLink>
        <NavLink
          to="/history"
          className={({ isActive }) =>
            isActive
              ? "text-blue-600 font-medium"
              : "text-gray-500 hover:text-gray-900 transition-colors"
          }
        >
          History
        </NavLink>
      </nav>
    </header>
  );
}

function App() {
  return (
    <div className="min-h-screen flex flex-col bg-gray-50">
      <NavBar />
      <main className="flex-1">
        <Routes>
          <Route path="/" element={<Home />} />
          <Route path="/dashboard/:analysisId" element={<Dashboard />} />
          <Route path="/history" element={<History />} />
        </Routes>
      </main>
    </div>
  );
}

export default App;
