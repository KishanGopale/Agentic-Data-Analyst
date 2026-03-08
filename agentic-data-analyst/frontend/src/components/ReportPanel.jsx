import React from 'react'

export default function ReportPanel({ content, filename }) {
  if (!content) return null

  const handleDownload = () => {
    const blob = new Blob([content], { type: 'text/markdown' })
    const url = URL.createObjectURL(blob)
    const a = document.createElement('a')
    a.href = url
    a.download = filename || 'report.md'
    a.click()
    URL.revokeObjectURL(url)
  }

  const handleCopy = () => {
    navigator.clipboard.writeText(content)
  }

  return (
    <div className="section-card">
      <h2>Analysis Report</h2>
      <div className="section-card-body">
        <div className="report-actions">
          <button onClick={handleDownload}>Download Report</button>
          <button onClick={handleCopy}>Copy to Clipboard</button>
        </div>
        <div className="report-content">{content}</div>
      </div>
    </div>
  )
}
