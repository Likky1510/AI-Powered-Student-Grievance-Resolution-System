import { NavLink, useNavigate } from 'react-router-dom'
import { useAuth } from '../api/AuthContext'

export default function Layout({ children }) {
  const { user, logout } = useAuth()
  const navigate = useNavigate()

  function handleLogout() {
    logout()
    navigate('/login')
  }

  return (
    <div className="layout">
      <aside className="sidebar">
        <div className="brand">Grievance Desk</div>
        <div className="brand-sub">Case Tracking System</div>

        <nav>
          {user?.role === 'student' && (
            <>
              <NavLink to="/submit" className={({isActive}) => isActive ? 'active' : ''}>File a Complaint</NavLink>
              <NavLink to="/my-cases" className={({isActive}) => isActive ? 'active' : ''}>My Cases</NavLink>
            </>
          )}
          {(user?.role === 'staff' || user?.role === 'admin') && (
            <NavLink to="/queue" className={({isActive}) => isActive ? 'active' : ''}>Department Queue</NavLink>
          )}
          {user?.role === 'admin' && (
            <NavLink to="/analytics" className={({isActive}) => isActive ? 'active' : ''}>Analytics</NavLink>
          )}
        </nav>

        <div className="user-tag">
          <div>{user?.name}</div>
          <div>{user?.role?.toUpperCase()}</div>
          <a href="#" onClick={handleLogout} style={{color: '#d8dfd9', display: 'block', marginTop: 8}}>
            Sign out
          </a>
        </div>
      </aside>

      <main className="main">{children}</main>
    </div>
  )
}
