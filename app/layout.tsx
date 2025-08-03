import type { Metadata } from 'next'
import '@fontsource/geist-sans';
import '@fontsource/geist-mono';

import './globals.css'

export const metadata: Metadata = {
  title: 'v0 App',
  description: 'Created with v0',
  generator: 'v0.dev',
}

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode
}>) {
  return (
    <html lang="en">
      <head>
        <style>{`
          html {
            font-family: 'Geist Sans', sans-serif;
          }

          code, pre {
            font-family: 'Geist Mono', monospace;
          }
        `}</style>
      </head>
      <body>{children}</body>
    </html>
  )
}