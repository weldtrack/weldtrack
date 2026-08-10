import api from './api'
import type { InventoryItem, StockMovement, BackendInventoryItem, BackendStockMovement } from '../types/inventory'

export function toInventoryItem(item: BackendInventoryItem): InventoryItem {
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

export function toStockMovement(movement: BackendStockMovement): StockMovement {
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

export async function fetchInventory() {
  const { data } = await api.get<BackendInventoryItem[]>('/inventory')
  return Array.isArray(data) ? data.map(toInventoryItem) : []
}

export async function fetchMovements(params?: { bookingId?: string; taskId?: string; itemId?: string }) {
  const { data } = await api.get<BackendStockMovement[]>('/inventory/movements/history', {
    params: {
      booking_id: params?.bookingId,
      task_id: params?.taskId,
      item_id: params?.itemId,
    },
  })
  return Array.isArray(data) ? data.map(toStockMovement) : []
}

export async function addItem(payload: Omit<InventoryItem, 'id'>) {
  const { data } = await api.post<BackendInventoryItem>('/inventory', {
    name: payload.name,
    quantity: payload.quantity,
    unit_price: payload.unitPrice,
    supplier: payload.supplier,
    low_stock_threshold: payload.lowStockThreshold,
  })

  return toInventoryItem(data)
}

export async function updateItem(id: string, patch: Partial<InventoryItem>) {
  const { data } = await api.patch<BackendInventoryItem>(`/inventory/${id}`, {
    ...(patch.name !== undefined ? { name: patch.name } : {}),
    ...(patch.quantity !== undefined ? { quantity: patch.quantity } : {}),
    ...(patch.unitPrice !== undefined ? { unit_price: patch.unitPrice } : {}),
    ...(patch.supplier !== undefined ? { supplier: patch.supplier } : {}),
    ...(patch.lowStockThreshold !== undefined ? { low_stock_threshold: patch.lowStockThreshold } : {}),
  })

  return toInventoryItem(data)
}

export async function deleteItem(id: string) {
  await api.delete(`/inventory/${id}`)
}
