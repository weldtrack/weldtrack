import { defineStore } from 'pinia'
import api from '../services/api'

export type BookingStatus = 'pending' | 'confirmed' | 'completed' | 'cancelled'

export interface BookingItem {
  id: number
  customerName?: string
  projectType: string
  email?: string
  phone?: string
  createdDate?: string
  preferredDate?: string
  scheduleDate?: string
  estimatedCost?: number
  materialCost?: number
  totalPrice?: number
  description?: string
  cancelReason?: string
  cancelledBy?: 'admin' | 'customer'
  status: BookingStatus
  materials?: Array<{
    id?: string
    itemId: string
    name: string
    qty: number
    unitPrice: number
    subtotal: number
    isTemp?: boolean
  }>
  beforeImages?: string[]
  afterImages?: string[]
}

function normalizeBookingsResponse(data: unknown): BookingItem[] | null {
  if (Array.isArray(data)) {
    return data as BookingItem[]
  }

  if (data && typeof data === 'object') {
    const maybeData = (data as { data?: unknown }).data
    if (Array.isArray(maybeData)) {
      return maybeData as BookingItem[]
    }
  }

  return null
}

const initialBookings: BookingItem[] = [
  {
    id: 1,
    customerName: 'Maria Santos',
    projectType: 'Steel Railing Installation',
    email: 'maria@example.com',
    phone: '+63 912 345 6789',
    createdDate: '2026-04-28T09:00:00Z',
    preferredDate: '2026-05-06T09:00:00Z',
    scheduleDate: '2026-05-08T09:00:00Z',
    estimatedCost: 24500,
    materialCost: 1200,
    totalPrice: undefined,
    description: 'Steel railing installation for residential staircase',
    status: 'completed',
    materials: [
      { id: 'mat-1', itemId: 'steel-rod', name: 'Steel Rods (12mm)', qty: 10, unitPrice: 120, subtotal: 1200 },
    ],
  },
  {
    id: 2,
    customerName: 'Jose Delgado',
    projectType: 'Gate Fabrication',
    email: 'jose@example.com',
    phone: '+63 917 111 2222',
    createdDate: '2026-04-20T10:30:00Z',
    preferredDate: '2026-04-25T09:00:00Z',
    scheduleDate: '2026-04-26T09:00:00Z',
    estimatedCost: 38000,
    materialCost: 5000,
    totalPrice: undefined,
    description: 'Main entrance gate fabrication',
    status: 'cancelled',
    cancelReason: 'Client postponed project',
  },
  {
    id: 3,
    customerName: 'Lina Mercado',
    projectType: 'Truck Bed Repair',
    email: 'lina@example.com',
    phone: '+63 918 333 4444',
    createdDate: '2026-03-15T08:15:00Z',
    preferredDate: '2026-03-20T09:00:00Z',
    scheduleDate: '2026-03-22T09:00:00Z',
    estimatedCost: 14500,
    materialCost: 1500,
    totalPrice: undefined,
    description: 'Repair and reinforcement of truck bed frame',
    status: 'completed',
    materials: [
      { id: 'mat-3', itemId: 'plates', name: 'Steel Plates', qty: 4, unitPrice: 375, subtotal: 1500 },
    ],
  },
  {
    id: 4,
    customerName: 'Guest User',
    projectType: 'Sample Preview Project',
    email: 'preview@example.com',
    phone: '+63 900 000 0000',
    createdDate: new Date().toISOString(),
    preferredDate: '',
    scheduleDate: '',
    estimatedCost: 8000,
    materialCost: 400,
    totalPrice: undefined,
    description: 'Temporary preview booking',
    status: 'confirmed',
  },
]

export const useBookingsStore = defineStore('bookings', {
  state: () => ({
    bookings: initialBookings as BookingItem[],
  }),
  actions: {
    async fetchBookings(params?: Record<string, any>) {
      try {
        const res = await api.get('/bookings', { params })
        const normalizedBookings = normalizeBookingsResponse(res.data)
        if (normalizedBookings) {
          this.bookings = normalizedBookings
        }
        return this.bookings
      } catch (err) {
        console.warn('fetchBookings failed, using local data', err)
        return this.bookings
      }
    },

    async createBooking(payload: Partial<BookingItem>) {
      try {
        const res = await api.post('/bookings', payload)
        const created = res.data
        this.bookings.unshift(created)
        return created
      } catch (err) {
        console.warn('createBooking failed, creating locally', err)
        const id = Date.now()
        const b: BookingItem = { id, status: 'pending', projectType: payload.projectType || 'unknown', customerName: payload.customerName, email: payload.email, phone: payload.phone, createdDate: new Date().toISOString(), preferredDate: payload.preferredDate || '', estimatedCost: payload.estimatedCost }
        this.bookings.unshift(b)
        return b
      }
    },

    async getBooking(id: number) {
      try {
        const res = await api.get(`/bookings/${id}`)
        return res.data
      } catch (err) {
        console.warn('getBooking failed, falling back to local', err)
        return this.bookings.find((b) => b.id === id) ?? null
      }
    },

    async updateBooking(id: number, patch: Partial<BookingItem>) {
      try {
        const res = await api.patch(`/bookings/${id}`, patch)
        const updated = res.data
        const idx = this.bookings.findIndex((b) => b.id === id)
        if (idx > -1) this.bookings[idx] = updated
        return updated
      } catch (err) {
        console.warn('updateBooking failed, updating locally', err)
        const idx = this.bookings.findIndex((b) => b.id === id)
        if (idx === -1) return null
        this.bookings[idx] = { ...this.bookings[idx], ...patch }
        return this.bookings[idx]
      }
    },
  },
})
