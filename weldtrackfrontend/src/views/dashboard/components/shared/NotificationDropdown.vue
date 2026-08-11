<script setup lang="ts">
import { computed, onMounted, onUnmounted, ref } from 'vue'
import { useRouter } from 'vue-router'
import { AlertTriangle, Bell, Calendar, CheckCircle2, LoaderCircle } from 'lucide-vue-next'
import type { Component } from 'vue'
import { useAuthStore } from '../../../../stores/auth'
import { useBookingsStore } from '../../../../stores/bookings'
import { useInventoryStore } from '../../../../stores/inventory'
import { useStaffTasksStore } from '../../../../stores/staffTasks'

type NotificationItem = {
  id: string
  title: string
  message: string
  occurredAt?: string
  icon: Component
  iconColor: string
  bgColor: string
}

const authStore = useAuthStore()
const bookingsStore = useBookingsStore()
const inventoryStore = useInventoryStore()
const staffTasksStore = useStaffTasksStore()
const router = useRouter()

const isOpen = ref(false)
const isLoading = ref(false)
const loadFailed = ref(false)
const notifications = ref<NotificationItem[]>([])
const dropdownRef = ref<HTMLElement | null>(null)
const readIds = ref(new Set<string>())

const storageKey = computed(() => `weldtrack-notifications-read:${authStore.user?.id || authStore.email}`)
const unreadCount = computed(() => notifications.value.filter((item) => !readIds.value.has(item.id)).length)

function loadReadState() {
  try {
    const stored = JSON.parse(localStorage.getItem(storageKey.value) || '[]')
    readIds.value = new Set(Array.isArray(stored) ? stored.map(String) : [])
  } catch {
    readIds.value = new Set()
  }
}

function saveReadState() {
  localStorage.setItem(storageKey.value, JSON.stringify([...readIds.value]))
}

function bookingNotification(booking: (typeof bookingsStore.bookings)[number]): NotificationItem {
  const statusLabels = {
    pending: 'Booking received',
    confirmed: 'Booking approved',
    'in-progress': 'Project in progress',
    completed: 'Project completed',
    cancelled: 'Booking cancelled',
  }
  const positive = booking.status === 'confirmed' || booking.status === 'completed'
  return {
    id: `booking:${booking.id}:${booking.status}`,
    title: statusLabels[booking.status],
    message: `${booking.projectType}${booking.scheduleDate ? ` • ${booking.scheduleDate}` : ''}`,
    occurredAt: booking.createdDate,
    icon: positive ? CheckCircle2 : booking.status === 'cancelled' ? AlertTriangle : Calendar,
    iconColor: positive ? 'text-emerald-500' : booking.status === 'cancelled' ? 'text-red-500' : 'text-sky-500',
    bgColor: positive ? 'bg-emerald-100 dark:bg-emerald-500/20' : booking.status === 'cancelled' ? 'bg-red-100 dark:bg-red-500/20' : 'bg-sky-100 dark:bg-sky-500/20',
  }
}

async function loadNotifications() {
  isLoading.value = true
  loadFailed.value = false
  try {
    if (authStore.role === 'customer') {
      await bookingsStore.fetchBookings({ limit: 50 })
      notifications.value = bookingsStore.bookings
        .filter((booking) => !booking.email || booking.email.toLowerCase() === authStore.email.toLowerCase())
        .map(bookingNotification)
    } else if (authStore.role === 'staff') {
      await staffTasksStore.fetchTasks()
      const userId = String(authStore.user?.id || '')
      notifications.value = staffTasksStore.tasks
        .filter((task) => task.assignedStaffIds.includes(userId) || task.assignedStaffEmails.includes(authStore.email))
        .map((task) => ({
          id: `task:${task.id}:${task.status}`,
          title: task.status === 'done' ? 'Task completed' : task.status === 'in-progress' ? 'Task in progress' : 'New task assigned',
          message: `${task.title} • ${task.projectName}`,
          occurredAt: task.assignedAt,
          icon: task.status === 'done' ? CheckCircle2 : Calendar,
          iconColor: task.status === 'done' ? 'text-emerald-500' : 'text-sky-500',
          bgColor: task.status === 'done' ? 'bg-emerald-100 dark:bg-emerald-500/20' : 'bg-sky-100 dark:bg-sky-500/20',
        }))
    } else {
      await Promise.all([bookingsStore.fetchBookings({ limit: 50 }), inventoryStore.fetchInventory()])
      const bookingItems = bookingsStore.bookings.map(bookingNotification)
      const lowStockItems: NotificationItem[] = inventoryStore.items
        .filter((item) => item.quantity <= item.lowStockThreshold)
        .map((item) => ({
          id: `stock:${item.id}:${item.quantity}`,
          title: 'Low stock alert',
          message: `${item.name} has ${item.quantity} remaining (threshold: ${item.lowStockThreshold}).`,
          occurredAt: item.dateAdded,
          icon: AlertTriangle,
          iconColor: 'text-amber-500',
          bgColor: 'bg-amber-100 dark:bg-amber-500/20',
        }))
      notifications.value = [...lowStockItems, ...bookingItems]
    }

    notifications.value.sort((a, b) => new Date(b.occurredAt || 0).getTime() - new Date(a.occurredAt || 0).getTime())
  } catch {
    notifications.value = []
    loadFailed.value = true
  } finally {
    isLoading.value = false
  }
}

function formatTime(value?: string) {
  if (!value) return 'Recently updated'
  const date = new Date(value)
  if (Number.isNaN(date.getTime())) return value
  const seconds = Math.round((date.getTime() - Date.now()) / 1000)
  const formatter = new Intl.RelativeTimeFormat('en', { numeric: 'auto' })
  if (Math.abs(seconds) < 60) return formatter.format(seconds, 'second')
  const minutes = Math.round(seconds / 60)
  if (Math.abs(minutes) < 60) return formatter.format(minutes, 'minute')
  const hours = Math.round(minutes / 60)
  if (Math.abs(hours) < 24) return formatter.format(hours, 'hour')
  const days = Math.round(hours / 24)
  if (Math.abs(days) < 30) return formatter.format(days, 'day')
  return date.toLocaleDateString('en-PH', { month: 'short', day: 'numeric', year: 'numeric' })
}

async function toggleDropdown() {
  isOpen.value = !isOpen.value
  if (isOpen.value) await loadNotifications()
}

function markAsRead(id: string) {
  readIds.value.add(id)
  readIds.value = new Set(readIds.value)
  saveReadState()
}

function markAllAsRead() {
  readIds.value = new Set(notifications.value.map((item) => item.id))
  saveReadState()
}

function viewAllActivity() {
  isOpen.value = false
  const routeName = authStore.role === 'customer' ? 'customer-history' : authStore.role === 'staff' ? 'staff-tasks' : 'admin-overview'
  router.push({ name: routeName }).catch(() => {})
}

function handleClickOutside(event: MouseEvent) {
  if (dropdownRef.value && !dropdownRef.value.contains(event.target as Node)) isOpen.value = false
}

onMounted(() => {
  loadReadState()
  loadNotifications()
  document.addEventListener('click', handleClickOutside)
})
onUnmounted(() => document.removeEventListener('click', handleClickOutside))
</script>

<template>
  <div ref="dropdownRef" class="relative">
    <button type="button" class="dashboard-icon-btn relative flex items-center justify-center" aria-label="Notifications" @click.stop="toggleDropdown">
      <Bell class="h-4 w-4" />
      <span v-if="unreadCount > 0" class="absolute right-[0.35rem] top-[0.35rem] flex h-2 w-2">
        <span class="absolute inline-flex h-full w-full animate-ping rounded-full bg-red-400 opacity-75"></span>
        <span class="relative inline-flex h-2 w-2 rounded-full bg-red-500"></span>
      </span>
    </button>

    <div v-if="isOpen" class="absolute right-0 z-50 mt-3 w-[min(24rem,calc(100vw-2rem))] origin-top-right overflow-hidden rounded-xl border shadow-2xl" style="border-color: var(--db-border); background: var(--db-panel-solid); color: var(--db-text);">
      <div class="flex items-center justify-between border-b px-4 py-3" style="border-color: var(--db-border);">
        <h3 class="text-[15px] font-semibold">Notifications</h3>
        <button v-if="unreadCount > 0" type="button" class="text-xs font-semibold text-sky-600 transition hover:text-sky-700 dark:text-sky-400" @click="markAllAsRead">Mark all as read</button>
      </div>

      <div class="max-h-[28rem] overflow-y-auto" style="scrollbar-width: thin;">
        <div v-if="isLoading" class="flex items-center justify-center gap-2 px-4 py-8 text-sm" style="color: var(--db-muted)">
          <LoaderCircle class="h-4 w-4 animate-spin" /> Loading activity…
        </div>
        <div v-else-if="loadFailed" class="px-4 py-8 text-center text-sm" style="color: var(--db-muted)">
          Notifications could not be loaded. <button class="font-semibold text-sky-500" @click="loadNotifications">Try again</button>
        </div>
        <div v-else-if="notifications.length === 0" class="px-4 py-8 text-center text-sm" style="color: var(--db-muted)">No notifications yet.</div>
        <div v-else class="divide-y divide-slate-200/60 dark:divide-slate-800">
          <button v-for="notification in notifications" :key="notification.id" type="button" class="flex w-full items-start gap-3 p-4 text-left transition hover:bg-slate-100/60 dark:hover:bg-slate-800/60" :class="{ 'bg-sky-50/40 dark:bg-sky-900/10': !readIds.has(notification.id) }" @click="markAsRead(notification.id)">
            <div class="mt-0.5 flex h-9 w-9 shrink-0 items-center justify-center rounded-full" :class="notification.bgColor">
              <component :is="notification.icon" class="h-4 w-4" :class="notification.iconColor" />
            </div>
            <div class="min-w-0 flex-1">
              <p class="text-sm leading-snug" :class="{ 'font-semibold': !readIds.has(notification.id), 'font-medium': readIds.has(notification.id) }">{{ notification.title }}</p>
              <p class="mt-1 line-clamp-2 text-sm" style="color: var(--db-muted)">{{ notification.message }}</p>
              <p class="mt-1.5 text-xs font-medium opacity-70">{{ formatTime(notification.occurredAt) }}</p>
            </div>
            <div v-if="!readIds.has(notification.id)" class="mt-2 h-2 w-2 shrink-0 rounded-full bg-sky-500"></div>
          </button>
        </div>
      </div>
      <div class="border-t p-3 text-center" style="border-color: var(--db-border);">
        <button type="button" class="text-xs font-semibold tracking-wide" @click="viewAllActivity">View all activity</button>
      </div>
    </div>
  </div>
</template>
