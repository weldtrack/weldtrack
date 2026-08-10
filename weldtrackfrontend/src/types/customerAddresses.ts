export interface CustomerAddressItem {
  id: string
  userId: string
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
  id: string
  user_id: string
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
