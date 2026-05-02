import { Link } from 'react-router-dom'

export default function DiagnosisPage() {
  return (
    <div className="min-h-screen flex flex-col items-center justify-center p-8">
      <h1 className="text-3xl font-bold mb-8">诊断页</h1>
      <nav className="flex flex-col gap-3">
        <Link to="/" className="text-blue-600 hover:underline">首页</Link>
        <Link to="/auth/login" className="text-blue-600 hover:underline">登录页</Link>
        <Link to="/daily-clearance" className="text-blue-600 hover:underline">日清页</Link>
        <Link to="/execution" className="text-blue-600 hover:underline">任务执行页</Link>
      </nav>
    </div>
  )
}
