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
    <div class="flex items-start gap-3">
      <div class="flex h-12 w-12 items-center justify-center rounded-lg bg-linear-to-br from-sky-50 to-sky ring-1 ring-sky-100">
        <Folder class="dashboard-view-icon h-6 w-6 text-sky-600 dark:text-sky-400" />
      </div>
      <div>
        <h3 class="mb-1 text-2xl font-semibold text-gray-900">Project History</h3>
        <p class="text-sm text-gray-600">Completed and cancelled projects from booking decisions</p>
      </div>
    </div>

    <div class="grid grid-cols-1 gap-4 sm:grid-cols-2">
      <div class="rounded-lg bg-sky-50 p-4">
        <p class="text-xs uppercase tracking-wide text-sky-600 font-semibold">Completed Projects</p>
        <p class="mt-1 text-2xl font-bold text-gray-900">{{ completedCount }}</p>
      </div>
      <div class="rounded-lg bg-red-50 p-4">
        <p class="text-xs uppercase tracking-wide text-red-600 font-semibold">Cancelled Projects</p>
        <p class="mt-1 text-2xl font-bold text-gray-900">{{ cancelledCount }}</p>
      </div>
    </div>

    <div class="grid grid-cols-1 gap-4 sm:grid-cols-2 lg:grid-cols-3">
      <div v-if="loadError" class="rounded-lg border border-red-200 bg-red-50 p-8 text-center col-span-full">
        <h3 class="text-lg font-medium text-red-800">Unable to load project history</h3>
        <p class="mt-1 text-sm text-red-700">{{ loadError }}</p>
        <button
          type="button"
          class="mt-4 inline-flex items-center justify-center rounded-lg bg-red-600 px-4 py-2 text-sm font-semibold text-white transition-colors hover:bg-red-700"
          @click="loadProjects"
        >
          Try again
        </button>
      </div>
      <div v-else-if="projectHistory.length === 0" class="rounded-lg border border-gray-200 bg-gray-50 p-8 text-center col-span-full">
        <h3 class="text-lg font-medium text-gray-900">No completed or cancelled projects yet.</h3>
        <p class="mt-1 text-sm text-gray-600">Completed and cancelled projects will appear here.</p>
      </div>
      <HistoryCard v-for="item in projectHistory" :key="item.id" :item="item" />
    </div>
  </section>
</template>
