import { defineStore } from 'pinia'

export type AdminSection =
  | 'dashboard'
  | 'inventory'
  | 'projects'
  | 'booking'
  | 'booking-history'
  | 'feedback'
  | 'reports'
  | 'staff'
  | 'staff-attendance'
  | 'staff-tasks'
  | 'staff-contributions'
  | 'staff-feedback'
  | 'staff-create'

export const useAdminSectionStore = defineStore('admin-section', {
  state: () => ({
    section: 'dashboard' as AdminSection,
    selectedMaterial: null as null | { id: number; name: string; price: number; requestedQuantity?: number },
  }),
  actions: {
    setSection(section: AdminSection) {
      this.section = section
    },
    setSelectedMaterial(payload: { id: number; name: string; price: number; requestedQuantity?: number }) {
      this.selectedMaterial = payload
    },
    clearSelectedMaterial() {
      this.selectedMaterial = null
    },
  },
})