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

export type BackendInventoryItem = {
  id: number
  name: string
  quantity: number
  unit_price: number
  supplier?: string | null
  date_added?: string
  low_stock_threshold: number
}

export type BackendStockMovement = {
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
