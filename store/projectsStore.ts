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
      setProjects: (projects) => {
        set({ projects })
      },

      addProject: (project) => {
        const { projects } = get()
        set({ projects: [project, ...projects] })
      },

      updateProject: (id, updates) => {
        const { projects } = get()
        const updatedProjects = projects.map(project =>
          project.id === id 
            ? { ...project, ...updates, updatedAt: new Date() }
            : project
        )
        set({ projects: updatedProjects })
      },

      setIsLoading: (loading) => {
        set({ isLoading: loading })
      },

      setCurrentPage: (page) => {
        set({ currentPage: page })
      }
    }),
    { name: 'ProjectsStore' }
  )
)
