import { useState } from 'react'
import { useNavigate, Link } from 'react-router-dom'
import { useAuth } from '../api/AuthContext'
import { authApi, departmentApi } from '../api/client'

export default function Register() {
  const [name, setName] = useState('')
  const [email, setEmail] = useState('')
  const [password, setPassword] = useState('')
  const [phone, setPhone] = useState('')
  const [role, setRole] = useState('student')
  const [departmentId, setDepartmentId] = useState('')
  const [departments, setDepartments] = useState([])
  const [loading, setLoading] = useState(false)
  const [departments_loading, setDepartmentsLoading] = useState(false)
  const [error, setError] = useState('')
  const { login } = useAuth()
  const navigate = useNavigate()

  // Load departments when staff role is selected
  const handleRoleChange = async (e) => {
    setRole(e.target.value)
    if (e.target.value === 'staff') {
      setDepartmentsLoading(true)
      try {
        const res = await departmentApi.list()
        setDepartments(res.data)
      } catch (err) {
        setError('Could not load departments')
      } finally {
        setDepartmentsLoading(false)
      }
    }
  }

  async function handleSubmit(e) {
    e.preventDefault()
    setError('')
    setLoading(true)

    if (password.length < 6) {
      setError('Password must be at least 6 characters')
      setLoading(false)
      return
    }

    try {
      const payload = {
        name,
        email,
        password,
        role,
        phone: phone || undefined,
      }

      if (role === 'staff') {
        if (!departmentId) {
          setError('Staff must select a department')
          setLoading(false)
          return
        }
        payload.department_id = departmentId
      }

      const res = await authApi.register(payload)
      // Auto-login after registration
      const loginRes = await authApi.login(email, password)
      localStorage.setItem('access_token', loginRes.data.access_token)
      localStorage.setItem('user', JSON.stringify(loginRes.data.user))
      const user = await login(email, password)
      
      if (user.role === 'student') navigate('/submit')
      else if (user.role === 'staff') navigate('/queue')
      else navigate('/analytics')
    } catch (err) {
      setError(err.response?.data?.detail || 'Registration failed. Try another email.')
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="login-screen">
      <div className="login-card" style={{ maxWidth: '450px' }}>
        <h1>Create Account</h1>
        <div className="sub">Sign up to file grievances</div>

        <form onSubmit={handleSubmit}>
          <div className="field">
            <label>Full Name</label>
            <input type="text" value={name} onChange={e => setName(e.target.value)} required />
          </div>

          <div className="field">
            <label>Email</label>
            <input type="email" value={email} onChange={e => setEmail(e.target.value)} required />
          </div>

          <div className="field">
            <label>Password</label>
            <input type="password" value={password} onChange={e => setPassword(e.target.value)} required minLength="6" />
            <div className="helper-text">Min 6 characters</div>
          </div>

          <div className="field">
            <label>Phone (optional)</label>
            <input type="tel" value={phone} onChange={e => setPhone(e.target.value)} />
          </div>

          <div className="field">
            <label>Role</label>
            <select value={role} onChange={handleRoleChange}>
              <option value="student">Student</option>
              <option value="staff">Staff Member</option>
            </select>
          </div>

          {role === 'staff' && (
            <div className="field">
              <label>Department</label>
              {departments_loading ? (
                <div style={{ color: 'var(--ink-soft)', fontSize: '0.9rem' }}>Loading departments...</div>
              ) : (
                <select value={departmentId} onChange={e => setDepartmentId(e.target.value)} required>
                  <option value="">-- Select Department --</option>
                  {departments.map(d => (
                    <option key={d.id} value={d.id}>{d.name}</option>
                  ))}
                </select>
              )}
            </div>
          )}

          {error && <div className="error-text">{error}</div>}

          <button className="btn" type="submit" disabled={loading} style={{ width: '100%', marginTop: 8 }}>
            {loading ? 'Creating account…' : 'Register'}
          </button>
        </form>

        <div style={{ marginTop: 20, textAlign: 'center', borderTop: '1px solid var(--line)', paddingTop: 16 }}>
          Already have an account? <Link to="/login" style={{ color: 'var(--accent)', textDecoration: 'none', fontWeight: 500 }}>Sign in →</Link>
        </div>
      </div>
    </div>
  )
}
