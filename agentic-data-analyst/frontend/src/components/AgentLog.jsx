import React from 'react'

export default function AgentLog({ messages }) {
  if (!messages.length) return null

  return (
    <div className="section-card">
      <h2>Agent Activity Log</h2>
      <div className="section-card-body agent-log">
        {messages.map((msg, i) => {
          const match = msg.match(/^\[(\w+)\]\s(.+)$/)
          return (
            <div key={i} className="msg">
              {match ? (
                <>
                  <span className="agent-name">[{match[1]}]</span> {match[2]}
                </>
              ) : (
                msg
              )}
            </div>
          )
        })}
      </div>
    </div>
  )
}
