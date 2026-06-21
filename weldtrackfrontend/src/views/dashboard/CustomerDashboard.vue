<template>
  <Layout title="Customer Dashboard">
    <div class="panel">
      <CustomerServicesBrowse v-if="adminSectionStore.section === 'services'" />
      <CustomerBooking v-else-if="adminSectionStore.section === 'booking'" />
      <CustomerAddresses v-else-if="adminSectionStore.section === 'addresses'" />
      <BookingHistory v-else-if="adminSectionStore.section === 'booking-history'" />
      <ServiceFeedback v-else-if="adminSectionStore.section === 'feedback'" />
    </div>
  </Layout>
</template>

<script setup lang="ts">
import Layout from './DashboardLayout.vue'
import CustomerServicesBrowse from './components/customer/CustomerServicesBrowse.vue'
import CustomerBooking from './components/customer/CustomerBooking.vue'
import CustomerAddresses from './components/customer/CustomerAddresses.vue'
import BookingHistory from './components/customer/BookingHistory.vue'
import ServiceFeedback from './components/shared/ServiceFeedback.vue'
import { useAdminSectionStore } from '../../stores/adminSection'

const adminSectionStore = useAdminSectionStore()
</script>
