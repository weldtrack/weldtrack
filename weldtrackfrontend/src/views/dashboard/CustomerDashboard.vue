<template>
  <Layout title="Customer Dashboard">
    <div class="panel">
      <CustomerBooking v-if="adminSectionStore.section === 'booking'" />
      <BookingHistory v-else-if="adminSectionStore.section === 'booking-history'" />
      <ServiceFeedback v-else-if="adminSectionStore.section === 'feedback'" />
      <div v-else class="space-y-6">
        <div class="rounded-xl border border-blue-200 bg-blue-50 p-5">
          <h2 class="text-xl font-semibold text-blue-900">Customer Dashboard Overview</h2>
          <p class="mt-1 text-sm text-blue-800">Select a section from the sidebar to view bookings or feedback. The preview below keeps the dashboard populated even if no section is active.</p>
        </div>
        <CustomerBooking />
        <BookingHistory />
        <ServiceFeedback />
      </div>
    </div>
  </Layout>
</template>

<script setup lang="ts">
import Layout from './DashboardLayout.vue'
import CustomerBooking from './components/CustomerBooking.vue'
import BookingHistory from './components/BookingHistory.vue'
import ServiceFeedback from './components/ServiceFeedback.vue'
import { useAdminSectionStore } from '../../stores/adminSection'

const adminSectionStore = useAdminSectionStore()
</script>
