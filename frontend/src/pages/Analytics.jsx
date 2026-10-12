import { useEffect, useState } from 'react'
import { BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer } from 'recharts'
import Layout from '../components/Layout'
import { analyticsApi } from '../api/client'

export default function Analytics() {
  const [data, setData] = useState(null)
  const [loading, setLoading] = useState(true)
  const [checking, setChecking] = useState(false)
  const [error, setError] = useState('')

  useEffect(() => {
    loadSummary()
  }, [])

  function loadSummary() {
    setLoading(true)
    analyticsApi.summary()
      .then(res => setData(res.data))
      .catch(err => setError(err.response?.data?.detail || 'Could not load analytics.'))
      .finally(() => setLoading(false))
  }

  async function handleEscalationCheck() {
    setChecking(true)
    try {
      const res = await analyticsApi.runEscalationCheck()
      loadSummary()
      alert(`Escalation check complete. ${res.data.escalated_count} case(s) escalated.`)
    } finally {
      setChecking(false)
    }
  }

  if (loading) return <Layout><p>Loading…</p></Layout>
  if (error) return <Layout><div className="error-text">{error}</div></Layout>
  if (!data) return null

  return (
    <Layout>
      <div className="page-header">
        <div>
          <div className="eyebrow">Process Intelligence</div>
          <h2>Analytics</h2>
        </div>
        <button className="btn btn-secondary" onClick={handleEscalationCheck} disabled={checking}>
          {checking ? 'Checking…' : 'Run escalation check'}
        </button>
      </div>

      <div className="grid grid-4" style={{marginBottom: 24}}>
        <div className="card stat-card">
          <div className="stat-value">{data.total_grievances}</div>
          <div className="stat-label">Total Cases</div>
        </div>
        <div className="card stat-card">
          <div className="stat-value">{data.resolved}</div>
          <div className="stat-label">Resolved</div>
        </div>
        <div className="card stat-card">
          <div className="stat-value">{data.pending}</div>
          <div className="stat-label">Pending</div>
        </div>
        <div className="card stat-card">
          <div className="stat-value">{data.escalated}</div>
          <div className="stat-label">Escalated</div>
        </div>
      </div>

      {data.ai_summary && (
        <div className="card" style={{borderLeft: '3px solid var(--accent)', marginBottom: 24}}>
          <div className="eyebrow" style={{marginBottom: 8}}>AI-Generated Insight</div>
          <p style={{margin: 0}}>{data.ai_summary}</p>
        </div>
      )}

      <div className="card" style={{marginBottom: 24}}>
        <h3 style={{marginBottom: 16, fontSize: '1.05rem'}}>Average Resolution Time by Department (hrs)</h3>
        <ResponsiveContainer width="100%" height={260}>
          <BarChart data={data.by_department}>
            <CartesianGrid strokeDasharray="3 3" stroke="var(--line)" />
            <XAxis dataKey="department_name" tick={{ fontSize: 11 }} angle={-15} textAnchor="end" height={70} />
            <YAxis tick={{ fontSize: 11 }} />
            <Tooltip />
            <Bar dataKey="avg_resolution_hours" fill="var(--accent)" radius={[3, 3, 0, 0]} />
          </BarChart>
        </ResponsiveContainer>
      </div>

      <div className="card">
        <h3 style={{marginBottom: 12, fontSize: '1.05rem'}}>Department Breakdown</h3>
        <table>
          <thead>
            <tr>
              <th>Department</th>
              <th>Total</th>
              <th>Resolved</th>
              <th>Avg. resolution (hrs)</th>
              <th>Escalation rate</th>
              <th>SLA breach rate</th>
            </tr>
          </thead>
          <tbody>
            {data.by_department.map((d, i) => (
              <tr key={i}>
                <td>{d.department_name}</td>
                <td>{d.total_grievances}</td>
                <td>{d.resolved_count}</td>
                <td>{d.avg_resolution_hours ?? '—'}</td>
                <td>{(d.escalation_rate * 100).toFixed(0)}%</td>
                <td>{(d.sla_breach_rate * 100).toFixed(0)}%</td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </Layout>
  )
}
