export interface CustomerAddressItem {
  id: number
  userId: number
  label: string
  country: string
  region: string
  province: string
  municipality: string
  barangay: string
  house: string
  isActive: boolean
  createdAt?: string
}

export type BackendCustomerAddress = {
  id: number
  user_id: number
  label: string
  country: string
  region: string
  province: string
  municipality: string
  barangay: string
  house: string
  is_active: boolean
  created_at?: string
}
