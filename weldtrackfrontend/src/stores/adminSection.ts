import { defineStore } from 'pinia'
import type { AdminSection } from '../types/adminSection'

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
    selectedMaterial: null as null | { id: string; name: string; price: number; requestedQuantity?: number },
    selectedService: null as null | {
      id: string
      name: string
      description?: string | null
      pricing_type?: 'hourly' | 'fixed' | 'hybrid'
      price_fixed?: number
      price_hour: number
      image_url?: string | null
    },
  }),
  actions: {
    setSection(section: AdminSection) {
      this.section = section
      if (typeof window !== 'undefined') {
        window.localStorage.setItem(STORAGE_KEY, section)
      }
    },
    setSelectedMaterial(payload: { id: string; name: string; price: number; requestedQuantity?: number }) {
      this.selectedMaterial = payload
    },
    setSelectedService(payload: {
      id: string
      name: string
      description?: string | null
      pricing_type?: 'hourly' | 'fixed' | 'hybrid'
      price_fixed?: number
      price_hour: number
      image_url?: string | null
    }) {
      this.selectedService = payload
    },
    clearSelectedMaterial() {
      this.selectedMaterial = null
    },
    clearSelectedService() {
      this.selectedService = null
    },
  },
})
