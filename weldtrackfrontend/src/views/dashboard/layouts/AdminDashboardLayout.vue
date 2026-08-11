<script setup lang="ts">
import {
  Archive,
  BarChart2,
  Briefcase,
  Calendar,
  Folder,
  LayoutDashboard,
  ReceiptText,
  Star,
  Users,
} from 'lucide-vue-next'
import DashboardShell from './DashboardShell.vue'
import type { SidebarEntry } from './DashboardShell.vue'

const adminNavigation: SidebarEntry[] = [
  { kind: 'item', id: 'admin-overview', label: 'Dashboard', icon: LayoutDashboard },
  {
    kind: 'group',
    id: 'admin-group-management',
    label: 'Management',
    icon: Briefcase,
    children: [
      { kind: 'item', id: 'admin-approval', label: 'Booking', icon: Calendar },
      { kind: 'item', id: 'admin-inventory', label: 'Inventory', icon: Archive },
      { kind: 'item', id: 'admin-services', label: 'Services', icon: Briefcase },
      { kind: 'item', id: 'admin-users', label: 'Users', icon: Users },
    ],
  },
  { kind: 'item', id: 'admin-staff', label: 'Staff', icon: Users, routeName: 'admin-staff-attendance' },
  { kind: 'item', id: 'admin-payroll', label: 'Payroll', icon: ReceiptText },
  { kind: 'item', id: 'admin-reports', label: 'Reports', icon: BarChart2 },
  { kind: 'item', id: 'admin-projects', label: 'Project History', icon: Folder },
  { kind: 'item', id: 'admin-feedback', label: 'Customer Feedback', icon: Star },
]
</script>

<template>
  <DashboardShell
    title="Admin Dashboard"
    role="admin"
    role-label="Admin Control Center"
    role-hint="Oversight, approvals, staffing, and reporting"
    accent="var(--role-accent-admin)"
    :navigation="adminNavigation"
  >
    <slot />
  </DashboardShell>
</template>
