<script setup lang="ts">
import { ref, computed, onMounted, onBeforeUnmount } from 'vue'
import LocalLoader from '../../../../components/ui/LocalLoader.vue'
import { Users } from 'lucide-vue-next'
import api from '../../../../api/api'
import { useModalStore } from '../../../../stores/modal'

type User = {
  id: string
  email: string
  role: string
  created_at: string
  is_banned: boolean
  is_online?: boolean
  last_active?: string | null
}

const users = ref<User[]>([])
const view = ref<'all' | 'online'>('all')
const roleFilter = ref<'all' | 'customers' | 'staff'>('all')
const search = ref('')
const loading = ref(false)
const refreshInterval = ref<number | null>(null)
const modalStore = useModalStore()

async function fetchUsers() {
  loading.value = true
  try {
    const res = await api.get('/auth/admin/users', { skipGlobalLoading: true } as any)
    users.value = res.data || []
  } finally {
    loading.value = false
  }
}

async function fetchOnline() {
  loading.value = true
  try {
    const res = await api.get('/auth/admin/online', { skipGlobalLoading: true } as any)
    users.value = res.data || []
  } finally {
    loading.value = false
  }
}

async function refresh() {
  if (view.value === 'online') await fetchOnline()
  else await fetchUsers()
}

function banUser(id: string) {
  modalStore.open({
    title: 'Confirm Ban',
    message: 'Are you sure you want to ban this user?',
    variant: 'error',
    confirmLabel: 'Ban',
    cancelLabel: 'Cancel',
    onConfirm: async () => {
      loading.value = true
      try {
        await api.post(`/auth/admin/ban/${id}`, {}, { skipGlobalLoading: true } as any)
        await refresh()
      } catch (e) {
      } finally {
        loading.value = false
      }
    },
  })
}

function unbanUser(id: string) {
  modalStore.open({
    title: 'Confirm Unban',
    message: 'Are you sure you want to unban this user?',
    variant: 'warning',
    confirmLabel: 'Unban',
    cancelLabel: 'Cancel',
    onConfirm: async () => {
      loading.value = true
      try {
        await api.post(`/auth/admin/unban/${id}`, {}, { skipGlobalLoading: true } as any)
        await refresh()
      } catch (e) {
      } finally {
        loading.value = false
      }
    },
  })
}

function isOnline(user: User) {
  return Boolean(user.is_online)
}

const filtered = computed(() => {
  const term = search.value.trim().toLowerCase()
  return users.value
    .filter((u) => u.role.toLowerCase() !== 'admin')
    .filter((u) => {
      if (roleFilter.value === 'customers') return u.role.toLowerCase() === 'customer'
      if (roleFilter.value === 'staff') return u.role.toLowerCase() === 'staff'
      return true
    })
    .filter((u) => {
      if (!term) return true
      return (
        u.email.toLowerCase().includes(term) ||
        u.role.toLowerCase().includes(term) ||
        String(u.id).includes(term)
      )
    })
})

onMounted(() => {
  refresh()
  refreshInterval.value = window.setInterval(() => {
    refresh()
  }, 5000)
})

onBeforeUnmount(() => {
  if (refreshInterval.value !== null) {
    window.clearInterval(refreshInterval.value)
    refreshInterval.value = null
  }
})
</script>

<template>
  <section class="relative space-y-6">
    <LocalLoader v-if="loading" />
    <header class="flex items-start gap-3">
      <div class="flex h-12 w-12 shrink-0 items-center justify-center">
        <Users class="dashboard-view-icon h-6 w-6 text-sky-600 dark:text-sky-400" />
      </div>
      <div>
        <h3 class="text-2xl font-semibold text-slate-900 dark:text-slate-100">Users</h3>
        <p class="text-sm text-slate-600 dark:text-slate-400">Manage customer and staff accounts</p>
      </div>
    </header>

    <article class="overflow-hidden rounded-2xl border border-slate-200 bg-white shadow-xs dark:border-slate-800 dark:bg-slate-900">
      <div class="border-b border-slate-100 px-5 py-4 dark:border-slate-800">
        <div class="flex flex-col gap-3 sm:flex-row sm:items-center">
          <input 
            v-model="search" 
            placeholder="Search users by email or ID..." 
            class="w-full rounded-xl border border-slate-200 bg-slate-50 px-4 py-2 text-sm text-slate-900 outline-none transition focus:border-sky-500 focus:bg-white dark:border-slate-800 dark:bg-slate-950 dark:text-slate-100 sm:flex-1" 
          />

          <div class="w-full sm:w-44">
            <div class="relative">
              <select
                v-model="roleFilter"
                class="w-full appearance-none rounded-xl border border-slate-200 bg-slate-50 px-4 py-2 pr-8 text-sm text-slate-800 outline-none focus:border-sky-500 focus:bg-white dark:border-slate-800 dark:bg-slate-950 dark:text-slate-100"
              >
                <option value="all">All Roles</option>
                <option value="customers">Customers</option>
                <option value="staff">Staff</option>
              </select>
              <span class="pointer-events-none absolute inset-y-0 right-3 flex items-center text-slate-400">
                <svg viewBox="0 0 20 20" fill="currentColor" class="h-4 w-4" aria-hidden="true">
                  <path fill-rule="evenodd" d="M5.23 7.21a.75.75 0 011.06.02L10 11.168l3.71-3.938a.75.75 0 111.08 1.04l-4.25 4.51a.75.75 0 01-1.08 0l-4.25-4.51a.75.75 0 01.02-1.06z" clip-rule="evenodd" />
                </svg>
              </span>
            </div>
          </div>

          <button
            class="whitespace-nowrap rounded-xl border px-4 py-2 text-xs font-semibold sm:text-sm transition-all"
            :class="view === 'online' ? 'border-sky-600 bg-sky-600 text-white shadow-xs' : 'border-slate-200 bg-slate-100 text-slate-700 hover:bg-slate-200 dark:border-slate-700 dark:bg-slate-800 dark:text-slate-300 dark:hover:bg-slate-700'"
            @click="(view = view === 'online' ? 'all' : 'online'); refresh()"
          >
            {{ view === 'online' ? 'Online Only' : 'All Users' }}
          </button>
        </div>
      </div>

      <div class="overflow-x-auto">
        <table class="w-full min-w-[700px] text-xs sm:text-sm divide-y divide-slate-100 dark:divide-slate-800">
          <thead class="bg-slate-50 dark:bg-slate-800/80">
            <tr class="text-left">
              <th class="px-5 py-3.5 text-xs font-bold uppercase tracking-wider text-slate-500 dark:text-slate-400">ID</th>
              <th class="px-5 py-3.5 text-xs font-bold uppercase tracking-wider text-slate-500 dark:text-slate-400">Email</th>
              <th class="px-5 py-3.5 text-xs font-bold uppercase tracking-wider text-slate-500 dark:text-slate-400 hidden sm:table-cell">Role</th>
              <th class="px-5 py-3.5 text-xs font-bold uppercase tracking-wider text-slate-500 dark:text-slate-400">Status</th>
              <th class="px-5 py-3.5 text-xs font-bold uppercase tracking-wider text-slate-500 dark:text-slate-400 hidden lg:table-cell">Last Active</th>
              <th class="px-5 py-3.5 text-xs font-bold uppercase tracking-wider text-slate-500 dark:text-slate-400 text-right sticky right-0 z-10 bg-slate-50 dark:bg-slate-800 shadow-[-12px_0_15px_-4px_rgba(0,0,0,0.05)]">Actions</th>
            </tr>
          </thead>
          <tbody class="divide-y divide-slate-100 dark:divide-slate-800 bg-transparent">
            <tr v-for="u in filtered" :key="u.id" class="transition-colors hover:bg-slate-50/50 dark:hover:bg-slate-800/50 text-xs sm:text-sm group">
              <td class="px-5 py-4 text-slate-500 dark:text-slate-400 font-mono">{{ u.id }}</td>
              <td class="px-5 py-4 font-semibold text-slate-900 dark:text-slate-100 truncate max-w-[200px] sm:max-w-xs">{{ u.email }}</td>
              <td class="px-5 py-4 text-slate-600 dark:text-slate-300 capitalize hidden sm:table-cell font-medium">{{ u.role }}</td>
              <td class="px-5 py-4">
                <div class="flex items-center gap-2">
                  <span
                    class="h-2.5 w-2.5 rounded-full"
                    :class="isOnline(u) ? 'bg-emerald-500 shadow-xs shadow-emerald-500/50' : 'bg-slate-300 dark:bg-slate-600'"
                  ></span>
                  <span class="font-semibold hidden sm:inline" :class="isOnline(u) ? 'text-emerald-600 dark:text-emerald-400' : 'text-slate-500 dark:text-slate-400'">
                    {{ isOnline(u) ? 'Online' : 'Offline' }}
                  </span>
                </div>
              </td>
              <td class="px-5 py-4 text-slate-500 dark:text-slate-400 hidden lg:table-cell text-xs">{{ u.last_active ? new Date(u.last_active).toLocaleString() : '-' }}</td>
              <td class="px-5 py-4 text-right sticky right-0 z-10 bg-white dark:bg-slate-900 group-hover:bg-slate-50 dark:group-hover:bg-slate-800 shadow-[-12px_0_15px_-4px_rgba(0,0,0,0.05)]">
                <div class="flex items-center justify-end gap-2">
                  <button
                    v-if="!u.is_banned"
                    class="rounded-lg bg-rose-600 px-3 py-1 text-xs font-semibold text-white shadow-xs hover:bg-rose-700 transition dark:bg-rose-600 dark:hover:bg-rose-500"
                    @click="banUser(u.id)"
                  >
                    Ban
                  </button>
                  <button
                    v-else
                    class="rounded-lg bg-emerald-600 px-3 py-1 text-xs font-semibold text-white shadow-xs hover:bg-emerald-700 transition dark:bg-emerald-600 dark:hover:bg-emerald-500"
                    @click="unbanUser(u.id)"
                  >
                    Unban
                  </button>
                </div>
              </td>
            </tr>
            <tr v-if="filtered.length === 0">
              <td colspan="6" class="px-5 py-8 text-center text-sm font-medium text-slate-500 dark:text-slate-400">No matching users found</td>
            </tr>
        </tbody>
      </table>
    </div>
    </article>
  </section>
</template>

<style scoped>
</style>
