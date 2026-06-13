import { useState } from "react";
import { BrowserRouter, Routes, Route } from "react-router-dom";
import "./App.css";

function App() {
  <Routes>
    <Route index element={<Home />} />
    <Route path="/dashboard/:analysisId" element={<Dashboard />} />
    <Route path="/History" element={<History />} />
  </Routes>;
}

export default App;
