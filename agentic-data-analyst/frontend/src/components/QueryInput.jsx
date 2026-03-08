import React, { useState } from 'react'

const EXAMPLE_QUERIES = [
  'Why did sales drop in March?',
  'Which region has the highest sales?',
  'What are the top 5 products by profit?',
  'Show monthly sales trend for 2024',
  'Compare sales across all regions',
]

export default function QueryInput({ onSubmit, loading }) {
  const [query, setQuery] = useState('')

  const handleSubmit = (e) => {
    e.preventDefault()
    if (query.trim() && !loading) {
      onSubmit(query.trim())
    }
  }

  return (
    <div>
      <form className="query-form" onSubmit={handleSubmit}>
        <input
          type="text"
          value={query}
          onChange={(e) => setQuery(e.target.value)}
          placeholder="Ask a question about your sales data..."
          disabled={loading}
        />
        <button type="submit" disabled={loading || !query.trim()}>
          {loading ? 'Analyzing...' : 'Analyze'}
        </button>
      </form>
      <div style={{ display: 'flex', gap: '0.5rem', marginTop: '0.75rem', flexWrap: 'wrap' }}>
        {EXAMPLE_QUERIES.map((q) => (
          <button
            key={q}
            onClick={() => { setQuery(q); if (!loading) onSubmit(q) }}
            style={{
              padding: '0.35rem 0.75rem',
              border: '1px solid #2a2d3a',
              borderRadius: '20px',
              background: 'transparent',
              color: '#888',
              fontSize: '0.78rem',
              cursor: loading ? 'not-allowed' : 'pointer',
            }}
            disabled={loading}
          >
            {q}
          </button>
        ))}
      </div>
    </div>
  )
}
