import { NavLink, Outlet } from 'react-router-dom'
import useUserStore from '../../stores/useUserStore'
import AileAvatar from '../ui/AileAvatar'

export default function AppLayout() {
  const logout = useUserStore((state) => state.actions.logout)

  const linkClass = ({ isActive }: { isActive: boolean }) =>
    `px-3 py-2 rounded-md text-sm font-medium transition-colors ${
      isActive
        ? 'bg-white text-indigo-700'
        : 'text-indigo-100 hover:bg-indigo-500 hover:text-white'
    }`

  return (
    <div className="min-h-screen flex flex-col">
      <nav className="bg-indigo-600 shadow-md">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex items-center justify-between h-14">
            <div className="flex items-center gap-2">
              <AileAvatar size={30} />
              <span className="text-white text-lg font-bold tracking-wide">艾乐学伴</span>
            </div>

            <div className="flex items-center space-x-2">
              <NavLink to="/" className={linkClass} end>
                主界面
              </NavLink>
              <NavLink to="/daily-clearance" className={linkClass}>
                艾乐对话
              </NavLink>
              <NavLink to="/execution" className={linkClass}>
                学习计划
              </NavLink>
              <NavLink to="/diagnosis" className={linkClass}>
                诊断
              </NavLink>
              <button
                onClick={logout}
                className="px-3 py-2 rounded-md text-sm font-medium text-indigo-100 hover:bg-indigo-500 hover:text-white"
              >
                退出
              </button>
            </div>
          </div>
        </div>
      </nav>

      <main className="flex-1 aile-page-enter">
        <Outlet />
      </main>
    </div>
  )
}
