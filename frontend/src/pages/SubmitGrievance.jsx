import { useState } from 'react'
import { useNavigate } from 'react-router-dom'
import Layout from '../components/Layout'
import { grievanceApi } from '../api/client'
import { PriorityBadge } from '../components/Badges'

export default function SubmitGrievance() {
  const [text, setText] = useState('')
  const [submitting, setSubmitting] = useState(false)
  const [result, setResult] = useState(null)
  const [error, setError] = useState('')
  const navigate = useNavigate()

  async function handleSubmit(e) {
    e.preventDefault()
    setError('')
    setSubmitting(true)
    try {
      const res = await grievanceApi.submit(text)
      setResult(res.data)
      setText('')
    } catch (err) {
      setError(err.response?.data?.detail || 'Could not submit complaint. Please try again.')
    } finally {
      setSubmitting(false)
    }
  }

  return (
    <Layout>
      <div className="page-header">
        <div>
          <div className="eyebrow">New Submission</div>
          <h2>File a Complaint</h2>
        </div>
      </div>

      <div className="card">
        <form onSubmit={handleSubmit}>
          <div className="field">
            <label>Describe your issue</label>
            <textarea
              rows={6}
              value={text}
              onChange={e => setText(e.target.value)}
              placeholder="Describe what happened, when, and where. Be specific -- this helps us route and prioritize your case correctly."
              required
              minLength={10}
            />
          </div>
          {error && <div className="error-text">{error}</div>}
          <button className="btn" type="submit" disabled={submitting}>
            {submitting ? 'Submitting…' : 'Submit complaint'}
          </button>
        </form>
      </div>

      {result && (
        <div className="card" style={{borderColor: 'var(--accent)'}}>
          <div className="eyebrow" style={{marginBottom: 8}}>Submitted</div>
          <p style={{marginTop: 0}}>
            Case <span className="case-id">{result.id.slice(0, 8)}</span> has been logged.
          </p>
          <p>
            Classified as <strong>{result.category}</strong> with priority{' '}
            <PriorityBadge priority={result.priority} />.
          </p>
          {result.classification_reason && (
            <p className="helper-text">{result.classification_reason}</p>
          )}
          <button className="btn btn-secondary" onClick={() => navigate('/my-cases')}>
            View my cases →
          </button>
        </div>
      )}
    </Layout>
  )
}
