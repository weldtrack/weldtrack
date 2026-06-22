<script setup lang="ts">
import { computed, onMounted } from 'vue'
import Layout from './DashboardLayout.vue'
import InventoryManagement from './components/admin/InventoryManagement.vue'
import ProjectHistory from './components/shared/ProjectHistory.vue'
import Reports from './components/admin/Reports.vue'
import BookingApproval from './components/admin/BookingApproval.vue'
import StaffWorkspace from './components/staff/StaffWorkspace.vue'
import ServiceFeedback from './components/shared/ServiceFeedback.vue'
import ServiceManagement from './components/admin/ServiceManagement.vue'
import AdminUsers from './components/admin/AdminUsers.vue'
import { useAdminSectionStore } from '../../stores/adminSection'
import { type AdminSection as AdminSectionType } from '../../types/adminSection'
import { useBookingsStore } from '../../stores/bookings'
import { getServicePriceDisplay } from '../../services/servicePricing'

type AdminSection = AdminSectionType

const adminSectionStore = useAdminSectionStore()
const currentSection = computed<AdminSection>(() => adminSectionStore.section)
const bookingsStore = useBookingsStore()

onMounted(() => {
  bookingsStore.fetchBookings()
})

const bookings = computed(() => bookingsStore.bookings)

function formatCurrency(value: number) {
  return `₱${value.toLocaleString('en-PH', { minimumFractionDigits: 2 })}`
}

function formatDate(value?: string) {
  if (!value) return '-'
  const d = new Date(value)
  if (Number.isNaN(d.getTime())) return '-'
  return d.toLocaleDateString('en-PH', {
    year: 'numeric',
    month: 'short',
    day: '2-digit',
  })
}

function getBookingCost(booking: { projectType?: string; estimatedCost?: number; materialCost?: number }) {
  return getServicePriceDisplay(booking.projectType || '', booking.estimatedCost) + Number(booking.materialCost ?? 0)
}

const customers = computed(() => {
  const seen = new Set<string>()
  return bookings.value.filter((booking) => {
    const key = (booking.email || booking.customerName || '').trim().toLowerCase()
    if (!key || seen.has(key)) return false
    seen.add(key)
    return true
  })
})

const totalCustomers = computed(() => customers.value.length)

const newCustomersThisMonth = computed(() => {
  const now = new Date()
  const firstSeen = new Map<string, number>()

  bookings.value.forEach((booking) => {
    const key = (booking.email || booking.customerName || '').trim().toLowerCase()
    if (!key || !booking.createdDate) return
    const ts = new Date(booking.createdDate).getTime()
    if (Number.isNaN(ts)) return
    const prev = firstSeen.get(key)
    if (prev === undefined || ts < prev) {
      firstSeen.set(key, ts)
    }
  })

  let count = 0
  firstSeen.forEach((ts) => {
    const d = new Date(ts)
    if (d.getMonth() === now.getMonth() && d.getFullYear() === now.getFullYear()) {
      count += 1
    }
  })
  return count
})

const ongoingProjects = computed(() => bookings.value.filter((booking) => booking.status === 'confirmed').length)

const completedProjects = computed(() => bookings.value.filter((booking) => booking.status === 'completed').length)

const completedBookings = computed(() => bookings.value.filter((booking) => booking.status === 'completed'))

const totalProjectValue = computed(() =>
  completedBookings.value.reduce((sum, booking) => sum + getBookingCost(booking), 0),
)

const recentCompletedProjects = computed(() =>
  bookings.value
    .filter((booking) => booking.status === 'completed')
    .map((booking) => ({
      id: booking.id,
      endDate: booking.scheduleDate || booking.createdDate,
      name: booking.projectType,
      client: booking.customerName || booking.email || '-',
      materialsCost: Number(booking.materialCost ?? 0),
      laborCost: getServicePriceDisplay(booking.projectType, booking.estimatedCost),
      totalCost: getBookingCost(booking),
    }))
    .sort((a, b) => new Date(b.endDate || 0).getTime() - new Date(a.endDate || 0).getTime()),
)

const monthlyExpenses = computed(() => {
  const now = new Date()
  const months = Array.from({ length: 6 }).map((_, i) => {
    const d = new Date(now.getFullYear(), now.getMonth() - (5 - i), 1)
    return {
      month: d.toLocaleDateString('en-PH', { month: 'short' }),
      year: d.getFullYear(),
      monthIndex: d.getMonth(),
      amount: 0,
    }
  })

  completedBookings.value.forEach((booking) => {
    const rawDate = booking.scheduleDate || booking.createdDate
    if (!rawDate) return
    const d = new Date(rawDate)
    if (Number.isNaN(d.getTime())) return
    const target = months.find((m) => m.year === d.getFullYear() && m.monthIndex === d.getMonth())
    if (!target) return
    target.amount += getBookingCost(booking)
  })

  return months.map(({ month, amount }) => ({ month, amount }))
})

const projectStatusBreakdown = computed(() => {
  const completed = bookings.value.filter((booking) => booking.status === 'completed').length
  const ongoing = bookings.value.filter((booking) => booking.status === 'confirmed').length
  const pending = bookings.value.filter((booking) => booking.status === 'pending').length
  const total = completed + ongoing + pending

  const toPercent = (value: number) => (total > 0 ? Math.round((value / total) * 100) : 0)

  return [
    { name: 'Completed', value: toPercent(completed), color: '#16a34a' },
    { name: 'Ongoing', value: toPercent(ongoing), color: '#2563eb' },
    { name: 'Pending', value: toPercent(pending), color: '#f59e0b' },
  ]
})



const lineChart = computed(() => {
  const width = 640
  const height = 300
  const paddingX = 40
  const paddingY = 32
  const values = monthlyExpenses.value.map((entry) => entry.amount)
  const minValue = 0
  const maxValue = Math.max(...values, 1)
  const chartWidth = width - paddingX * 2
  const chartHeight = height - paddingY * 2

  const points = monthlyExpenses.value.map((entry, index) => {
    const x = paddingX + (chartWidth / Math.max(monthlyExpenses.value.length - 1, 1)) * index
    const ratio = (entry.amount - minValue) / (maxValue - minValue || 1)
    const y = height - paddingY - ratio * chartHeight
    return { x, y, month: entry.month, amount: entry.amount }
  })

  const linePath = points.map((point) => `${point.x},${point.y}`).join(' ')
  const gridValues = [0, 0.25, 0.5, 0.75, 1]

  return {
    width,
    height,
    points,
    linePath,
    gridValues,
    maxValue,
  }
})

const pieStyle = computed(() => {
  const total = projectStatusBreakdown.value.reduce((sum, item) => sum + item.value, 0)
  let start = 0
  const segments = projectStatusBreakdown.value.map((item) => {
    const end = start + (item.value / total) * 100
    const segment = `${item.color} ${start}% ${end}%`
    start = end
    return segment
  })

  return `conic-gradient(${segments.join(', ')})`
})


import { LayoutDashboard } from 'lucide-vue-next'

</script>

<template>
  <Layout title="Admin Dashboard">
    <div v-if="currentSection === 'dashboard'" class="space-y-6">
      <div class="flex items-start gap-3">
        <div class="flex h-12 w-12 items-center justify-center rounded-xl bg-linear-to-br from-sky-50 to-sky-25 ring-1 ring-sky-100">
          <LayoutDashboard class="h-6 w-6 text-sky-600" />
        </div>
        <div>
          <h3 class="mb-1 text-2xl font-semibold text-gray-900">Booking Approval</h3>
          <p class="text-sm text-gray-600">Review customer requests and approve bookings</p>
        </div>
      </div>

      <div class="grid grid-cols-1 gap-4 sm:grid-cols-3">
        <div class="rounded-lg bg-sky-50 p-6">
          <p class="text-xs uppercase tracking-wide text-sky-600 font-semibold">Completed Projects</p>
          <p class="mt-2 text-2xl font-bold text-gray-900">{{ completedProjects }}</p>
        </div>

        <div class="rounded-lg bg-sky-50 p-6">
          <p class="text-xs uppercase tracking-wide text-sky-600 font-semibold">Ongoing Projects</p>
          <p class="mt-2 text-2xl font-bold text-gray-900">{{ ongoingProjects }}</p>
        </div>

        <div class="rounded-lg bg-sky-50 p-6">
          <p class="text-xs uppercase tracking-wide text-sky-600 font-semibold">Total Project Value</p>
          <p class="mt-2 text-2xl font-bold text-gray-900">{{ formatCurrency(totalProjectValue) }}</p>
        </div>

        <div class="rounded-lg bg-sky-50 p-6">
          <p class="text-xs uppercase tracking-wide text-sky-600 font-semibold">Total Customers</p>
          <p class="mt-2 text-2xl font-bold text-gray-900">{{ totalCustomers }}</p>
        </div>

        <div class="rounded-lg bg-sky-50 p-6">
          <p class="text-xs uppercase tracking-wide text-sky-600 font-semibold">New Customers This Month</p>
          <p class="mt-2 text-2xl font-bold text-gray-900">{{ newCustomersThisMonth }}</p>
        </div>
      </div>

      <div class="grid grid-cols-1 gap-6 xl:grid-cols-2">
        <div class="rounded-lg border border-gray-200 bg-white p-6">
          <h3 class="mb-4 text-lg font-semibold text-gray-900">Monthly Project Cost Trend</h3>
          <svg class="h-75 w-full" viewBox="0 0 640 300" role="img" aria-label="Monthly project cost trend chart">
            <line v-for="grid in lineChart.gridValues" :key="grid" x1="40" :x2="600" :y1="32 + (236 * grid)"
              :y2="32 + (236 * grid)" stroke="#e5e7eb" stroke-dasharray="4 4" />

            <polyline fill="none" stroke="#10b981" stroke-width="3" stroke-linecap="round" stroke-linejoin="round"
              :points="lineChart.linePath" />

            <circle v-for="point in lineChart.points" :key="point.month" :cx="point.x" :cy="point.y" r="5"
              fill="#10b981" />

            <text v-for="point in lineChart.points" :key="`${point.month}-label`" :x="point.x" y="286"
              text-anchor="middle" class="fill-gray-500 text-xs">
              {{ point.month }}
            </text>
          </svg>
        </div>

        <div class="rounded-lg border border-gray-200 bg-white p-6">
          <h3 class="mb-4 text-lg font-semibold text-gray-900">Project Status Breakdown</h3>
          <div class="flex flex-col items-center gap-6 md:flex-row md:items-center md:justify-between">
            <div class="relative flex h-64 w-64 items-center justify-center">
              <div class="h-56 w-56 rounded-full" :style="{ background: pieStyle }"></div>
              <div class="absolute h-32 w-32 rounded-full bg-white shadow-inner"></div>
            </div>

            <div class="w-full space-y-3 md:max-w-xs">
              <div v-for="item in projectStatusBreakdown" :key="item.name"
                class="flex items-center justify-between rounded-lg border border-gray-200 px-4 py-3">
                <div class="flex items-center gap-3">
                  <span class="h-3 w-3 rounded-full" :style="{ backgroundColor: item.color }"></span>
                  <span class="text-sm font-medium text-gray-700">{{ item.name }}</span>
                </div>
                <span class="text-sm text-gray-500">{{ item.value }}%</span>
              </div>
            </div>
          </div>
        </div>
      </div>

      <div class="rounded-lg border border-gray-200 bg-white p-6">
        <h3 class="mb-4 text-lg font-semibold text-gray-900">Recent Completed Projects</h3>
        <div class="overflow-x-auto">
          <table class="w-full min-w-180">
            <thead>
              <tr class="border-b border-gray-200 text-left">
                <th class="px-4 py-3 font-semibold text-gray-700">Completed On</th>
                <th class="px-4 py-3 font-semibold text-gray-700">Project</th>
                <th class="px-4 py-3 font-semibold text-gray-700">Client</th>
                <th class="px-4 py-3 font-semibold text-gray-700">Materials</th>
                <th class="px-4 py-3 font-semibold text-gray-700">Labor</th>
                <th class="px-4 py-3 font-semibold text-gray-700">Total Cost</th>
              </tr>
            </thead>
            <tbody>
              <tr v-for="project in recentCompletedProjects.slice(0, 5)" :key="project.id"
                class="border-b border-gray-100 hover:bg-gray-50">
                <td class="px-4 py-3 text-gray-700">{{ formatDate(project.endDate) }}</td>
                <td class="px-4 py-3 font-medium text-gray-900">{{ project.name }}</td>
                <td class="px-4 py-3 text-gray-700">{{ project.client }}</td>
                <td class="px-4 py-3 text-gray-900">{{ formatCurrency(project.materialsCost) }}</td>
                <td class="px-4 py-3 text-gray-900">{{ formatCurrency(project.laborCost) }}</td>
                <td class="px-4 py-3 text-gray-900">{{ formatCurrency(project.totalCost) }}</td>
              </tr>
            </tbody>
          </table>
        </div>
      </div>


    </div>

    <InventoryManagement v-else-if="currentSection === 'inventory'" />
    <ServiceManagement v-else-if="currentSection === 'services'" />
    <ProjectHistory v-else-if="currentSection === 'projects'" />
    <BookingApproval v-else-if="currentSection === 'booking'" />
    <ServiceFeedback v-else-if="currentSection === 'feedback'" :is-admin="true" />
    <Reports v-else-if="currentSection === 'reports'" />
    <AdminUsers v-else-if="currentSection === 'users'" />
    <StaffWorkspace
      v-else-if="currentSection === 'staff' || currentSection === 'staff-attendance' || currentSection === 'staff-tasks' || currentSection === 'staff-contributions' || currentSection === 'staff-create'" />
  </Layout>
</template>
