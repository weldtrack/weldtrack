<script setup lang="ts">
import {
  Briefcase,
  Calendar,
  Folder,
  MapPin,
  MessageCircle,
} from 'lucide-vue-next'
import DashboardShell from './DashboardShell.vue'
import type { SidebarEntry } from './DashboardShell.vue'

const customerNavigation: SidebarEntry[] = [
  { kind: 'item', id: 'customer-services', label: 'Services', icon: Briefcase },
  { kind: 'item', id: 'customer-booking', label: 'New Booking', icon: Calendar },
  { kind: 'item', id: 'customer-addresses', label: 'Addresses', icon: MapPin },
  { kind: 'item', id: 'customer-history', label: 'Booking History', icon: Folder },
  { kind: 'item', id: 'customer-feedback', label: 'Service Feedback', icon: MessageCircle },
]
</script>

<template>
  <DashboardShell
    title="Client Dashboard"
    role="customer"
    role-label="Client Portal"
    role-hint="Browse services, book work, and manage account history"
    accent="var(--role-accent-customer)"
    :navigation="customerNavigation"
  >
    <slot />
  </DashboardShell>
</template>
