'use client'

import React from 'react'
import Link from 'next/link'
import { Button } from '@/components/ui/button'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'
import { 
  MessageCircle, 
  Building2, 
  FolderOpen, 
  Sparkles, 
  Zap, 
  FileText,
  Database,
  Cloud,
  ArrowRight,
  CheckCircle
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
                <Button size="lg" className="text-lg px-8 py-3">
                  <MessageCircle className="w-5 h-5 mr-2" />
                  Comenzar Chat
                </Button>
              </Link>
              <Link href="/arquitecto">
                <Button size="lg" variant="outline" className="text-lg px-8 py-3">
                  <Building2 className="w-5 h-5 mr-2" />
                  Modo Arquitecto
                </Button>
              </Link>
            </div>
          </div>

          {/* Features Grid */}
          <div className="grid md:grid-cols-2 lg:grid-cols-3 gap-8 mb-16">
            <FeatureCard
              icon={<MessageCircle className="w-8 h-8 text-blue-600" />}
              title="Chat Libre"
              description="Conversa con modelos IA avanzados sobre cualquier tema de AWS. Selecciona entre Nova Pro, Claude Haiku y más."
              features={["Múltiples modelos IA", "Respuestas expertas", "Historial persistente"]}
            />
            <FeatureCard
              icon={<Building2 className="w-8 h-8 text-green-600" />}
              title="Arquitecto AWS"
              description="Entrevista guiada paso a paso que genera automáticamente todos los entregables profesionales."
              features={["Entrevista inteligente", "Documentos automáticos", "Diagramas profesionales"]}
            />
            <FeatureCard
              icon={<FileText className="w-8 h-8 text-purple-600" />}
              title="Entregables Completos"
              description="Genera automáticamente Word, CSV, YAML, diagramas SVG/PNG y guías de calculadora AWS."
              features={["Documentos Word", "Scripts CloudFormation", "Estimaciones de costos"]}
            />
          </div>

          {/* Technology Stack */}
          <div className="bg-white rounded-2xl shadow-lg p-8 mb-16">
            <h2 className="text-3xl font-bold text-center text-gray-900 mb-8">
              Stack Tecnológico Avanzado
            </h2>
            <div className="grid md:grid-cols-2 lg:grid-cols-4 gap-6">
              <TechCard
                icon="⚡"
                title="Next.js 14"
                description="App Router, Server Components"
              />
              <TechCard
                icon="🤖"
                title="Amazon Bedrock"
                description="Nova Pro, Claude, Titan"
              />
              <TechCard
                icon="🗃️"
                title="DynamoDB"
                description="Mensajes y proyectos"
              />
              <TechCard
                icon="☁️"
                title="AWS S3"
                description="Documentos generados"
              />
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

          {/* CTA Section */}
          <div className="bg-gradient-to-r from-blue-600 to-purple-600 rounded-2xl p-8 text-center text-white">
            <h2 className="text-3xl font-bold mb-4">
              ¿Listo para crear tu propuesta AWS?
            </h2>
            <p className="text-xl mb-8 opacity-90">
              Comienza ahora y genera documentos profesionales en minutos
            </p>
            <div className="flex items-center justify-center space-x-4">
              <Link href="/arquitecto">
                <Button size="lg" variant="secondary" className="text-lg px-8 py-3">
                  <Building2 className="w-5 h-5 mr-2" />
                  Iniciar Proyecto
                  <ArrowRight className="w-5 h-5 ml-2" />
                </Button>
              </Link>
            </div>
          </div>
        </div>
      </section>
    </div>
  )
}

interface FeatureCardProps {
  icon: React.ReactNode
  title: string
  description: string
  features: string[]
}

function FeatureCard({ icon, title, description, features }: FeatureCardProps) {
  return (
    <Card className="h-full hover:shadow-lg transition-shadow">
      <CardHeader>
        <div className="mb-4">{icon}</div>
        <CardTitle className="text-xl">{title}</CardTitle>
        <CardDescription className="text-base">{description}</CardDescription>
      </CardHeader>
      <CardContent>
        <ul className="space-y-2">
          {features.map((feature, index) => (
            <li key={index} className="flex items-center text-sm text-gray-600">
              <CheckCircle className="w-4 h-4 text-green-500 mr-2 flex-shrink-0" />
              {feature}
            </li>
          ))}
        </ul>
      </CardContent>
    </Card>
  )
}

interface TechCardProps {
  icon: string
  title: string
  description: string
}

function TechCard({ icon, title, description }: TechCardProps) {
  return (
    <div className="text-center p-4">
      <div className="text-4xl mb-3">{icon}</div>
      <h3 className="font-semibold text-gray-900 mb-2">{title}</h3>
      <p className="text-sm text-gray-600">{description}</p>
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
