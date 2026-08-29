import { defineStore } from 'pinia'
import axios from 'axios'
import type { InventoryItem, StockMovement } from '../types/inventory'
import * as inventoryService from '../api/inventory'

export const useInventoryStore = defineStore('inventory', {
  state: () => ({
    items: [] as InventoryItem[],
    archivedItems: [] as InventoryItem[],
    movements: [] as StockMovement[],
  }),
  actions: {
    async fetchInventory() {
      try {
        this.items = await inventoryService.fetchInventory()
        return this.items
      } catch (error) {
        if (axios.isAxiosError(error) && error.response?.status === 404) {
          this.items = []
          return this.items
        }
        throw error
      }
    },

    async fetchArchivedInventory() {
      this.archivedItems = await inventoryService.fetchInventory(true)
      return this.archivedItems
    },

    async fetchMovements(params?: { bookingId?: string; taskId?: string; itemId?: string }) {
      try {
        this.movements = await inventoryService.fetchMovements(params)
        return this.movements
      } catch (error) {
        if (axios.isAxiosError(error) && error.response?.status === 404) {
          this.movements = []
          return this.movements
        }
        throw error
      }
    },

    async addItem(payload: Omit<InventoryItem, 'id' | 'isArchived' | 'archivedAt'>) {
      const created = await inventoryService.addItem(payload)
      this.items.unshift(created)
      return created
    },

    async updateItem(id: string, patch: Partial<InventoryItem>) {
      const updated = await inventoryService.updateItem(id, patch)
      const idx = this.items.findIndex((i) => i.id === id)
      if (idx !== -1) {
        this.items[idx] = updated
      }
      return updated
    },

    async archiveItem(id: string) {
      const archived = await inventoryService.archiveItem(id)
      this.items = this.items.filter((i) => i.id !== id)
      this.archivedItems.unshift(archived)
    },

    async restoreItem(id: string) {
      const restored = await inventoryService.restoreItem(id)
      this.archivedItems = this.archivedItems.filter((i) => i.id !== id)
      this.items.unshift(restored)
    },

    async stockIn(itemId: string, qty: number) {
      if (qty <= 0) return
      const item = this.items.find((i) => i.id === itemId)
      if (!item) return
      await this.updateItem(itemId, { quantity: item.quantity + qty })
      await this.fetchMovements()
    },

    async stockOut(itemId: string, qty: number) {
      if (qty <= 0) return
      const item = this.items.find((i) => i.id === itemId)
      if (!item) return
      await this.updateItem(itemId, { quantity: Math.max(0, item.quantity - qty) })
      await this.fetchMovements()
    },

    getMovementsForBooking(bookingId: string) {
      return this.movements.filter((m) => m.bookingId === bookingId)
    },

    getMovementsForTask(taskId: string) {
      return this.movements.filter((m) => m.taskId === taskId)
    },
  },
})
