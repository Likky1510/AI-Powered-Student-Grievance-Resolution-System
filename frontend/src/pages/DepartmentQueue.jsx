import { useEffect, useState } from 'react'
import Layout from '../components/Layout'
import { grievanceApi } from '../api/client'
import { PriorityBadge, StatusBadge } from '../components/Badges'

const STATUS_OPTIONS = [
  'submitted', 'categorized', 'assigned', 'in_progress', 'escalated', 'resolved', 'closed',
]

export default function DepartmentQueue() {
  const [cases, setCases] = useState([])
  const [loading, setLoading] = useState(true)
  const [updatingId, setUpdatingId] = useState(null)
  const [noteDrafts, setNoteDrafts] = useState({})
  const [error, setError] = useState('')

  useEffect(() => {
    loadQueue()
  }, [])

  function loadQueue() {
    setLoading(true)
    grievanceApi.departmentQueue()
      .then(res => setCases(res.data))
      .catch(err => setError(err.response?.data?.detail || 'Could not load queue.'))
      .finally(() => setLoading(false))
  }

  async function handleStatusChange(id, newStatus) {
    setUpdatingId(id)
    try {
      await grievanceApi.updateStatus(id, newStatus, noteDrafts[id] || undefined)
      setNoteDrafts(prev => ({ ...prev, [id]: '' }))
      loadQueue()
    } catch (err) {
      setError(err.response?.data?.detail || 'Could not update status.')
    } finally {
      setUpdatingId(null)
    }
  }

  // Sort: urgent/high priority and longest-waiting cases surface first --
  // this is the "process intelligence" view for staff, not just a raw list.
  const sorted = [...cases].sort((a, b) => {
    const priorityRank = { urgent: 0, high: 1, medium: 2, low: 3 }
    const pa = priorityRank[a.priority] ?? 4
    const pb = priorityRank[b.priority] ?? 4
    if (pa !== pb) return pa - pb
    return new Date(a.created_at) - new Date(b.created_at)
  })

  return (
    <Layout>
      <div className="page-header">
        <div>
          <div className="eyebrow">Active Queue</div>
          <h2>Department Queue</h2>
        </div>
      </div>

      {error && <div className="error-text" style={{marginBottom: 12}}>{error}</div>}
      {loading && <p>Loading…</p>}

      {!loading && sorted.length === 0 && (
        <div className="empty-state">No grievances currently assigned to this department.</div>
      )}

      {!loading && sorted.map(c => (
        <div className="card" key={c.id}>
          <div style={{display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start'}}>
            <div style={{flex: 1}}>
              <div style={{display: 'flex', gap: 10, alignItems: 'center', marginBottom: 6}}>
                <span className="case-id">{c.id.slice(0, 8)}</span>
                <PriorityBadge priority={c.priority} />
                <StatusBadge status={c.status} />
                {c.is_escalated && <span className="badge badge-urgent">escalated</span>}
              </div>
              <p style={{margin: '6px 0', fontSize: '0.92rem'}}>{c.raw_text}</p>
              <p className="helper-text">
                Category: {c.category} · Filed {new Date(c.created_at).toLocaleDateString()}
                {c.priority_reason && <> · {c.priority_reason}</>}
              </p>
            </div>

            <div style={{minWidth: 220, marginLeft: 20}}>
              <div className="field">
                <label>Update status</label>
                <select
                  value={c.status}
                  disabled={updatingId === c.id}
                  onChange={(e) => handleStatusChange(c.id, e.target.value)}
                >
                  {STATUS_OPTIONS.map(s => (
                    <option key={s} value={s}>{s.replace('_', ' ')}</option>
                  ))}
                </select>
              </div>
              <div className="field">
                <input
                  placeholder="Add a note (optional)"
                  value={noteDrafts[c.id] || ''}
                  onChange={(e) => setNoteDrafts(prev => ({ ...prev, [c.id]: e.target.value }))}
                />
              </div>
            </div>
          </div>
        </div>
      ))}
    </Layout>
  )
}
