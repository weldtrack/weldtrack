import { defineStore } from 'pinia'
import axios from 'axios'
import api from '../services/api'

export interface InventoryItem {
  id: string
  name: string
  quantity: number
  unitPrice: number
  supplier: string
  dateAdded: string
  lowStockThreshold: number
}

export type MovementType = 'stock-in' | 'stock-out'

export interface StockMovement {
  id: string
  itemId: string
  itemName: string
  quantity: number
  type: MovementType
  timestamp: string
  rawTimestamp?: string
  bookingId?: number | null
  taskId?: string | null
  teamEmails: string[]
}

type BackendInventoryItem = {
  id: number
  name: string
  quantity: number
  unit_price: number
  supplier?: string | null
  date_added?: string
  low_stock_threshold: number
}

type BackendStockMovement = {
  id: number
  item_id: number
  item_name: string
  quantity: number
  type: MovementType
  timestamp?: string
  booking_id?: number | null
  task_id?: string | null
  team_emails?: string[]
}

function toInventoryItem(item: BackendInventoryItem): InventoryItem {
  return {
    id: String(item.id),
    name: item.name,
    quantity: Number(item.quantity ?? 0),
    unitPrice: Number(item.unit_price ?? 0),
    supplier: item.supplier ?? '',
    dateAdded: item.date_added ?? '',
    lowStockThreshold: Number(item.low_stock_threshold ?? 0),
  }
}

function toStockMovement(movement: BackendStockMovement): StockMovement {
  return {
    id: String(movement.id),
    itemId: String(movement.item_id),
    itemName: movement.item_name,
    quantity: Number(movement.quantity ?? 0),
    type: movement.type,
    rawTimestamp: movement.timestamp ?? '',
    timestamp: movement.timestamp ? new Date(movement.timestamp).toLocaleString('en-PH') : '',
    bookingId: movement.booking_id ?? null,
    taskId: movement.task_id ?? null,
    teamEmails: Array.isArray(movement.team_emails) ? movement.team_emails.filter(Boolean) : [],
  }
}

export const useInventoryStore = defineStore('inventory', {
  state: () => ({
    items: [] as InventoryItem[],
    movements: [] as StockMovement[],
  }),
  actions: {
    async fetchInventory() {
      try {
        const { data } = await api.get<BackendInventoryItem[]>('/inventory')
        this.items = Array.isArray(data) ? data.map(toInventoryItem) : []
        return this.items
      } catch (error) {
        if (axios.isAxiosError(error) && error.response?.status === 404) {
          this.items = []
          return this.items
        }
        throw error
      }
    },

    async fetchMovements(params?: { bookingId?: number; taskId?: string; itemId?: string }) {
      try {
        const { data } = await api.get<BackendStockMovement[]>('/inventory/movements/history', {
          params: {
            booking_id: params?.bookingId,
            task_id: params?.taskId,
            item_id: params?.itemId ? Number(params.itemId) : undefined,
          },
        })
        this.movements = Array.isArray(data) ? data.map(toStockMovement) : []
        return this.movements
      } catch (error) {
        if (axios.isAxiosError(error) && error.response?.status === 404) {
          this.movements = []
          return this.movements
        }
        throw error
      }
    },

    async addItem(payload: Omit<InventoryItem, 'id'>) {
      const { data } = await api.post<BackendInventoryItem>('/inventory', {
        name: payload.name,
        quantity: payload.quantity,
        unit_price: payload.unitPrice,
        supplier: payload.supplier,
        low_stock_threshold: payload.lowStockThreshold,
      })

      const created = toInventoryItem(data)
      this.items.unshift(created)
      return created
    },

    async updateItem(id: string, patch: Partial<InventoryItem>) {
      const { data } = await api.patch<BackendInventoryItem>(`/inventory/${id}`, {
        ...(patch.name !== undefined ? { name: patch.name } : {}),
        ...(patch.quantity !== undefined ? { quantity: patch.quantity } : {}),
        ...(patch.unitPrice !== undefined ? { unit_price: patch.unitPrice } : {}),
        ...(patch.supplier !== undefined ? { supplier: patch.supplier } : {}),
        ...(patch.lowStockThreshold !== undefined ? { low_stock_threshold: patch.lowStockThreshold } : {}),
      })

      const updated = toInventoryItem(data)
      const idx = this.items.findIndex((i) => i.id === id)
      if (idx !== -1) {
        this.items[idx] = updated
      }
      return updated
    },

    async deleteItem(id: string) {
      await api.delete(`/inventory/${id}`)
      this.items = this.items.filter((i) => i.id !== id)
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

    getMovementsForBooking(bookingId: number) {
      return this.movements.filter((m) => m.bookingId === bookingId)
    },

    getMovementsForTask(taskId: string) {
      return this.movements.filter((m) => m.taskId === taskId)
    },
  },
})
