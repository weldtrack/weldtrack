<script setup lang="ts">
import { computed, onMounted, ref } from 'vue'
import { BarChart2 } from 'lucide-vue-next'
import html2pdf from 'html2pdf.js'
import axios from 'axios'
import api from '../../../api/api'
import { useBookingsStore } from '../../../stores/bookings'
import { useInventoryStore } from '../../../stores/inventory'
import { useModalStore } from '../../../stores/modal'
import { getUserFriendlyApiError } from '../../../services/errorMessage'
import { getServicePriceDisplay } from '../../../services/servicePricing'

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
const isExporting = ref(false)
const SALES_MARKUP = 0.2

const fetchAttendanceData = async (startDate: string, endDate: string) => {
  try {
    const { data } = await api.get<AttendanceRecord[]>('/attendance', {
      params: {
        limit: 200,
      },
    })
    
    const start = new Date(`${startDate}T00:00:00`)
    const end = new Date(`${endDate}T23:59:59`)
    
    attendanceRecords.value = Array.isArray(data)
      ? data.filter((record) => {
          const recordDate = new Date(`${record.date}T00:00:00`)
          return recordDate >= start && recordDate <= end
        })
      : []
  } catch (err) {
    if (axios.isAxiosError(err) && err.response?.status === 404) {
      attendanceRecords.value = []
      return
    }

    modalStore.open({
      title: 'Error',
      message: getUserFriendlyApiError(err),
      variant: 'error',
    })
  }
}

onMounted(async () => {
  await Promise.all([
    bookingsStore.fetchBookings(),
    inventoryStore.fetchInventory(),
    inventoryStore.fetchMovements(),
  ])

  const today = new Date()
  const monthStart = `${today.getFullYear()}-${String(today.getMonth() + 1).padStart(2, '0')}-01`
  const monthEnd = `${today.getFullYear()}-${String(today.getMonth() + 1).padStart(2, '0')}-${String(today.getDate()).padStart(2, '0')}`
  
  await fetchAttendanceData(monthStart, monthEnd)
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
const movements = computed(() => inventoryStore.movements)

function formatDateTime(dateStr?: string) {
  if (!dateStr) return ''
  const d = new Date(dateStr)
  return d.toLocaleString('en-PH', {
    year: 'numeric',
    month: 'short',
    day: '2-digit',
    hour: 'numeric',
    minute: '2-digit',
    hour12: true,
  })
}

const projects = computed(() =>
  bookingsStore.bookings
    .filter((b) => b.status !== 'cancelled')
    .map((b) => {
      const laborCost = getServicePriceDisplay(b.projectType, b.estimatedCost)
      const baseCost = Number(b.totalPrice ?? laborCost + Number(b.materialCost ?? 0))
      return {
        id: String(b.id),
        status: b.status === 'completed' ? 'completed' : 'ongoing',
        materialsCost: Number(b.materialCost ?? 0),
        laborCost,
        baseCost,
        salesPrice: Number((baseCost * (1 + SALES_MARKUP)).toFixed(2)),
      }
    }),
)

const totalProjectCosts = computed(() =>
  projects.value.reduce((sum, project) => sum + project.materialsCost + project.laborCost, 0),
)

const ongoingProjects = computed(() => projects.value.filter((p) => p.status === 'ongoing').length)
const completedProjects = computed(() => projects.value.filter((p) => p.status === 'completed').length)

const totalSalesRevenue = computed(() =>
  projects.value.reduce((sum, project) => sum + Number(project.salesPrice || 0), 0),
)

const netProfit = computed(() => totalSalesRevenue.value - totalProjectCosts.value)

const totalMaterialsCost = computed(() =>
  projects.value.reduce((sum, p) => sum + Number(p.materialsCost || 0), 0),
)

const totalLaborCost = computed(() =>
  projects.value.reduce((sum, p) => sum + Number(p.laborCost || 0), 0),
)

const averageProfitPerProject = computed(() => {
  const count = projects.value.length
  return count > 0 ? Math.round((netProfit.value / count) * 100) / 100 : 0
})

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

async function updateDateRange() {
  if (hasInvalidDateRange.value) {
    modalStore.open({
      title: 'Invalid date range',
      message: 'Start Date must be on or before End Date.',
      variant: 'warning',
    })
    return
  }
  await Promise.all([
    fetchAttendanceData(selectedStartDate.value, selectedEndDate.value),
    inventoryStore.fetchMovements(),
  ])
}

function computeMovementValuesForRange() {
  const start = new Date(`${selectedStartDate.value}T00:00:00`)
  const end = new Date(`${selectedEndDate.value}T23:59:59`)
  let totalIn = 0
  let totalOut = 0

  movements.value.forEach((m) => {
    const t = m.rawTimestamp || m.timestamp
    const d = new Date(t)
    if (isNaN(d.getTime()) || d < start || d > end) return
    const item = inventory.value.find((it) => it.id === m.itemId)
    const unitPrice = item ? Number(item.unitPrice || 0) : 0
    const value = unitPrice * Number(m.quantity || 0)
    if (m.type === 'stock-in') totalIn += value
    else if (m.type === 'stock-out') totalOut += value
  })

  return { totalIn, totalOut }
}

function formatCurrency(value: number) {
  return `₱${value.toLocaleString('en-PH', { minimumFractionDigits: 2 })}`
}

function formatHours(value: number) {
  return `${Number(value || 0).toLocaleString('en-PH', { maximumFractionDigits: 1 })}h`
}

function formatDate(dateStr: string) {
  const date = new Date(`${dateStr}T00:00:00`)
  return date.toLocaleDateString('en-PH', {
    year: 'numeric',
    month: 'short',
    day: '2-digit',
  })
}

async function generateStockInReportPDF() {
  if (isExporting.value) return
  isExporting.value = true

  try {
    const element = document.createElement('div')
    element.innerHTML = `
      <div style="font-family: Arial, sans-serif; padding: 20px;">
        <h2 style="text-align: center; margin-bottom: 30px;">Stock-In Report</h2>
        <p><strong>Report Period:</strong> ${formatDate(selectedStartDate.value)} to ${formatDate(selectedEndDate.value)}</p>
        <p><strong>Generated:</strong> ${new Date().toLocaleString('en-PH')}</p>
        
        <h3 style="margin-top: 20px; border-bottom: 1px solid #333; padding-bottom: 10px;">Summary</h3>
        <table style="width: 100%; border-collapse: collapse; margin-top: 15px;">
          <tr style="background-color: #f0f0f0;">
            <td style="padding: 8px; border: 1px solid #ddd;"><strong>Total Stocked Items</strong></td>
            <td style="padding: 8px; border: 1px solid #ddd; text-align: right;">${inventory.value.length}</td>
          </tr>
          <tr>
            <td style="padding: 8px; border: 1px solid #ddd;"><strong>Low Stock Items</strong></td>
            <td style="padding: 8px; border: 1px solid #ddd; text-align: right;">${lowStockCount.value}</td>
          </tr>
          <tr style="background-color: #f0f0f0;">
            <td style="padding: 8px; border: 1px solid #ddd;"><strong>Total Stock Value</strong></td>
            <td style="padding: 8px; border: 1px solid #ddd; text-align: right;">${formatCurrency(totalInventoryValue.value)}</td>
          </tr>
        </table>

        <h3 style="margin-top: 25px; border-bottom: 1px solid #333; padding-bottom: 10px;">Inventory Details</h3>
        <table style="width: 100%; border-collapse: collapse; margin-top: 15px;">
          <thead>
            <tr style="background-color: #333; color: white;">
              <th style="padding: 10px; border: 1px solid #ddd; text-align: left;">Material Name</th>
              <th style="padding: 10px; border: 1px solid #ddd; text-align: center;">Quantity</th>
              <th style="padding: 10px; border: 1px solid #ddd; text-align: right;">Unit Price</th>
              <th style="padding: 10px; border: 1px solid #ddd; text-align: right;">Total Value</th>
              <th style="padding: 10px; border: 1px solid #ddd; text-align: left;">Status</th>
            </tr>
          </thead>
          <tbody>
            ${inventory.value.map((item) => `
              <tr>
                <td style="padding: 8px; border: 1px solid #ddd;">${item.name}</td>
                <td style="padding: 8px; border: 1px solid #ddd; text-align: center;">${item.quantity}</td>
                <td style="padding: 8px; border: 1px solid #ddd; text-align: right;">${formatCurrency(item.unitPrice)}</td>
                <td style="padding: 8px; border: 1px solid #ddd; text-align: right;">${formatCurrency(item.quantity * item.unitPrice)}</td>
                <td style="padding: 8px; border: 1px solid #ddd;">${item.quantity <= item.lowStockThreshold ? '<strong style="color: orange;">Low Stock</strong>' : '<strong style="color: green;">In Stock</strong>'}</td>
              </tr>
            `).join('')}
          </tbody>
        </table>
      </div>
    `

    const start = new Date(`${selectedStartDate.value}T00:00:00`)
    const end = new Date(`${selectedEndDate.value}T23:59:59`)

    const movementsFiltered = movements.value.filter((m) => {
      const t = m.rawTimestamp || m.timestamp
      const d = new Date(t)
      return !isNaN(d.getTime()) && d >= start && d <= end
    })

    const options = {
      margin: 10,
      filename: `stock-in-report-${selectedStartDate.value}.pdf`,
      image: { type: 'png' as const, quality: 0.98 },
      html2canvas: { scale: 2 },
      jsPDF: { orientation: 'landscape' as const, unit: 'mm' as const, format: 'a4' as const },
    }

    const movementRows = movementsFiltered.map((m) => `
      <tr>
        <td style="padding:8px;border:1px solid #ddd;">${formatDateTime(m.rawTimestamp || m.timestamp)}</td>
        <td style="padding:8px;border:1px solid #ddd;">${m.itemName}</td>
        <td style="padding:8px;border:1px solid #ddd;text-align:center;">${m.type}</td>
        <td style="padding:8px;border:1px solid #ddd;text-align:right;">${m.quantity}</td>
        <td style="padding:8px;border:1px solid #ddd;">${m.bookingId ?? m.taskId ?? ''}</td>
      </tr>
    `).join('')

    if (movementRows) {
      element.querySelector('div')!.innerHTML += `
        <h3 style="margin-top:25px;border-bottom:1px solid #333;padding-bottom:10px;">Stock Movement Log</h3>
        <table style="width:100%;border-collapse:collapse;margin-top:15px;">
          <thead>
            <tr style="background-color:#333;color:white;">
              <th style="padding:10px;border:1px solid #ddd;text-align:left;">Timestamp</th>
              <th style="padding:10px;border:1px solid #ddd;text-align:left;">Item</th>
              <th style="padding:10px;border:1px solid #ddd;text-align:center;">Type</th>
              <th style="padding:10px;border:1px solid #ddd;text-align:right;">Qty</th>
              <th style="padding:10px;border:1px solid #ddd;text-align:left;">Ref</th>
            </tr>
          </thead>
          <tbody>
            ${movementRows}
          </tbody>
        </table>
      `
    }

    html2pdf().set(options).from(element).save()
    
    modalStore.open({
      title: 'Success',
      message: 'Stock-In Report PDF generated successfully!',
      variant: 'success',
    })
  } catch (err) {
    modalStore.open({
      title: 'Error',
      message: 'Failed to generate PDF report',
      variant: 'error',
    })
  } finally {
    isExporting.value = false
  }
}

async function generateFinancialReportPDF() {
  if (isExporting.value) return
  isExporting.value = true

  try {
    const { totalIn, totalOut } = computeMovementValuesForRange()
    const netMovement = totalIn - totalOut

    const element = document.createElement('div')
    element.innerHTML = `
      <div style="font-family: Arial, sans-serif; padding: 20px;">
        <h2 style="text-align: center; margin-bottom: 30px;">Financial Summary Report</h2>
        <p><strong>Report Period:</strong> ${formatDate(selectedStartDate.value)} to ${formatDate(selectedEndDate.value)}</p>
        <p><strong>Generated:</strong> ${new Date().toLocaleString('en-PH')}</p>

        <h3 style="margin-top: 20px; border-bottom: 1px solid #333; padding-bottom: 10px;">Project Overview</h3>
        <table style="width: 100%; border-collapse: collapse; margin-top: 15px;">
          <tr style="background-color: #f0f0f0;">
            <td style="padding: 8px; border: 1px solid #ddd;"><strong>Total Projects</strong></td>
            <td style="padding: 8px; border: 1px solid #ddd; text-align: right;">${projects.value.length}</td>
          </tr>
          <tr>
            <td style="padding: 8px; border: 1px solid #ddd;"><strong>Ongoing Projects</strong></td>
            <td style="padding: 8px; border: 1px solid #ddd; text-align: right;">${ongoingProjects.value}</td>
          </tr>
          <tr style="background-color: #f0f0f0;">
            <td style="padding: 8px; border: 1px solid #ddd;"><strong>Completed Projects</strong></td>
            <td style="padding: 8px; border: 1px solid #ddd; text-align: right;">${completedProjects.value}</td>
          </tr>
        </table>

        <h3 style="margin-top: 25px; border-bottom: 1px solid #333; padding-bottom: 10px;">Financial Summary</h3>
        <table style="width: 100%; border-collapse: collapse; margin-top: 15px;">
          <tr style="background-color: #f9f9f9;">
            <td style="padding: 8px; border: 1px solid #ddd;"><strong>Materials Cost</strong></td>
            <td style="padding: 8px; border: 1px solid #ddd; text-align: right;">${formatCurrency(totalMaterialsCost.value)}</td>
          </tr>
          <tr>
            <td style="padding: 8px; border: 1px solid #ddd;"><strong>Labor Cost</strong></td>
            <td style="padding: 8px; border: 1px solid #ddd; text-align: right;">${formatCurrency(totalLaborCost.value)}</td>
          </tr>
          <tr style="background-color: #f0f0f0;">
            <td style="padding: 8px; border: 1px solid #ddd;"><strong>Total Expenses</strong></td>
            <td style="padding: 8px; border: 1px solid #ddd; text-align: right;">${formatCurrency(totalProjectCosts.value)}</td>
          </tr>
          <tr>
            <td style="padding: 8px; border: 1px solid #ddd;"><strong>Sales Revenue</strong></td>
            <td style="padding: 8px; border: 1px solid #ddd; text-align: right; color: green;"><strong>${formatCurrency(totalSalesRevenue.value)}</strong></td>
          </tr>
          <tr style="background-color: #e8f5e9; font-size: 14px;">
            <td style="padding: 12px; border: 2px solid #4caf50;"><strong>NET PROFIT</strong></td>
            <td style="padding: 12px; border: 2px solid #4caf50; text-align: right; color: green;"><strong>${formatCurrency(netProfit.value)}</strong></td>
          </tr>
          <tr>
            <td style="padding: 8px; border: 1px solid #ddd; font-size:12px; color:#666;">Avg Profit / Project</td>
            <td style="padding: 8px; border: 1px solid #ddd; text-align: right; font-size:12px; color:#666;">${formatCurrency(averageProfitPerProject.value)}</td>
          </tr>
        </table>

        <h3 style="margin-top: 20px; border-bottom: 1px solid #333; padding-bottom: 10px;">Stock Movement Values</h3>
        <table style="width: 100%; border-collapse: collapse; margin-top: 10px;">
          <tr style="background-color: #f9f9f9;">
            <td style="padding: 8px; border: 1px solid #ddd;"><strong>Stock Movement (In)</strong></td>
            <td style="padding: 8px; border: 1px solid #ddd; text-align: right;">${formatCurrency(totalIn)}</td>
          </tr>
          <tr>
            <td style="padding: 8px; border: 1px solid #ddd;"><strong>Stock Movement (Out)</strong></td>
            <td style="padding: 8px; border: 1px solid #ddd; text-align: right;">${formatCurrency(totalOut)}</td>
          </tr>
          <tr style="background-color: #fff7e6;">
            <td style="padding: 10px; border: 1px solid #ddd;"><strong>Net Movement Value</strong></td>
            <td style="padding: 10px; border: 1px solid #ddd; text-align: right; color: #333;"><strong>${formatCurrency(netMovement)}</strong></td>
          </tr>
        </table>

        <h3 style="margin-top:25px;border-bottom:1px solid #333;padding-bottom:10px;">Projects (Itemized)</h3>
        <table style="width:100%;border-collapse:collapse;margin-top:15px; font-size:12px;">
              <th style="padding:8px;border:1px solid #ddd;text-align:right;">Materials</th>
              <th style="padding:8px;border:1px solid #ddd;text-align:right;">Labor</th>
              <th style="padding:8px;border:1px solid #ddd;text-align:right;">Total</th>
            </tr>
          </thead>
          <tbody>
            ${projects.value.map((p) => `
              <tr>
                <td style="padding:8px;border:1px solid #ddd;">${p.id}</td>
                <td style="padding:8px;border:1px solid #ddd;">${p.status}</td>
                <td style="padding:8px;border:1px solid #ddd;text-align:right;">${formatCurrency(p.materialsCost)}</td>
                <td style="padding:8px;border:1px solid #ddd;text-align:right;">${formatCurrency(p.laborCost)}</td>
                <td style="padding:8px;border:1px solid #ddd;text-align:right;">${formatCurrency(p.salesPrice)}</td>
              </tr>
            `).join('')}
          </tbody>
        </table>
      </div>
    `

    const options = {
      margin: 10,
      filename: `financial-report-${selectedStartDate.value}.pdf`,
      image: { type: 'png' as const, quality: 0.98 },
      html2canvas: { scale: 2 },
      jsPDF: { orientation: 'portrait' as const, unit: 'mm' as const, format: 'a4' as const },
    }

    html2pdf().set(options).from(element).save()
    
    modalStore.open({
      title: 'Success',
      message: 'Financial Report PDF generated successfully!',
      variant: 'success',
    })
  } catch (err) {

    modalStore.open({
      title: 'Error',
      message: 'Failed to generate PDF report',
      variant: 'error',
    })
  } finally {
    isExporting.value = false
  }
}

async function generateStaffAttendanceReportPDF() {
  if (isExporting.value) return
  isExporting.value = true

  try {
    const element = document.createElement('div')
    element.innerHTML = `
      <div style="font-family: Arial, sans-serif; padding: 20px;">
        <h2 style="text-align: center; margin-bottom: 30px;">Staff Attendance Report</h2>
        <p><strong>Report Period:</strong> ${formatDate(selectedStartDate.value)} to ${formatDate(selectedEndDate.value)}</p>
        <p><strong>Generated:</strong> ${new Date().toLocaleString('en-PH')}</p>
        
        <h3 style="margin-top: 20px; border-bottom: 1px solid #333; padding-bottom: 10px;">Summary</h3>
        <table style="width: 100%; border-collapse: collapse; margin-top: 15px;">
          <tr style="background-color: #f0f0f0;">
            <td style="padding: 8px; border: 1px solid #ddd;"><strong>Total Staff</strong></td>
            <td style="padding: 8px; border: 1px solid #ddd; text-align: right;">${staffData.value.length}</td>
          </tr>
          <tr>
            <td style="padding: 8px; border: 1px solid #ddd;"><strong>Total Hours</strong></td>
            <td style="padding: 8px; border: 1px solid #ddd; text-align: right;">${formatHours(totalStaffHours.value)}</td>
          </tr>
          <tr>
            <td style="padding: 8px; border: 1px solid #ddd;"><strong>Total Overtime</strong></td>
            <td style="padding: 8px; border: 1px solid #ddd; text-align: right; color: red;"><strong>${formatHours(totalOvertimeHours.value)}</strong></td>
          </tr>
          <tr style="background-color: #f0f0f0;">
            <td style="padding: 8px; border: 1px solid #ddd;"><strong>Staff with Overtime</strong></td>
            <td style="padding: 8px; border: 1px solid #ddd; text-align: right;">${staffWithOvertimeCount.value}</td>
          </tr>
        </table>

        <h3 style="margin-top: 25px; border-bottom: 1px solid #333; padding-bottom: 10px;">Attendance Details</h3>
        <table style="width: 100%; border-collapse: collapse; margin-top: 15px;">
          <thead>
            <tr style="background-color: #333; color: white;">
              <th style="padding: 10px; border: 1px solid #ddd; text-align: left;">Email</th>
              <th style="padding: 10px; border: 1px solid #ddd; text-align: center;">Date</th>
              <th style="padding: 10px; border: 1px solid #ddd; text-align: center;">Hours Worked</th>
              <th style="padding: 10px; border: 1px solid #ddd; text-align: center;">Overtime</th>
            </tr>
          </thead>
          <tbody>
            ${filteredAttendanceRecords.value.map((record) => `
              <tr>
                <td style="padding: 8px; border: 1px solid #ddd;">${record.email}</td>
                <td style="padding: 8px; border: 1px solid #ddd; text-align: center;">${formatDate(record.date)}</td>
                <td style="padding: 8px; border: 1px solid #ddd; text-align: center;">${record.hours_worked}</td>
                <td style="padding: 8px; border: 1px solid #ddd; text-align: center; color: ${record.overtime_hours > 0 ? 'red' : 'black'};"><strong>${formatHours(record.overtime_hours)}</strong></td>
              </tr>
            `).join('')}
          </tbody>
        </table>
      </div>
    `

    const options = {
      margin: 10,
      filename: `attendance-report-${selectedStartDate.value}.pdf`,
      image: { type: 'png' as const, quality: 0.98 },
      html2canvas: { scale: 2 },
      jsPDF: { orientation: 'landscape' as const, unit: 'mm' as const, format: 'a4' as const },
    }

    html2pdf().set(options).from(element).save()
    
    modalStore.open({
      title: 'Success',
      message: 'Staff Attendance Report PDF generated successfully!',
      variant: 'success',
    })
  } catch (err) {
    modalStore.open({
      title: 'Error',
      message: 'Failed to generate PDF report',
      variant: 'error',
    })
  } finally {
    isExporting.value = false
  }
}
</script>

<template>
  <section class="space-y-6">
    <div class="flex items-start gap-3">
      <div class="flex h-12 w-12 items-center justify-center rounded-lg bg-linear-to-br from-indigo-50 to-white ring-1 ring-indigo-100">
        <BarChart2 class="h-6 w-6 text-indigo-600" />
      </div>
      <div>
        <h3 class="mb-1 text-2xl font-semibold text-gray-900">Reports</h3>
        <p class="text-sm text-gray-600">Generate and export business reports</p>
      </div>
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
        <div class="lg:col-span-2 flex items-end gap-2">
          <button
            type="button"
            class="rounded-lg bg-blue-600 px-4 py-2 font-semibold text-white transition-colors hover:bg-blue-700 disabled:bg-gray-400"
            :disabled="hasInvalidDateRange || isExporting"
            @click="updateDateRange"
          >
            {{ isExporting ? 'Loading...' : 'Update' }}
          </button>
          <p class="text-sm text-gray-600">
            <span class="font-semibold text-gray-900">{{ selectedStartDate }}</span>
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
          class="mt-auto w-full rounded-lg bg-blue-600 px-4 py-2.5 font-semibold text-white transition-colors hover:bg-blue-700 disabled:bg-gray-400"
          :disabled="isExporting"
          @click="generateStockInReportPDF"
        >
          <svg class="mr-2 inline h-5 w-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path
              stroke-linecap="round"
              stroke-linejoin="round"
              stroke-width="2"
              d="M12 10v6m0 0l-3-3m3 3l3-3m2 8H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z"
            />
          </svg>
          {{ isExporting ? 'Generating...' : 'Export PDF' }}
        </button>
      </div>

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
            <span class="text-gray-600">Materials Cost:</span>
            <span class="text-gray-900">{{ formatCurrency(totalMaterialsCost) }}</span>
          </div>
          <div class="flex justify-between text-sm">
            <span class="text-gray-600">Labor Cost:</span>
            <span class="text-gray-900">{{ formatCurrency(totalLaborCost) }}</span>
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
          <div class="flex justify-between text-xs text-gray-600">
            <span>Avg Profit / Project:</span>
            <span>{{ formatCurrency(averageProfitPerProject) }}</span>
          </div>
        </div>
        <div class="flex gap-2 mt-auto">
          <button
            type="button"
            class="flex-1 rounded-lg bg-purple-600 px-4 py-2.5 font-semibold text-white transition-colors hover:bg-purple-700 disabled:bg-gray-400"
            :disabled="isExporting"
            @click="generateFinancialReportPDF"
          >
          <svg class="mr-2 inline h-5 w-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path
              stroke-linecap="round"
              stroke-linejoin="round"
              stroke-width="2"
              d="M12 10v6m0 0l-3-3m3 3l3-3m2 8H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z"
            />
          </svg>
            {{ isExporting ? 'Generating...' : 'Export PDF' }}
          </button>
        </div>
      </div>

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
            <span class="text-gray-900">{{ formatHours(totalStaffHours) }}</span>
          </div>
          <div class="border-t border-gray-200 pt-3">
            <div class="flex justify-between text-sm">
              <span class="text-gray-600">Total Overtime (Month):</span>
              <span class="font-semibold text-red-600">{{ formatHours(totalOvertimeHours) }}</span>
            </div>
            <div class="mt-2 flex justify-between text-sm">
              <span class="text-gray-600">Staff with OT:</span>
              <span class="text-gray-900">{{ staffWithOvertimeCount }}</span>
            </div>
          </div>
        </div>
        <button
          type="button"
          class="mt-auto w-full rounded-lg bg-indigo-600 px-4 py-2.5 font-semibold text-white transition-colors hover:bg-indigo-700 disabled:bg-gray-400"
          :disabled="isExporting"
          @click="generateStaffAttendanceReportPDF"
        >
          <svg class="mr-2 inline h-5 w-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path
              stroke-linecap="round"
              stroke-linejoin="round"
              stroke-width="2"
              d="M12 10v6m0 0l-3-3m3 3l3-3m2 8H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z"
            />
          </svg>
          {{ isExporting ? 'Generating...' : 'Export PDF' }}
        </button>
      </div>
    </div>

  </section>
</template>
