export type BookingStatus = 'pending' | 'confirmed' | 'in-progress' | 'completed' | 'cancelled'

export interface BookingItem {
  id: string
  customerName?: string
  projectType: string
  email?: string
  phone?: string
  createdDate?: string
  preferredDate?: string
  scheduleDate?: string
  estimatedCost?: number
  estimatedLaborHours?: number
  actualLaborCost?: number
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
  location?: {
    country?: string
    region?: string
    province?: string
    municipality?: string
    barangay?: string
    house?: string
  }
}

export type BackendMaterial = {
  id?: string
  booking_id?: string
  item_id: string
  name: string
  qty: number
  unit_price: number
  subtotal: number
  is_temp?: boolean
}

export type BackendBooking = {
  id: string
  customer_name?: string
  project_type: string
  email?: string
  phone?: string
  created_date?: string
  preferred_date?: string
  schedule_date?: string
  estimated_cost?: number
  estimated_labor_hours?: number
  actual_labor_cost?: number
  material_cost?: number
  total_price?: number
  description?: string
  cancel_reason?: string
  cancelled_by?: 'admin' | 'customer'
  status: BookingStatus
  materials?: BackendMaterial[]
  before_images?: string[]
  after_images?: string[]
  country?: string
  region?: string
  province?: string
  municipality?: string
  barangay?: string
  house?: string
}
