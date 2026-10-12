import { useEffect, useState } from 'react'
import Layout from '../components/Layout'
import { grievanceApi } from '../api/client'
import { PriorityBadge, StatusBadge } from '../components/Badges'

export default function MyCases() {
  const [cases, setCases] = useState([])
  const [loading, setLoading] = useState(true)
  const [selected, setSelected] = useState(null)
  const [history, setHistory] = useState([])

  useEffect(() => {
    grievanceApi.myGrievances().then(res => setCases(res.data)).finally(() => setLoading(false))
  }, [])

  async function viewHistory(g) {
    setSelected(g)
    const res = await grievanceApi.getHistory(g.id)
    setHistory(res.data)
  }

  return (
    <Layout>
      <div className="page-header">
        <div>
          <div className="eyebrow">Tracking</div>
          <h2>My Cases</h2>
        </div>
      </div>

      {loading && <p>Loading…</p>}

      {!loading && cases.length === 0 && (
        <div className="empty-state">
          You haven't filed any complaints yet.
        </div>
      )}

      {!loading && cases.length > 0 && (
        <div style={{display: 'flex', gap: 20}}>
          <div className="card" style={{flex: selected ? 1.4 : 1}}>
            <table>
              <thead>
                <tr>
                  <th>Case ID</th>
                  <th>Category</th>
                  <th>Priority</th>
                  <th>Status</th>
                  <th></th>
                </tr>
              </thead>
              <tbody>
                {cases.map(c => (
                  <tr key={c.id}>
                    <td className="case-id">{c.id.slice(0, 8)}</td>
                    <td>{c.category}</td>
                    <td><PriorityBadge priority={c.priority} /></td>
                    <td><StatusBadge status={c.status} /></td>
                    <td>
                      <a href="#" onClick={(e) => { e.preventDefault(); viewHistory(c) }}>
                        View timeline
                      </a>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>

          {selected && (
            <div className="card" style={{flex: 1}}>
              <div className="eyebrow">Case <span className="case-id">{selected.id.slice(0,8)}</span></div>
              <p style={{fontSize: '0.9rem', color: 'var(--ink-soft)'}}>{selected.raw_text}</p>
              <div className="timeline" style={{marginTop: 16}}>
                {history.map((h, i) => (
                  <div className="timeline-item" key={i}>
                    <div><StatusBadge status={h.status} /></div>
                    {h.note && <div style={{fontSize: '0.85rem', marginTop: 2}}>{h.note}</div>}
                    <div className="ts">{new Date(h.created_at).toLocaleString()}</div>
                  </div>
                ))}
              </div>
            </div>
          )}
        </div>
      )}
    </Layout>
  )
}
