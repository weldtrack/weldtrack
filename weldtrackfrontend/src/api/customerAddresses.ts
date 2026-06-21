import api from './api'
import type { CustomerAddressItem, BackendCustomerAddress } from '../types/customerAddresses'

export function toFrontendAddress(address: BackendCustomerAddress): CustomerAddressItem {
  return {
    id: address.id,
    userId: address.user_id,
    label: address.label,
    country: address.country,
    region: address.region,
    province: address.province,
    municipality: address.municipality,
    barangay: address.barangay,
    house: address.house,
    isActive: address.is_active,
    createdAt: address.created_at,
  }
}

export function toBackendAddressPayload(payload: Partial<CustomerAddressItem>) {
  return {
    ...(payload.label !== undefined ? { label: payload.label } : {}),
    ...(payload.country !== undefined ? { country: payload.country } : {}),
    ...(payload.region !== undefined ? { region: payload.region } : {}),
    ...(payload.province !== undefined ? { province: payload.province } : {}),
    ...(payload.municipality !== undefined ? { municipality: payload.municipality } : {}),
    ...(payload.barangay !== undefined ? { barangay: payload.barangay } : {}),
    ...(payload.house !== undefined ? { house: payload.house } : {}),
    ...(payload.isActive !== undefined ? { is_active: payload.isActive } : {}),
  }
}

export async function fetchMyAddresses() {
  const { data } = await api.get('/customer-addresses/me')
  return Array.isArray(data)
    ? (data as BackendCustomerAddress[]).map(toFrontendAddress)
    : []
}

export async function createAddress(payload: Partial<CustomerAddressItem>) {
  const { data } = await api.post('/customer-addresses', toBackendAddressPayload(payload))
  return toFrontendAddress(data as BackendCustomerAddress)
}

export async function updateAddress(id: number, payload: Partial<CustomerAddressItem>) {
  const { data } = await api.patch(`/customer-addresses/${id}`, toBackendAddressPayload(payload))
  return toFrontendAddress(data as BackendCustomerAddress)
}

export async function activateAddress(id: number) {
  const { data } = await api.post(`/customer-addresses/${id}/activate`)
  return toFrontendAddress(data as BackendCustomerAddress)
}

export async function deleteAddress(id: number) {
  await api.delete(`/customer-addresses/${id}`)
}
