import type { Metadata } from 'next'
import { Inter } from 'next/font/google'
import './globals.css'

const inter = Inter({ subsets: ['latin'] })

export const metadata: Metadata = {
  title: 'AWS Propuestas v3 - Sistema Conversacional Profesional',
  description: 'Sistema conversacional profesional para generar propuestas ejecutivas de soluciones AWS con IA',
  keywords: ['AWS', 'Bedrock', 'IA', 'Propuestas', 'Arquitectura', 'Cloud'],
  authors: [{ name: 'Daniel' }],
  viewport: 'width=device-width, initial-scale=1',
}

export default function RootLayout({
  children,
}: {
  children: React.ReactNode
}) {
  return (
    <html lang="es">
      <body className={inter.className}>
        <div className="min-h-screen bg-gradient-to-br from-slate-50 to-blue-50">
          {children}
        </div>
      </body>
    </html>
  )
}
