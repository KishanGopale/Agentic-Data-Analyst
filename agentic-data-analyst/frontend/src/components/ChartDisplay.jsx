import React from 'react'

export default function ChartDisplay({ charts }) {
  if (!charts.length) return null

  return (
    <div className="section-card">
      <h2>Generated Charts</h2>
      <div className="section-card-body">
        <div className="chart-grid">
          {charts.map((chart, i) => (
            <img
              key={chart.id || i}
              src={chart.url}
              alt={`Chart ${i + 1}`}
              loading="lazy"
            />
          ))}
        </div>
      </div>
    </div>
  )
}
