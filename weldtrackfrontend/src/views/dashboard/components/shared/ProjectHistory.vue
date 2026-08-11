<script setup lang="ts">
import { computed, onMounted, ref } from 'vue'
import LocalLoader from '../../../../components/ui/LocalLoader.vue'
import { Folder } from 'lucide-vue-next'
import { useBookingsStore } from '../../../../stores/bookings.ts'
import { getUserFriendlyApiError } from '../../../../services/errorMessage.ts'
import HistoryCard from './HistoryCard.vue'

const bookingsStore = useBookingsStore()
const loadError = ref('')

const isLoading = ref(true)

onMounted(async () => {
  isLoading.value = true
  try {
    await loadProjects()
  } finally {
    isLoading.value = false
  }
})

async function loadProjects() {
  loadError.value = ''
  try {
    await bookingsStore.fetchBookings()
  } catch (error) {
    loadError.value = getUserFriendlyApiError(error)
  }
}

const projectHistory = computed(() => {
  const bookings = Array.isArray(bookingsStore.bookings) ? bookingsStore.bookings : []

  return bookings
    .filter((booking) => booking.status === 'completed' || booking.status === 'cancelled')
    .sort((a, b) => new Date(b.createdDate ?? 0).getTime() - new Date(a.createdDate ?? 0).getTime())
})


const completedCount = computed(() => projectHistory.value.filter((item) => item.status === 'completed').length)
const cancelledCount = computed(() => projectHistory.value.filter((item) => item.status === 'cancelled').length)

</script>

<template>
  <section class="space-y-6 relative">
    <LocalLoader v-if="isLoading" />

    <!-- Header -->
    <div class="flex items-start gap-3">
      <div class="flex h-12 w-12 items-center justify-center">
        <Folder class="dashboard-view-icon h-6 w-6 text-sky-600 dark:text-sky-400" />
      </div>
      <div>
        <h3 class="text-2xl font-semibold text-slate-900 dark:text-slate-100">Project History</h3>
        <p class="text-sm text-slate-600 dark:text-slate-400">Completed and cancelled projects from booking decisions</p>
      </div>
    </div>

    <!-- Summary Metric Cards -->
    <div class="grid grid-cols-1 gap-4 sm:grid-cols-2">
      <div class="rounded-xl border border-sky-200 bg-sky-50 p-5 dark:border-sky-900/50 dark:bg-sky-950/40">
        <p class="text-xs font-bold uppercase tracking-wider text-sky-700 dark:text-sky-300">Completed Projects</p>
        <p class="mt-2 text-3xl font-black text-slate-900 dark:text-slate-100">{{ completedCount }}</p>
      </div>
      <div class="rounded-xl border border-rose-200 bg-rose-50 p-5 dark:border-rose-900/50 dark:bg-rose-950/40">
        <p class="text-xs font-bold uppercase tracking-wider text-rose-700 dark:text-rose-300">Cancelled Projects</p>
        <p class="mt-2 text-3xl font-black text-slate-900 dark:text-slate-100">{{ cancelledCount }}</p>
      </div>
    </div>

    <!-- Full-width project list -->
    <div class="grid w-full grid-cols-1 gap-4">
      <div v-if="loadError" class="rounded-xl border border-red-200 bg-red-50 p-8 text-center col-span-full dark:border-red-900/50 dark:bg-red-950/40">
        <h3 class="text-lg font-bold text-red-800 dark:text-red-300">Unable to load project history</h3>
        <p class="mt-1 text-sm text-red-700 dark:text-red-400">{{ loadError }}</p>
        <button
          type="button"
          class="mt-4 inline-flex items-center justify-center rounded-xl bg-red-600 px-5 py-2.5 text-sm font-semibold text-white transition-colors hover:bg-red-700"
          @click="loadProjects"
        >
          Try again
        </button>
      </div>
      <div v-else-if="projectHistory.length === 0" class="rounded-xl border border-slate-200 bg-slate-50 p-8 text-center col-span-full dark:border-slate-800 dark:bg-slate-900">
        <h3 class="text-lg font-bold text-slate-900 dark:text-slate-100">No completed or cancelled projects yet</h3>
        <p class="mt-1 text-sm text-slate-500 dark:text-slate-400">Completed and cancelled projects will appear here once finalized.</p>
      </div>
      <HistoryCard v-for="item in projectHistory" :key="item.id" :item="item" />
    </div>
  </section>
</template>
