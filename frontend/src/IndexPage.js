import React, { useState } from "react";
import "./index.css";

function IndexPage({ setQueryParams }) {
  const [year, setYear] = useState("");
  const [lwrPoints, setLwrPoints] = useState(15);
  const [lwrEfg, setLwrEfg] = useState(40);
  const [lwrGs, setLwrGs] = useState(50);

  const handleSubmit = (e) => {
    e.preventDefault();
    setQueryParams({
      year,
      lwrPoints,
      lwrEfg,
      lwrGs,
    });
  };

  return (
    <div className="index-container">
      <h1>NBA Stats - Input Parameters</h1>
      <form onSubmit={handleSubmit} className="input-form">
        <label>
          Year:
          <input
            type="text"
            value={year}
            onChange={(e) => setYear(e.target.value)}
            required
          />
        </label>
        <label>
          Points Lower Bound:
          <input
            type="number"
            value={lwrPoints}
            onChange={(e) => setLwrPoints(e.target.value)}
          />
        </label>
        <label>
          eFG% Lower Bound:
          <input
            type="number"
            value={lwrEfg}
            onChange={(e) => setLwrEfg(e.target.value)}
          />
        </label>
        <label>
          Games Played Lower Bound:
          <input
            type="number"
            value={lwrGs}
            onChange={(e) => setLwrGs(e.target.value)}
          />
        </label>
        <button type="submit">Submit</button>
      </form>
    </div>
  );
}

// ✅ Make sure to add the default export
export default IndexPage;
