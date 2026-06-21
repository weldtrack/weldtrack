<script setup lang="ts">
import { computed } from 'vue'
import { Clock } from 'lucide-vue-next'
import { useInventoryStore } from '../../../../stores/inventory'
import { getServicePriceDisplay } from '../../../../services/servicePricing'

const { item } = defineProps<{ item: any }>()
const inventoryStore = useInventoryStore()



function getMaterialLines(bookingId: number, materials?: any[]) {
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

  return []
}

function getMaterialsTotal(bookingId: number, materials?: any[]) {
  return getMaterialLines(bookingId, materials).reduce((sum: number, line: any) => sum + (line.subtotal || 0), 0)
}

function getGrandTotal(item: any) {
  const labor = getServicePriceDisplay(item.projectType, item.estimatedCost)
  const materials = getMaterialsTotal(item.id, item.materials)
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

const materialLines = computed(() => getMaterialLines(item.id, item.materials))
const materialsTotal = computed(() => getMaterialsTotal(item.id, item.materials))
const grandTotal = computed(() => getGrandTotal(item))
</script>

<template>
  <div class="rounded-lg border border-gray-200 bg-white p-4">
    <div class="flex flex-col gap-4 sm:flex-row sm:items-start sm:justify-between">
      <div class="flex items-start gap-3 sm:min-w-0 sm:flex-1">
        <div class="h-10 w-10 flex items-center justify-center rounded-md bg-slate-100 ring-1 ring-slate-200 shrink-0">
          <Clock class="h-5 w-5 text-slate-500" />
        </div>
        <div class="flex-1 min-w-0">
          <p class="text-sm text-gray-500">Booking #{{ item.id }}</p>
          <h4 class="mt-1 text-lg font-medium text-gray-900 wrap-break-word">{{ item.projectType || item.name || item.projectType }}</h4>
          <p class="mt-1 text-sm text-gray-500 wrap-break-word">{{ item.email || item.client || '-' }} · Booked: {{ formatDate(item.createdDate) }}</p>
        </div>
      </div>
      <div class="text-left sm:text-right sm:shrink-0">
        <p class="text-sm text-gray-500">Schedule</p>
        <p class="mt-1 font-medium text-gray-900">{{ formatDate(item.scheduleDate || item.endDate) }}</p>
        <p class="mt-3 text-sm text-gray-500">Status</p>
        <span class="mt-1 inline-block rounded-full px-3 py-1 text-xs font-semibold capitalize" :class="getStatusClass(item.status)">{{ item.status }}</span>
      </div>
    </div>

    <div class="mt-3 space-y-2 text-sm">
      <div class="flex items-center justify-between">
        <span class="text-gray-600">Project Price (Labor)</span>
        <span class="font-medium text-gray-900">{{ formatCurrency(getServicePriceDisplay(item.projectType, item.estimatedCost)) }}</span>
      </div>

      <div>
        <p class="text-gray-600">Material Price Per Item</p>
        <ul class="mt-1 space-y-1">
          <li v-for="line in materialLines" :key="line.id" class="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-1 sm:gap-2">
            <span class="text-gray-700 wrap-break-word">{{ line.name }} · x{{ line.qty }} @ {{ formatCurrency(line.unitPrice) }}</span>
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
