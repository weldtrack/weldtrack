import { defineStore } from 'pinia'

export type AdminSection =
  | 'dashboard'
  | 'inventory'
  | 'projects'
  | 'booking'
  | 'users'
  | 'booking-history'
  | 'feedback'
  | 'reports'
  | 'staff'
  | 'staff-attendance'
  | 'staff-tasks'
  | 'staff-contributions'
  | 'staff-feedback'
  | 'staff-create'

const STORAGE_KEY = 'weldtrack-admin-section'

function getInitialSection(): AdminSection {
  if (typeof window === 'undefined') {
    return 'dashboard'
  }
  
  const saved = window.localStorage.getItem(STORAGE_KEY)
  return (saved as AdminSection) || 'dashboard'
}

export const useAdminSectionStore = defineStore('admin-section', {
  state: () => ({
    section: getInitialSection() as AdminSection,
    selectedMaterial: null as null | { id: number; name: string; price: number; requestedQuantity?: number },
  }),
  actions: {
    setSection(section: AdminSection) {
      this.section = section
      if (typeof window !== 'undefined') {
        window.localStorage.setItem(STORAGE_KEY, section)
      }
    },
    setSelectedMaterial(payload: { id: number; name: string; price: number; requestedQuantity?: number }) {
      this.selectedMaterial = payload
    },
    clearSelectedMaterial() {
      this.selectedMaterial = null
    },
  },
})