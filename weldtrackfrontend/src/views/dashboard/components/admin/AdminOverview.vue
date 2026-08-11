<script setup lang="ts">
import { computed, onMounted, ref } from 'vue'
import LocalLoader from '../../../../components/ui/LocalLoader.vue'
import { LayoutDashboard, CheckCircle2, Clock, DollarSign, Users, UserPlus } from 'lucide-vue-next'
import { useBookingsStore } from '../../../../stores/bookings'
import { getServicePriceDisplay } from '../../../../services/servicePricing'
import api from '../../../../api/api'
import type { UserRead } from '../../../../types/auth'

const bookingsStore = useBookingsStore()

const isLoading = ref(true)
const users = ref<UserRead[]>([])

onMounted(async () => {
  isLoading.value = true
  try {
    const [, usersResponse] = await Promise.all([
      bookingsStore.fetchBookings(),
      api.get<UserRead[]>('/auth/admin/users'),
    ])
    users.value = Array.isArray(usersResponse.data) ? usersResponse.data : []
  } finally {
    isLoading.value = false
  }
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

function getBookingCost(booking: { projectType?: string; estimatedCost?: number; materialCost?: number; totalPrice?: number }) {
  return Number(booking.totalPrice ?? (getServicePriceDisplay(booking.projectType || '', booking.estimatedCost) + Number(booking.materialCost ?? 0)))
}

const customers = computed(() => users.value.filter((user) => user.role === 'customer'))

const totalCustomers = computed(() => customers.value.length)

const newCustomersThisMonth = computed(() => {
  const now = new Date()
  return customers.value.filter((customer) => {
    const created = new Date(customer.created_at)
    return !Number.isNaN(created.getTime())
      && created.getMonth() === now.getMonth()
      && created.getFullYear() === now.getFullYear()
  }).length
})

const ongoingProjects = computed(() => bookings.value.filter((booking) => booking.status === 'confirmed' || booking.status === 'in-progress').length)

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

const monthlyRevenue = computed(() => {
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
  const ongoing = bookings.value.filter((booking) => booking.status === 'confirmed' || booking.status === 'in-progress').length
  const pending = bookings.value.filter((booking) => booking.status === 'pending').length
  const total = completed + ongoing + pending

  const toPercent = (value: number) => (total > 0 ? parseFloat(((value / total) * 100).toFixed(1)) : 0)

  return [
    { name: 'Completed', value: toPercent(completed), count: completed, color: "#10b981" },
    { name: 'Ongoing', value: toPercent(ongoing), count: ongoing, color: "#0284c7" },
    { name: 'Pending', value: toPercent(pending), count: pending, color: "#f59e0b" },
  ]
})

const lineChart = computed(() => {
  const width = 640
  const height = 260
  const paddingX = 45
  const paddingY = 30
  const values = monthlyRevenue.value.map((entry) => entry.amount)
  const minValue = 0
  const maxValue = Math.max(...values, 1000)
  const chartWidth = width - paddingX * 2
  const chartHeight = height - paddingY * 2

  const points = monthlyRevenue.value.map((entry, index) => {
    const x = paddingX + (chartWidth / Math.max(monthlyRevenue.value.length - 1, 1)) * index
    const ratio = (entry.amount - minValue) / (maxValue - minValue || 1)
    const y = height - paddingY - ratio * chartHeight
    return { x, y, month: entry.month, amount: entry.amount }
  })

  const linePath = points.map((point) => `${point.x},${point.y}`).join(' ')
  const areaPath = points.length > 0
    ? `${points[0].x},${height - paddingY} ${linePath} ${points[points.length - 1].x},${height - paddingY}`
    : ''
  const gridValues = [0, 0.33, 0.66, 1]

  return {
    width,
    height,
    points,
    linePath,
    areaPath,
    gridValues,
    maxValue,
  }
})

const pieStyle = computed(() => {
  const items = projectStatusBreakdown.value
  const total = items.reduce((sum, item) => sum + item.value, 0)

  if (!total) return 'none'

  let start = 0
  const segments = items.map((item) => {
    const end = start + (item.value / total) * 100
    const segment = `${item.color} ${start}% ${end}%`
    start = end
    return segment
  })

  return `conic-gradient(${segments.join(', ')})`
})
</script>

<template>
  <div class="space-y-6 relative">
    <LocalLoader v-if="isLoading" />

    <!-- Header -->
    <div class="flex items-start gap-3">
      <div class="flex h-12 w-12 items-center justify-center">
        <LayoutDashboard class="dashboard-view-icon h-6 w-6 text-sky-600 dark:text-sky-400" />
      </div>
      <div>
        <h3 class="text-2xl font-semibold text-slate-900 dark:text-slate-100">Admin Dashboard</h3>
        <p class="text-sm text-slate-600 dark:text-slate-400">Executive overview of system activity, metrics, and financials</p>
      </div>
    </div>

    <!-- Top KPI Cards Grid -->
    <div class="grid grid-cols-1 gap-4 sm:grid-cols-2 lg:grid-cols-3 xl:grid-cols-5">
      <!-- Completed Projects -->
      <div class="group rounded-2xl border border-emerald-200 bg-emerald-50/60 p-5 shadow-xs transition-all hover:border-emerald-300 dark:border-emerald-900/50 dark:bg-emerald-950/40">
        <div class="flex items-center justify-between">
          <span class="text-xs font-bold uppercase tracking-wider text-emerald-700 dark:text-emerald-300">Completed</span>
          <div class="flex h-8 w-8 items-center justify-center rounded-xl bg-emerald-100 text-emerald-700 dark:bg-emerald-900/60 dark:text-emerald-300">
            <CheckCircle2 class="h-4 w-4" />
          </div>
        </div>
        <p class="mt-3 text-3xl font-black text-slate-900 dark:text-slate-100">{{ completedProjects }}</p>
        <p class="mt-1 text-xs text-slate-500 dark:text-slate-400 font-medium">Finished projects</p>
      </div>

      <!-- Ongoing Projects -->
      <div class="group rounded-2xl border border-sky-200 bg-sky-50/60 p-5 shadow-xs transition-all hover:border-sky-300 dark:border-sky-900/50 dark:bg-sky-950/40">
        <div class="flex items-center justify-between">
          <span class="text-xs font-bold uppercase tracking-wider text-sky-700 dark:text-sky-300">Ongoing</span>
          <div class="flex h-8 w-8 items-center justify-center rounded-xl bg-sky-100 text-sky-700 dark:bg-sky-900/60 dark:text-sky-300">
            <Clock class="h-4 w-4" />
          </div>
        </div>
        <p class="mt-3 text-3xl font-black text-slate-900 dark:text-slate-100">{{ ongoingProjects }}</p>
        <p class="mt-1 text-xs text-slate-500 dark:text-slate-400 font-medium">In progress or confirmed</p>
      </div>

      <!-- Total Revenue -->
      <div class="group rounded-2xl border border-indigo-200 bg-indigo-50/60 p-5 shadow-xs transition-all hover:border-indigo-300 dark:border-indigo-900/50 dark:bg-indigo-950/40">
        <div class="flex items-center justify-between">
          <span class="text-xs font-bold uppercase tracking-wider text-indigo-700 dark:text-indigo-300">Total Value</span>
          <div class="flex h-8 w-8 items-center justify-center rounded-xl bg-indigo-100 text-indigo-700 dark:bg-indigo-900/60 dark:text-indigo-300">
            <DollarSign class="h-4 w-4" />
          </div>
        </div>
        <p class="mt-3 text-2xl font-black text-slate-900 dark:text-slate-100 truncate" :title="formatCurrency(totalProjectValue)">
          {{ formatCurrency(totalProjectValue) }}
        </p>
        <p class="mt-1 text-xs text-slate-500 dark:text-slate-400 font-medium">Completed projects revenue</p>
      </div>

      <!-- Total Customers -->
      <div class="group rounded-2xl border border-purple-200 bg-purple-50/60 p-5 shadow-xs transition-all hover:border-purple-300 dark:border-purple-900/50 dark:bg-purple-950/40">
        <div class="flex items-center justify-between">
          <span class="text-xs font-bold uppercase tracking-wider text-purple-700 dark:text-purple-300">Customers</span>
          <div class="flex h-8 w-8 items-center justify-center rounded-xl bg-purple-100 text-purple-700 dark:bg-purple-900/60 dark:text-purple-300">
            <Users class="h-4 w-4" />
          </div>
        </div>
        <p class="mt-3 text-3xl font-black text-slate-900 dark:text-slate-100">{{ totalCustomers }}</p>
        <p class="mt-1 text-xs text-slate-500 dark:text-slate-400 font-medium">Total registered clients</p>
      </div>

      <!-- New Customers -->
      <div class="group rounded-2xl border border-amber-200 bg-amber-50/60 p-5 shadow-xs transition-all hover:border-amber-300 dark:border-amber-900/50 dark:bg-amber-950/40">
        <div class="flex items-center justify-between">
          <span class="text-xs font-bold uppercase tracking-wider text-amber-700 dark:text-amber-300">New Clients</span>
          <div class="flex h-8 w-8 items-center justify-center rounded-xl bg-amber-100 text-amber-700 dark:bg-amber-900/60 dark:text-amber-300">
            <UserPlus class="h-4 w-4" />
          </div>
        </div>
        <p class="mt-3 text-3xl font-black text-slate-900 dark:text-slate-100">{{ newCustomersThisMonth }}</p>
        <p class="mt-1 text-xs text-slate-500 dark:text-slate-400 font-medium">Added this month</p>
      </div>
    </div>

    <!-- Charts Section -->
    <div class="grid grid-cols-1 gap-6 xl:grid-cols-2">
      <!-- Line Chart Card -->
      <div class="rounded-2xl border border-slate-200 bg-white p-6 shadow-xs dark:border-slate-800 dark:bg-slate-900">
        <div class="flex items-center justify-between mb-4">
          <div>
            <h4 class="text-base font-bold text-slate-900 dark:text-slate-100">Completed Project Value</h4>
            <p class="text-xs text-slate-500 dark:text-slate-400">Recorded completed-booking totals grouped by scheduled month</p>
          </div>
        </div>

        <div class="relative w-full">
          <svg class="h-64 w-full" viewBox="0 0 640 260" role="img" aria-label="Monthly revenue trend chart">
            <defs>
              <linearGradient id="chartGradient" x1="0" y1="0" x2="0" y2="1">
                <stop offset="0%" stop-color="#0284c7" stop-opacity="0.3" />
                <stop offset="100%" stop-color="#0284c7" stop-opacity="0.0" />
              </linearGradient>
            </defs>

            <!-- Grid Lines -->
            <line 
              v-for="(grid, i) in lineChart.gridValues" 
              :key="i" 
              x1="45" 
              x2="595" 
              :y1="30 + (200 * grid)" 
              :y2="30 + (200 * grid)" 
              stroke="rgba(148, 163, 184, 0.2)" 
              stroke-dasharray="4 4" 
            />

            <!-- Area Fill -->
            <polygon :points="lineChart.areaPath" fill="url(#chartGradient)" />

            <!-- Smooth Line Path -->
            <polyline 
              fill="none" 
              stroke="#0284c7" 
              stroke-width="3" 
              stroke-linecap="round" 
              stroke-linejoin="round" 
              :points="lineChart.linePath" 
            />

            <!-- Data Point Circles & Tooltip Labels -->
            <g v-for="point in lineChart.points" :key="point.month">
              <circle :cx="point.x" :cy="point.y" r="5" class="fill-sky-600 stroke-white stroke-2 dark:stroke-slate-900" />
              <text :x="point.x" y="250" text-anchor="middle" class="fill-slate-400 text-xs font-semibold">
                {{ point.month }}
              </text>
            </g>
          </svg>
        </div>
      </div>

      <!-- Pie / Status Breakdown Card -->
      <div class="rounded-2xl border border-slate-200 bg-white p-6 shadow-xs dark:border-slate-800 dark:bg-slate-900">
        <div class="flex items-center justify-between mb-4">
          <div>
            <h4 class="text-base font-bold text-slate-900 dark:text-slate-100">Project Status Distribution</h4>
            <p class="text-xs text-slate-500 dark:text-slate-400">Share of completed, ongoing, and pending projects</p>
          </div>
        </div>

        <div class="flex flex-col items-center gap-6 md:flex-row md:items-center md:justify-around py-4">
          <div class="relative flex h-48 w-48 items-center justify-center shrink-0">
            <div class="h-40 w-40 rounded-full shadow-inner transition-all duration-300" :style="{ backgroundImage: pieStyle }"></div>
            <div class="absolute h-24 w-24 rounded-full bg-white dark:bg-slate-900 flex flex-col items-center justify-center shadow-xs">
              <span class="text-xs font-bold text-slate-400">Total</span>
              <span class="text-lg font-black text-slate-900 dark:text-slate-100">{{ bookings.length }}</span>
            </div>
          </div>

          <div class="w-full space-y-3 md:max-w-xs">
            <div 
              v-for="item in projectStatusBreakdown" 
              :key="item.name"
              class="flex items-center justify-between rounded-xl border border-slate-100 bg-slate-50 px-4 py-3 dark:border-slate-800 dark:bg-slate-800/60"
            >
              <div class="flex items-center gap-3">
                <span class="h-3 w-3 rounded-full" :style="{ backgroundColor: item.color }"></span>
                <span class="text-xs font-bold text-slate-800 dark:text-slate-200">{{ item.name }}</span>
              </div>
              <div class="text-right">
                <span class="text-xs font-bold text-slate-900 dark:text-slate-100">{{ item.count }}</span>
                <span class="text-xs text-slate-400 ml-1.5 font-medium">({{ item.value }}%)</span>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- Recent Completed Projects Table Card -->
    <div class="rounded-2xl border border-slate-200 bg-white shadow-xs dark:border-slate-800 dark:bg-slate-900 overflow-hidden">
      <div class="border-b border-slate-100 px-6 py-4 dark:border-slate-800 flex items-center justify-between">
        <h4 class="text-base font-bold text-slate-900 dark:text-slate-100">Recent Completed Projects</h4>
        <span class="text-xs font-semibold text-slate-400">Latest 5 Entries</span>
      </div>

      <div class="overflow-x-auto">
        <table class="w-full min-w-[700px] divide-y divide-slate-100 dark:divide-slate-800">
          <thead class="bg-slate-50 dark:bg-slate-800/80">
            <tr class="text-left">
              <th class="px-6 py-3.5 text-xs font-bold uppercase tracking-wider text-slate-500 dark:text-slate-400">Schedule / Record Date</th>
              <th class="px-6 py-3.5 text-xs font-bold uppercase tracking-wider text-slate-500 dark:text-slate-400">Project Type</th>
              <th class="px-6 py-3.5 text-xs font-bold uppercase tracking-wider text-slate-500 dark:text-slate-400">Client Email</th>
              <th class="px-6 py-3.5 text-xs font-bold uppercase tracking-wider text-slate-500 dark:text-slate-400">Materials</th>
              <th class="px-6 py-3.5 text-xs font-bold uppercase tracking-wider text-slate-500 dark:text-slate-400">Labor</th>
              <th class="px-6 py-3.5 text-xs font-bold uppercase tracking-wider text-slate-500 dark:text-slate-400 text-right">Total Revenue</th>
            </tr>
          </thead>
          <tbody class="divide-y divide-slate-100 dark:divide-slate-800 bg-transparent">
            <tr v-for="project in recentCompletedProjects.slice(0, 5)" :key="project.id" class="transition-colors hover:bg-slate-50/50 dark:hover:bg-slate-800/50">
              <td class="px-6 py-4 text-xs font-medium text-slate-500 dark:text-slate-400">{{ formatDate(project.endDate) }}</td>
              <td class="px-6 py-4 text-sm font-bold text-slate-900 dark:text-slate-100">{{ project.name }}</td>
              <td class="px-6 py-4 text-xs text-slate-600 dark:text-slate-300 truncate max-w-[180px]">{{ project.client }}</td>
              <td class="px-6 py-4 text-xs font-medium text-slate-700 dark:text-slate-300">{{ formatCurrency(project.materialsCost) }}</td>
              <td class="px-6 py-4 text-xs font-medium text-slate-700 dark:text-slate-300">{{ formatCurrency(project.laborCost) }}</td>
              <td class="px-6 py-4 text-sm font-extrabold text-slate-900 dark:text-slate-100 text-right">{{ formatCurrency(project.totalCost) }}</td>
            </tr>
            <tr v-if="recentCompletedProjects.length === 0">
              <td colspan="6" class="px-6 py-8 text-center text-sm font-medium text-slate-500 dark:text-slate-400">No completed projects recorded yet.</td>
            </tr>
          </tbody>
        </table>
      </div>
    </div>
  </div>
</template>
