import React from "react"

type ChartContainerProps = {
  children: React.ReactNode
  className?: string
  config?: Record<string, { label: string; color?: string }>
}

export const ChartContainer: React.FC<ChartContainerProps> = ({ children, className = "", config }) => {
  return (
    <div className={`rounded-md border border-gray-200 bg-white p-4 shadow-sm ${className}`}>
      {children}
    </div>
  )
}