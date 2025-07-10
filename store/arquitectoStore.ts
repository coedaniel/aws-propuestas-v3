import { create } from 'zustand'
import { devtools, persist } from 'zustand/middleware'
import { ArquitectoStore, ProjectInfo, ArquitectoFlow } from '@/lib/types'

export const useArquitectoStore = create<ArquitectoStore>()(
  devtools(
    persist(
      (set, get) => ({
        // State
        currentProject: null,
        flow: null,
        isGeneratingDocuments: false,

        // Actions
        setCurrentProject: (project) => {
          set({ currentProject: project })
        },

        setFlow: (flow) => {
          set({ flow })
        },

        updateProjectInfo: (info) => {
          const { currentProject } = get()
          if (currentProject) {
            const updatedProject = {
              ...currentProject,
              ...info,
              updatedAt: new Date()
            }
            set({ currentProject: updatedProject })
          }
        },

        setIsGeneratingDocuments: (generating) => {
          set({ isGeneratingDocuments: generating })
        },

        completeProject: () => {
          const { currentProject } = get()
          if (currentProject) {
            const completedProject = {
              ...currentProject,
              status: 'COMPLETED' as const,
              completedAt: new Date(),
              updatedAt: new Date()
            }
            set({ currentProject: completedProject })
          }
        }
      }),
      {
        name: 'arquitecto-store',
        partialize: (state) => ({
          currentProject: state.currentProject,
          flow: state.flow
        })
      }
    ),
    { name: 'ArquitectoStore' }
  )
)
