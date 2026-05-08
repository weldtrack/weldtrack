import { defineStore } from 'pinia'
import axios from 'axios'
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
  }>
  beforeImages?: string[]
  afterImages?: string[]
}

type BackendMaterial = {
  id?: number
  booking_id?: number
  item_id: string
  name: string
  qty: number
  unit_price: number
  subtotal: number
  is_temp?: boolean
}

type BackendBooking = {
  id: number
  customer_name?: string
  project_type: string
  email?: string
  phone?: string
  created_date?: string
  preferred_date?: string
  schedule_date?: string
  estimated_cost?: number
  material_cost?: number
  total_price?: number
  description?: string
  cancel_reason?: string
  cancelled_by?: 'admin' | 'customer'
  status: BookingStatus
  materials?: BackendMaterial[]
  before_images?: string[]
  after_images?: string[]
}

function toFrontendBooking(booking: BackendBooking): BookingItem {
  return {
    id: booking.id,
    customerName: booking.customer_name,
    projectType: booking.project_type,
    email: booking.email,
    phone: booking.phone,
    createdDate: booking.created_date,
    preferredDate: booking.preferred_date,
    scheduleDate: booking.schedule_date,
    estimatedCost: booking.estimated_cost,
    materialCost: booking.material_cost,
    totalPrice: booking.total_price,
    description: booking.description,
    cancelReason: booking.cancel_reason,
    cancelledBy: booking.cancelled_by,
    status: booking.status,
    materials: Array.isArray(booking.materials)
      ? booking.materials.map((line) => ({
          id: line.id ? String(line.id) : undefined,
          itemId: line.item_id,
          name: line.name,
          qty: line.qty,
          unitPrice: line.unit_price,
          subtotal: line.subtotal,
        }))
      : [],
    beforeImages: booking.before_images || [],
    afterImages: booking.after_images || [],
  }
}

function toBackendMaterial(lines?: BookingItem['materials']) {
  if (!Array.isArray(lines)) return undefined
  return lines.map((line) => ({
    item_id: line.itemId,
    name: line.name,
    qty: line.qty,
    unit_price: line.unitPrice,
    subtotal: line.subtotal,
  }))
}

function toBackendBookingPayload(payload: Partial<BookingItem>) {
  return {
    ...(payload.projectType !== undefined ? { project_type: payload.projectType } : {}),
    ...(payload.customerName !== undefined ? { customer_name: payload.customerName } : {}),
    ...(payload.email !== undefined ? { email: payload.email } : {}),
    ...(payload.phone !== undefined ? { phone: payload.phone } : {}),
    ...(payload.description !== undefined ? { description: payload.description } : {}),
    ...(payload.preferredDate !== undefined ? { preferred_date: payload.preferredDate } : {}),
    ...(payload.scheduleDate !== undefined ? { schedule_date: payload.scheduleDate } : {}),
    ...(payload.estimatedCost !== undefined ? { estimated_cost: payload.estimatedCost } : {}),
    ...(payload.materialCost !== undefined ? { material_cost: payload.materialCost } : {}),
    ...(payload.totalPrice !== undefined ? { total_price: payload.totalPrice } : {}),
    ...(payload.status !== undefined ? { status: payload.status } : {}),
    ...(payload.cancelReason !== undefined ? { cancel_reason: payload.cancelReason } : {}),
    ...(payload.cancelledBy !== undefined ? { cancelled_by: payload.cancelledBy } : {}),
    ...(payload.beforeImages !== undefined ? { before_images: payload.beforeImages } : {}),
    ...(payload.afterImages !== undefined ? { after_images: payload.afterImages } : {}),
    ...(payload.materials !== undefined ? { materials: toBackendMaterial(payload.materials) } : {}),
  }
}

function normalizeBookingsResponse(data: unknown): BookingItem[] | null {
  if (Array.isArray(data)) {
    return (data as BackendBooking[]).map(toFrontendBooking)
  }

  if (data && typeof data === 'object') {
    const maybeData = (data as { data?: unknown }).data
    if (Array.isArray(maybeData)) {
      return (maybeData as BackendBooking[]).map(toFrontendBooking)
    }
  }

  return null
}

export const useBookingsStore = defineStore('bookings', {
  state: () => ({
    bookings: [] as BookingItem[],
  }),
  actions: {
    async fetchBookings(params?: Record<string, any>) {
      try {
        const res = await api.get('/bookings', { params })
        const normalizedBookings = normalizeBookingsResponse(res.data)
        this.bookings = normalizedBookings ?? []
        return this.bookings
      } catch (error) {
        if (axios.isAxiosError(error) && error.response?.status === 404) {
          this.bookings = []
          return this.bookings
        }
        throw error
      }
    },

    async createBooking(payload: Partial<BookingItem>) {
      const res = await api.post('/bookings', toBackendBookingPayload(payload))
      const created = toFrontendBooking(res.data as BackendBooking)
      this.bookings.unshift(created)
      return created
    },

    async getBooking(id: number) {
      const res = await api.get(`/bookings/${id}`)
      const booking = toFrontendBooking(res.data as BackendBooking)
      const idx = this.bookings.findIndex((b) => b.id === id)
      if (idx > -1) this.bookings[idx] = booking
      else this.bookings.unshift(booking)
      return booking
    },

    async updateBooking(id: number, patch: Partial<BookingItem>) {
      const res = await api.patch(`/bookings/${id}`, toBackendBookingPayload(patch))
      const updated = toFrontendBooking(res.data as BackendBooking)
      const idx = this.bookings.findIndex((b) => b.id === id)
      if (idx > -1) this.bookings[idx] = updated
      return updated
    },
  },
})
