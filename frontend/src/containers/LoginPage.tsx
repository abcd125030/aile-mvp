import { FormEvent, useEffect, useState } from 'react'
import { useNavigate } from 'react-router-dom'

import useUserStore from '../stores/useUserStore'

const gradeOptions = ['高一', '高二', '高三']
const textbookOptions = ['人教版A版', '人教版B版', '北师大版']

export default function LoginPage() {
  const navigate = useNavigate()
  const {
    isAuthenticated,
    needsOnboarding,
    isLoading,
    error,
    actions: { login, completeOnboarding },
  } = useUserStore()

  const [phone, setPhone] = useState('13800000001')
  const [smsCode, setSmsCode] = useState('8888')

  const [grade, setGrade] = useState('高二')
  const [textbookVersion, setTextbookVersion] = useState('人教版A版')
  const [targetUniversity, setTargetUniversity] = useState('北京大学')
  const [localError, setLocalError] = useState<string | null>(null)

  useEffect(() => {
    if (isAuthenticated && !needsOnboarding) {
      navigate('/', { replace: true })
    }
  }, [isAuthenticated, needsOnboarding, navigate])

  const handleLogin = async (event: FormEvent<HTMLFormElement>) => {
    event.preventDefault()
    setLocalError(null)

    if (!/^1\d{10}$/.test(phone.trim())) {
      setLocalError('请输入正确的11位手机号')
      return
    }

    if (!smsCode.trim()) {
      setLocalError('请输入验证码')
      return
    }

    try {
      await login(phone.trim(), smsCode.trim())
    } catch {
      // error is already handled in store
    }
  }

  const handleOnboarding = async (event: FormEvent<HTMLFormElement>) => {
    event.preventDefault()
    setLocalError(null)

    if (!targetUniversity.trim()) {
      setLocalError('请填写目标院校')
      return
    }

    try {
      await completeOnboarding({
        grade,
        textbook_version: textbookVersion,
        target_university: targetUniversity.trim(),
      })
      navigate('/', { replace: true })
    } catch {
      // error is already handled in store
    }
  }

  return (
    <div className="min-h-screen bg-slate-50 flex items-center justify-center p-4 aile-page-enter">
      <div className="w-full max-w-md aile-card p-6 space-y-6">
        <div className="text-center space-y-2">
          <h1 className="text-2xl font-bold text-slate-900">艾乐学伴</h1>
          <p className="text-sm text-slate-600">登录后继续你的学习计划</p>
        </div>

        {!needsOnboarding ? (
          <form className="space-y-4" onSubmit={handleLogin}>
            <div>
              <label className="block text-sm text-slate-700 mb-1">手机号</label>
              <input
                className="w-full rounded-lg border border-slate-300 px-3 py-2 outline-none focus:ring-2 focus:ring-indigo-200"
                value={phone}
                onChange={(e) => setPhone(e.target.value)}
                placeholder="请输入手机号"
              />
            </div>
            <div>
              <label className="block text-sm text-slate-700 mb-1">验证码（Demo 固定 8888）</label>
              <input
                className="w-full rounded-lg border border-slate-300 px-3 py-2 outline-none focus:ring-2 focus:ring-indigo-200"
                value={smsCode}
                onChange={(e) => setSmsCode(e.target.value)}
                placeholder="请输入验证码"
              />
            </div>

            {(localError || error) && (
              <p className="text-sm text-red-600">{localError || error}</p>
            )}

            <button
              type="submit"
              disabled={isLoading}
              className="w-full rounded-lg bg-indigo-600 text-white py-2 font-medium disabled:opacity-50"
            >
              {isLoading ? '登录中...' : '登录'}
            </button>
          </form>
        ) : (
          <form className="space-y-4" onSubmit={handleOnboarding}>
            <p className="text-sm text-slate-600">欢迎首次登录，请补充学习画像</p>
            <div>
              <label className="block text-sm text-slate-700 mb-1">年级</label>
              <select
                className="w-full rounded-lg border border-slate-300 px-3 py-2 outline-none focus:ring-2 focus:ring-indigo-200"
                value={grade}
                onChange={(e) => setGrade(e.target.value)}
              >
                {gradeOptions.map((item) => (
                  <option key={item} value={item}>
                    {item}
                  </option>
                ))}
              </select>
            </div>
            <div>
              <label className="block text-sm text-slate-700 mb-1">教材版本</label>
              <select
                className="w-full rounded-lg border border-slate-300 px-3 py-2 outline-none focus:ring-2 focus:ring-indigo-200"
                value={textbookVersion}
                onChange={(e) => setTextbookVersion(e.target.value)}
              >
                {textbookOptions.map((item) => (
                  <option key={item} value={item}>
                    {item}
                  </option>
                ))}
              </select>
            </div>
            <div>
              <label className="block text-sm text-slate-700 mb-1">目标院校</label>
              <input
                className="w-full rounded-lg border border-slate-300 px-3 py-2 outline-none focus:ring-2 focus:ring-indigo-200"
                value={targetUniversity}
                onChange={(e) => setTargetUniversity(e.target.value)}
                placeholder="例如：北京大学"
              />
            </div>
            {(localError || error) && (
              <p className="text-sm text-red-600">{localError || error}</p>
            )}
            <button
              type="submit"
              disabled={isLoading}
              className="w-full rounded-lg bg-indigo-600 text-white py-2 font-medium disabled:opacity-50"
            >
              {isLoading ? '保存中...' : '完成并进入首页'}
            </button>
          </form>
        )}
      </div>
    </div>
  )
}
