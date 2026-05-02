import { BrowserRouter, Navigate, Route, Routes } from 'react-router-dom'
import AppLayout from './components/layout/AppLayout'
import HomePage from './containers/HomePage'
import LoginPage from './containers/LoginPage'
import DailyClearancePage from './containers/DailyClearancePage'
import ExecutionPage from './containers/ExecutionPage'
import DiagnosisPage from './containers/DiagnosisPage'
import useUserStore from './stores/useUserStore'

function ProtectedRoute({ children }: { children: JSX.Element }) {
  const isAuthenticated = useUserStore((state) => state.isAuthenticated)
  if (!isAuthenticated) {
    return <Navigate to="/auth/login" replace />
  }
  return children
}

export default function App() {
  return (
    <BrowserRouter>
      <Routes>
        {/* 登录页不使用 AppLayout（无导航栏） */}
        <Route path="/auth/login" element={<LoginPage />} />

        {/* 使用 AppLayout 布局的页面 */}
        <Route element={<AppLayout />}>
          <Route
            path="/"
            element={
              <ProtectedRoute>
                <HomePage />
              </ProtectedRoute>
            }
          />
          <Route
            path="/daily-clearance"
            element={
              <ProtectedRoute>
                <DailyClearancePage />
              </ProtectedRoute>
            }
          />
          <Route
            path="/execution"
            element={
              <ProtectedRoute>
                <ExecutionPage />
              </ProtectedRoute>
            }
          />
          <Route
            path="/diagnosis"
            element={
              <ProtectedRoute>
                <DiagnosisPage />
              </ProtectedRoute>
            }
          />
        </Route>
      </Routes>
    </BrowserRouter>
  )
}
