import { useState } from 'react'
import { useNavigate } from 'react-router-dom'
import { useAuth } from '../api/AuthContext'

export default function Login() {
  const [email, setEmail] = useState('')
  const [password, setPassword] = useState('')
  const [error, setError] = useState('')
  const [loading, setLoading] = useState(false)
  const { login } = useAuth()
  const navigate = useNavigate()

  async function handleSubmit(e) {
    e.preventDefault()
    setError('')
    setLoading(true)
    try {
      const user = await login(email, password)
      if (user.role === 'student') navigate('/submit')
      else if (user.role === 'staff') navigate('/queue')
      else navigate('/analytics')
    } catch (err) {
      setError(err.response?.data?.detail || 'Login failed. Check your credentials.')
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="login-screen">
      <div className="login-card">
        <h1>Grievance Desk</h1>
        <div className="sub">Sign in to continue</div>

        <form onSubmit={handleSubmit}>
          <div className="field">
            <label>Email</label>
            <input type="email" value={email} onChange={e => setEmail(e.target.value)} required />
          </div>
          <div className="field">
            <label>Password</label>
            <input type="password" value={password} onChange={e => setPassword(e.target.value)} required />
          </div>
          {error && <div className="error-text">{error}</div>}
          <button className="btn" type="submit" disabled={loading} style={{width: '100%', marginTop: 8}}>
            {loading ? 'Signing in…' : 'Sign in'}
          </button>
        </form>

        <div className="helper-text" style={{marginTop: 20}}>
          Demo accounts (after running the seed script):<br/>
          admin@college.edu / admin123<br/>
          fees.staff@college.edu / staff123<br/>
          student@college.edu / student123
        </div>

        <div style={{marginTop: 20, textAlign: 'center', borderTop: '1px solid var(--line)', paddingTop: 16}}>
          New user? <a href="/register" style={{color: 'var(--accent)', textDecoration: 'none', fontWeight: 500}}>Create an account →</a>
        </div>
      </div>
    </div>
  )
}
