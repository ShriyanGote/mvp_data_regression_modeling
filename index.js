import React, { useState } from "react";
import { BrowserRouter as Router, Routes, Route } from "react-router-dom";
import IndexPage from "./index";
import ResultPage from "./frontend/src/result";
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
