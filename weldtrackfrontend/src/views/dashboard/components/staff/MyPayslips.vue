<script setup lang="ts">
import { onMounted, ref } from 'vue'
import { Printer, ReceiptText } from 'lucide-vue-next'
import { fetchMyPayslips } from '../../../../api/payroll'
import type { Payslip } from '../../../../types/payroll'

const payslips = ref<Payslip[]>([])
const selected = ref<Payslip | null>(null)
const loading = ref(true)
const error = ref('')
const currency = (value: number | string) => new Intl.NumberFormat('en-PH', { style: 'currency', currency: 'PHP' }).format(Number(value || 0))
const printPayslip = () => window.print()

onMounted(async () => {
  try {
    payslips.value = await fetchMyPayslips()
    selected.value = payslips.value[0] || null
  } catch {
    error.value = 'Unable to load your payslips.'
  } finally {
    loading.value = false
  }
})
</script>

<template>
  <div class="space-y-6">
    <div class="no-print"><p class="text-sm font-medium text-emerald-600">Compensation records</p><h2 class="text-2xl font-semibold text-gray-900">My Payslips</h2><p class="mt-1 text-sm text-gray-500">View and print your finalized payroll records.</p></div>
    <p v-if="error" class="rounded-xl border border-red-200 bg-red-50 p-4 text-red-700">{{ error }}</p>
    <div v-if="loading" class="rounded-2xl border border-gray-200 bg-white p-8 text-center text-gray-500 shadow-sm">Loading payslips…</div>
    <div v-else-if="!payslips.length" class="rounded-2xl border border-gray-200 bg-white p-8 text-center text-gray-500 shadow-sm"><ReceiptText class="mx-auto mb-3 h-8 w-8" />No payslips are available yet.</div>
    <div v-else class="grid gap-6 lg:grid-cols-[280px_1fr]">
      <div class="no-print space-y-2"><button v-for="item in payslips" :key="item.id" class="w-full rounded-xl border border-gray-200 bg-white p-4 text-left shadow-sm" :class="selected?.id === item.id ? '!border-emerald-500 ring-1 ring-emerald-500' : ''" @click="selected = item"><p class="font-semibold">{{ item.period_start }} – {{ item.period_end }}</p><div class="mt-2 flex justify-between text-sm"><span class="capitalize text-gray-500">{{ item.status }}</span><span class="font-semibold">{{ currency(item.net_pay) }}</span></div></button></div>
      <article v-if="selected" class="payslip-print rounded-2xl border border-gray-200 bg-white p-6 shadow-sm sm:p-8">
        <div class="flex items-start justify-between border-b pb-5"><div><p class="text-sm font-semibold uppercase tracking-widest text-emerald-600">WeldTrack</p><h3 class="mt-1 text-2xl font-bold">Payslip</h3><p class="mt-1 text-sm text-gray-500">{{ selected.period_start }} to {{ selected.period_end }}</p></div><button class="no-print inline-flex items-center gap-2 rounded-xl border px-4 py-2 text-sm font-semibold" @click="printPayslip"><Printer class="h-4 w-4" /> Print</button></div>
        <div class="grid gap-4 border-b py-5 sm:grid-cols-2"><div><p class="text-xs uppercase text-gray-400">Employee</p><p class="font-semibold">{{ selected.staff_email }}</p></div><div><p class="text-xs uppercase text-gray-400">Status</p><p class="font-semibold capitalize">{{ selected.status }}</p></div></div>
        <div class="grid gap-8 py-6 sm:grid-cols-2"><div><h4 class="mb-3 font-semibold">Earnings</h4><dl class="space-y-2 text-sm"><div class="flex justify-between"><dt>Regular ({{ selected.regular_hours }} hrs × {{ currency(selected.hourly_rate) }})</dt><dd>{{ currency(selected.regular_pay) }}</dd></div><div class="flex justify-between"><dt>Overtime ({{ selected.overtime_hours }} hrs × {{ currency(selected.overtime_rate) }})</dt><dd>{{ currency(selected.overtime_pay) }}</dd></div><div class="flex justify-between"><dt>Allowances</dt><dd>{{ currency(selected.allowances) }}</dd></div><div class="flex justify-between"><dt>Bonuses</dt><dd>{{ currency(selected.bonuses) }}</dd></div></dl></div><div><h4 class="mb-3 font-semibold">Summary</h4><dl class="space-y-2 text-sm"><div class="flex justify-between"><dt>Gross pay</dt><dd>{{ currency(selected.gross_pay) }}</dd></div><div class="flex justify-between text-red-600"><dt>Deductions</dt><dd>− {{ currency(selected.deductions) }}</dd></div><div class="mt-4 flex justify-between border-t pt-4 text-lg font-bold"><dt>Net pay</dt><dd>{{ currency(selected.net_pay) }}</dd></div></dl></div></div>
        <div v-if="selected.notes" class="rounded-xl bg-gray-50 p-4 text-sm"><p class="mb-1 font-semibold">Notes</p><p class="text-gray-600">{{ selected.notes }}</p></div>
      </article>
    </div>
  </div>
</template>

<style scoped>
@media print {
  :global(body *) { visibility: hidden; }
  .payslip-print, .payslip-print * { visibility: visible; }
  .payslip-print { position: fixed; inset: 0; border: 0; }
  .no-print { display: none !important; }
}
</style>
