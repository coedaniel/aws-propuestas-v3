import { create } from 'zustand'
import { devtools, persist } from 'zustand/middleware'
import { ChatStore, Message, ChatSession } from '@/lib/types'

export const useChatStore = create<ChatStore>()(
  devtools(
    persist(
      (set, get) => ({
        // State
        currentSession: null,
        messages: [],
        isLoading: false,
        selectedModel: 'amazon.nova-pro-v1:0',

        // Actions
        setCurrentSession: (session) => {
          set({ 
            currentSession: session,
            messages: session?.messages || []
          })
        },

        addMessage: (message) => {
          const { messages, currentSession } = get()
          const newMessages = [...messages, message]
          
          set({ messages: newMessages })
          
          // Update current session if exists
          if (currentSession) {
            set({
              currentSession: {
                ...currentSession,
                messages: newMessages,
                updatedAt: new Date()
              }
            })
          }
        },

        setMessages: (messages) => {
          set({ messages })
          
          const { currentSession } = get()
          if (currentSession) {
            set({
              currentSession: {
                ...currentSession,
                messages,
                updatedAt: new Date()
              }
            })
          }
        },

        setIsLoading: (loading) => set({ isLoading: loading }),

        setSelectedModel: (modelId) => {
          set({ selectedModel: modelId })
          
          const { currentSession } = get()
          if (currentSession) {
            set({
              currentSession: {
                ...currentSession,
                modelId,
                updatedAt: new Date()
              }
            })
          }
        },

        clearMessages: () => {
          set({ 
            messages: [],
            currentSession: null
          })
        }
      }),
      {
        name: 'chat-store',
        partialize: (state) => ({
          selectedModel: state.selectedModel,
          currentSession: state.currentSession
        })
      }
    ),
    { name: 'ChatStore' }
  )
)
