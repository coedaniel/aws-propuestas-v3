import { create } from 'zustand'
import { devtools, persist } from 'zustand/middleware'
import { ChatStore, Message, ChatSession } from '@/lib/types'

export const useChatStore = create<ChatStore>()(
  devtools(
    persist(
      (set, get) => ({
        // State
        sessions: [],
        currentSessionId: null,
        isLoading: false,
        selectedModel: 'amazon.nova-pro-v1:0',

        // Computed property getter
        get messages(): Message[] {
          const state = get()
          const currentSession = state.sessions.find(s => s.id === state.currentSessionId)
          return currentSession?.messages || []
        },

        // Actions
        addSession: (session: ChatSession) => {
          set((state) => ({
            sessions: [...state.sessions, session],
            currentSessionId: session.id
          }))
        },

        setCurrentSession: (sessionId: string) => {
          set({ currentSessionId: sessionId })
        },

        addMessage: (message: Message) => {
          const { currentSessionId, sessions } = get()
          if (!currentSessionId) {
            // Si no hay sesión actual, crear una nueva
            const newSession: ChatSession = {
              id: Date.now().toString(),
              name: 'Nueva conversación',
              messages: [message],
              createdAt: new Date().toISOString(),
              updatedAt: new Date().toISOString(),
              modelId: get().selectedModel
            }
            set((state) => ({
              sessions: [...state.sessions, newSession],
              currentSessionId: newSession.id
            }))
            return
          }

          set({
            sessions: sessions.map(session =>
              session.id === currentSessionId
                ? { ...session, messages: [...session.messages, message], updatedAt: new Date().toISOString() }
                : session
            )
          })
        },

        updateMessage: (sessionId: string, messageIndex: number, updates: Partial<Message>) => {
          set((state) => ({
            sessions: state.sessions.map(session =>
              session.id === sessionId
                ? {
                    ...session,
                    messages: session.messages.map((msg, index) =>
                      index === messageIndex ? { ...msg, ...updates } : msg
                    )
                  }
                : session
            )
          }))
        },

        clearCurrentSession: () => {
          const { currentSessionId, sessions } = get()
          if (!currentSessionId) return

          set({
            sessions: sessions.map(session =>
              session.id === currentSessionId
                ? { ...session, messages: [] }
                : session
            )
          })
        },

        setMessages: (messages: Message[]) => {
          const { currentSessionId, sessions } = get()
          if (!currentSessionId) return

          set({
            sessions: sessions.map(session =>
              session.id === currentSessionId
                ? { ...session, messages, updatedAt: new Date().toISOString() }
                : session
            )
          })
        },

        deleteSession: (sessionId: string) => {
          set((state) => ({
            sessions: state.sessions.filter(session => session.id !== sessionId),
            currentSessionId: state.currentSessionId === sessionId ? null : state.currentSessionId
          }))
        },

        setLoading: (loading: boolean) => {
          set({ isLoading: loading })
        },

        setSelectedModel: (modelId: string) => {
          set({ selectedModel: modelId })
        }
      }),
      {
        name: 'chat-store',
        partialize: (state) => ({
          sessions: state.sessions,
          currentSessionId: state.currentSessionId,
          selectedModel: state.selectedModel
        })
      }
    ),
    { name: 'ChatStore' }
  )
)
