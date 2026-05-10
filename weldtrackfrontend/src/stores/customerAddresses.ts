import { defineStore } from 'pinia'
import api from '../services/api'

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

type BackendCustomerAddress = {
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

function toFrontendAddress(address: BackendCustomerAddress): CustomerAddressItem {
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

function toBackendAddressPayload(payload: Partial<CustomerAddressItem>) {
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

export const useCustomerAddressesStore = defineStore('customer-addresses', {
  state: () => ({
    addresses: [] as CustomerAddressItem[],
  }),
  getters: {
    activeAddress(state): CustomerAddressItem | null {
      return state.addresses.find((address) => address.isActive) || null
    },
  },
  actions: {
    async fetchMyAddresses() {
      const { data } = await api.get('/customer-addresses/me')
      this.addresses = Array.isArray(data)
        ? (data as BackendCustomerAddress[]).map(toFrontendAddress)
        : []
      return this.addresses
    },

    async createAddress(payload: Partial<CustomerAddressItem>) {
      const { data } = await api.post('/customer-addresses', toBackendAddressPayload(payload))
      await this.fetchMyAddresses()
      return toFrontendAddress(data as BackendCustomerAddress)
    },

    async updateAddress(id: number, payload: Partial<CustomerAddressItem>) {
      const { data } = await api.patch(`/customer-addresses/${id}`, toBackendAddressPayload(payload))
      await this.fetchMyAddresses()
      return toFrontendAddress(data as BackendCustomerAddress)
    },

    async activateAddress(id: number) {
      const { data } = await api.post(`/customer-addresses/${id}/activate`)
      await this.fetchMyAddresses()
      return toFrontendAddress(data as BackendCustomerAddress)
    },

    async deleteAddress(id: number) {
      await api.delete(`/customer-addresses/${id}`)
      await this.fetchMyAddresses()
    },
  },
})
