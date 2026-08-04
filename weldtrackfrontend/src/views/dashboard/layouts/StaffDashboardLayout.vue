<script setup lang="ts">
import {
  BarChart2,
  Calendar,
  ClipboardList,
  MessageCircle,
} from 'lucide-vue-next'
import DashboardShell from './DashboardShell.vue'
import type { SidebarEntry } from './DashboardShell.vue'

const staffNavigation: SidebarEntry[] = [
  { kind: 'item', id: 'staff-attendance', label: 'Attendance', icon: Calendar },
  { kind: 'item', id: 'staff-tasks', label: 'Tasks', icon: ClipboardList },
  { kind: 'item', id: 'staff-contributions', label: 'Contributions', icon: BarChart2 },
  { kind: 'item', id: 'staff-feedback', label: 'Service Feedback', icon: MessageCircle },
]
</script>

<template>
  <DashboardShell
    title="Staff Dashboard"
    role="staff"
    role-label="Staff Workspace"
    role-hint="Attendance, assigned work, and performance updates"
    accent="#4FD1C5"
    :navigation="staffNavigation"
  >
    <slot />
  </DashboardShell>
</template>
