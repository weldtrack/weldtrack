<script setup lang="ts">
import { computed, onMounted, ref } from 'vue'
import LocalLoader from '../../../../components/ui/LocalLoader.vue'
import { Clock } from 'lucide-vue-next'
import { useAuthStore } from '../../../../stores/auth'
import { useBookingsStore } from '../../../../stores/bookings'
import { getUserFriendlyApiError } from '../../../../services/errorMessage'
import HistoryCard from '../shared/HistoryCard.vue'

const authStore = useAuthStore()
const bookingsStore = useBookingsStore()
const loadError = ref('')

const currentEmail = computed(() => authStore.email || '')

const isLoading = ref(true)

onMounted(async () => {
  isLoading.value = true
  try {
    await loadBookings()
  } finally {
    isLoading.value = false
  }
})

async function loadBookings() {
  loadError.value = ''
  try {
    await bookingsStore.fetchBookings()
  } catch (error) {
    loadError.value = getUserFriendlyApiError(error)
  }
}

const customerBookings = computed(() => {
  const bookings = Array.isArray(bookingsStore.bookings) ? bookingsStore.bookings : []

  return bookings
    .filter((b) => b.email === currentEmail.value && (b.status === 'completed' || b.status === 'cancelled'))
    .sort((a, b) => {
        const tb = Number(new Date(b.createdDate ?? 0).getTime() || 0)
        const ta = Number(new Date(a.createdDate ?? 0).getTime() || 0)
        return tb - ta
      })
})

const completedBookings = computed(() => customerBookings.value.filter((b) => b.status === 'completed'))
const cancelledBookings = computed(() => customerBookings.value.filter((b) => b.status === 'cancelled'))
</script>

<template>
  <div class="space-y-6 relative">
    <LocalLoader v-if="isLoading" />

    <!-- Header -->
    <div class="flex items-start gap-3">
      <div class="flex h-12 w-12 items-center justify-center">
        <Clock class="dashboard-view-icon h-6 w-6 text-sky-600 dark:text-sky-400" />
      </div>
      <div>
        <h1 class="text-2xl font-semibold text-slate-900 dark:text-slate-100">Booking History</h1>
        <p class="text-sm text-slate-600 dark:text-slate-400">Track all your completed and cancelled welding project bookings</p>
      </div>
    </div>

    <!-- Summary Metric Cards -->
    <div class="grid grid-cols-1 gap-4 sm:grid-cols-3">
      <div class="rounded-xl border border-sky-200 bg-sky-50 p-5 dark:border-sky-900/50 dark:bg-sky-950/40">
        <p class="text-xs font-bold uppercase tracking-wider text-sky-700 dark:text-sky-300">Completed Bookings</p>
        <p class="mt-2 text-3xl font-black text-slate-900 dark:text-slate-100">{{ completedBookings.length }}</p>
      </div>
      <div class="rounded-xl border border-rose-200 bg-rose-50 p-5 dark:border-rose-900/50 dark:bg-rose-950/40">
        <p class="text-xs font-bold uppercase tracking-wider text-rose-700 dark:text-rose-300">Cancelled Bookings</p>
        <p class="mt-2 text-3xl font-black text-slate-900 dark:text-slate-100">{{ cancelledBookings.length }}</p>
      </div>
      <div class="rounded-xl border border-slate-200 bg-slate-50 p-5 dark:border-slate-800 dark:bg-slate-900/60">
        <p class="text-xs font-bold uppercase tracking-wider text-slate-500 dark:text-slate-400">Total Records</p>
        <p class="mt-2 text-3xl font-black text-slate-900 dark:text-slate-100">{{ customerBookings.length }}</p>
      </div>
    </div>

    <!-- Full-width history list -->
    <div class="grid w-full grid-cols-1 gap-4">
      <div v-if="loadError" class="rounded-xl border border-red-200 bg-red-50 p-8 text-center col-span-full dark:border-red-900/50 dark:bg-red-950/40">
        <h3 class="text-lg font-bold text-red-800 dark:text-red-300">Unable to load booking history</h3>
        <p class="mt-1 text-sm text-red-700 dark:text-red-400">{{ loadError }}</p>
        <button
          type="button"
          class="mt-4 inline-flex items-center justify-center rounded-xl bg-red-600 px-5 py-2.5 text-sm font-semibold text-white transition-colors hover:bg-red-700"
          @click="loadBookings"
        >
          Try again
        </button>
      </div>
      <div v-else-if="customerBookings.length === 0" class="rounded-xl border border-slate-200 bg-slate-50 p-8 text-center col-span-full dark:border-slate-800 dark:bg-slate-900">
        <Clock class="mx-auto h-10 w-10 text-slate-400" />
        <h3 class="mt-3 text-lg font-bold text-slate-900 dark:text-slate-100">No booking history recorded</h3>
        <p class="mt-1 text-sm text-slate-500 dark:text-slate-400">Your completed or cancelled bookings will appear here.</p>
      </div>
      <HistoryCard v-for="b in customerBookings" :key="b.id" :item="b" />
    </div>
  </div>
</template>
