<script setup lang="ts">
import { computed } from 'vue'
import { useInventoryStore } from '../../../stores/inventory'

const { item } = defineProps<{ item: any }>()
const inventoryStore = useInventoryStore()

function getLaborCost(estimatedCost?: number) {
  return estimatedCost ?? 0
}

function getMaterialLines(bookingId: number, materials?: any[], materialCost?: number) {
  if (Array.isArray(materials) && materials.length > 0) return materials

  const movements = inventoryStore.getMovementsForBooking(bookingId).filter((m) => m.type === 'stock-out')
  const grouped: Record<string, any> = {}

  movements.forEach((m) => {
    const item = inventoryStore.items.find((it) => it.id === m.itemId)
    const unitPrice = item?.unitPrice ?? 0
    if (!grouped[m.itemId]) {
      grouped[m.itemId] = {
        id: m.itemId,
        name: m.itemName,
        qty: 0,
        unitPrice,
        subtotal: 0,
      }
    }
    grouped[m.itemId].qty += m.quantity
    grouped[m.itemId].subtotal = grouped[m.itemId].qty * grouped[m.itemId].unitPrice
  })

  const lines = Object.values(grouped)
  if (lines.length > 0) return lines

  if ((materialCost ?? 0) > 0) {
    return [
      {
        id: `temp-${bookingId}`,
        name: 'Temporary Material Entry',
        qty: 1,
        unitPrice: materialCost ?? 0,
        subtotal: materialCost ?? 0,
        isTemp: true,
      },
    ]
  }

  return []
}

function getMaterialsTotal(bookingId: number, materials?: any[], materialCost?: number) {
  return getMaterialLines(bookingId, materials, materialCost).reduce((sum: number, line: any) => sum + (line.subtotal || 0), 0)
}

function getGrandTotal(item: any) {
  const labor = getLaborCost(item.estimatedCost)
  const materials = getMaterialsTotal(item.id, item.materials, item.materialCost)
  return item.totalPrice ?? labor + materials
}

function formatDate(value?: string) {
  if (!value) return '-'
  return new Date(value).toLocaleDateString('en-PH', {
    year: 'numeric',
    month: 'short',
    day: 'numeric',
  })
}

function formatCurrency(value?: number) {
  if (value == null) return '-'
  return `₱${value.toLocaleString('en-PH', { minimumFractionDigits: 2 })}`
}

function getStatusClass(status: string) {
  return status === 'completed' ? 'bg-green-100 text-green-700' : 'bg-red-100 text-red-700'
}

const materialLines = computed(() => getMaterialLines(item.id, item.materials, item.materialCost))
const materialsTotal = computed(() => getMaterialsTotal(item.id, item.materials, item.materialCost))
const grandTotal = computed(() => getGrandTotal(item))
</script>

<template>
  <div class="rounded-lg border border-gray-200 bg-white p-4">
    <div class="flex items-start justify-between">
      <div class="flex-1">
        <p class="text-sm text-gray-500">Booking #{{ item.id }}</p>
        <h4 class="mt-1 text-lg font-medium text-gray-900">{{ item.projectType || item.name || item.projectType }}</h4>
        <p class="mt-1 text-sm text-gray-500">{{ item.email || item.client || '-' }} · Booked: {{ formatDate(item.createdDate) }}</p>
      </div>
      <div class="ml-4 text-right">
        <p class="text-sm text-gray-500">Schedule</p>
        <p class="mt-1 font-medium text-gray-900">{{ formatDate(item.scheduleDate || item.endDate) }}</p>
        <p class="mt-3 text-sm text-gray-500">Status</p>
        <span class="mt-1 inline-block rounded-full px-3 py-1 text-xs font-semibold capitalize" :class="getStatusClass(item.status)">{{ item.status }}</span>
      </div>
    </div>

    <div class="mt-3 space-y-2 text-sm">
      <div class="flex items-center justify-between">
        <span class="text-gray-600">Project Price (Labor)</span>
        <span class="font-medium text-gray-900">{{ formatCurrency(getLaborCost(item.estimatedCost)) }}</span>
      </div>

      <div>
        <p class="text-gray-600">Material Price Per Item</p>
        <ul class="mt-1 space-y-1">
          <li v-for="line in materialLines" :key="line.id" class="flex items-center justify-between">
            <span class="truncate text-gray-700">{{ line.name }} · x{{ line.qty }} @ {{ formatCurrency(line.unitPrice) }} <span v-if="line.isTemp" class="text-xs text-amber-700">(temp)</span></span>
            <span class="font-medium text-gray-900">{{ formatCurrency(line.subtotal) }}</span>
          </li>
        </ul>
        <p v-if="materialLines.length === 0" class="text-gray-500">No materials submitted yet</p>
      </div>

      <div class="flex items-center justify-between border-t border-gray-100 pt-2">
        <span class="text-gray-600">Materials Total</span>
        <span class="font-medium text-gray-900">{{ formatCurrency(materialsTotal) }}</span>
      </div>

      <div class="flex items-center justify-between border-t border-gray-200 pt-2">
        <span class="font-semibold text-gray-800">Total Cost</span>
        <span class="font-semibold text-gray-900">{{ formatCurrency(grandTotal) }}</span>
      </div>
    </div>
  </div>
</template>
