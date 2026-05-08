<script setup lang="ts">
import { computed, onMounted, ref } from 'vue'
import api from '../../../services/api'
import { useBookingsStore } from '../../../stores/bookings'
import { useInventoryStore } from '../../../stores/inventory'
import { useModalStore } from '../../../stores/modal'
import { getLaborPrice } from '../../../constants/pricing'

interface AttendanceRecord {
  id: number
  email: string
  date: string
  hours_worked: number
  overtime_hours: number
}

const bookingsStore = useBookingsStore()
const inventoryStore = useInventoryStore()
const modalStore = useModalStore()
const attendanceRecords = ref<AttendanceRecord[]>([])

onMounted(async () => {
  await Promise.all([
    bookingsStore.fetchBookings(),
    inventoryStore.fetchInventory(),
  ])

  const { data } = await api.get<AttendanceRecord[]>('/attendance')
  attendanceRecords.value = Array.isArray(data) ? data : []
})

const today = new Date()
const defaultStart = `${today.getFullYear()}-${String(today.getMonth() + 1).padStart(2, '0')}-01`
const defaultEnd = `${today.getFullYear()}-${String(today.getMonth() + 1).padStart(2, '0')}-${String(today.getDate()).padStart(2, '0')}`
const selectedStartDate = ref(defaultStart)
const selectedEndDate = ref(defaultEnd)

const normalizedStart = computed(() => new Date(`${selectedStartDate.value}T00:00:00`))
const normalizedEnd = computed(() => new Date(`${selectedEndDate.value}T23:59:59.999`))

const hasInvalidDateRange = computed(() => normalizedStart.value > normalizedEnd.value)

function isWithinSelectedRange(isoDate: string) {
  const d = new Date(`${isoDate}T00:00:00`)
  return d >= normalizedStart.value && d <= normalizedEnd.value
}

const filteredAttendanceRecords = computed(() =>
  attendanceRecords.value.filter((record) => isWithinSelectedRange(record.date)),
)

const totalInventoryValue = computed(() =>
  inventoryStore.items.reduce((sum, item) => sum + item.quantity * item.unitPrice, 0),
)

const lowStockCount = computed(() =>
  inventoryStore.items.filter((item) => item.quantity <= item.lowStockThreshold).length,
)

const inventory = computed(() => inventoryStore.items)

const projects = computed(() =>
  bookingsStore.bookings
    .filter((b) => b.status !== 'cancelled')
    .map((b) => ({
      id: String(b.id),
      status: b.status === 'completed' ? 'completed' : 'ongoing',
      materialsCost: Number(b.materialCost ?? 0),
      laborCost: getLaborPrice(b.projectType),
      totalPrice: getLaborPrice(b.projectType) + Number(b.materialCost ?? 0),
    })),
)

const totalProjectCosts = computed(() =>
  projects.value.reduce((sum, project) => sum + project.materialsCost + project.laborCost, 0),
)

const ongoingProjects = computed(() => projects.value.filter((p) => p.status === 'ongoing').length)
const completedProjects = computed(() => projects.value.filter((p) => p.status === 'completed').length)

const totalSalesRevenue = computed(() =>
  projects.value.reduce((sum, project) => sum + (project.totalPrice || project.materialsCost + project.laborCost), 0),
)

const netProfit = computed(() => totalSalesRevenue.value - totalProjectCosts.value)

const totalStaffHours = computed(() =>
  filteredAttendanceRecords.value.reduce((sum, record) => sum + Number(record.hours_worked ?? 0), 0),
)

const totalOvertimeHours = computed(() =>
  filteredAttendanceRecords.value.reduce((sum, record) => sum + Number(record.overtime_hours ?? 0), 0),
)

const staffWithOvertimeCount = computed(
  () => new Set(filteredAttendanceRecords.value.filter((record) => Number(record.overtime_hours ?? 0) > 0).map((record) => record.email)).size,
)

const staffData = computed(() => {
  const emails = new Set(filteredAttendanceRecords.value.map((record) => record.email))
  return Array.from(emails)
})

const averageOvertimePerStaff = computed(() => {
  const uniqueStaff = new Set(filteredAttendanceRecords.value.map((record) => record.email)).size
  return uniqueStaff > 0 ? Math.round((totalOvertimeHours.value / uniqueStaff) * 10) / 10 : 0
})

const averageHoursPerStaff = computed(() => {
  const uniqueStaff = new Set(filteredAttendanceRecords.value.map((record) => record.email)).size
  return uniqueStaff > 0 ? Math.round((totalStaffHours.value / uniqueStaff) * 100) / 100 : 0
})

function handleExportPDF(reportType: string) {
  if (hasInvalidDateRange.value) {
    modalStore.open({
      title: 'Invalid date range',
      message: 'Start Date must be on or before End Date.',
      variant: 'warning',
    })
    return
  }
  modalStore.open({
    title: reportType,
    message: `Exporting ${reportType} from ${selectedStartDate.value} to ${selectedEndDate.value}... (Feature simulated for demo)`,
    variant: 'info',
  })
}

function formatCurrency(value: number) {
  return `₱${value.toLocaleString('en-PH', { minimumFractionDigits: 2 })}`
}
</script>

<template>
  <section class="space-y-6">
    <div>
      <h3 class="mb-1 text-2xl font-semibold text-gray-900">Reports</h3>
      <p class="text-sm text-gray-600">Generate and export business reports</p>
    </div>

    <div class="rounded-lg border border-gray-200 bg-white p-4">
      <div class="grid grid-cols-1 gap-3 md:grid-cols-2 lg:grid-cols-4">
        <div>
          <label class="mb-1 block text-xs font-semibold uppercase tracking-wide text-gray-600">Start Date</label>
          <input v-model="selectedStartDate" type="date" class="w-full rounded-lg border border-gray-300 px-3 py-2" />
        </div>
        <div>
          <label class="mb-1 block text-xs font-semibold uppercase tracking-wide text-gray-600">End Date</label>
          <input v-model="selectedEndDate" type="date" class="w-full rounded-lg border border-gray-300 px-3 py-2" />
        </div>
        <div class="lg:col-span-2 flex items-end">
          <p class="text-sm text-gray-600">
            Report range: <span class="font-semibold text-gray-900">{{ selectedStartDate }}</span>
            to
            <span class="font-semibold text-gray-900">{{ selectedEndDate }}</span>
          </p>
        </div>
      </div>
      <p v-if="hasInvalidDateRange" class="mt-2 text-sm text-red-600">
        Start Date must be earlier than or equal to End Date.
      </p>
    </div>

    <div class="grid grid-cols-1 gap-6 md:grid-cols-2 lg:grid-cols-3 2xl:grid-cols-4">
      <!-- Stock-In Report Card -->
      <div class="flex min-h-90 flex-col rounded-lg border border-gray-200 bg-white p-7">
        <div class="mb-4 flex items-center justify-between">
          <h3 class="text-gray-900">Stock-In Report</h3>
          <div class="flex h-12 w-12 items-center justify-center rounded-lg bg-blue-100">
            <svg class="h-6 w-6 text-blue-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path
                stroke-linecap="round"
                stroke-linejoin="round"
                stroke-width="2"
                d="M20 7l-8-4-8 4m16 0l-8 4m8-4v10l-8 4m0-10L4 7m8 4v10M4 7v10l8 4"
              />
            </svg>
          </div>
        </div>
        <div class="mb-6 flex-1 space-y-3">
          <div class="flex justify-between text-sm">
            <span class="text-gray-600">Total Stocked Items:</span>
            <span class="text-gray-900">{{ inventory.length }}</span>
          </div>
          <div class="flex justify-between text-sm">
            <span class="text-gray-600">Low Stock Items:</span>
            <span class="text-orange-600">{{ lowStockCount }}</span>
          </div>
          <div class="flex justify-between text-sm">
            <span class="text-gray-600">Total Stock Value:</span>
            <span class="text-gray-900">{{ formatCurrency(totalInventoryValue) }}</span>
          </div>
        </div>
        <button
          type="button"
          class="mt-auto w-full rounded-lg bg-blue-600 px-4 py-2.5 font-semibold text-white transition-colors hover:bg-blue-700"
          @click="handleExportPDF('Stock-In Report')"
        >
          <svg class="mr-2 inline h-5 w-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path
              stroke-linecap="round"
              stroke-linejoin="round"
              stroke-width="2"
              d="M12 10v6m0 0l-3-3m3 3l3-3m2 8H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z"
            />
          </svg>
          Export PDF
        </button>
      </div>

      <!-- Financial Summary Card -->
      <div class="flex min-h-90 flex-col rounded-lg border border-gray-200 bg-white p-7">
        <div class="mb-4 flex items-center justify-between">
          <h3 class="text-gray-900">Financial Summary</h3>
          <div class="flex h-12 w-12 items-center justify-center rounded-lg bg-purple-100">
            <svg class="h-6 w-6 text-purple-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path
                stroke-linecap="round"
                stroke-linejoin="round"
                stroke-width="2"
                d="M9 19v-6a2 2 0 00-2-2H5a2 2 0 00-2 2v6a2 2 0 002 2h2a2 2 0 002-2zm0 0V9a2 2 0 012-2h2a2 2 0 012 2v10m-6 0a2 2 0 002 2h2a2 2 0 002-2m0 0V5a2 2 0 012-2h2a2 2 0 012 2v14a2 2 0 01-2 2h-2a2 2 0 01-2-2z"
              />
            </svg>
          </div>
        </div>
        <div class="mb-6 flex-1 space-y-3">
          <div class="flex justify-between text-sm">
            <span class="text-gray-600">Total Projects:</span>
            <span class="text-gray-900">{{ projects.length }}</span>
          </div>
          <div class="flex justify-between text-sm">
            <span class="text-gray-600">Active / Completed:</span>
            <span class="text-gray-900">{{ ongoingProjects }} / {{ completedProjects }}</span>
          </div>
          <div class="flex justify-between text-sm">
            <span class="text-gray-600">Total Expenses:</span>
            <span class="text-gray-900">{{ formatCurrency(totalProjectCosts) }}</span>
          </div>
          <div class="flex justify-between text-sm">
            <span class="text-gray-600">Sales Revenue:</span>
            <span class="text-green-600">{{ formatCurrency(totalSalesRevenue) }}</span>
          </div>
          <div class="flex justify-between text-sm border-t border-gray-200 pt-3">
            <span class="text-gray-600 font-semibold">Net Profit:</span>
            <span class="text-gray-900 font-semibold">{{ formatCurrency(netProfit) }}</span>
          </div>
        </div>
        <button
          type="button"
          class="mt-auto w-full rounded-lg bg-purple-600 px-4 py-2.5 font-semibold text-white transition-colors hover:bg-purple-700"
          @click="handleExportPDF('Financial Summary')"
        >
          <svg class="mr-2 inline h-5 w-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path
              stroke-linecap="round"
              stroke-linejoin="round"
              stroke-width="2"
              d="M12 10v6m0 0l-3-3m3 3l3-3m2 8H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z"
            />
          </svg>
          Export PDF
        </button>
      </div>

      <!-- Staff Attendance Report Card -->
      <div class="flex min-h-90 flex-col rounded-lg border border-gray-200 bg-white p-7">
        <div class="mb-4 flex items-center justify-between">
          <h3 class="text-gray-900">Staff Attendance</h3>
          <div class="flex h-12 w-12 items-center justify-center rounded-lg bg-indigo-100">
            <svg class="h-6 w-6 text-indigo-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path
                stroke-linecap="round"
                stroke-linejoin="round"
                stroke-width="2"
                d="M12 4.354a4 4 0 110 5.292m0 0H8.646a4 4 0 010-5.292m3.354 0V3m0 16h-1a2 2 0 01-2-2V7a2 2 0 012-2h1m0 0h1a2 2 0 012 2v12a2 2 0 01-2 2h-1m0 0V3m6 0h-1a2 2 0 00-2 2v12a2 2 0 002 2h1"
              />
            </svg>
          </div>
        </div>
        <div class="mb-6 flex-1 space-y-3">
          <div class="flex justify-between text-sm">
            <span class="text-gray-600">Total Staff:</span>
            <span class="text-gray-900">{{ staffData.length }}</span>
          </div>
          <div class="flex justify-between text-sm">
            <span class="text-gray-600">Total Hours (Month):</span>
            <span class="text-gray-900">{{ totalStaffHours }}h</span>
          </div>
          <div class="flex justify-between text-sm">
            <span class="text-gray-600">Avg Hours/Staff:</span>
            <span class="text-gray-900">{{ averageHoursPerStaff }}h</span>
          </div>
          <div class="border-t border-gray-200 pt-3">
            <div class="flex justify-between text-sm">
              <span class="text-gray-600">Total Overtime (Month):</span>
              <span class="font-semibold text-red-600">{{ totalOvertimeHours }}h</span>
            </div>
            <div class="mt-2 flex justify-between text-sm">
              <span class="text-gray-600">Staff with OT:</span>
              <span class="text-gray-900">{{ staffWithOvertimeCount }}</span>
            </div>
            <div class="mt-2 flex justify-between text-sm">
              <span class="text-gray-600">Avg OT/Staff:</span>
              <span class="text-red-600">{{ averageOvertimePerStaff }}h</span>
            </div>
          </div>
        </div>
        <button
          type="button"
          class="mt-auto w-full rounded-lg bg-indigo-600 px-4 py-2.5 font-semibold text-white transition-colors hover:bg-indigo-700"
          @click="handleExportPDF('Staff Attendance Report')"
        >
          <svg class="mr-2 inline h-5 w-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path
              stroke-linecap="round"
              stroke-linejoin="round"
              stroke-width="2"
              d="M12 10v6m0 0l-3-3m3 3l3-3m2 8H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z"
            />
          </svg>
          Export PDF
        </button>
      </div>
    </div>

  </section>
</template>
