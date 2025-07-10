'use client'

import React, { useState } from 'react'
import { useRouter } from 'next/navigation'
import { Button } from '@/components/ui/button'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { Textarea } from '@/components/ui/textarea'
import ModelSelector from '@/components/ModelSelector'
import { ArrowLeft, Send, Loader2, Building2, Lightbulb } from 'lucide-react'
import { sendArquitectoRequest } from '@/lib/api'
import { AVAILABLE_MODELS } from '@/lib/types'

export default function ArquitectoPage() {
  const router = useRouter()
  const [prompt, setPrompt] = useState('')
  const [response, setResponse] = useState('')
  const [isLoading, setIsLoading] = useState(false)
  const [selectedModel, setSelectedModel] = useState('amazon.nova-pro-v1:0')

  const currentModel = AVAILABLE_MODELS.find(m => m.id === selectedModel) || AVAILABLE_MODELS[0]

  const handleSubmit = async () => {
    if (!prompt.trim() || isLoading) return

    setIsLoading(true)
    setResponse('')

    try {
      const data = await sendArquitectoRequest({
        prompt: prompt.trim(),
        modelId: selectedModel
      })

      setResponse(data.response)
    } catch (error) {
      console.error('Error calling arquitecto:', error)
      setResponse('Lo siento, hubo un error al procesar tu solicitud. Por favor, inténtalo de nuevo.')
    } finally {
      setIsLoading(false)
    }
  }

  const handleKeyPress = (e: React.KeyboardEvent) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault()
      handleSubmit()
    }
  }

  return (
    <div className="min-h-screen bg-gradient-to-br from-blue-50 to-indigo-100 p-4">
      <div className="max-w-4xl mx-auto">
        {/* Header */}
        <div className="flex items-center gap-4 mb-6">
          <Button
            variant="ghost"
            size="sm"
            onClick={() => router.push('/')}
            className="flex items-center gap-2"
          >
            <ArrowLeft className="h-4 w-4" />
            Volver
          </Button>
          <div className="flex items-center gap-2">
            <Building2 className="h-6 w-6 text-blue-600" />
            <h1 className="text-2xl font-bold text-gray-900">Arquitecto AWS</h1>
          </div>
        </div>

        {/* Model Selector */}
        <Card className="mb-6">
          <CardHeader>
            <CardTitle className="flex items-center gap-2">
              <Lightbulb className="h-5 w-5" />
              Configuración del Modelo
            </CardTitle>
          </CardHeader>
          <CardContent>
            <ModelSelector
              selectedModel={selectedModel}
              onModelChange={setSelectedModel}
            />
          </CardContent>
        </Card>

        {/* Input Section */}
        <Card className="mb-6">
          <CardHeader>
            <CardTitle>Arquitecto AWS - Consultor Experto</CardTitle>
            <p className="text-sm text-gray-600">
              El Arquitecto AWS te guiará paso a paso para dimensionar, documentar y entregar una solución profesional completa.
            </p>
          </CardHeader>
          <CardContent className="space-y-4">
            <Textarea
              value={prompt}
              onChange={(e) => setPrompt(e.target.value)}
              onKeyPress={handleKeyPress}
              placeholder="Escribe 'Hola' o 'Iniciar' para comenzar la consultoría..."
              className="min-h-[120px] resize-none"
              disabled={isLoading}
            />
            <div className="flex justify-between items-center">
              <span className="text-sm text-gray-500">
                Presiona Enter para enviar, Shift+Enter para nueva línea
              </span>
              <Button
                onClick={handleSubmit}
                disabled={!prompt.trim() || isLoading}
                className="flex items-center gap-2"
              >
                {isLoading ? (
                  <Loader2 className="h-4 w-4 animate-spin" />
                ) : (
                  <Send className="h-4 w-4" />
                )}
                {isLoading ? 'Consultando...' : 'Iniciar Consultoría'}
              </Button>
            </div>
          </CardContent>
        </Card>

        {/* Response Section */}
        {(response || isLoading) && (
          <Card>
            <CardHeader>
              <CardTitle className="flex items-center gap-2">
                <Building2 className="h-5 w-5" />
                Propuesta de Arquitectura
                <span className="text-sm font-normal text-gray-500">
                  ({currentModel.name})
                </span>
              </CardTitle>
            </CardHeader>
            <CardContent>
              {isLoading ? (
                <div className="flex items-center justify-center py-8">
                  <div className="text-center">
                    <Loader2 className="h-8 w-8 animate-spin mx-auto mb-4 text-blue-600" />
                    <p className="text-gray-600">El Arquitecto AWS está analizando tu proyecto...</p>
                  </div>
                </div>
              ) : (
                <div className="prose max-w-none">
                  <div className="whitespace-pre-wrap text-gray-800 leading-relaxed">
                    {response}
                  </div>
                </div>
              )}
            </CardContent>
          </Card>
        )}

        {/* Examples */}
        {!response && !isLoading && (
          <Card>
            <CardHeader>
              <CardTitle>Ejemplos de Proyectos</CardTitle>
            </CardHeader>
            <CardContent>
              <div className="grid md:grid-cols-2 gap-4">
                <div className="p-4 bg-blue-50 rounded-lg">
                  <h4 className="font-semibold mb-2">E-commerce Escalable</h4>
                  <p className="text-sm text-gray-600">
                    "Necesito una plataforma de e-commerce que maneje 50,000 productos, 10,000 usuarios concurrentes, con pagos, inventario y análisis."
                  </p>
                </div>
                <div className="p-4 bg-green-50 rounded-lg">
                  <h4 className="font-semibold mb-2">API Microservicios</h4>
                  <p className="text-sm text-gray-600">
                    "Quiero migrar mi aplicación monolítica a microservicios con alta disponibilidad y auto-escalado."
                  </p>
                </div>
                <div className="p-4 bg-purple-50 rounded-lg">
                  <h4 className="font-semibold mb-2">Data Analytics</h4>
                  <p className="text-sm text-gray-600">
                    "Necesito procesar 1TB de datos diarios, crear dashboards en tiempo real y machine learning."
                  </p>
                </div>
                <div className="p-4 bg-orange-50 rounded-lg">
                  <h4 className="font-semibold mb-2">App Móvil Backend</h4>
                  <p className="text-sm text-gray-600">
                    "Backend para app móvil con autenticación, notificaciones push, chat en tiempo real y geolocalización."
                  </p>
                </div>
              </div>
            </CardContent>
          </Card>
        )}
      </div>
    </div>
  )
}
