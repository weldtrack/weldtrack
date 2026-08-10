<script setup lang="ts">
import { computed, onMounted, reactive, ref } from 'vue'
import { Check, CircleDollarSign, Plus, Trash2 } from 'lucide-vue-next'
import LocalLoader from '../../../../components/ui/LocalLoader.vue'
import ModalShell from '../../../../components/ui/ModalShell.vue'
import { fetchStaffDirectoryApi } from '../../../../api/auth'
import { createPayslip, deletePayslip, fetchPayslips, updatePayslipStatus } from '../../../../api/payroll'
import type { Payslip, PayslipCreatePayload } from '../../../../types/payroll'

const payslips = ref<Payslip[]>([])
const staff = ref<{ id: string; email: string }[]>([])
const loading = ref(false)
const saving = ref(false)
const error = ref('')
const showForm = ref(false)

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
    Object.assign(form, { staff_id: '', period_start: '', period_end: '', hourly_rate: 0, overtime_rate: null, allowances: 0, bonuses: 0, deductions: 0, notes: '' })
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

onMounted(load)
</script>

<template>
  <section class="relative space-y-6 rounded-lg border border-gray-200 bg-white p-6">
    <LocalLoader v-if="loading" />
    <div class="flex flex-col gap-4 lg:flex-row lg:items-center lg:justify-between">
      <div class="flex items-start gap-3">
        <div class="flex h-10 w-10 items-center justify-center rounded-lg bg-linear-to-br from-sky-50 to-sky ring-1 ring-sky-100">
          <CircleDollarSign class="dashboard-view-icon h-5 w-5 text-sky-600 dark:text-sky-400" />
        </div>
        <div>
          <h2 class="text-2xl font-semibold text-gray-900">Payroll Management</h2>
          <p class="mt-1 text-sm text-gray-600">Create attendance-based payslips and manage payment status.</p>
        </div>
      </div>
      <button class="inline-flex items-center justify-center gap-2 rounded-lg bg-sky-600 px-4 py-3 font-semibold text-white transition-colors hover:bg-sky-700" @click="showForm = true">
        <Plus class="h-4 w-4" /> New payslip
      </button>
    </div>

    <div class="grid grid-cols-1 gap-4 sm:grid-cols-3">
      <div class="rounded-lg bg-sky-50 p-4"><p class="text-xs uppercase tracking-wide text-sky-600">Payslips</p><p class="mt-1 text-2xl font-bold text-gray-900">{{ payslips.length }}</p></div>
      <div class="rounded-lg bg-sky-50 p-4"><p class="text-xs uppercase tracking-wide text-sky-600">Total net payroll</p><p class="mt-1 text-2xl font-bold text-gray-900">{{ currency(totalPayroll) }}</p></div>
      <div class="rounded-lg bg-sky-50 p-4"><p class="text-xs uppercase tracking-wide text-sky-600">Awaiting approval</p><p class="mt-1 text-2xl font-bold text-gray-900">{{ payslips.filter(p => p.status === 'draft').length }}</p></div>
    </div>

    <ModalShell :show="showForm" title="Create Payslip" subtitle="Attendance-based payroll snapshot" tone="blue" size="xl" @close="showForm = false">
      <form id="payslip-form" class="grid gap-4 md:grid-cols-2" @submit.prevent="submit">
        <label class="text-sm font-semibold text-gray-700">Staff<select v-model="form.staff_id" required class="mt-1 w-full rounded-xl border border-gray-300 px-3 py-2.5"><option value="" disabled>Select staff</option><option v-for="member in staff" :key="member.id" :value="member.id">{{ member.email }}</option></select></label>
        <div></div>
        <label class="text-sm font-semibold text-gray-700">Period start<input v-model="form.period_start" required type="date" class="mt-1 w-full rounded-xl border border-gray-300 px-3 py-2.5"></label>
        <label class="text-sm font-semibold text-gray-700">Period end<input v-model="form.period_end" required type="date" class="mt-1 w-full rounded-xl border border-gray-300 px-3 py-2.5"></label>
        <label class="text-sm font-semibold text-gray-700">Hourly rate<input v-model.number="form.hourly_rate" required min="0.01" step="0.01" type="number" class="mt-1 w-full rounded-xl border border-gray-300 px-3 py-2.5"></label>
        <label class="text-sm font-semibold text-gray-700">Overtime rate <span class="font-normal text-gray-400">(default 1.25×)</span><input v-model.number="form.overtime_rate" min="0" step="0.01" type="number" class="mt-1 w-full rounded-xl border border-gray-300 px-3 py-2.5"></label>
        <label class="text-sm font-semibold text-gray-700">Allowances<input v-model.number="form.allowances" min="0" step="0.01" type="number" class="mt-1 w-full rounded-xl border border-gray-300 px-3 py-2.5"></label>
        <label class="text-sm font-semibold text-gray-700">Bonuses<input v-model.number="form.bonuses" min="0" step="0.01" type="number" class="mt-1 w-full rounded-xl border border-gray-300 px-3 py-2.5"></label>
        <label class="text-sm font-semibold text-gray-700">Deductions<input v-model.number="form.deductions" min="0" step="0.01" type="number" class="mt-1 w-full rounded-xl border border-gray-300 px-3 py-2.5"></label>
        <label class="text-sm font-semibold text-gray-700">Notes<input v-model="form.notes" maxlength="1000" class="mt-1 w-full rounded-xl border border-gray-300 px-3 py-2.5"></label>
      </form>
      <template #footer><button type="button" class="rounded-lg border border-gray-300 px-4 py-2.5 font-semibold text-gray-700" @click="showForm = false">Cancel</button><button form="payslip-form" :disabled="saving" class="rounded-lg bg-sky-600 px-5 py-2.5 font-semibold text-white disabled:opacity-60">{{ saving ? 'Creating…' : 'Calculate and create' }}</button></template>
    </ModalShell>

    <p v-if="error" class="rounded-xl border border-red-200 bg-red-50 px-4 py-3 text-sm text-red-700">{{ error }}</p>
    <div class="overflow-hidden rounded-lg border border-gray-200">
      <div v-if="loading" class="p-8 text-center text-gray-500">Loading payroll…</div>
      <div v-else-if="!payslips.length" class="p-8 text-center text-gray-500">No payslips created yet.</div>
      <div v-else class="overflow-x-auto"><table class="w-full text-left text-sm"><thead class="border-b bg-gray-50 text-gray-500"><tr><th class="p-4">Staff</th><th class="p-4">Period</th><th class="p-4">Hours</th><th class="p-4">Net pay</th><th class="p-4">Status</th><th class="p-4 text-right">Actions</th></tr></thead><tbody><tr v-for="item in payslips" :key="item.id" class="border-b last:border-0"><td class="p-4 font-medium">{{ item.staff_email }}</td><td class="p-4">{{ period(item) }}</td><td class="p-4">{{ item.regular_hours }} + {{ item.overtime_hours }} OT</td><td class="p-4 font-semibold">{{ currency(item.net_pay) }}</td><td class="p-4"><span class="rounded-full bg-slate-100 px-2.5 py-1 text-xs font-semibold capitalize">{{ item.status }}</span></td><td class="p-4"><div class="flex justify-end gap-2"><button v-if="item.status !== 'paid'" class="inline-flex items-center gap-1 rounded-lg border px-3 py-1.5" @click="advance(item)"><Check class="h-3.5 w-3.5" />{{ item.status === 'draft' ? 'Approve' : 'Mark paid' }}</button><button v-if="item.status === 'draft'" class="rounded-lg border p-2 text-red-600" aria-label="Delete draft" @click="remove(item)"><Trash2 class="h-4 w-4" /></button></div></td></tr></tbody></table></div>
    </div>
  </section>
</template>
