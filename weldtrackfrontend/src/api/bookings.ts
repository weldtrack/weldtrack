import api from './api'
import type { BookingItem, BackendBooking } from '../types/bookings'

export function toFrontendBooking(booking: BackendBooking): BookingItem {
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
    location: {
      country: booking.country ?? undefined,
      region: booking.region ?? undefined,
      province: booking.province ?? undefined,
      municipality: booking.municipality ?? undefined,
      barangay: booking.barangay ?? undefined,
      house: booking.house ?? undefined,
    },
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

export function toBackendBookingPayload(payload: Partial<BookingItem>) {
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
    ...(payload.location !== undefined
      ? {
          country: payload.location.country,
          region: payload.location.region,
          province: payload.location.province,
          municipality: payload.location.municipality,
          barangay: payload.location.barangay,
          house: payload.location.house,
        }
      : {}),
  }
}

export function normalizeBookingsResponse(data: unknown): BookingItem[] | null {
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

export async function fetchBookings(params?: Record<string, any>) {
  const res = await api.get('/bookings', { params })
  return normalizeBookingsResponse(res.data)
}

export async function createBooking(payload: Partial<BookingItem>) {
  const res = await api.post('/bookings', toBackendBookingPayload(payload))
  return toFrontendBooking(res.data as BackendBooking)
}

export async function getBooking(id: string) {
  const res = await api.get(`/bookings/${id}`)
  return toFrontendBooking(res.data as BackendBooking)
}

export async function updateBooking(id: string, patch: Partial<BookingItem>) {
  const res = await api.patch(`/bookings/${id}`, toBackendBookingPayload(patch))
  return toFrontendBooking(res.data as BackendBooking)
}
