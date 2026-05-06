<script setup lang="ts">
import { computed, ref } from 'vue'

interface InventoryItem {
  id: string
  name: string
  quantity: number
  unitPrice: number
  supplier: string
  lowStockThreshold: number
}

interface Project {
  id: string
  name: string
  client: string
  status: 'ongoing' | 'completed'
  materialsCost: number
  laborCost: number
}

interface Sale {
  id: string
  amount: number
}

interface Staff {
  id: string
  name: string
  position: string
  hoursWorkedThisMonth: number
  overtimeHoursThisMonth: number
}

interface AttendanceRecord {
  id: string
  staffId: string
  staffName: string
  date: string
  checkInTime: string
  checkOutTime?: string
  hoursWorked: number
  overtimeHours: number
}

// Sample data
const inventory: InventoryItem[] = [
  { id: '1', name: 'Steel Rods (12mm)', quantity: 150, unitPrice: 350, supplier: 'Metro Steel Corp', lowStockThreshold: 20 },
  { id: '2', name: 'Welding Electrodes E6013', quantity: 8, unitPrice: 450, supplier: 'Weld Pro Supplies', lowStockThreshold: 10 },
  { id: '3', name: 'MIG Welding Wire', quantity: 45, unitPrice: 1200, supplier: 'Industrial Metals Inc', lowStockThreshold: 15 },
  { id: '4', name: 'Metal Sheets (4x8)', quantity: 25, unitPrice: 2800, supplier: 'Manila Metal Traders', lowStockThreshold: 10 },
  { id: '5', name: 'Angle Bar (2x2)', quantity: 60, unitPrice: 520, supplier: 'Metro Steel Corp', lowStockThreshold: 20 },
]

const projects: Project[] = [
  {
    id: '1',
    name: 'Steel Frame Fabrication',
    client: 'XYZ Construction',
    status: 'ongoing',
    materialsCost: 45000,
    laborCost: 33000,
  },
  {
    id: '2',
    name: 'Staircase Installation',
    client: 'ABC Hotels',
    status: 'completed',
    materialsCost: 18000,
    laborCost: 14000,
  },
  {
    id: '3',
    name: 'Gate & Fence Work',
    client: 'Industrial Park Dev',
    status: 'ongoing',
    materialsCost: 32000,
    laborCost: 21000,
  },
]

const sales: Sale[] = [
  { id: '1', amount: 8750 },
  { id: '2', amount: 6000 },
  { id: '3', amount: 15000 },
  { id: '4', amount: 12500 },
]

// Staff data for attendance and overtime reporting
const staffData: Staff[] = [
  { id: '1', name: 'Juan Cruz', position: 'Welder', hoursWorkedThisMonth: 165, overtimeHoursThisMonth: 12.5 },
  { id: '2', name: 'Maria Santos', position: 'Fabricator', hoursWorkedThisMonth: 160, overtimeHoursThisMonth: 0 },
  { id: '3', name: 'Carlos Reyes', position: 'Welder', hoursWorkedThisMonth: 168, overtimeHoursThisMonth: 8 },
  { id: '4', name: 'Rosa Dela Cruz', position: 'Inspector', hoursWorkedThisMonth: 158, overtimeHoursThisMonth: 0 },
]

const attendanceRecords: AttendanceRecord[] = [
  { id: '1', staffId: '1', staffName: 'Juan Cruz', date: '2026-04-30', checkInTime: '08:00 AM', checkOutTime: '05:30 PM', hoursWorked: 9.5, overtimeHours: 1.5 },
  { id: '2', staffId: '2', staffName: 'Maria Santos', date: '2026-04-30', checkInTime: '08:15 AM', checkOutTime: '05:00 PM', hoursWorked: 8.75, overtimeHours: 0 },
  { id: '3', staffId: '3', staffName: 'Carlos Reyes', date: '2026-04-30', checkInTime: '07:45 AM', checkOutTime: '04:45 PM', hoursWorked: 9, overtimeHours: 1 },
]

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
  attendanceRecords.filter((record) => isWithinSelectedRange(record.date)),
)

const totalInventoryValue = computed(() =>
  inventory.reduce((sum, item) => sum + item.quantity * item.unitPrice, 0),
)

const lowStockCount = computed(() =>
  inventory.filter((item) => item.quantity <= item.lowStockThreshold).length,
)

const totalProjectCosts = computed(() =>
  projects.reduce((sum, project) => sum + project.materialsCost + project.laborCost, 0),
)

const ongoingProjects = computed(() => projects.filter((p) => p.status === 'ongoing').length)
const completedProjects = computed(() => projects.filter((p) => p.status === 'completed').length)

const totalSalesRevenue = computed(() => sales.reduce((sum, sale) => sum + sale.amount, 0))

const netProfit = computed(() => totalSalesRevenue.value - totalProjectCosts.value)

const totalStaffHours = computed(() =>
  filteredAttendanceRecords.value.reduce((sum, record) => sum + record.hoursWorked, 0),
)

const totalOvertimeHours = computed(() =>
  filteredAttendanceRecords.value.reduce((sum, record) => sum + record.overtimeHours, 0),
)

const staffWithOvertimeCount = computed(
  () => new Set(filteredAttendanceRecords.value.filter((record) => record.overtimeHours > 0).map((record) => record.staffId)).size,
)

const averageOvertimePerStaff = computed(() => {
  const uniqueStaff = new Set(filteredAttendanceRecords.value.map((record) => record.staffId)).size
  return uniqueStaff > 0 ? Math.round((totalOvertimeHours.value / uniqueStaff) * 10) / 10 : 0
})

const averageHoursPerStaff = computed(() => {
  const uniqueStaff = new Set(filteredAttendanceRecords.value.map((record) => record.staffId)).size
  return uniqueStaff > 0 ? Math.round((totalStaffHours.value / uniqueStaff) * 100) / 100 : 0
})

function handleExportPDF(reportType: string) {
  if (hasInvalidDateRange.value) {
    alert('Invalid date range. Start Date must be on or before End Date.')
    return
  }
  alert(`Exporting ${reportType} from ${selectedStartDate.value} to ${selectedEndDate.value}... (Feature simulated for demo)`)
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
