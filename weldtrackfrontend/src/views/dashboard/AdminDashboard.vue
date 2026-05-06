<script setup lang="ts">
import { computed, ref } from 'vue'
import Layout from './DashboardLayout.vue'
import InventoryManagement from './components/InventoryManagement.vue'
import ProjectHistory from './components/ProjectHistory.vue'
import Reports from './components/Reports.vue'
import BookingApproval from './components/BookingApproval.vue'
import StaffWorkspace from './components/StaffWorkspace.vue'
import ServiceFeedback from './components/ServiceFeedback.vue'
import { useAdminSectionStore, type AdminSection as AdminSectionType } from '../../stores/adminSection'

type AdminSection = AdminSectionType

const adminSectionStore = useAdminSectionStore()
const currentSection = computed<AdminSection>(() => adminSectionStore.section)

const customers = ref([
  { id: 1, name: 'Acme Fabrication', email: 'contact@acme.com', phone: '555-0101', registeredDate: 'Mar 15, 2026', totalOrders: 5 },
  { id: 2, name: 'Metro Builders', email: 'info@metrobuilders.com', phone: '555-0102', registeredDate: 'Feb 20, 2026', totalOrders: 3 },
  { id: 3, name: 'J. Santos Workshop', email: 'jsantos@workshop.com', phone: '555-0103', registeredDate: 'Apr 05, 2026', totalOrders: 2 },
  { id: 4, name: 'Northside Metalworks', email: 'contact@northside.com', phone: '555-0104', registeredDate: 'Apr 12, 2026', totalOrders: 4 },
  { id: 5, name: 'Prime Welders', email: 'sales@primewelders.com', phone: '555-0105', registeredDate: 'Jan 10, 2026', totalOrders: 8 },
  { id: 6, name: 'Luna Logistics', email: 'ops@lunalogstics.com', phone: '555-0106', registeredDate: 'Apr 01, 2026', totalOrders: 1 },
  { id: 7, name: 'Mendoza Residence', email: 'mendoza@email.com', phone: '555-0107', registeredDate: 'Mar 25, 2026', totalOrders: 1 },
  { id: 8, name: 'Cruz Transport', email: 'cruz.transport@email.com', phone: '555-0108', registeredDate: 'Apr 18, 2026', totalOrders: 2 },
])

const monthlyExpenses = ref([
  { month: 'Jan', amount: 42000 },
  { month: 'Feb', amount: 51500 },
  { month: 'Mar', amount: 47800 },
  { month: 'Apr', amount: 59600 },
  { month: 'May', amount: 54800 },
  { month: 'Jun', amount: 63400 },
])

const projects = ref([
  {
    id: 1,
    name: 'Warehouse Gate Fabrication',
    client: 'Luna Logistics',
    description: 'Heavy-duty rolling gate and support frame for the main warehouse entrance.',
    materialsCost: 32000,
    laborCost: 18000,
    miscCost: 4500,
    startDate: 'Apr 10, 2026',
    endDate: 'Apr 25, 2026',
    status: 'ongoing',
  },
  {
    id: 2,
    name: 'Balcony Railings',
    client: 'Mendoza Residence',
    description: 'Custom decorative railings for the second-floor balcony and stairs.',
    materialsCost: 18500,
    laborCost: 9200,
    miscCost: 2100,
    startDate: 'Mar 18, 2026',
    endDate: 'Apr 02, 2026',
    status: 'completed',
  },
  {
    id: 3,
    name: 'Truck Bed Repair',
    client: 'Cruz Transport',
    description: 'Repair and reinforcement of damaged truck bed frame and side panels.',
    materialsCost: 14500,
    laborCost: 7600,
    miscCost: 900,
    startDate: 'Apr 20, 2026',
    endDate: 'Apr 29, 2026',
    status: 'pending',
  },
])

const projectStatusBreakdown = [
  { name: 'Completed', value: 45, color: '#16a34a' },
  { name: 'Ongoing', value: 35, color: '#2563eb' },
  { name: 'Pending', value: 20, color: '#f59e0b' },
]

const totalCustomers = computed(() => customers.value.length)

const newCustomersThisMonth = computed(() => {
  const currentDate = new Date()
  const currentMonth = currentDate.getMonth()
  const currentYear = currentDate.getFullYear()
  return customers.value.filter((customer) => {
    const regDate = new Date(customer.registeredDate)
    return regDate.getMonth() === currentMonth && regDate.getFullYear() === currentYear
  }).length
})

const ongoingProjects = computed(() => projects.value.filter((project) => project.status === 'ongoing').length)

const completedProjects = computed(() => projects.value.filter((project) => project.status === 'completed').length)

const totalProjectValue = computed(() =>
  projects.value.reduce((sum, project) => sum + project.materialsCost + project.laborCost + project.miscCost, 0),
)

const recentCompletedProjects = computed(() =>
  [...projects.value]
    .filter((project) => project.status === 'completed')
    .sort((a, b) => new Date(b.endDate).getTime() - new Date(a.endDate).getTime()),
)



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
  const total = projectStatusBreakdown.reduce((sum, item) => sum + item.value, 0)
  let start = 0
  const segments = projectStatusBreakdown.map((item) => {
    const end = start + (item.value / total) * 100
    const segment = `${item.color} ${start}% ${end}%`
    start = end
    return segment
  })

  return `conic-gradient(${segments.join(', ')})`
})




</script>

<template>
  <Layout title="Admin Dashboard">
    <div v-if="currentSection === 'dashboard'" class="space-y-6">
      <div>
        <h2 class="mb-1 text-2xl font-semibold text-gray-900">Admin Dashboard</h2>
        <p class="text-gray-600">Project progress, expenses, and customer information</p>
      </div>

      <div class="grid grid-cols-1 gap-4 md:grid-cols-3">
        <div class="rounded-lg border border-gray-200 bg-white p-6 transition-shadow hover:shadow-lg">
          <div class="flex items-center gap-3">
            <div class="flex h-12 w-12 items-center justify-center rounded-lg bg-green-100">
              <svg class="h-6 w-6 text-green-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2"
                  d="M5 13l4 4L19 7M4 6h16M4 18h8" />
              </svg>
            </div>
            <div>
              <p class="text-2xl font-semibold text-gray-900">{{ completedProjects }}</p>
              <p class="text-sm text-gray-600">Completed Projects</p>
            </div>
          </div>
        </div>

        <div class="rounded-lg border border-gray-200 bg-white p-6 transition-shadow hover:shadow-lg">
          <div class="flex items-center gap-3">
            <div class="flex h-12 w-12 items-center justify-center rounded-lg bg-purple-100">
              <svg class="h-6 w-6 text-purple-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2"
                  d="M13 10V3L4 14h7v7l9-11h-7z" />
              </svg>
            </div>
            <div>
              <p class="text-2xl font-semibold text-gray-900">{{ ongoingProjects }}</p>
              <p class="text-sm text-gray-600">Ongoing Projects</p>
            </div>
          </div>
        </div>

        <div class="rounded-lg border border-gray-200 bg-white p-6 transition-shadow hover:shadow-lg">
          <div class="flex items-center gap-3">
            <div class="flex h-12 w-12 items-center justify-center rounded-lg bg-blue-100">
              <svg class="h-6 w-6 text-blue-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 19V6h13" />
              </svg>
            </div>
            <div>
              <p class="text-2xl font-semibold text-gray-900">₱{{ totalProjectValue.toLocaleString('en-PH') }}</p>
              <p class="text-sm text-gray-600">Total Project Value</p>
            </div>
          </div>
        </div>

        <div class="rounded-lg border border-gray-200 bg-white p-6 transition-shadow hover:shadow-lg">
          <div class="flex items-center gap-3">
            <div class="flex h-12 w-12 items-center justify-center rounded-lg bg-indigo-100">
              <svg class="h-6 w-6 text-indigo-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M17 20h5v-2a3 3 0 00-5.856-1.487M15 10a3 3 0 11-6 0 3 3 0 016 0zM6 20a7 7 0 1114 0" />
              </svg>
            </div>
            <div>
              <p class="text-2xl font-semibold text-gray-900">{{ totalCustomers }}</p>
              <p class="text-sm text-gray-600">Total Customers</p>
            </div>
          </div>
        </div>

        <div class="rounded-lg border border-gray-200 bg-white p-6 transition-shadow hover:shadow-lg">
          <div class="flex items-center gap-3">
            <div class="flex h-12 w-12 items-center justify-center rounded-lg bg-orange-100">
              <svg class="h-6 w-6 text-orange-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 4v16m8-8H4" />
              </svg>
            </div>
            <div>
              <p class="text-2xl font-semibold text-gray-900">{{ newCustomersThisMonth }}</p>
              <p class="text-sm text-gray-600">New Customers This Month</p>
            </div>
          </div>
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
                <td class="px-4 py-3 text-gray-700">{{ project.endDate }}</td>
                <td class="px-4 py-3 font-medium text-gray-900">{{ project.name }}</td>
                <td class="px-4 py-3 text-gray-700">{{ project.client }}</td>
                <td class="px-4 py-3 text-gray-900">₱{{ project.materialsCost.toLocaleString('en-PH', {
                  minimumFractionDigits: 2
                  }) }}</td>
                <td class="px-4 py-3 text-gray-900">₱{{ project.laborCost.toLocaleString('en-PH', {
                  minimumFractionDigits: 2
                  }) }}</td>
                <td class="px-4 py-3 text-gray-900">₱{{ (project.materialsCost + project.laborCost + project.miscCost).toLocaleString('en-PH', {
                  minimumFractionDigits: 2
                  }) }}</td>
              </tr>
            </tbody>
          </table>
        </div>
      </div>


    </div>

    <InventoryManagement v-else-if="currentSection === 'inventory'" />
    <ProjectHistory v-else-if="currentSection === 'projects'" />
    <BookingApproval v-else-if="currentSection === 'booking'" />
    <ServiceFeedback v-else-if="currentSection === 'feedback'" :is-admin="true" />
    <Reports v-else-if="currentSection === 'reports'" />
    <StaffWorkspace
      v-else-if="currentSection === 'staff' || currentSection === 'staff-attendance' || currentSection === 'staff-tasks' || currentSection === 'staff-contributions' || currentSection === 'staff-create'" />
  </Layout>
</template>
