import React, { useState } from "react";
import { BrowserRouter as Router, Routes, Route } from "react-router-dom";
import IndexPage from "./IndexPage"; // ✅ Ensure correct import
import ResultPage from "./result"; // ✅ Ensure this file exists
import "./index.css";
import "./result.css";

function App() {
  const [queryParams, setQueryParams] = useState({});

  return (
    <Router>
      <Routes>
        <Route path="/" element={<IndexPage setQueryParams={setQueryParams} />} />
        <Route path="/result" element={<ResultPage queryParams={queryParams} />} />
      </Routes>
    </Router>
  );
}

export default App;
