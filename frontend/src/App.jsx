import { Routes, Route } from "react-router-dom";
import "./App.css";
import Home from "./pages/Home";
import Dashboard from "./pages/Dashboard";
import History from "./pages/History";

function App() {
  return (
    <Routes>
      <Route path="/" element={<Home />} />
      <Route path="/dashboard/:analysisId" element={<Dashboard />} />
      <Route path="/history" element={<History />} />
    </Routes>
  );
}

export default App;
