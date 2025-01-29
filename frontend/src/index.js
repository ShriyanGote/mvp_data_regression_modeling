import React from "react";
import ReactDOM from "react-dom/client";
import App from "./App"; // ✅ Ensure correct import
import "./index.css";

// ✅ Use ReactDOM.createRoot for React 18+
const root = ReactDOM.createRoot(document.getElementById("root"));
root.render(
  <React.StrictMode>
    <App />
  </React.StrictMode>
);
