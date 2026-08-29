<script setup lang="ts">
import { computed } from 'vue'
import { Clock } from 'lucide-vue-next'
import { useInventoryStore } from '../../../../stores/inventory'
import { getServicePriceDisplay } from '../../../../services/servicePricing'

const { item } = defineProps<{ item: any }>()
const inventoryStore = useInventoryStore()



function getMaterialLines(bookingId: string, materials?: any[]) {
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

function getMaterialsTotal(bookingId: string, materials?: any[]) {
  return getMaterialLines(bookingId, materials).reduce((sum: number, line: any) => sum + (line.subtotal || 0), 0)
}

function getGrandTotal(item: any) {
  const labor = item.actualLaborCost ?? getServicePriceDisplay(item.projectType, item.estimatedCost)
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



const materialLines = computed(() => getMaterialLines(item.id, item.materials))
const materialsTotal = computed(() => getMaterialsTotal(item.id, item.materials))
const grandTotal = computed(() => getGrandTotal(item))
</script>

<template>
  <article class="group relative w-full overflow-hidden rounded-2xl border border-slate-200 bg-white shadow-sm transition duration-200 hover:border-slate-300 hover:shadow-md dark:border-slate-800 dark:bg-slate-900 dark:hover:border-slate-700">
    <div class="p-4 sm:p-6">
      <!-- Project identity and status -->
      <div class="flex flex-col gap-4 border-b border-slate-100 pb-5 dark:border-slate-800 sm:flex-row sm:items-start sm:justify-between">
        <div class="flex min-w-0 items-start gap-3 sm:gap-4">
          <div class="flex h-11 w-11 shrink-0 items-center justify-center rounded-xl bg-slate-100 text-slate-600 ring-1 ring-inset ring-slate-200 dark:bg-slate-800 dark:text-slate-300 dark:ring-slate-700">
            <Clock class="h-5 w-5" />
          </div>
          <div class="min-w-0 flex-1">
            <p class="break-all text-xs font-medium text-slate-400">Booking #{{ item.id }}</p>
            <h4 class="mt-0.5 break-words text-lg font-semibold leading-snug text-slate-900 dark:text-slate-100">
              {{ item.projectType || item.name || 'Welding Project' }}
            </h4>
            <p class="mt-1 break-words text-sm text-slate-500 dark:text-slate-400">
              {{ item.email || item.client || '-' }}
            </p>
          </div>
        </div>

        <div class="flex shrink-0 flex-row items-center justify-between gap-3 sm:flex-col sm:items-end">
          <div class="relative inline-block">
            <span 
              class="inline-flex items-center rounded-full px-3 py-1 text-xs font-semibold capitalize ring-1 ring-inset" 
              :class="item.status === 'completed'
                ? 'bg-emerald-50 text-emerald-700 ring-emerald-600/20 dark:bg-emerald-950/60 dark:text-emerald-300 dark:ring-emerald-800'
                : 'bg-rose-50 text-rose-700 ring-rose-600/20 dark:bg-rose-950/60 dark:text-rose-300 dark:ring-rose-800'"
            >
              {{ item.status }}
            </span>
          </div>
          <p class="text-xs text-slate-400">{{ formatDate(item.createdDate) }}</p>
        </div>
      </div>

      <!-- Details and financial breakdown -->
      <div class="mt-5 grid gap-6 lg:grid-cols-[minmax(0,1fr)_minmax(18rem,0.7fr)] lg:gap-10">
        <div class="min-w-0">
          <p class="text-xs font-semibold uppercase tracking-wider text-slate-400">Project details</p>
          <dl class="mt-3 grid grid-cols-1 gap-3 sm:grid-cols-2">
            <div class="rounded-xl bg-slate-50 px-4 py-3 dark:bg-slate-800/60">
              <dt class="text-xs text-slate-500 dark:text-slate-400">Booked on</dt>
              <dd class="mt-1 text-sm font-medium text-slate-800 dark:text-slate-200">{{ formatDate(item.createdDate) }}</dd>
            </div>
            <div class="rounded-xl bg-slate-50 px-4 py-3 dark:bg-slate-800/60">
              <dt class="text-xs text-slate-500 dark:text-slate-400">Scheduled date</dt>
              <dd class="mt-1 text-sm font-medium text-slate-800 dark:text-slate-200">{{ formatDate(item.scheduleDate || item.endDate) }}</dd>
            </div>
          </dl>
          <div v-if="item.status === 'cancelled'" class="mt-3 rounded-xl border border-rose-100 bg-rose-50/70 px-4 py-3 dark:border-rose-900/50 dark:bg-rose-950/30">
            <p class="text-xs font-medium text-rose-600 dark:text-rose-400">Cancellation reason</p>
            <p class="mt-1 break-words text-sm text-rose-800 dark:text-rose-200">{{ item.cancelReason || 'No reason provided' }}</p>
          </div>
        </div>

        <div class="min-w-0">
          <p class="text-xs font-semibold uppercase tracking-wider text-slate-400">Cost summary</p>
          <div class="mt-3 space-y-3 text-sm">
            <div class="flex items-start justify-between gap-4">
              <span class="text-slate-500 dark:text-slate-400">Labor</span>
              <span class="shrink-0 font-medium text-slate-800 dark:text-slate-200">{{ formatCurrency(item.actualLaborCost ?? getServicePriceDisplay(item.projectType, item.estimatedCost)) }}</span>
            </div>
            <ul v-if="materialLines.length > 0" class="space-y-2 border-y border-slate-100 py-3 dark:border-slate-800">
              <li v-for="line in materialLines" :key="line.id" class="flex items-start justify-between gap-4 text-sm">
              <span class="min-w-0 break-words text-slate-500 dark:text-slate-400">
                {{ line.name }} <span class="whitespace-nowrap text-slate-400">× {{ line.qty }}</span>
              </span>
              <span class="shrink-0 font-medium text-slate-800 dark:text-slate-200">
                {{ formatCurrency(line.subtotal) }}
              </span>
            </li>
            </ul>
            <p v-else class="border-y border-slate-100 py-3 text-xs italic text-slate-400 dark:border-slate-800">No materials recorded</p>
            <div class="flex items-center justify-between gap-4">
              <span class="text-slate-500 dark:text-slate-400">Materials total</span>
              <span class="shrink-0 font-medium text-slate-800 dark:text-slate-200">{{ formatCurrency(materialsTotal) }}</span>
            </div>
          </div>
        </div>
      </div>
    </div>

    <div class="flex flex-col gap-1 border-t border-slate-200 bg-slate-50 px-4 py-4 dark:border-slate-800 dark:bg-slate-800/60 sm:flex-row sm:items-center sm:justify-between sm:px-6">
      <span class="text-xs font-semibold uppercase tracking-wider text-slate-500 dark:text-slate-400">Total project cost</span>
      <span class="text-xl font-semibold text-slate-900 dark:text-slate-100">{{ formatCurrency(grandTotal) }}</span>
    </div>
  </article>
</template>
