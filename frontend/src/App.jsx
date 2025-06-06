// frontend/src/App.jsx
import React from "react";

import { BrowserRouter as Router, Route, Routes } from "react-router-dom";
import Dashboard from "./pages/Dashboard";
import FileTracker from "./pages/FileTracker";

function App() {
  return (
    <Router>
      <Routes>
        <Route path="/" element={<Dashboard />} />
        <Route path="/files" element={<FileTracker />} />
        {/* Future: TaskDetail, FileTracker, etc */}
      </Routes>
    </Router>
  );
}

export default App;
