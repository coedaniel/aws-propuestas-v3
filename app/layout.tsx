import type { Metadata, Viewport } from 'next'
import { Inter } from 'next/font/google'
import './globals.css'
import { AppLayout } from '@/components/AppLayout'

const inter = Inter({ 
  subsets: ['latin'],
  display: 'swap',
  preload: true
})

export const metadata: Metadata = {
  title: 'AWS Propuestas v3 - Plataforma de Arquitectura Inteligente',
  description: 'Plataforma profesional para generar propuestas arquitectónicas AWS con IA y servicios MCP',
  keywords: ['AWS', 'Bedrock', 'IA', 'Propuestas', 'Arquitectura', 'Cloud', 'MCP'],
  authors: [{ name: 'Daniel' }],
}

export const viewport: Viewport = {
  width: 'device-width',
  initialScale: 1,
}

export default function RootLayout({
  children,
}: {
  children: React.ReactNode
}) {
  return (
    <html lang="es" className="dark">
      <body className={inter.className}>
        <AppLayout>
          {children}
        </AppLayout>
      </body>
    </html>
  )
}
