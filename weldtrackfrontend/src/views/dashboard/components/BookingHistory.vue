<script setup lang="ts">
import { computed, onMounted, ref } from 'vue'
import { useAuthStore } from '../../../stores/auth'
import { useBookingsStore } from '../../../stores/bookings'
import { getUserFriendlyApiError } from '../../../services/errorMessage'
import HistoryCard from './HistoryCard.vue'

const authStore = useAuthStore()
const bookingsStore = useBookingsStore()
const loadError = ref('')

const currentEmail = computed(() => authStore.email || '')

onMounted(() => {
  void loadBookings()
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
  <div class="space-y-8">
    <div class="mb-6">
      <h1 class="text-3xl font-bold text-gray-900">Booking History</h1>
      <p class="mt-2 text-gray-600">Track all your welding project bookings and their status</p>
    </div>

    <div class="grid grid-cols-1 gap-4 sm:grid-cols-2 lg:grid-cols-3">
      <div class="rounded-lg border border-green-200 bg-green-50 p-4">
        <p class="text-sm font-medium text-green-700">Completed</p>
        <p class="mt-1 text-2xl font-bold text-green-900">{{ completedBookings.length }}</p>
      </div>
      <div class="rounded-lg border border-red-200 bg-red-50 p-4">
        <p class="text-sm font-medium text-red-700">Cancelled</p>
        <p class="mt-1 text-2xl font-bold text-red-900">{{ cancelledBookings.length }}</p>
      </div>
      <div class="rounded-lg border border-purple-200 bg-purple-50 p-4">
        <p class="text-sm font-medium text-purple-700">Total</p>
        <p class="mt-1 text-2xl font-bold text-purple-900">{{ customerBookings.length }}</p>
      </div>
    </div>

    <div class="grid grid-cols-1 gap-4 sm:grid-cols-2 lg:grid-cols-3">
      <div v-if="loadError" class="rounded-lg border border-red-200 bg-red-50 p-8 text-center col-span-full">
        <h3 class="text-lg font-medium text-red-800">Unable to load booking history</h3>
        <p class="mt-1 text-sm text-red-700">{{ loadError }}</p>
        <button
          type="button"
          class="mt-4 inline-flex items-center justify-center rounded-lg bg-red-600 px-4 py-2 text-sm font-semibold text-white transition-colors hover:bg-red-700"
          @click="loadBookings"
        >
          Try again
        </button>
      </div>
      <div v-else-if="customerBookings.length === 0" class="rounded-lg border border-gray-200 bg-gray-50 p-8 text-center col-span-full">
        <svg class="mx-auto h-12 w-12 text-gray-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z" />
        </svg>
        <h3 class="mt-4 text-lg font-medium text-gray-900">No completed or cancelled bookings</h3>
        <p class="mt-1 text-sm text-gray-600">Your booking history will appear here once projects are completed or cancelled</p>
      </div>
      <HistoryCard v-for="b in customerBookings" :key="b.id" :item="b" />
    </div>
  </div>
</template>
