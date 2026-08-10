import { defineStore } from 'pinia'
import type { CustomerAddressItem } from '../types/customerAddresses'
import * as customerAddressService from '../api/customerAddresses'

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
      this.addresses = await customerAddressService.fetchMyAddresses()
      return this.addresses
    },

    async createAddress(payload: Partial<CustomerAddressItem>) {
      const created = await customerAddressService.createAddress(payload)
      await this.fetchMyAddresses()
      return created
    },

    async updateAddress(id: string, payload: Partial<CustomerAddressItem>) {
      const updated = await customerAddressService.updateAddress(id, payload)
      await this.fetchMyAddresses()
      return updated
    },

    async activateAddress(id: string) {
      const activated = await customerAddressService.activateAddress(id)
      await this.fetchMyAddresses()
      return activated
    },

    async deleteAddress(id: string) {
      await customerAddressService.deleteAddress(id)
      await this.fetchMyAddresses()
    },
  },
})
