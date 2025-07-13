'use client'

import React from 'react'
import Link from 'next/link'
import { Button } from '@/components/ui/button'
import { 
  MessageCircle, 
  Building2, 
  FolderOpen, 
  Sparkles, 
  Zap, 
  FileText,
  Database,
  Cloud,
  ArrowRight
} from 'lucide-react'

export default function HomePage() {
  return (
    <div className="min-h-screen">
      {/* Header */}
      <header className="border-b bg-white/80 backdrop-blur-sm sticky top-0 z-50">
        <div className="container mx-auto px-4 py-4">
          <div className="flex items-center justify-between">
            <div className="flex items-center space-x-3">
              <div className="w-10 h-10 bg-gradient-to-br from-blue-600 to-purple-600 rounded-lg flex items-center justify-center">
                <Cloud className="w-6 h-6 text-white" />
              </div>
              <div>
                <h1 className="text-xl font-bold text-gray-900">AWS Propuestas v3</h1>
                <p className="text-sm text-gray-600">Sistema Conversacional Profesional</p>
              </div>
            </div>
            <div className="flex items-center space-x-2">
              <Link href="/projects">
                <Button variant="outline" size="sm">
                  <FolderOpen className="w-4 h-4 mr-2" />
                  Proyectos
                </Button>
              </Link>
            </div>
          </div>
        </div>
      </header>

      {/* Hero Section */}
      <section className="py-20 px-4">
        <div className="container mx-auto max-w-6xl">
          <div className="text-center mb-16">
            <div className="inline-flex items-center px-4 py-2 bg-blue-100 text-blue-800 rounded-full text-sm font-medium mb-6">
              <Sparkles className="w-4 h-4 mr-2" />
              Potenciado por Amazon Bedrock
            </div>
            <h1 className="text-5xl font-bold text-gray-900 mb-6">
              Genera Propuestas AWS
              <span className="block text-blue-600">con Inteligencia Artificial</span>
            </h1>
            <p className="text-xl text-gray-600 max-w-3xl mx-auto mb-8">
              Sistema conversacional profesional que combina IA avanzada con expertise en AWS 
              para crear propuestas ejecutivas completas con documentos, diagramas y estimaciones.
            </p>
            <div className="flex items-center justify-center space-x-4">
              <Link href="/chat">
                <Button size="lg" variant="outline" className="text-lg px-8 py-3">
                  <MessageCircle className="w-5 h-5 mr-2" />
                  Chat Libre
                </Button>
              </Link>
              <Link href="/arquitecto">
                <Button size="lg" className="text-lg px-8 py-3 bg-gradient-to-r from-blue-600 to-purple-600 hover:from-blue-700 hover:to-purple-700 shadow-lg">
                  <Building2 className="w-5 h-5 mr-2" />
                  Crear Propuesta AWS
                  <ArrowRight className="w-5 h-5 ml-2" />
                </Button>
              </Link>
            </div>
          </div>

          {/* Process Flow */}
          <div className="text-center mb-16">
            <h2 className="text-3xl font-bold text-gray-900 mb-8">
              Flujo de Trabajo Profesional
            </h2>
            <div className="grid md:grid-cols-4 gap-6">
              <ProcessStep
                number="1"
                title="Conversación"
                description="Inicia chat libre o modo arquitecto guiado"
                icon={<MessageCircle className="w-6 h-6" />}
              />
              <ProcessStep
                number="2"
                title="Análisis IA"
                description="La IA analiza requerimientos y genera soluciones"
                icon={<Zap className="w-6 h-6" />}
              />
              <ProcessStep
                number="3"
                title="Generación"
                description="Crea automáticamente todos los documentos"
                icon={<FileText className="w-6 h-6" />}
              />
              <ProcessStep
                number="4"
                title="Entrega"
                description="Descarga archivos desde S3 y dashboard"
                icon={<Database className="w-6 h-6" />}
              />
            </div>
          </div>
        </div>
      </section>
    </div>
  )
}

interface ProcessStepProps {
  number: string
  title: string
  description: string
  icon: React.ReactNode
}

function ProcessStep({ number, title, description, icon }: ProcessStepProps) {
  return (
    <div className="relative">
      <div className="flex flex-col items-center">
        <div className="w-16 h-16 bg-blue-100 rounded-full flex items-center justify-center mb-4 relative">
          <div className="absolute -top-2 -right-2 w-6 h-6 bg-blue-600 text-white rounded-full flex items-center justify-center text-sm font-bold">
            {number}
          </div>
          {icon}
        </div>
        <h3 className="font-semibold text-gray-900 mb-2">{title}</h3>
        <p className="text-sm text-gray-600 text-center">{description}</p>
      </div>
    </div>
  )
}
