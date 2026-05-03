interface SkeletonBlockProps {
  className?: string
}

export default function SkeletonBlock({ className = '' }: SkeletonBlockProps) {
  return <div className={`aile-skeleton ${className}`} />
}
