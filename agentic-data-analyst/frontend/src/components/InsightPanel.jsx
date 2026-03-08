import React from 'react'

export default function InsightPanel({ insight }) {
  if (!insight) return null

  return (
    <div className="section-card">
      <h2>AI Insights</h2>
      <div className="section-card-body">
        <div className="insight-text">{insight}</div>
      </div>
    </div>
  )
}
