import { create } from 'zustand'
import { devtools } from 'zustand/middleware'
import { ProjectsStore, ProjectInfo } from '@/lib/types'

export const useProjectsStore = create<ProjectsStore>()(
  devtools(
    (set, get) => ({
      // State
      projects: [],
      isLoading: false,
      currentPage: 1,
      totalPages: 1,

      // Actions
      setProjects: (projects: ProjectInfo[]) => {
        set({ projects })
      },

      addProject: (project: ProjectInfo) => {
        const { projects } = get()
        set({ projects: [project, ...projects] })
      },

      updateProject: (id: string, updates: Partial<ProjectInfo>) => {
        const { projects } = get()
        const updatedProjects = projects.map((project: ProjectInfo) =>
          project.id === id 
            ? { ...project, ...updates, updatedAt: new Date().toISOString() }
            : project
        )
        set({ projects: updatedProjects })
      },

      deleteProject: (id: string) => {
        const { projects } = get()
        set({ projects: projects.filter((project: ProjectInfo) => project.id !== id) })
      },

      setLoading: (loading: boolean) => {
        set({ isLoading: loading })
      },

      setCurrentPage: (page: number) => {
        set({ currentPage: page })
      }
    }),
    { name: 'ProjectsStore' }
  )
)
