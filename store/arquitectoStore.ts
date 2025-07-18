import { create } from 'zustand'
import { devtools, persist } from 'zustand/middleware'
import { ArquitectoStore, ProjectInfo, ArquitectoFlow } from '@/lib/types'

export const useArquitectoStore = create<ArquitectoStore>()(
  devtools(
    persist(
      (set, get) => ({
        // State
        currentProject: null,
        flow: {
          currentStep: 0,
          totalSteps: 5,
          stepName: 'Inicio',
          isComplete: false,
          canProceed: true
        },
        isGeneratingDocuments: false,

        // Actions
        setCurrentProject: (project: ProjectInfo) => {
          set({ currentProject: project })
        },

        updateFlow: (flow: Partial<ArquitectoFlow>) => {
          set((state) => ({
            flow: { ...state.flow, ...flow }
          }))
        },

        setProjectInfo: (info: Partial<ProjectInfo>) => {
          const { currentProject } = get()
          if (currentProject) {
            const updatedProject = {
              ...currentProject,
              ...info,
              updatedAt: new Date().toISOString()
            }
            set({ currentProject: updatedProject })
          }
        },

        nextStep: () => {
          set((state) => {
            const newStep = Math.min(state.flow.currentStep + 1, state.flow.totalSteps - 1)
            return {
              flow: {
                ...state.flow,
                currentStep: newStep,
                isComplete: newStep === state.flow.totalSteps - 1
              }
            }
          })
        },

        previousStep: () => {
          set((state) => ({
            flow: {
              ...state.flow,
              currentStep: Math.max(state.flow.currentStep - 1, 0)
            }
          }))
        },

        resetFlow: () => {
          set({
            flow: {
              currentStep: 0,
              totalSteps: 5,
              stepName: 'Inicio',
              isComplete: false,
              canProceed: true
            },
            currentProject: null
          })
        },

        completeFlow: () => {
          set((state) => ({
            flow: { ...state.flow, isComplete: true }
          }))
        },

        setGeneratingDocuments: (generating: boolean) => {
          set({ isGeneratingDocuments: generating })
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
