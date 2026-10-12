import { BrowserRouter, Routes, Route, Navigate } from 'react-router-dom'
import { AuthProvider, useAuth } from './api/AuthContext'
import ProtectedRoute from './components/ProtectedRoute'

import Login from './pages/Login'
import Register from './pages/Register'
import SubmitGrievance from './pages/SubmitGrievance'
import MyCases from './pages/MyCases'
import DepartmentQueue from './pages/DepartmentQueue'
import Analytics from './pages/Analytics'

function HomeRedirect() {
  const { user } = useAuth()
  if (!user) return <Navigate to="/login" replace />
  if (user.role === 'student') return <Navigate to="/submit" replace />
  if (user.role === 'staff') return <Navigate to="/queue" replace />
  return <Navigate to="/analytics" replace />
}

export default function App() {
  return (
    <AuthProvider>
      <BrowserRouter>
        <Routes>
          <Route path="/login" element={<Login />} />
          <Route path="/register" element={<Register />} />

          <Route path="/submit" element={
            <ProtectedRoute allowedRoles={['student']}><SubmitGrievance /></ProtectedRoute>
          } />
          <Route path="/my-cases" element={
            <ProtectedRoute allowedRoles={['student']}><MyCases /></ProtectedRoute>
          } />

          <Route path="/queue" element={
            <ProtectedRoute allowedRoles={['staff', 'admin']}><DepartmentQueue /></ProtectedRoute>
          } />

          <Route path="/analytics" element={
            <ProtectedRoute allowedRoles={['admin']}><Analytics /></ProtectedRoute>
          } />

          <Route path="/" element={<HomeRedirect />} />
        </Routes>
      </BrowserRouter>
    </AuthProvider>
  )
}
