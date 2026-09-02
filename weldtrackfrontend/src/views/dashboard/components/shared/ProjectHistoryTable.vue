<script setup lang="ts">
import { computed, ref } from 'vue'
import {
  Clock,
  Eye,
  Search,
  X,
  Calendar,
  CheckCircle2,
  XCircle,
  Package,
  Wrench,
  AlertTriangle,
  User,
  MapPin,
  Phone,
  Mail,
} from 'lucide-vue-next'
import { type BookingItem } from '../../../../types/bookings'
import { useInventoryStore } from '../../../../stores/inventory'
import { getServicePriceDisplay, formatCurrency } from '../../../../services/servicePricing'
import { resolveImageUrl } from '../../../../services/images'

const props = withDefaults(
  defineProps<{
    items: BookingItem[]
    showCustomerColumn?: boolean
    emptyMessage?: string
    title?: string
  }>(),
  {
    showCustomerColumn: true,
    emptyMessage: 'No project history records found.',
    title: 'Project History',
  },
)

const inventoryStore = useInventoryStore()

const searchTerm = ref('')
const statusFilter = ref<'all' | 'completed' | 'cancelled'>('all')
const selectedItem = ref<BookingItem | null>(null)
const isDetailsModalOpen = ref(false)

function formatDate(value?: string) {
  if (!value) return '-'
  return new Date(value).toLocaleDateString('en-PH', {
    year: 'numeric',
    month: 'short',
    day: 'numeric',
  })
}

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

  return Object.values(grouped)
}

function getMaterialsTotal(bookingId: string, materials?: any[]) {
  return getMaterialLines(bookingId, materials).reduce((sum: number, line: any) => sum + (line.subtotal || 0), 0)
}

function getLaborCost(item: BookingItem) {
  if (item.status === 'cancelled') return 0
  return item.actualLaborCost ?? getServicePriceDisplay(item.projectType, item.estimatedCost)
}

function getGrandTotal(item: BookingItem) {
  if (item.status === 'cancelled') return 0
  const labor = getLaborCost(item)
  const materials = getMaterialsTotal(item.id, item.materials)
  return item.totalPrice ?? labor + materials
}

function formatAddress(item: BookingItem) {
  if (!item.location) return ''
  const parts = [
    item.location.house,
    item.location.barangay,
    item.location.municipality,
    item.location.province,
  ].filter(Boolean)
  return parts.join(', ')
}

const filteredItems = computed(() => {
  const query = searchTerm.value.trim().toLowerCase()

  const list = props.items.filter((item) => {
    // Status filter
    if (statusFilter.value !== 'all' && item.status !== statusFilter.value) {
      return false
    }

    // Search query
    if (!query) return true

    const idMatch = item.id.toLowerCase().includes(query)
    const projectMatch = (item.projectType || '').toLowerCase().includes(query)
    const customerMatch = (item.customerName || '').toLowerCase().includes(query)
    const emailMatch = (item.email || '').toLowerCase().includes(query)
    const phoneMatch = (item.phone || '').toLowerCase().includes(query)
    const reasonMatch = (item.cancelReason || '').toLowerCase().includes(query)

    return idMatch || projectMatch || customerMatch || emailMatch || phoneMatch || reasonMatch
  })

  // Fixed to Date Latest (Newest First)
  return list.sort((a, b) => {
    const timeA = a.createdDate ? new Date(a.createdDate).getTime() : 0
    const timeB = b.createdDate ? new Date(b.createdDate).getTime() : 0
    return timeB - timeA
  })
})

const completedCount = computed(() => props.items.filter((i) => i.status === 'completed').length)
const cancelledCount = computed(() => props.items.filter((i) => i.status === 'cancelled').length)

function openDetails(item: BookingItem) {
  selectedItem.value = item
  isDetailsModalOpen.value = true
}

function closeDetails() {
  isDetailsModalOpen.value = false
  selectedItem.value = null
}
</script>

<template>
  <div class="space-y-4">
    <!-- Search and Filter Bar Card -->
    <div class="rounded-2xl border border-slate-200 bg-white p-4 shadow-xs dark:border-slate-800 dark:bg-slate-900">
      <div class="flex flex-col gap-4 sm:flex-row sm:items-center sm:justify-between">
        <!-- Search Input -->
        <div class="relative flex-1 max-w-md">
          <Search class="absolute left-3.5 top-1/2 h-4 w-4 -translate-y-1/2 text-slate-400" />
          <input
            v-model="searchTerm"
            type="text"
            placeholder="Search by project, ID, client, or reason..."
            class="w-full rounded-xl border border-slate-200 bg-slate-50 py-2.5 pl-10 pr-4 text-sm text-slate-900 outline-none transition focus:border-sky-500 focus:bg-white dark:border-slate-800 dark:bg-slate-950 dark:text-slate-100 dark:focus:border-sky-500"
          />
        </div>

        <!-- Filter Pills -->
        <div class="flex flex-wrap items-center gap-2">
          <button
            type="button"
            @click="statusFilter = 'all'"
            :class="[
              'rounded-xl px-3.5 py-2 text-xs font-bold transition-all',
              statusFilter === 'all'
                ? 'bg-sky-600 text-white shadow-xs ring-1 ring-sky-500'
                : 'border border-slate-200 bg-slate-100 text-slate-700 hover:bg-slate-200 dark:border-slate-700 dark:bg-slate-800 dark:text-slate-200 dark:hover:bg-slate-700',
            ]"
          >
            All ({{ props.items.length }})
          </button>
          <button
            type="button"
            @click="statusFilter = 'completed'"
            :class="[
              'rounded-xl px-3.5 py-2 text-xs font-bold transition-all inline-flex items-center gap-1.5',
              statusFilter === 'completed'
                ? 'bg-emerald-600 text-white shadow-xs ring-1 ring-emerald-500'
                : 'border border-emerald-200/80 bg-emerald-50 text-emerald-700 hover:bg-emerald-100 dark:border-emerald-800/80 dark:bg-emerald-950/60 dark:text-emerald-300 dark:hover:bg-emerald-900/60',
            ]"
          >
            <CheckCircle2 class="h-3.5 w-3.5" />
            Completed ({{ completedCount }})
          </button>
          <button
            type="button"
            @click="statusFilter = 'cancelled'"
            :class="[
              'rounded-xl px-3.5 py-2 text-xs font-bold transition-all inline-flex items-center gap-1.5',
              statusFilter === 'cancelled'
                ? 'bg-rose-600 text-white shadow-xs ring-1 ring-rose-500'
                : 'border border-rose-200/80 bg-rose-50 text-rose-700 hover:bg-rose-100 dark:border-rose-800/80 dark:bg-rose-950/60 dark:text-rose-300 dark:hover:bg-rose-900/60',
            ]"
          >
            <XCircle class="h-3.5 w-3.5" />
            Cancelled ({{ cancelledCount }})
          </button>
        </div>
      </div>
    </div>

    <!-- Table Container Card -->
    <div class="overflow-hidden rounded-2xl border border-slate-200 bg-white shadow-xs dark:border-slate-800 dark:bg-slate-900">
      <div v-if="filteredItems.length === 0" class="p-12 text-center">
        <Clock class="mx-auto h-12 w-12 text-slate-300 dark:text-slate-700" />
        <h4 class="mt-3 text-base font-bold text-slate-900 dark:text-slate-100">{{ emptyMessage }}</h4>
        <p class="mt-1 text-xs text-slate-500 dark:text-slate-400">
          {{ searchTerm ? 'Try adjusting your search or filter criteria.' : 'Projects will appear here once completed or cancelled.' }}
        </p>
      </div>

      <div v-else class="overflow-x-auto">
        <table class="w-full min-w-[950px] divide-y divide-slate-100 dark:divide-slate-800 text-left">
          <thead class="bg-slate-50 dark:bg-slate-800/80">
            <tr>
              <th class="px-6 py-4 text-xs font-bold uppercase tracking-wider text-slate-500 dark:text-slate-400">
                Booking ID & Date
              </th>
              <th class="px-6 py-4 text-xs font-bold uppercase tracking-wider text-slate-500 dark:text-slate-400">
                Service / Project
              </th>
              <th
                v-if="showCustomerColumn"
                class="px-6 py-4 text-xs font-bold uppercase tracking-wider text-slate-500 dark:text-slate-400"
              >
                Customer
              </th>
              <th class="px-6 py-4 text-xs font-bold uppercase tracking-wider text-slate-500 dark:text-slate-400">
                Schedule
              </th>
              <th class="px-6 py-4 text-xs font-bold uppercase tracking-wider text-slate-500 dark:text-slate-400 text-right">
                Labor Cost
              </th>
              <th class="px-6 py-4 text-xs font-bold uppercase tracking-wider text-slate-500 dark:text-slate-400 text-right">
                Materials
              </th>
              <th class="px-6 py-4 text-xs font-bold uppercase tracking-wider text-slate-500 dark:text-slate-400 text-right">
                Total Cost
              </th>
              <th class="px-6 py-4 text-xs font-bold uppercase tracking-wider text-slate-500 dark:text-slate-400 text-center">
                Status
              </th>
              <th class="sticky right-0 z-10 bg-slate-50 dark:bg-slate-800 px-6 py-4 text-xs font-bold uppercase tracking-wider text-slate-500 dark:text-slate-400 text-right shadow-[-12px_0_15px_-4px_rgba(0,0,0,0.05)]">
                Action
              </th>
            </tr>
          </thead>
          <tbody class="divide-y divide-slate-100 dark:divide-slate-800 bg-transparent">
            <tr
              v-for="item in filteredItems"
              :key="item.id"
              class="group transition-colors hover:bg-slate-50/60 dark:hover:bg-slate-800/50"
            >
              <!-- Booking ID & Date -->
              <td class="px-6 py-4 whitespace-nowrap">
                <div class="flex flex-col">
                  <span class="font-mono text-xs font-semibold text-sky-600 dark:text-sky-400">
                    #{{ item.id.substring(0, 10) }}...
                  </span>
                  <span class="mt-0.5 text-xs text-slate-500 dark:text-slate-400">
                    Booked {{ formatDate(item.createdDate) }}
                  </span>
                </div>
              </td>

              <!-- Service / Project -->
              <td class="px-6 py-4">
                <div class="flex flex-col min-w-[180px]">
                  <span class="font-bold text-slate-900 dark:text-slate-100">
                    {{ item.projectType || 'Welding Project' }}
                  </span>
                  <span v-if="item.description" class="mt-0.5 line-clamp-1 text-xs text-slate-500 dark:text-slate-400">
                    {{ item.description }}
                  </span>
                </div>
              </td>

              <!-- Customer (Admin view) -->
              <td v-if="showCustomerColumn" class="px-6 py-4 whitespace-nowrap">
                <div class="flex flex-col">
                  <span class="font-semibold text-slate-900 dark:text-slate-100">
                    {{ item.customerName || item.email || '-' }}
                  </span>
                  <span v-if="item.phone" class="mt-0.5 text-xs text-slate-500 dark:text-slate-400">
                    {{ item.phone }}
                  </span>
                </div>
              </td>

              <!-- Schedule -->
              <td class="px-6 py-4 whitespace-nowrap text-sm text-slate-600 dark:text-slate-300">
                {{ formatDate(item.scheduleDate) }}
              </td>

              <!-- Labor Cost -->
              <td class="px-6 py-4 whitespace-nowrap text-right font-medium text-slate-800 dark:text-slate-200">
                <span v-if="item.status === 'cancelled'" class="text-xs text-slate-400">—</span>
                <span v-else>{{ formatCurrency(getLaborCost(item)) }}</span>
              </td>

              <!-- Materials Cost -->
              <td class="px-6 py-4 whitespace-nowrap text-right font-medium text-slate-800 dark:text-slate-200">
                <span v-if="item.status === 'cancelled'" class="text-xs text-slate-400">—</span>
                <div v-else class="flex flex-col items-end">
                  <span>{{ formatCurrency(getMaterialsTotal(item.id, item.materials)) }}</span>
                  <span
                    v-if="getMaterialLines(item.id, item.materials).length > 0"
                    class="text-[11px] text-slate-400"
                  >
                    {{ getMaterialLines(item.id, item.materials).length }} item(s)
                  </span>
                </div>
              </td>

              <!-- Total Cost -->
              <td class="px-6 py-4 whitespace-nowrap text-right font-bold text-slate-900 dark:text-slate-100">
                <span v-if="item.status === 'cancelled'" class="text-xs text-rose-500 font-medium">No Charge</span>
                <span v-else class="text-emerald-700 dark:text-emerald-400 font-black">
                  {{ formatCurrency(getGrandTotal(item)) }}
                </span>
              </td>

              <!-- Status Badge -->
              <td class="px-6 py-4 whitespace-nowrap text-center">
                <span
                  class="inline-flex items-center gap-1 rounded-full px-3 py-1 text-xs font-bold capitalize ring-1 ring-inset"
                  :class="
                    item.status === 'completed'
                      ? 'bg-emerald-50 text-emerald-700 ring-emerald-600/20 dark:bg-emerald-950/60 dark:text-emerald-300 dark:ring-emerald-800'
                      : 'bg-rose-50 text-rose-700 ring-rose-600/20 dark:bg-rose-950/60 dark:text-rose-300 dark:ring-rose-800'
                  "
                >
                  <CheckCircle2 v-if="item.status === 'completed'" class="h-3 w-3" />
                  <XCircle v-else class="h-3 w-3" />
                  {{ item.status }}
                </span>
              </td>

              <!-- Actions (Sticky Right) -->
              <td class="sticky right-0 z-10 bg-white dark:bg-slate-900 group-hover:bg-slate-50/60 dark:group-hover:bg-slate-800/50 px-6 py-4 whitespace-nowrap text-right shadow-[-12px_0_15px_-4px_rgba(0,0,0,0.05)]">
                <button
                  type="button"
                  @click="openDetails(item)"
                  class="inline-flex items-center gap-1.5 rounded-xl border border-slate-200 bg-white px-3 py-1.5 text-xs font-bold text-sky-600 shadow-2xs transition-all hover:border-sky-300 hover:bg-sky-50 dark:border-slate-700 dark:bg-slate-800 dark:text-sky-400 dark:hover:border-sky-600 dark:hover:bg-slate-700"
                >
                  <Eye class="h-3.5 w-3.5" />
                  <span>Details</span>
                </button>
              </td>
            </tr>
          </tbody>
        </table>
      </div>
    </div>

    <!-- Project Details Modal -->
    <div
      v-if="isDetailsModalOpen && selectedItem"
      class="fixed inset-0 z-50 flex items-center justify-center p-4 bg-slate-900/60 backdrop-blur-xs animate-in fade-in duration-200"
    >
      <div class="relative w-full max-w-2xl max-h-[90vh] overflow-y-auto rounded-3xl bg-white p-6 shadow-2xl dark:bg-slate-900 sm:p-8">
        <!-- Close Button -->
        <button
          type="button"
          @click="closeDetails"
          class="absolute right-5 top-5 rounded-full p-2 text-slate-400 hover:bg-slate-100 hover:text-slate-600 dark:hover:bg-slate-800 dark:hover:text-slate-200 transition"
        >
          <X class="h-5 w-5" />
        </button>

        <!-- Modal Header -->
        <div class="flex items-start gap-4 border-b border-slate-100 pb-5 dark:border-slate-800">
          <div class="flex h-12 w-12 shrink-0 items-center justify-center rounded-2xl bg-sky-50 text-sky-600 dark:bg-sky-950/60 dark:text-sky-400">
            <Wrench class="h-6 w-6" />
          </div>
          <div>
            <div class="flex flex-wrap items-center gap-2">
              <span class="font-mono text-xs font-bold text-sky-600 dark:text-sky-400">
                Booking #{{ selectedItem.id }}
              </span>
              <span
                class="inline-flex items-center gap-1 rounded-full px-2.5 py-0.5 text-xs font-bold capitalize ring-1 ring-inset"
                :class="
                  selectedItem.status === 'completed'
                    ? 'bg-emerald-50 text-emerald-700 ring-emerald-600/20 dark:bg-emerald-950/60 dark:text-emerald-300 dark:ring-emerald-800'
                    : 'bg-rose-50 text-rose-700 ring-rose-600/20 dark:bg-rose-950/60 dark:text-rose-300 dark:ring-rose-800'
                "
              >
                {{ selectedItem.status }}
              </span>
            </div>
            <h3 class="mt-1 text-xl font-black text-slate-900 dark:text-white">
              {{ selectedItem.projectType || 'Welding Project' }}
            </h3>
          </div>
        </div>

        <div class="mt-6 space-y-6">
          <!-- Client & Dates Information -->
          <div class="rounded-2xl border border-slate-200 bg-slate-50/70 p-4 dark:border-slate-800 dark:bg-slate-950/40">
            <h4 class="text-xs font-bold uppercase tracking-wider text-slate-400 dark:text-slate-500 mb-3">
              Booking Information
            </h4>
            <div class="grid grid-cols-1 gap-3 sm:grid-cols-2 text-sm">
              <div v-if="selectedItem.customerName" class="flex items-center gap-2 text-slate-700 dark:text-slate-300">
                <User class="h-4 w-4 text-slate-400 shrink-0" />
                <span class="font-medium">{{ selectedItem.customerName }}</span>
              </div>
              <div v-if="selectedItem.email" class="flex items-center gap-2 text-slate-700 dark:text-slate-300">
                <Mail class="h-4 w-4 text-slate-400 shrink-0" />
                <span class="truncate">{{ selectedItem.email }}</span>
              </div>
              <div v-if="selectedItem.phone" class="flex items-center gap-2 text-slate-700 dark:text-slate-300">
                <Phone class="h-4 w-4 text-slate-400 shrink-0" />
                <span>{{ selectedItem.phone }}</span>
              </div>
              <div class="flex items-center gap-2 text-slate-700 dark:text-slate-300">
                <Calendar class="h-4 w-4 text-slate-400 shrink-0" />
                <span>Booked: {{ formatDate(selectedItem.createdDate) }}</span>
              </div>
              <div class="flex items-center gap-2 text-slate-700 dark:text-slate-300">
                <Clock class="h-4 w-4 text-slate-400 shrink-0" />
                <span>Scheduled: {{ formatDate(selectedItem.scheduleDate) }}</span>
              </div>
              <div v-if="formatAddress(selectedItem)" class="flex items-start gap-2 text-slate-700 dark:text-slate-300 sm:col-span-2">
                <MapPin class="h-4 w-4 text-slate-400 shrink-0 mt-0.5" />
                <span>{{ formatAddress(selectedItem) }}</span>
              </div>
            </div>
          </div>

          <!-- Description if provided -->
          <div v-if="selectedItem.description" class="rounded-2xl border border-slate-200 bg-slate-50/70 p-4 dark:border-slate-800 dark:bg-slate-950/40">
            <h4 class="text-xs font-bold uppercase tracking-wider text-slate-400 dark:text-slate-500 mb-1.5">
              Project Description
            </h4>
            <p class="text-sm leading-relaxed text-slate-700 dark:text-slate-300">
              {{ selectedItem.description }}
            </p>
          </div>

          <!-- Cancellation Notice if Cancelled -->
          <div
            v-if="selectedItem.status === 'cancelled'"
            class="rounded-2xl border border-rose-200 bg-rose-50 p-4 text-sm text-rose-800 dark:border-rose-900/50 dark:bg-rose-950/40 dark:text-rose-300"
          >
            <div class="flex items-start gap-2.5">
              <AlertTriangle class="h-5 w-5 shrink-0 text-rose-600 dark:text-rose-400" />
              <div>
                <p class="font-bold">Project Cancelled {{ selectedItem.cancelledBy ? `by ${selectedItem.cancelledBy}` : '' }}</p>
                <p class="mt-1 leading-relaxed">
                  {{ selectedItem.cancelReason || 'No cancellation reason specified.' }}
                </p>
                <p class="mt-2 text-xs font-semibold text-rose-600 dark:text-rose-400">
                  No project fees or material costs were charged for this booking.
                </p>
              </div>
            </div>
          </div>

          <!-- Cost Breakdown & Materials (if not cancelled) -->
          <div v-if="selectedItem.status !== 'cancelled'" class="space-y-4">
            <div class="rounded-2xl border border-slate-200 bg-slate-50/70 p-4 dark:border-slate-800 dark:bg-slate-950/40">
              <h4 class="text-xs font-bold uppercase tracking-wider text-slate-400 dark:text-slate-500 mb-3">
                Cost Breakdown
              </h4>

              <!-- Labor Cost Line -->
              <div class="flex items-center justify-between py-2 text-sm border-b border-slate-200/70 dark:border-slate-800">
                <span class="font-medium text-slate-600 dark:text-slate-400 flex items-center gap-2">
                  <Wrench class="h-4 w-4 text-sky-500" /> Labor Fee
                </span>
                <span class="font-bold text-slate-900 dark:text-slate-100">
                  {{ formatCurrency(getLaborCost(selectedItem)) }}
                </span>
              </div>

              <!-- Materials List -->
              <div class="py-2">
                <div class="flex items-center justify-between text-sm mb-2">
                  <span class="font-medium text-slate-600 dark:text-slate-400 flex items-center gap-2">
                    <Package class="h-4 w-4 text-emerald-500" /> Recorded Materials
                  </span>
                  <span class="font-bold text-slate-900 dark:text-slate-100">
                    {{ formatCurrency(getMaterialsTotal(selectedItem.id, selectedItem.materials)) }}
                  </span>
                </div>

                <div
                  v-if="getMaterialLines(selectedItem.id, selectedItem.materials).length > 0"
                  class="rounded-xl border border-slate-200 bg-white dark:border-slate-800 dark:bg-slate-900 overflow-hidden mt-2"
                >
                  <table class="w-full text-left text-xs divide-y divide-slate-100 dark:divide-slate-800">
                    <thead class="bg-slate-50 dark:bg-slate-800/60 font-semibold text-slate-500 dark:text-slate-400">
                      <tr>
                        <th class="px-3 py-2">Item</th>
                        <th class="px-3 py-2 text-center">Qty</th>
                        <th class="px-3 py-2 text-right">Unit Price</th>
                        <th class="px-3 py-2 text-right">Subtotal</th>
                      </tr>
                    </thead>
                    <tbody class="divide-y divide-slate-100 dark:divide-slate-800">
                      <tr v-for="line in getMaterialLines(selectedItem.id, selectedItem.materials)" :key="line.id">
                        <td class="px-3 py-2 font-medium text-slate-800 dark:text-slate-200">{{ line.name }}</td>
                        <td class="px-3 py-2 text-center text-slate-600 dark:text-slate-400">{{ line.qty }}</td>
                        <td class="px-3 py-2 text-right text-slate-600 dark:text-slate-400">{{ formatCurrency(line.unitPrice) }}</td>
                        <td class="px-3 py-2 text-right font-bold text-slate-900 dark:text-slate-100">{{ formatCurrency(line.subtotal) }}</td>
                      </tr>
                    </tbody>
                  </table>
                </div>
                <p v-else class="text-xs italic text-slate-400 dark:text-slate-500 mt-1 pl-6">
                  No materials recorded for this project.
                </p>
              </div>

              <!-- Grand Total Box -->
              <div class="mt-3 flex items-center justify-between rounded-xl bg-slate-900 px-4 py-3 text-white dark:bg-slate-800">
                <span class="text-xs font-bold uppercase tracking-wider text-slate-300">Total Project Cost</span>
                <span class="text-lg font-black text-white">
                  {{ formatCurrency(getGrandTotal(selectedItem)) }}
                </span>
              </div>
            </div>
          </div>

          <!-- Before / After Images (if available) -->
          <div
            v-if="(selectedItem.beforeImages?.length || 0) > 0 || (selectedItem.afterImages?.length || 0) > 0"
            class="rounded-2xl border border-slate-200 bg-slate-50/70 p-4 dark:border-slate-800 dark:bg-slate-950/40"
          >
            <h4 class="text-xs font-bold uppercase tracking-wider text-slate-400 dark:text-slate-500 mb-3">
              Project Field Photos
            </h4>
            <div class="grid grid-cols-1 gap-4 sm:grid-cols-2">
              <div v-if="selectedItem.beforeImages?.length">
                <p class="text-xs font-semibold text-slate-500 mb-2">Before Work</p>
                <div class="flex flex-wrap gap-2">
                  <a
                    v-for="(img, idx) in selectedItem.beforeImages"
                    :key="`before-${idx}`"
                    :href="resolveImageUrl(img)"
                    target="_blank"
                    rel="noreferrer"
                  >
                    <img
                      :src="resolveImageUrl(img)"
                      alt="Before work"
                      class="h-24 w-32 rounded-xl border border-slate-200 object-cover shadow-sm transition hover:scale-105"
                    />
                  </a>
                </div>
              </div>
              <div v-if="selectedItem.afterImages?.length">
                <p class="text-xs font-semibold text-slate-500 mb-2">After Completion</p>
                <div class="flex flex-wrap gap-2">
                  <a
                    v-for="(img, idx) in selectedItem.afterImages"
                    :key="`after-${idx}`"
                    :href="resolveImageUrl(img)"
                    target="_blank"
                    rel="noreferrer"
                  >
                    <img
                      :src="resolveImageUrl(img)"
                      alt="After completion"
                      class="h-24 w-32 rounded-xl border border-slate-200 object-cover shadow-sm transition hover:scale-105"
                    />
                  </a>
                </div>
              </div>
            </div>
          </div>
        </div>

        <!-- Footer -->
        <div class="mt-8 pt-4 border-t border-slate-100 dark:border-slate-800 flex justify-end">
          <button
            type="button"
            @click="closeDetails"
            class="rounded-xl border border-slate-200 bg-white px-6 py-2.5 text-sm font-semibold text-slate-700 shadow-xs hover:bg-slate-50 dark:border-slate-700 dark:bg-slate-800 dark:text-slate-300 dark:hover:bg-slate-700 transition"
          >
            Close
          </button>
        </div>
      </div>
    </div>
  </div>
</template>
