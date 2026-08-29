export interface InventoryItem {
  id: string
  name: string
  quantity: number
  unitPrice: number
  supplier: string
  dateAdded: string
  lowStockThreshold: number
  isArchived: boolean
  archivedAt: string | null
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
  bookingId?: string | null
  taskId?: string | null
  teamEmails: string[]
}

export type BackendInventoryItem = {
  id: string
  name: string
  quantity: number
  unit_price: number
  supplier?: string | null
  date_added?: string
  low_stock_threshold: number
  is_archived?: boolean
  archived_at?: string | null
}

export type BackendStockMovement = {
  id: string
  item_id: string
  item_name: string
  quantity: number
  type: MovementType
  timestamp?: string
  booking_id?: string | null
  task_id?: string | null
  team_emails?: string[]
}
