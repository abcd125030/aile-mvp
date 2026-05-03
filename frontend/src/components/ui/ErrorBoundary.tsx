import { Component, ErrorInfo, ReactNode } from 'react'
import { Link } from 'react-router-dom'

interface ErrorBoundaryProps {
  children: ReactNode
}

interface ErrorBoundaryState {
  hasError: boolean
}

class ErrorBoundary extends Component<ErrorBoundaryProps, ErrorBoundaryState> {
  public state: ErrorBoundaryState = {
    hasError: false,
  }

  public static getDerivedStateFromError(): ErrorBoundaryState {
    return { hasError: true }
  }

  public componentDidCatch(error: Error, errorInfo: ErrorInfo) {
    console.error('Unhandled React error:', error, errorInfo)
  }

  public render() {
    if (this.state.hasError) {
      return (
        <div className="min-h-screen bg-slate-50 flex items-center justify-center px-4">
          <div className="max-w-md w-full rounded-2xl border border-rose-200 bg-white p-6 text-center">
            <h1 className="text-xl font-semibold text-slate-900">页面出现异常</h1>
            <p className="mt-2 text-sm text-slate-600">我们已自动拦截错误，避免白屏。请返回首页继续使用。</p>
            <div className="mt-4">
              <Link
                to="/"
                className="inline-flex rounded-lg bg-indigo-600 px-4 py-2 text-sm font-medium text-white"
              >
                返回首页
              </Link>
            </div>
          </div>
        </div>
      )
    }

    return this.props.children
  }
}

export default ErrorBoundary
