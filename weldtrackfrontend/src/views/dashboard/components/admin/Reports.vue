<script setup lang="ts">
import InfoTooltip from '../../../../components/ui/InfoTooltip.vue'
import { computed, onMounted, ref } from 'vue'
import LocalLoader from '../../../../components/ui/LocalLoader.vue'
import { BarChart2 } from 'lucide-vue-next'
import html2pdf from 'html2pdf.js'
import axios from 'axios'
import api from '../../../../api/api'
import { useBookingsStore } from '../../../../stores/bookings'
import { useInventoryStore } from '../../../../stores/inventory'
import { useModalStore } from '../../../../stores/modal'
import { getUserFriendlyApiError } from '../../../../services/errorMessage'
import { getServicePriceDisplay } from '../../../../services/servicePricing'

interface AttendanceRecord {
  id: string
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
const isLoading = ref(true)

const fetchAttendanceData = async (startDate: string, endDate: string) => {
  try {
    const allRecords: AttendanceRecord[] = []
    const pageSize = 200
    for (let skip = 0; ; skip += pageSize) {
      const { data } = await api.get<AttendanceRecord[]>('/attendance', { params: { skip, limit: pageSize } })
      const page = Array.isArray(data) ? data : []
      allRecords.push(...page)
      if (page.length < pageSize) break
    }
    
    const start = new Date(`${startDate}T00:00:00`)
    const end = new Date(`${endDate}T23:59:59`)
    
    attendanceRecords.value = allRecords.filter((record) => {
          const recordDate = new Date(`${record.date}T00:00:00`)
          return recordDate >= start && recordDate <= end
        })
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
  isLoading.value = true
  try {
    await Promise.all([
      bookingsStore.fetchBookings(),
      inventoryStore.fetchInventory(),
      inventoryStore.fetchMovements(),
    ])
    await onRangeChange()
  } finally {
    isLoading.value = false
  }
})

const today = new Date()
const toDateValue = (date: Date) => `${date.getFullYear()}-${String(date.getMonth() + 1).padStart(2, '0')}-${String(date.getDate()).padStart(2, '0')}`
const maxDate = toDateValue(today)

const dateRanges = computed(() => {
  const ranges = [{ label: 'All recorded data', start: '2000-01-01', end: maxDate }]
  const now = new Date()

  for (let monthsAgo = 0; monthsAgo < 5; monthsAgo++) {
    const start = new Date(now.getFullYear(), now.getMonth() - monthsAgo, 1)
    const naturalEnd = new Date(now.getFullYear(), now.getMonth() - monthsAgo + 1, 0)
    const end = naturalEnd > now ? now : naturalEnd
    const labelStart = start.toLocaleDateString('en-PH', { month: 'short', day: 'numeric' })
    const labelEnd = end.toLocaleDateString('en-PH', { month: 'short', day: 'numeric', year: 'numeric' })
    ranges.push({ label: `${labelStart} – ${labelEnd}`, start: toDateValue(start), end: toDateValue(end) })
  }
  return ranges
})

const selectedRange = ref(`${dateRanges.value[0].start}|${dateRanges.value[0].end}`)
const selectedStartDate = ref(dateRanges.value[0].start)
const selectedEndDate = ref(dateRanges.value[0].end)

async function refreshData(start: string, end: string) {
  // ISO date strings sort chronologically. Comparing date-only values avoids
  // UTC/local-time shifts incorrectly marking today's date as future.
  if (!start || !end || start > end || start > maxDate || end > maxDate) return
  
  await Promise.all([
    fetchAttendanceData(start, end),
    inventoryStore.fetchMovements(),
  ])
}

async function onRangeChange() {
  const [start, end] = selectedRange.value.split('|')
  selectedStartDate.value = start
  selectedEndDate.value = end
  await refreshData(start, end)
}

// Auto-update on manual input change
import { watch } from 'vue'
watch([selectedStartDate, selectedEndDate], async () => {
  if (!hasInvalidDateRange.value) {
    await refreshData(selectedStartDate.value, selectedEndDate.value)
  }
})

const normalizedStart = computed(() => new Date(`${selectedStartDate.value}T00:00:00`))
const normalizedEnd = computed(() => new Date(`${selectedEndDate.value}T23:59:59.999`))

const hasInvalidDateRange = computed(() => {
  return !selectedStartDate.value
    || !selectedEndDate.value
    || selectedStartDate.value > selectedEndDate.value
    || selectedStartDate.value > maxDate
    || selectedEndDate.value > maxDate
})

function isWithinSelectedRange(isoDate: string) {
  const dateValue = isoDate.includes('T') ? isoDate : `${isoDate}T00:00:00`
  const d = new Date(dateValue)
  if (isNaN(d.getTime())) return false
  return d >= normalizedStart.value && d <= normalizedEnd.value
}

const filteredAttendanceRecords = computed(() =>
  attendanceRecords.value.filter((record) => isWithinSelectedRange(record.date)),
)

const inventoryInPeriod = computed(() => {
  const start = normalizedStart.value
  const end = normalizedEnd.value

  const movementsInRange = movements.value.filter((m) => {
    const t = m.rawTimestamp || m.timestamp
    const d = new Date(t)
    return m.type === 'stock-in' && !isNaN(d.getTime()) && d >= start && d <= end
  })

  const itemIds = new Set(movementsInRange.map((m) => m.itemId))
  return inventory.value.filter((item) => itemIds.has(item.id))
})

const totalInventoryValueInPeriod = computed(() => computeMovementValuesForRange().totalIn)

const lowStockCountInPeriod = computed(() =>
  inventoryInPeriod.value.filter((item) => item.quantity <= item.lowStockThreshold).length,
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
    .filter((b) => b.status !== 'cancelled' && b.createdDate && isWithinSelectedRange(b.createdDate))
    .map((b) => {
      const laborCost = getServicePriceDisplay(b.projectType, b.estimatedCost)
      const recordedTotal = Number(b.totalPrice ?? laborCost + Number(b.materialCost ?? 0))
      return {
        id: String(b.id),
        status: b.status === 'completed' ? 'completed' : 'ongoing',
        materialsCost: Number(b.materialCost ?? 0),
        laborCost,
        recordedTotal,
      }
    }),
)

const ongoingProjects = computed(() => projects.value.filter((p) => p.status === 'ongoing').length)
const completedProjects = computed(() => projects.value.filter((p) => p.status === 'completed').length)

const totalSalesRevenue = computed(() =>
  projects.value
    .filter((project) => project.status === 'completed')
    .reduce((sum, project) => sum + Number(project.recordedTotal || 0), 0),
)

const totalMaterialsCost = computed(() =>
  projects.value.filter((p) => p.status === 'completed').reduce((sum, p) => sum + Number(p.materialsCost || 0), 0),
)

const totalLaborCost = computed(() =>
  projects.value.filter((p) => p.status === 'completed').reduce((sum, p) => sum + Number(p.laborCost || 0), 0),
)

const averageCompletedProjectRevenue = computed(() => completedProjects.value > 0
  ? Math.round((totalSalesRevenue.value / completedProjects.value) * 100) / 100
  : 0)

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
    const start = new Date(`${selectedStartDate.value}T00:00:00`)
    const end = new Date(`${selectedEndDate.value}T23:59:59`)

    const movementsFiltered = movements.value.filter((m) => {
      const t = m.rawTimestamp || m.timestamp
      const d = new Date(t)
      return !isNaN(d.getTime()) && d >= start && d <= end
    })

    const itemsWithMovementsIds = new Set(movementsFiltered.map((m) => m.itemId))
    const filteredInventory = inventory.value.filter((item) => itemsWithMovementsIds.has(item.id))
    
    const filteredTotalValue = filteredInventory.reduce((sum, item) => sum + item.quantity * item.unitPrice, 0)
    const filteredLowStockCount = filteredInventory.filter((item) => item.quantity <= item.lowStockThreshold).length

    const element = document.createElement('div')
    element.innerHTML = `
      <div style="font-family: Arial, sans-serif; padding: 20px;">
        <h2 style="text-align: center; margin-bottom: 30px;">Stock-In Report</h2>
        <p><strong>Report Period:</strong> ${formatDate(selectedStartDate.value)} to ${formatDate(selectedEndDate.value)}</p>
        <p><strong>Generated:</strong> ${new Date().toLocaleString('en-PH')}</p>
        
        <h3 style="margin-top: 20px; border-bottom: 1px solid #333; padding-bottom: 10px;">Summary</h3>
        <table style="width: 100%; border-collapse: collapse; margin-top: 15px;">
          <tr style="background-color: #f0f0f0;">
            <td style="padding: 8px; border: 1px solid var(--table-border, #ddd);"><strong>Total Stocked Items (in period)</strong></td>
            <td style="padding: 8px; border: 1px solid var(--table-border, #ddd); text-align: right;">${filteredInventory.length}</td>
          </tr>
          <tr>
            <td style="padding: 8px; border: 1px solid var(--table-border, #ddd);"><strong>Low Stock Items</strong></td>
            <td style="padding: 8px; border: 1px solid var(--table-border, #ddd); text-align: right;">${filteredLowStockCount}</td>
          </tr>
          <tr style="background-color: #f0f0f0;">
            <td style="padding: 8px; border: 1px solid var(--table-border, #ddd);"><strong>Recorded Stock-In Value</strong></td>
            <td style="padding: 8px; border: 1px solid var(--table-border, #ddd); text-align: right;">${formatCurrency(filteredTotalValue)}</td>
          </tr>
        </table>

        <h3 style="margin-top: 25px; border-bottom: 1px solid #333; padding-bottom: 10px;">Inventory Details (Period Items)</h3>
        <table style="width: 100%; border-collapse: collapse; margin-top: 15px;">
          <thead>
            <tr style="background-color: var(--public-text, #0f172a); color: var(--public-text, #f8fafc);">
              <th style="padding: 10px; border: 1px solid var(--table-border, #ddd); text-align: left;">Material Name</th>
              <th style="padding: 10px; border: 1px solid var(--table-border, #ddd); text-align: center;">Quantity</th>
              <th style="padding: 10px; border: 1px solid var(--table-border, #ddd); text-align: right;">Unit Price</th>
              <th style="padding: 10px; border: 1px solid var(--table-border, #ddd); text-align: right;">Total Value</th>
              <th style="padding: 10px; border: 1px solid var(--table-border, #ddd); text-align: left;">Status</th>
            </tr>
          </thead>
          <tbody>
            ${filteredInventory.map((item) => `
              <tr>
                <td style="padding: 8px; border: 1px solid var(--table-border, #ddd);">${item.name}</td>
                <td style="padding: 8px; border: 1px solid var(--table-border, #ddd); text-align: center;">${item.quantity}</td>
                <td style="padding: 8px; border: 1px solid var(--table-border, #ddd); text-align: right;">${formatCurrency(item.unitPrice)}</td>
                <td style="padding: 8px; border: 1px solid var(--table-border, #ddd); text-align: right;">${formatCurrency(item.quantity * item.unitPrice)}</td>
                <td style="padding: 8px; border: 1px solid var(--table-border, #ddd);">${item.quantity <= item.lowStockThreshold ? '<strong style="color: var(--status-warning, orange);">Low Stock</strong>' : '<strong style="color: var(--status-success, green);">In Stock</strong>'}</td>
              </tr>
            `).join('')}
          </tbody>
        </table>
      </div>
    `

    const options = {
      margin: 10,
      filename: `stock-in-report-${selectedStartDate.value}.pdf`,
      image: { type: 'png' as const, quality: 0.98 },
      html2canvas: { scale: 2 },
      jsPDF: { orientation: 'landscape' as const, unit: 'mm' as const, format: 'a4' as const },
    }

    const movementRows = movementsFiltered.map((m) => `
      <tr>
        <td style="padding:8px;border:1px solid var(--table-border, #ddd);">${formatDateTime(m.rawTimestamp || m.timestamp)}</td>
        <td style="padding:8px;border:1px solid var(--table-border, #ddd);">${m.itemName}</td>
        <td style="padding:8px;border:1px solid var(--table-border, #ddd);text-align:center;">${m.type}</td>
        <td style="padding:8px;border:1px solid var(--table-border, #ddd);text-align:right;">${m.quantity}</td>
        <td style="padding:8px;border:1px solid var(--table-border, #ddd);">${m.bookingId ?? m.taskId ?? ''}</td>
      </tr>
    `).join('')

    if (movementRows) {
      element.querySelector('div')!.innerHTML += `
        <h3 style="margin-top:25px;border-bottom:1px solid #333;padding-bottom:10px;">Stock Movement Log</h3>
        <table style="width:100%;border-collapse:collapse;margin-top:15px;">
          <thead>
            <tr style="background-color: var(--public-text, #0f172a);color: var(--public-text, #f8fafc);">
              <th style="padding:10px;border:1px solid var(--table-border, #ddd);text-align:left;">Timestamp</th>
              <th style="padding:10px;border:1px solid var(--table-border, #ddd);text-align:left;">Item</th>
              <th style="padding:10px;border:1px solid var(--table-border, #ddd);text-align:center;">Type</th>
              <th style="padding:10px;border:1px solid var(--table-border, #ddd);text-align:right;">Qty</th>
              <th style="padding:10px;border:1px solid var(--table-border, #ddd);text-align:left;">Ref</th>
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
            <td style="padding: 8px; border: 1px solid var(--table-border, #ddd);"><strong>Total Projects</strong></td>
            <td style="padding: 8px; border: 1px solid var(--table-border, #ddd); text-align: right;">${projects.value.length}</td>
          </tr>
          <tr>
            <td style="padding: 8px; border: 1px solid var(--table-border, #ddd);"><strong>Ongoing Projects</strong></td>
            <td style="padding: 8px; border: 1px solid var(--table-border, #ddd); text-align: right;">${ongoingProjects.value}</td>
          </tr>
          <tr style="background-color: #f0f0f0;">
            <td style="padding: 8px; border: 1px solid var(--table-border, #ddd);"><strong>Completed Projects</strong></td>
            <td style="padding: 8px; border: 1px solid var(--table-border, #ddd); text-align: right;">${completedProjects.value}</td>
          </tr>
        </table>

        <h3 style="margin-top: 25px; border-bottom: 1px solid #333; padding-bottom: 10px;">Financial Summary</h3>
        <table style="width: 100%; border-collapse: collapse; margin-top: 15px;">
          <tr style="background-color: #f9f9f9;">
            <td style="padding: 8px; border: 1px solid var(--table-border, #ddd);"><strong>Recorded Materials (completed projects)</strong></td>
            <td style="padding: 8px; border: 1px solid var(--table-border, #ddd); text-align: right;">${formatCurrency(totalMaterialsCost.value)}</td>
          </tr>
          <tr>
            <td style="padding: 8px; border: 1px solid var(--table-border, #ddd);"><strong>Labor Charges (completed projects)</strong></td>
            <td style="padding: 8px; border: 1px solid var(--table-border, #ddd); text-align: right;">${formatCurrency(totalLaborCost.value)}</td>
          </tr>
          <tr>
            <td style="padding: 8px; border: 1px solid var(--table-border, #ddd);"><strong>Recorded Completed-Project Revenue</strong></td>
            <td style="padding: 8px; border: 1px solid var(--table-border, #ddd); text-align: right; color: var(--status-success, green);"><strong>${formatCurrency(totalSalesRevenue.value)}</strong></td>
          </tr>
          <tr>
            <td style="padding: 8px; border: 1px solid var(--table-border, #ddd); font-size:12px; color:#666;">Average Revenue / Completed Project</td>
            <td style="padding: 8px; border: 1px solid var(--table-border, #ddd); text-align: right; font-size:12px; color:#666;">${formatCurrency(averageCompletedProjectRevenue.value)}</td>
          </tr>
        </table>

        <h3 style="margin-top: 20px; border-bottom: 1px solid #333; padding-bottom: 10px;">Stock Movement Values</h3>
        <table style="width: 100%; border-collapse: collapse; margin-top: 10px;">
          <tr style="background-color: #f9f9f9;">
            <td style="padding: 8px; border: 1px solid var(--table-border, #ddd);"><strong>Stock Movement (In)</strong></td>
            <td style="padding: 8px; border: 1px solid var(--table-border, #ddd); text-align: right;">${formatCurrency(totalIn)}</td>
          </tr>
          <tr>
            <td style="padding: 8px; border: 1px solid var(--table-border, #ddd);"><strong>Stock Movement (Out)</strong></td>
            <td style="padding: 8px; border: 1px solid var(--table-border, #ddd); text-align: right;">${formatCurrency(totalOut)}</td>
          </tr>
          <tr style="background-color: #fff7e6;">
            <td style="padding: 10px; border: 1px solid var(--table-border, #ddd);"><strong>Net Movement Value</strong></td>
            <td style="padding: 10px; border: 1px solid var(--table-border, #ddd); text-align: right; color: var(--public-text, #0f172a);"><strong>${formatCurrency(netMovement)}</strong></td>
          </tr>
        </table>

        <h3 style="margin-top:25px;border-bottom:1px solid #333;padding-bottom:10px;">Projects (Itemized)</h3>
        <table style="width:100%;border-collapse:collapse;margin-top:15px; font-size:12px;">
          <thead>
            <tr>
              <th style="padding:8px;border:1px solid var(--table-border, #ddd);text-align:left;">Booking ID</th>
              <th style="padding:8px;border:1px solid var(--table-border, #ddd);text-align:left;">Status</th>
              <th style="padding:8px;border:1px solid var(--table-border, #ddd);text-align:right;">Materials</th>
              <th style="padding:8px;border:1px solid var(--table-border, #ddd);text-align:right;">Labor</th>
              <th style="padding:8px;border:1px solid var(--table-border, #ddd);text-align:right;">Recorded Total</th>
            </tr>
          </thead>
          <tbody>
            ${projects.value.map((p) => `
              <tr>
                <td style="padding:8px;border:1px solid var(--table-border, #ddd);">${p.id}</td>
                <td style="padding:8px;border:1px solid var(--table-border, #ddd);">${p.status}</td>
                <td style="padding:8px;border:1px solid var(--table-border, #ddd);text-align:right;">${formatCurrency(p.materialsCost)}</td>
                <td style="padding:8px;border:1px solid var(--table-border, #ddd);text-align:right;">${formatCurrency(p.laborCost)}</td>
                <td style="padding:8px;border:1px solid var(--table-border, #ddd);text-align:right;">${formatCurrency(p.recordedTotal)}</td>
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
            <td style="padding: 8px; border: 1px solid var(--table-border, #ddd);"><strong>Total Staff</strong></td>
            <td style="padding: 8px; border: 1px solid var(--table-border, #ddd); text-align: right;">${staffData.value.length}</td>
          </tr>
          <tr>
            <td style="padding: 8px; border: 1px solid var(--table-border, #ddd);"><strong>Total Hours</strong></td>
            <td style="padding: 8px; border: 1px solid var(--table-border, #ddd); text-align: right;">${formatHours(totalStaffHours.value)}</td>
          </tr>
          <tr>
            <td style="padding: 8px; border: 1px solid var(--table-border, #ddd);"><strong>Total Overtime</strong></td>
            <td style="padding: 8px; border: 1px solid var(--table-border, #ddd); text-align: right; color: var(--status-danger, red);"><strong>${formatHours(totalOvertimeHours.value)}</strong></td>
          </tr>
          <tr style="background-color: #f0f0f0;">
            <td style="padding: 8px; border: 1px solid var(--table-border, #ddd);"><strong>Staff with Overtime</strong></td>
            <td style="padding: 8px; border: 1px solid var(--table-border, #ddd); text-align: right;">${staffWithOvertimeCount.value}</td>
          </tr>
        </table>

        <h3 style="margin-top: 25px; border-bottom: 1px solid #333; padding-bottom: 10px;">Attendance Details</h3>
        <table style="width: 100%; border-collapse: collapse; margin-top: 15px;">
          <thead>
            <tr style="background-color: var(--public-text, #0f172a); color: var(--public-text, #f8fafc);">
              <th style="padding: 10px; border: 1px solid var(--table-border, #ddd); text-align: left;">Email</th>
              <th style="padding: 10px; border: 1px solid var(--table-border, #ddd); text-align: center;">Date</th>
              <th style="padding: 10px; border: 1px solid var(--table-border, #ddd); text-align: center;">Hours Worked</th>
              <th style="padding: 10px; border: 1px solid var(--table-border, #ddd); text-align: center;">Overtime</th>
            </tr>
          </thead>
          <tbody>
            ${filteredAttendanceRecords.value.map((record) => `
              <tr>
                <td style="padding: 8px; border: 1px solid var(--table-border, #ddd);">${record.email}</td>
                <td style="padding: 8px; border: 1px solid var(--table-border, #ddd); text-align: center;">${formatDate(record.date)}</td>
                <td style="padding: 8px; border: 1px solid var(--table-border, #ddd); text-align: center;">${record.hours_worked}</td>
                <td style="padding: 8px; border: 1px solid var(--table-border, #ddd); text-align: center; color: ${record.overtime_hours > 0 ? 'red' : 'black'};"><strong>${formatHours(record.overtime_hours)}</strong></td>
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
  <section class="space-y-6 relative">
    <LocalLoader v-if="isLoading" />

    <!-- Header -->
    <div class="flex items-start gap-3">
      <div class="flex h-12 w-12 items-center justify-center">
        <BarChart2 class="dashboard-view-icon h-6 w-6 text-sky-600 dark:text-sky-400" />
      </div>
      <div>
        <h3 class="text-2xl font-semibold text-slate-900">Reports</h3>
        <p class="text-sm text-slate-600">Generate, analyze, and export comprehensive business reports</p>
      </div>
    </div>

    <!-- Date Range Controls -->
    <div class="rounded-xl border border-slate-200 bg-white shadow-sm p-6 dark:border-slate-800 dark:bg-slate-900">
      <div class="border-b border-slate-100 pb-4 mb-5 flex items-center justify-between">
        <div>
          <h4 class="text-base font-bold text-slate-900">Report Filter Period</h4>
          <p class="text-xs text-slate-500 mt-0.5">Select a preset date window or enter custom start/end dates</p>
        </div>
      </div>

      <div class="grid grid-cols-1 gap-5 lg:grid-cols-3">
        <div>
          <label class="flex items-center text-xs font-bold uppercase tracking-wider text-slate-500 mb-2">
            Preset Window <InfoTooltip text="Choose a standard 15-day or monthly accounting period." />
          </label>
          <select 
            v-model="selectedRange" 
            @change="onRangeChange"
            class="w-full rounded-xl border border-slate-200 bg-white px-4 py-3 text-sm shadow-sm outline-none transition focus:border-sky-500 focus:ring-2 focus:ring-sky-200"
          >
            <option v-for="range in dateRanges" :key="range.start" :value="range.start + '|' + range.end">
              {{ range.label }}
            </option>
          </select>
        </div>

        <div>
          <label class="flex items-center text-xs font-bold uppercase tracking-wider text-slate-500 mb-2">
            Start Date <InfoTooltip text="Filter data beginning from this date." />
          </label>
          <input
            v-model="selectedStartDate"
            type="date"
            :max="maxDate"
            class="w-full rounded-xl border border-slate-200 bg-white px-4 py-3 text-sm shadow-sm outline-none transition focus:border-sky-500 focus:ring-2 focus:ring-sky-200"
          />
        </div>

        <div>
          <label class="flex items-center text-xs font-bold uppercase tracking-wider text-slate-500 mb-2">
            End Date <InfoTooltip text="Filter data up to this end date." />
          </label>
          <input
            v-model="selectedEndDate"
            type="date"
            :max="maxDate"
            class="w-full rounded-xl border border-slate-200 bg-white px-4 py-3 text-sm shadow-sm outline-none transition focus:border-sky-500 focus:ring-2 focus:ring-sky-200"
          />
        </div>
      </div>

      <p v-if="hasInvalidDateRange" class="mt-4 rounded-xl border border-red-200 bg-red-50 p-3 text-xs font-semibold text-red-700">
        Invalid date range: Ensure dates are not in the future, and start date is before end date.
      </p>
      <p v-else class="mt-4 text-xs leading-relaxed text-slate-500 dark:text-slate-400">
        Financial figures use persisted completed-booking totals. Stock movement values use recorded quantities at the inventory item's current unit cost. Net profit is intentionally excluded because a complete operating-expense ledger is not available.
      </p>
    </div>

    <!-- Report Cards Grid -->
    <div class="grid grid-cols-1 gap-6 md:grid-cols-2 lg:grid-cols-3">
      <!-- Stock-In Report Card -->
      <div class="group relative flex flex-col justify-between rounded-2xl border border-slate-200 bg-white p-6 shadow-xs transition-all duration-200 hover:border-slate-300 hover:shadow-md">
        <div>
          <div class="flex items-center justify-between mb-5">
            <h4 class="text-lg font-bold text-slate-900">Stock-In Report</h4>
            <div class="flex h-10 w-10 items-center justify-center rounded-xl bg-sky-50 text-sky-600">
              <svg class="h-5 w-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M20 7l-8-4-8 4m16 0l-8 4m8-4v10l-8 4m0-10L4 7m8 4v10M4 7v10l8 4" />
              </svg>
            </div>
          </div>

          <div class="space-y-3 border-t border-slate-100 pt-4">
            <div class="flex justify-between text-xs sm:text-sm">
              <span class="text-slate-500 font-medium">Stocked Items (Period):</span>
              <span class="font-bold text-slate-900">{{ inventoryInPeriod.length }}</span>
            </div>
            <div class="flex justify-between text-xs sm:text-sm">
              <span class="text-slate-500 font-medium">Low Stock Flagged:</span>
              <span class="font-bold text-amber-600">{{ lowStockCountInPeriod }}</span>
            </div>
            <div class="flex justify-between text-xs sm:text-sm">
              <span class="text-slate-500 font-medium">Recorded Stock-In Value:</span>
              <span class="font-bold text-slate-900">{{ formatCurrency(totalInventoryValueInPeriod) }}</span>
            </div>
          </div>
        </div>

        <div class="mt-8 pt-4 border-t border-slate-100">
          <button
            type="button"
            class="w-full inline-flex items-center justify-center gap-2 rounded-xl bg-linear-to-r from-sky-600 to-sky-700 px-4 py-2.5 font-semibold text-white shadow-md shadow-sky-600/20 hover:from-sky-700 hover:to-sky-800 disabled:opacity-50 transition-all text-sm"
            :disabled="isExporting"
            @click="generateStockInReportPDF"
          >
            <svg class="h-4 w-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 10v6m0 0l-3-3m3 3l3-3m2 8H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
            </svg>
            {{ isExporting ? 'Exporting PDF...' : 'Export Stock-In PDF' }}
          </button>
        </div>
      </div>

      <!-- Financial Summary Report Card -->
      <div class="group relative flex flex-col justify-between rounded-2xl border border-slate-200 bg-white p-6 shadow-xs transition-all duration-200 hover:border-slate-300 hover:shadow-md">
        <div>
          <div class="flex items-center justify-between mb-5">
            <h4 class="text-lg font-bold text-slate-900">Financial Summary</h4>
            <div class="flex h-10 w-10 items-center justify-center rounded-xl bg-emerald-50 text-emerald-600">
              <svg class="h-5 w-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 19v-6a2 2 0 00-2-2H5a2 2 0 00-2 2v6a2 2 0 002 2h2a2 2 0 002-2zm0 0V9a2 2 0 012-2h2a2 2 0 012 2v10m-6 0a2 2 0 002 2h2a2 2 0 002-2m0 0V5a2 2 0 012-2h2a2 2 0 012 2v14a2 2 0 01-2 2h-2a2 2 0 01-2-2z" />
              </svg>
            </div>
          </div>

          <div class="space-y-2.5 border-t border-slate-100 pt-4 text-xs sm:text-sm">
            <div class="flex justify-between">
              <span class="text-slate-500 font-medium">Projects in Period (Active / Done):</span>
              <span class="font-bold text-slate-900">{{ ongoingProjects }} / {{ completedProjects }}</span>
            </div>
            <div class="flex justify-between">
              <span class="text-slate-500 font-medium">Completed Materials:</span>
              <span class="font-semibold text-slate-800">{{ formatCurrency(totalMaterialsCost) }}</span>
            </div>
            <div class="flex justify-between">
              <span class="text-slate-500 font-medium">Completed Labor Charges:</span>
              <span class="font-semibold text-slate-800">{{ formatCurrency(totalLaborCost) }}</span>
            </div>
            <div class="flex justify-between border-t border-slate-100 pt-2">
              <span class="text-slate-500 font-medium">Completed Revenue:</span>
              <span class="font-bold text-emerald-700">{{ formatCurrency(totalSalesRevenue) }}</span>
            </div>
            <div class="rounded-xl border border-sky-100 bg-sky-50 p-2.5 text-xs leading-relaxed text-sky-900 mt-2">
              Profit is not shown because payroll, overhead, taxes, and other operating expenses are not fully recorded in WeldTrack.
            </div>
          </div>
        </div>

        <div class="mt-6 pt-4 border-t border-slate-100">
          <button
            type="button"
            class="w-full inline-flex items-center justify-center gap-2 rounded-xl bg-linear-to-r from-emerald-600 to-green-600 px-4 py-2.5 font-semibold text-white shadow-md shadow-emerald-600/20 hover:from-emerald-700 hover:to-green-700 disabled:opacity-50 transition-all text-sm"
            :disabled="isExporting"
            @click="generateFinancialReportPDF"
          >
            <svg class="h-4 w-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 10v6m0 0l-3-3m3 3l3-3m2 8H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
            </svg>
            {{ isExporting ? 'Exporting PDF...' : 'Export Financial PDF' }}
          </button>
        </div>
      </div>

      <!-- Staff Attendance Report Card -->
      <div class="group relative flex flex-col justify-between rounded-2xl border border-slate-200 bg-white p-6 shadow-xs transition-all duration-200 hover:border-slate-300 hover:shadow-md">
        <div>
          <div class="flex items-center justify-between mb-5">
            <h4 class="text-lg font-bold text-slate-900">Staff Attendance</h4>
            <div class="flex h-10 w-10 items-center justify-center rounded-xl bg-sky-50 text-sky-600">
              <svg class="h-5 w-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 4.354a4 4 0 110 5.292m0 0H8.646a4 4 0 010-5.292m3.354 0V3m0 16h-1a2 2 0 01-2-2V7a2 2 0 012-2h1m0 0h1a2 2 0 012 2v12a2 2 0 01-2 2h-1m0 0V3m6 0h-1a2 2 0 00-2 2v12a2 2 0 002 2h1" />
              </svg>
            </div>
          </div>

          <div class="space-y-3 border-t border-slate-100 pt-4">
            <div class="flex justify-between text-xs sm:text-sm">
              <span class="text-slate-500 font-medium">Active Staff Recorded:</span>
              <span class="font-bold text-slate-900">{{ staffData.length }}</span>
            </div>
            <div class="flex justify-between text-xs sm:text-sm">
              <span class="text-slate-500 font-medium">Total Worked Hours:</span>
              <span class="font-bold text-slate-900">{{ formatHours(totalStaffHours) }}</span>
            </div>
            <div class="flex justify-between text-xs sm:text-sm">
              <span class="text-slate-500 font-medium">Total Overtime:</span>
              <span class="font-bold text-amber-600">{{ formatHours(totalOvertimeHours) }}</span>
            </div>
            <div class="flex justify-between text-xs sm:text-sm">
              <span class="text-slate-500 font-medium">Staff with OT:</span>
              <span class="font-semibold text-slate-800">{{ staffWithOvertimeCount }}</span>
            </div>
          </div>
        </div>

        <div class="mt-8 pt-4 border-t border-slate-100">
          <button
            type="button"
            class="w-full inline-flex items-center justify-center gap-2 rounded-xl bg-linear-to-r from-sky-600 to-sky-700 px-4 py-2.5 font-semibold text-white shadow-md shadow-sky-600/20 hover:from-sky-700 hover:to-sky-800 disabled:opacity-50 transition-all text-sm"
            :disabled="isExporting"
            @click="generateStaffAttendanceReportPDF"
          >
            <svg class="h-4 w-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 10v6m0 0l-3-3m3 3l3-3m2 8H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
            </svg>
            {{ isExporting ? 'Exporting PDF...' : 'Export Attendance PDF' }}
          </button>
        </div>
      </div>
    </div>
  </section>
</template>
