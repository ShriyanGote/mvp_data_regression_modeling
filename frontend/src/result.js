import React, { useEffect, useState } from "react";
import "./result.css";

function ResultPage({ queryParams }) {
  const [data, setData] = useState([]);
  const [error, setError] = useState("");

  useEffect(() => {
    const { year, lwrPoints, lwrEfg, lwrGs } = queryParams;

    fetch(
      `/result?year=${year}&lwr_points=${lwrPoints}&lwr_efg=${lwrEfg}&lwr_gs=${lwrGs}`
    )
      .then((response) => response.json())
      .then((result) => {
        if (result.error) {
          setError(result.error);
        } else {
          setData(result);
        }
      })
      .catch(() => setError("Failed to fetch data"));
  }, [queryParams]);

  if (error) {
    return <div className="error-message">Error: {error}</div>;
  }

  return (
    <div className="result-container">
      <h1 className="title">MVP Scores</h1>
      <div className="cards">
        {data.length > 0 ? (
          data.map((item) => (
            <div
              className={`card ${item.MVP ? "mvp-highlight" : ""}`}
              key={item.Player}
            >
              <h2 className="player-name">{item.Player}</h2>
              <p className="mvp-score">MVP Score: {item["MVP Score"]}</p>
            </div>
          ))
        ) : (
          <p>No players matched the criteria.</p>
        )}
      </div>
    </div>
  );
}

export default ResultPage;
