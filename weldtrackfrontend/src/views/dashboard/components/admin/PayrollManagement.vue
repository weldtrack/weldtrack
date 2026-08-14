<script setup lang="ts">
import InfoTooltip from '../../../../components/ui/InfoTooltip.vue'
import { computed, onMounted, reactive, ref } from 'vue'
import { Check, PhilippinePeso, Plus, Trash2 } from 'lucide-vue-next'
import LocalLoader from '../../../../components/ui/LocalLoader.vue'
import { fetchStaffDirectoryApi } from '../../../../api/auth'
import { createPayslip, deletePayslip, fetchPayslips, updatePayslipStatus } from '../../../../api/payroll'
import type { Payslip, PayslipCreatePayload } from '../../../../types/payroll'

const payslips = ref<Payslip[]>([])
const staff = ref<{ id: string; email: string }[]>([])
const loading = ref(false)
const saving = ref(false)
const error = ref('')
const showForm = ref(false)
const rateSettingsMessage = ref('')
const RATE_SETTINGS_KEY = 'weldtrack.payroll-rate-defaults'

const rateSettings = reactive({
  hourlyRate: 0,
  overtimeRate: 0,
})

const form = reactive<PayslipCreatePayload>({
  staff_id: '',
  period_start: '',
  period_end: '',
  hourly_rate: 0,
  overtime_rate: null,
  allowances: 0,
  bonuses: 0,
  deductions: 0,
  notes: '',
})

const totalPayroll = computed(() => payslips.value.reduce((sum, item) => sum + Number(item.net_pay), 0))

const currency = (value: number | string) => new Intl.NumberFormat('en-PH', {
  style: 'currency', currency: 'PHP', minimumFractionDigits: 2,
}).format(Number(value || 0))

const period = (item: Payslip) => `${item.period_start} – ${item.period_end}`

function toDateInput(date: Date) {
  return `${date.getFullYear()}-${String(date.getMonth() + 1).padStart(2, '0')}-${String(date.getDate()).padStart(2, '0')}`
}

function semiMonthlyPeriod(reference = new Date(), half?: 'first' | 'second') {
  const selectedHalf = half ?? (reference.getDate() <= 15 ? 'first' : 'second')
  const year = reference.getFullYear()
  const month = reference.getMonth()
  const start = selectedHalf === 'first' ? new Date(year, month, 1) : new Date(year, month, 16)
  const end = selectedHalf === 'first' ? new Date(year, month, 15) : new Date(year, month + 1, 0)
  return { start: toDateInput(start), end: toDateInput(end) }
}

function applyPayPeriod(half?: 'first' | 'second') {
  const dates = semiMonthlyPeriod(new Date(), half)
  form.period_start = dates.start
  form.period_end = dates.end
}

function loadRateSettings() {
  try {
    const stored = JSON.parse(localStorage.getItem(RATE_SETTINGS_KEY) || '{}')
    rateSettings.hourlyRate = Math.max(0, Number(stored.hourlyRate || 0))
    rateSettings.overtimeRate = Math.max(0, Number(stored.overtimeRate || 0))
  } catch {
    localStorage.removeItem(RATE_SETTINGS_KEY)
  }
}

function saveRateSettings() {
  if (rateSettings.hourlyRate <= 0 || rateSettings.overtimeRate <= 0) {
    rateSettingsMessage.value = 'Enter a valid hourly rate and overtime rate.'
    return
  }
  localStorage.setItem(RATE_SETTINGS_KEY, JSON.stringify(rateSettings))
  rateSettingsMessage.value = 'Default payroll rates saved on this device.'
}

function openPayslipForm() {
  Object.assign(form, {
    staff_id: '',
    hourly_rate: rateSettings.hourlyRate,
    overtime_rate: rateSettings.overtimeRate || null,
    allowances: 0,
    bonuses: 0,
    deductions: 0,
    notes: '',
  })
  applyPayPeriod()
  showForm.value = true
}

function messageFrom(errorValue: unknown) {
  const response = errorValue as { response?: { data?: { detail?: string } } }
  return response.response?.data?.detail || 'Unable to complete the payroll request.'
}

async function load() {
  loading.value = true
  error.value = ''
  try {
    const [payslipData, staffData] = await Promise.all([fetchPayslips(), fetchStaffDirectoryApi()])
    payslips.value = payslipData
    staff.value = (Array.isArray(staffData) ? staffData : []).map((item: { id?: string; email?: string }) => ({
      id: String(item.id || ''), email: item.email || '',
    }))
  } catch (err) {
    error.value = messageFrom(err)
  } finally {
    loading.value = false
  }
}

async function submit() {
  saving.value = true
  error.value = ''
  try {
    await createPayslip(form)
    showForm.value = false
    Object.assign(form, { staff_id: '', period_start: '', period_end: '', hourly_rate: rateSettings.hourlyRate, overtime_rate: rateSettings.overtimeRate || null, allowances: 0, bonuses: 0, deductions: 0, notes: '' })
    await load()
  } catch (err) {
    error.value = messageFrom(err)
  } finally {
    saving.value = false
  }
}

async function advance(item: Payslip) {
  const next = item.status === 'draft' ? 'approved' : 'paid'
  try {
    await updatePayslipStatus(item.id, next)
    await load()
  } catch (err) {
    error.value = messageFrom(err)
  }
}

async function remove(item: Payslip) {
  if (!window.confirm(`Delete the draft payslip for ${item.staff_email}?`)) return
  try {
    await deletePayslip(item.id)
    await load()
  } catch (err) {
    error.value = messageFrom(err)
  }
}

onMounted(() => {
  loadRateSettings()
  void load()
})
</script>

<template>
  <section class="relative space-y-6">
    <LocalLoader v-if="loading" />
    <!-- List View -->
    <template v-if="!showForm">
      <div class="flex flex-col gap-4 lg:flex-row lg:items-center lg:justify-between">
        <div class="flex items-start gap-3">
          <div class="flex h-10 w-10 items-center justify-center rounded-lg ">
            <PhilippinePeso class="dashboard-view-icon h-5 w-5 text-sky-600 dark:text-sky-400" />
          </div>
          <div>
            <h2 class="text-2xl font-semibold text-gray-900">Payroll Management</h2>
            <p class="mt-1 text-sm text-gray-600">Create attendance-based payslips and manage payment status.</p>
          </div>
        </div>
        <button class="inline-flex items-center justify-center gap-2 rounded-lg bg-sky-600 px-4 py-3 font-semibold text-white transition-colors hover:bg-sky-700" @click="openPayslipForm">
          <Plus class="h-4 w-4" /> New payslip
        </button>
      </div>

      <div class="grid grid-cols-1 gap-4 sm:grid-cols-3">
        <div class="rounded-xl border border-sky-200 bg-sky-50 p-5 dark:border-sky-900/50 dark:bg-sky-950/40">
          <p class="text-xs font-bold uppercase tracking-wider text-sky-700 dark:text-sky-300">Payslips</p>
          <p class="mt-2 text-3xl font-black text-slate-900 dark:text-slate-100">{{ payslips.length }}</p>
        </div>
        <div class="rounded-xl border border-amber-200 bg-amber-50 p-5 dark:border-amber-900/50 dark:bg-amber-950/40">
          <p class="text-xs font-bold uppercase tracking-wider text-amber-700 dark:text-amber-300">Total Net Payroll</p>
          <p class="mt-2 text-3xl font-black text-slate-900 dark:text-slate-100">{{ currency(totalPayroll) }}</p>
        </div>
        <div class="rounded-xl border border-emerald-200 bg-emerald-50 p-5 dark:border-emerald-900/50 dark:bg-emerald-950/40">
          <p class="text-xs font-bold uppercase tracking-wider text-emerald-700 dark:text-emerald-300">Awaiting Approval</p>
          <p class="mt-2 text-3xl font-black text-slate-900 dark:text-slate-100">{{ payslips.filter(p => p.status === 'draft').length }}</p>
        </div>
      </div>

      <!-- Reusable payroll rates -->
      <div class="rounded-2xl border border-slate-200 bg-white p-5 shadow-sm dark:border-slate-800 dark:bg-slate-900 sm:p-6">
        <div class="flex flex-col gap-4 lg:flex-row lg:items-end lg:justify-between">
          <div class="grid flex-1 gap-4 sm:grid-cols-2">
            <div class="sm:col-span-2">
              <h3 class="font-semibold text-slate-900 dark:text-slate-100">Default Payroll Rates</h3>
              <p class="mt-1 text-sm text-slate-500 dark:text-slate-400">These rates automatically fill every new payslip on this device.</p>
            </div>
            <label class="text-sm font-medium text-slate-700 dark:text-slate-300">
              Hourly rate
              <input v-model.number="rateSettings.hourlyRate" min="0.01" step="0.01" type="number" class="mt-1.5 w-full rounded-xl border border-slate-200 bg-white px-4 py-2.5 text-slate-900 outline-none focus:border-sky-500 dark:border-slate-700 dark:bg-slate-950 dark:text-slate-100">
            </label>
            <label class="text-sm font-medium text-slate-700 dark:text-slate-300">
              Overtime rate per hour
              <input v-model.number="rateSettings.overtimeRate" min="0.01" step="0.01" type="number" class="mt-1.5 w-full rounded-xl border border-slate-200 bg-white px-4 py-2.5 text-slate-900 outline-none focus:border-sky-500 dark:border-slate-700 dark:bg-slate-950 dark:text-slate-100">
            </label>
          </div>
          <button type="button" class="rounded-xl bg-slate-900 px-5 py-2.5 text-sm font-semibold text-white hover:bg-slate-800 dark:bg-sky-600 dark:hover:bg-sky-500" @click="saveRateSettings">Save Rate Defaults</button>
        </div>
        <p v-if="rateSettingsMessage" class="mt-3 text-sm text-slate-600 dark:text-slate-400">{{ rateSettingsMessage }}</p>
      </div>

      <p v-if="error" class="rounded-xl border border-red-200 bg-red-50 px-4 py-3 text-sm text-red-700">{{ error }}</p>
      
      <div v-if="loading" class="rounded-2xl border border-slate-200 bg-white p-8 text-center dark:border-slate-800 dark:bg-slate-900">
        <p class="text-slate-600 dark:text-slate-400">Loading payroll...</p>
      </div>
      <div v-else-if="!payslips.length" class="rounded-2xl border border-slate-200 bg-white p-8 text-center dark:border-slate-800 dark:bg-slate-900">
        <p class="text-slate-600 dark:text-slate-400">No payslips created yet.</p>
      </div>
      <div v-else class="overflow-hidden rounded-2xl border border-slate-200 bg-white shadow-xs dark:border-slate-800 dark:bg-slate-900">
        <div class="overflow-x-auto">
          <table class="w-full min-w-[900px] divide-y divide-slate-100 dark:divide-slate-800">
            <thead class="bg-slate-50 dark:bg-slate-800/80">
              <tr class="text-left">
                <th class="px-6 py-4 text-xs font-bold uppercase tracking-wider text-slate-500 dark:text-slate-400">Staff</th>
                <th class="px-6 py-4 text-xs font-bold uppercase tracking-wider text-slate-500 dark:text-slate-400">Period</th>
                <th class="px-6 py-4 text-xs font-bold uppercase tracking-wider text-slate-500 dark:text-slate-400">Hours</th>
                <th class="px-6 py-4 text-xs font-bold uppercase tracking-wider text-slate-500 dark:text-slate-400">Net Pay</th>
                <th class="px-6 py-4 text-xs font-bold uppercase tracking-wider text-slate-500 dark:text-slate-400">Status</th>
                <th class="px-6 py-4 text-xs font-bold uppercase tracking-wider text-slate-500 dark:text-slate-400 text-right sticky right-0 z-10 bg-slate-50 dark:bg-slate-800 shadow-[-12px_0_15px_-4px_rgba(0,0,0,0.05)]">Actions</th>
              </tr>
            </thead>
            <tbody class="divide-y divide-slate-100 dark:divide-slate-800 bg-transparent">
              <tr v-for="item in payslips" :key="item.id" class="transition-colors hover:bg-slate-50/50 dark:hover:bg-slate-800/50 group">
                <td class="px-6 py-4 font-semibold text-gray-900 whitespace-nowrap">{{ item.staff_email }}</td>
                <td class="px-6 py-4 text-gray-700 whitespace-nowrap">{{ period(item) }}</td>
                <td class="px-6 py-4 text-gray-700 whitespace-nowrap">{{ item.regular_hours }} + {{ item.overtime_hours }} OT</td>
                <td class="px-6 py-4 font-semibold text-gray-900 whitespace-nowrap">{{ currency(item.net_pay) }}</td>
                <td class="px-6 py-4 whitespace-nowrap">
                  <span
                    :class="[
                      'inline-flex items-center rounded-full px-2.5 py-1 text-xs font-semibold whitespace-nowrap capitalize',
                      item.status === 'paid' ? 'bg-emerald-50 text-emerald-700 ring-1 ring-inset ring-emerald-600/20' : 
                      item.status === 'approved' ? 'bg-blue-50 text-blue-700 ring-1 ring-inset ring-blue-600/20' : 
                      'bg-slate-100 text-slate-700 ring-1 ring-inset ring-slate-600/20'
                    ]"
                  >
                    {{ item.status }}
                  </span>
                </td>
                <td class="px-6 py-4 whitespace-nowrap sticky right-0 z-10 bg-white dark:bg-slate-900 group-hover:bg-slate-50 dark:group-hover:bg-slate-800 shadow-[-12px_0_15px_-4px_rgba(0,0,0,0.05)]">
                  <div class="flex justify-end gap-3">
                    <button
                      v-if="item.status !== 'paid'"
                      class="inline-flex items-center gap-1.5 rounded-lg border border-slate-200 bg-white px-3 py-1.5 text-xs font-semibold text-slate-700 shadow-sm hover:bg-slate-50 transition-colors"
                      @click="advance(item)"
                    >
                      <Check class="h-3.5 w-3.5 text-emerald-600" />
                      {{ item.status === 'draft' ? 'Approve' : 'Mark paid' }}
                    </button>
                    <button
                      v-if="item.status === 'draft'"
                      class="text-red-600 transition-colors hover:text-red-800 p-1.5"
                      aria-label="Delete draft"
                      @click="remove(item)"
                    >
                      <Trash2 class="h-4 w-4" />
                    </button>
                  </div>
                </td>
              </tr>
            </tbody>
          </table>
        </div>
      </div>
    </template>

    <!-- Form View -->
    <template v-else>
      <div class="rounded-xl border border-slate-200 bg-white shadow-sm dark:border-slate-800 dark:bg-slate-900">
        <div class="border-b border-slate-100 px-6 py-5 flex items-center justify-between bg-transparent">
          <div>
            <h3 class="text-xl font-bold text-slate-900">Create Payslip</h3>
            <p class="text-sm text-slate-500 mt-1">Attendance-based payroll snapshot</p>
          </div>
          <button 
            @click="showForm = false" 
            class="text-sm font-semibold text-slate-600 hover:text-slate-900 transition-colors"
          >
            Cancel
          </button>
        </div>

        <div class="p-6">
          <form id="payslip-form" class="grid gap-5 md:grid-cols-2 max-w-4xl" @submit.prevent="submit">
            <div class="md:col-span-1">
              <label class="flex items-center text-sm font-semibold text-gray-700 mb-1.5">Staff <span class="text-red-500">*</span><InfoTooltip text="Please provide the staff." /></label>
              <select v-model="form.staff_id" required class="w-full rounded-xl border border-gray-300 bg-white px-4 py-3 shadow-sm outline-none transition focus:border-sky-500 focus:ring-2 focus:ring-sky-200">
                <option value="" disabled>Select staff</option>
                <option v-for="member in staff" :key="member.id" :value="member.id">{{ member.email }}</option>
              </select>
            </div>
            <div class="hidden md:block"></div>
            
            <div>
              <label class="flex items-center text-sm font-semibold text-gray-700 mb-1.5">Period start <span class="text-red-500">*</span><InfoTooltip text="Please provide the period start." /></label>
              <input v-model="form.period_start" required type="date" class="w-full rounded-xl border border-gray-300 bg-white px-4 py-3 shadow-sm outline-none transition focus:border-sky-500 focus:ring-2 focus:ring-sky-200">
            </div>
            
            <div>
              <label class="flex items-center text-sm font-semibold text-gray-700 mb-1.5">Period end <span class="text-red-500">*</span><InfoTooltip text="Please provide the period end." /></label>
              <input v-model="form.period_end" required type="date" class="w-full rounded-xl border border-gray-300 bg-white px-4 py-3 shadow-sm outline-none transition focus:border-sky-500 focus:ring-2 focus:ring-sky-200">
            </div>

            <div class="md:col-span-2 flex flex-wrap items-center gap-2 rounded-xl bg-slate-50 p-3 dark:bg-slate-800/60">
              <span class="mr-1 text-xs font-semibold uppercase tracking-wide text-slate-500">Current month cutoff</span>
              <button type="button" class="rounded-lg border border-slate-200 bg-white px-3 py-1.5 text-xs font-semibold text-slate-700 hover:bg-slate-100 dark:border-slate-700 dark:bg-slate-900 dark:text-slate-300" @click="applyPayPeriod('first')">1st–15th</button>
              <button type="button" class="rounded-lg border border-slate-200 bg-white px-3 py-1.5 text-xs font-semibold text-slate-700 hover:bg-slate-100 dark:border-slate-700 dark:bg-slate-900 dark:text-slate-300" @click="applyPayPeriod('second')">16th–Month End</button>
            </div>
            
            <div>
              <label class="flex items-center text-sm font-semibold text-gray-700 mb-1.5">Hourly rate <span class="text-red-500">*</span><InfoTooltip text="Please provide the hourly rate." /></label>
              <input v-model.number="form.hourly_rate" required min="0.01" step="0.01" type="number" class="w-full rounded-xl border border-gray-300 bg-white px-4 py-3 shadow-sm outline-none transition focus:border-sky-500 focus:ring-2 focus:ring-sky-200">
            </div>
            
            <div>
              <label class="flex items-center text-sm font-semibold text-gray-700 mb-1.5">Overtime rate <span class="font-normal text-gray-400">(default 1.25×)</span><InfoTooltip text="Please provide the overtime rate default 125." /></label>
              <input v-model.number="form.overtime_rate" min="0" step="0.01" type="number" class="w-full rounded-xl border border-gray-300 bg-white px-4 py-3 shadow-sm outline-none transition focus:border-sky-500 focus:ring-2 focus:ring-sky-200">
            </div>
            
            <div>
              <label class="flex items-center text-sm font-semibold text-gray-700 mb-1.5">Allowances<InfoTooltip text="Please provide the allowances." /></label>
              <input v-model.number="form.allowances" min="0" step="0.01" type="number" class="w-full rounded-xl border border-gray-300 bg-white px-4 py-3 shadow-sm outline-none transition focus:border-sky-500 focus:ring-2 focus:ring-sky-200">
            </div>
            
            <div>
              <label class="flex items-center text-sm font-semibold text-gray-700 mb-1.5">Bonuses<InfoTooltip text="Please provide the bonuses." /></label>
              <input v-model.number="form.bonuses" min="0" step="0.01" type="number" class="w-full rounded-xl border border-gray-300 bg-white px-4 py-3 shadow-sm outline-none transition focus:border-sky-500 focus:ring-2 focus:ring-sky-200">
            </div>
            
            <div>
              <label class="flex items-center text-sm font-semibold text-gray-700 mb-1.5">Deductions<InfoTooltip text="Please provide the deductions." /></label>
              <input v-model.number="form.deductions" min="0" step="0.01" type="number" class="w-full rounded-xl border border-gray-300 bg-white px-4 py-3 shadow-sm outline-none transition focus:border-sky-500 focus:ring-2 focus:ring-sky-200">
            </div>
            
            <div class="md:col-span-2">
              <label class="flex items-center text-sm font-semibold text-gray-700 mb-1.5">Notes<InfoTooltip text="Please provide the notes." /></label>
              <input v-model="form.notes" maxlength="1000" class="w-full rounded-xl border border-gray-300 bg-white px-4 py-3 shadow-sm outline-none transition focus:border-sky-500 focus:ring-2 focus:ring-sky-200">
            </div>
            
            <div class="md:col-span-2 mt-4 pt-4 border-t border-slate-100 flex justify-end gap-3">
              <button type="button" class="rounded-xl border border-slate-200 bg-white px-5 py-2.5 font-semibold text-slate-700 shadow-sm hover:bg-slate-50 transition-colors" @click="showForm = false">Cancel</button>
              <button type="submit" :disabled="saving" class="inline-flex min-w-40 items-center justify-center gap-2 rounded-xl bg-linear-to-r from-sky-600 to-sky-700 px-6 py-2.5 font-semibold text-white shadow-md shadow-sky-600/20 hover:from-sky-700 hover:to-sky-800 disabled:opacity-60 transition-all">{{ saving ? 'Creating…' : 'Calculate and create' }}</button>
            </div>
          </form>
        </div>
      </div>
    </template>
  </section>
</template>
