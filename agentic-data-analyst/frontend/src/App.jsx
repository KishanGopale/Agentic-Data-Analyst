import React, { useState } from 'react'
import QueryInput from './components/QueryInput'
import AgentLog from './components/AgentLog'
import ChartDisplay from './components/ChartDisplay'
import InsightPanel from './components/InsightPanel'
import ReportPanel from './components/ReportPanel'
import './App.css'

const API_BASE = ''

export default function App() {
  const [result, setResult] = useState(null)
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState('')

  const handleAnalyze = async (question) => {
    setLoading(true)
    setError('')
    setResult(null)

    try {
      const res = await fetch(`${API_BASE}/analyze`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ question }),
      })

      if (!res.ok) {
        const errData = await res.json().catch(() => ({}))
        throw new Error(errData.detail || `Server error: ${res.status}`)
      }

      const data = await res.json()
      if (data.error) {
        setError(data.error)
      }
      setResult(data)
    } catch (err) {
      setError(err.message)
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="app">
      <header className="header">
        <h1>Agentic Data Analyst</h1>
        <p className="subtitle">Multi-Agent AI Data Analysis System</p>
      </header>

      <main className="main">
        <QueryInput onSubmit={handleAnalyze} loading={loading} />

        {error && <div className="error-banner">{error}</div>}

        {loading && (
          <div className="loading">
            <div className="spinner" />
            <p>Agents are analyzing your data...</p>
          </div>
        )}

        {result && (
          <div className="results">
            {result.understanding && (
              <div className="understanding">
                <strong>Understanding:</strong> {result.understanding}
              </div>
            )}

            <AgentLog messages={result.messages || []} />
            <ChartDisplay charts={result.charts || []} />
            <InsightPanel insight={result.insight || ''} />
            <ReportPanel
              content={result.report_content || ''}
              filename={result.report_filename || ''}
            />
          </div>
        )}
      </main>

      <footer className="footer">
        Powered by LangGraph + Gemini + FastAPI
      </footer>
    </div>
  )
}
