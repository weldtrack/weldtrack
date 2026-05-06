import { defineStore } from 'pinia'

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
  bookingId?: number | null
  taskId?: string | null
}

const initialInventory: InventoryItem[] = [
  { id: '1', name: 'Steel Rods (12mm)', quantity: 150, unitPrice: 350, supplier: 'Metro Steel Corp', dateAdded: '2026-03-15', lowStockThreshold: 20 },
  { id: '2', name: 'Welding Electrodes E6013', quantity: 8, unitPrice: 450, supplier: 'Weld Pro Supplies', dateAdded: '2026-03-20', lowStockThreshold: 10 },
  { id: '3', name: 'MIG Welding Wire', quantity: 45, unitPrice: 1200, supplier: 'Industrial Metals Inc', dateAdded: '2026-03-10', lowStockThreshold: 15 },
  { id: '4', name: 'Metal Sheets (4x8)', quantity: 25, unitPrice: 2800, supplier: 'Manila Metal Traders', dateAdded: '2026-03-18', lowStockThreshold: 10 },
  { id: '5', name: 'Angle Bar (2x2)', quantity: 60, unitPrice: 520, supplier: 'Metro Steel Corp', dateAdded: '2026-03-22', lowStockThreshold: 20 },
  { id: '6', name: 'Square Tubing', quantity: 5, unitPrice: 680, supplier: 'Industrial Metals Inc', dateAdded: '2026-03-25', lowStockThreshold: 10 },
  { id: '7', name: 'Cutting Discs', quantity: 120, unitPrice: 85, supplier: 'Tool Haven PH', dateAdded: '2026-03-12', lowStockThreshold: 30 },
  { id: '8', name: 'Grinding Wheels', quantity: 95, unitPrice: 125, supplier: 'Tool Haven PH', dateAdded: '2026-03-14', lowStockThreshold: 25 },
]

export const useInventoryStore = defineStore('inventory', {
  state: () => ({
    items: initialInventory as InventoryItem[],
    movements: [] as StockMovement[],
  }),
  actions: {
    addItem(payload: Omit<InventoryItem, 'id'>) {
      const id = `${Date.now()}-${Math.random().toString(36).slice(2, 8)}`
      const item: InventoryItem = { id, ...payload }
      this.items.push(item)
      return item
    },

    updateItem(id: string, patch: Partial<InventoryItem>) {
      const idx = this.items.findIndex((i) => i.id === id)
      if (idx === -1) return null
      this.items[idx] = { ...this.items[idx], ...patch }
      return this.items[idx]
    },

    deleteItem(id: string) {
      this.items = this.items.filter((i) => i.id !== id)
    },

    stockIn(itemId: string, qty: number, opts?: { bookingId?: number | null; taskId?: string | null }) {
      if (qty <= 0) return
      const item = this.items.find((i) => i.id === itemId)
      if (!item) return
      item.quantity += qty
      this.logMovement(itemId, item.name, qty, 'stock-in', opts)
    },

    stockOut(itemId: string, qty: number, opts?: { bookingId?: number | null; taskId?: string | null }) {
      if (qty <= 0) return
      const item = this.items.find((i) => i.id === itemId)
      if (!item) return
      item.quantity = Math.max(0, item.quantity - qty)
      this.logMovement(itemId, item.name, qty, 'stock-out', opts)
    },

    logMovement(itemId: string, itemName: string, qty: number, type: MovementType, opts?: { bookingId?: number | null; taskId?: string | null }) {
      const m: StockMovement = {
        id: `${Date.now()}-${Math.random().toString(36).slice(2, 6)}`,
        itemId,
        itemName,
        quantity: qty,
        type,
        timestamp: new Date().toLocaleString('en-PH'),
        bookingId: opts?.bookingId ?? null,
        taskId: opts?.taskId ?? null,
      }
      this.movements.unshift(m)
    },

    getMovementsForBooking(bookingId: number) {
      return this.movements.filter((m) => m.bookingId === bookingId)
    },

    getMovementsForTask(taskId: string) {
      return this.movements.filter((m) => m.taskId === taskId)
    },
  },
})
