<script setup lang="ts">
import { computed, onMounted, ref } from 'vue'
import { useBookingsStore } from '../../../stores/bookings'
import { getUserFriendlyApiError } from '../../../services/errorMessage'
import HistoryCard from './HistoryCard.vue'

const bookingsStore = useBookingsStore()
const loadError = ref('')

onMounted(() => {
  void loadProjects()
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

// Only counts are needed here; HistoryCard renders details.
</script>

<template>
  <section class="space-y-6">
    <div>
      <h3 class="mb-1 text-2xl font-semibold text-gray-900">Project History</h3>
      <p class="text-sm text-gray-600">Completed and cancelled projects from booking decisions</p>
    </div>

    <div class="grid grid-cols-1 gap-4 md:grid-cols-2">
      <div class="rounded-lg border border-gray-200 bg-white p-4">
        <p class="text-sm text-gray-600">Completed Projects</p>
        <p class="text-2xl text-gray-900">{{ completedCount }}</p>
      </div>
      <div class="rounded-lg border border-gray-200 bg-white p-4">
        <p class="text-sm text-gray-600">Cancelled Projects</p>
        <p class="text-2xl text-gray-900">{{ cancelledCount }}</p>
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
