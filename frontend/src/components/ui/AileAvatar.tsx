import { useState } from 'react'
import avatarUrl from '../../assets/aile-avatar.svg'

interface AileAvatarProps {
  size?: number
  className?: string
}

export default function AileAvatar({ size = 40, className = '' }: AileAvatarProps) {
  const [hasError, setHasError] = useState(false)

  if (hasError) {
    return (
      <div
        style={{ width: size, height: size }}
        className={`rounded-full bg-indigo-100 text-indigo-700 border border-indigo-200 grid place-items-center text-xs font-semibold ${className}`}
      >
        艾乐
      </div>
    )
  }

  return (
    <img
      src={avatarUrl}
      alt="艾乐头像"
      width={size}
      height={size}
      className={`rounded-full border border-indigo-200 bg-white object-cover ${className}`}
      onError={() => setHasError(true)}
    />
  )
}
