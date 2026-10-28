<script setup lang="ts">
import { ref, onMounted, watch } from 'vue'
import {
  Activity,
  Calendar,
  ChevronLeft,
  ChevronRight,
  Clock,
  Eye,
  FileText,
  Filter,
  Laptop,
  RefreshCw,
  Search,
  Shield,
  User,
  X,
} from 'lucide-vue-next'
import api from '../../../../api/api'
import LocalLoader from '../../../../components/ui/LocalLoader.vue'
import { getUserFriendlyApiError } from '../../../../services/errorMessage'

interface AuditLogItem {
  id: string
  user_id?: string | null
  user_name?: string | null
  user_role?: string | null
  action: string
  description: string
  auditable_type?: string | null
  auditable_id?: string | null
  properties?: Record<string, any> | null
  ip_address?: string | null
  user_agent?: string | null
  created_at: string
}

interface PaginationMeta {
  current_page: number
  last_page: number
  per_page: number
  total: number
}

interface AuditStats {
  total_logs: number
  today_logs: number
  actions_count: Record<string, number>
}

const logs = ref<AuditLogItem[]>([])
const stats = ref<AuditStats>({ total_logs: 0, today_logs: 0, actions_count: {} })
const pagination = ref<PaginationMeta>({ current_page: 1, last_page: 1, per_page: 20, total: 0 })
const page = ref(1)
const search = ref('')
const actionFilter = ref('')
const roleFilter = ref('')
const loading = ref(false)
const error = ref('')
const selectedLog = ref<AuditLogItem | null>(null)

async function fetchLogs(targetPage = page.value) {
  loading.value = true
  error.value = ''
  try {
    const params: Record<string, any> = {
      page: targetPage,
      per_page: 20,
    }
    if (search.value.trim()) params.search = search.value.trim()
    if (actionFilter.value) params.action = actionFilter.value
    if (roleFilter.value) params.role = roleFilter.value

    const res = await api.get('/admin/audit-logs', { params, skipGlobalLoading: true } as any)
    const data = res.data
    logs.value = data.logs || []
    pagination.value = data.pagination || { current_page: 1, last_page: 1, per_page: 20, total: 0 }
    stats.value = data.stats || { total_logs: 0, today_logs: 0, actions_count: {} }
  } catch (err) {
    error.value = getUserFriendlyApiError(err, 'Failed to load audit logs.')
  } finally {
    loading.value = false
  }
}

watch([actionFilter, roleFilter], () => {
  page.value = 1
  fetchLogs(1)
})

function handleSearch() {
  page.value = 1
  fetchLogs(1)
}

function getActionBadgeClass(action: string) {
  const act = (action || '').toUpperCase()
  if (act.startsWith('AUTH')) {
    return 'bg-blue-500/10 text-blue-600 dark:text-blue-400 border-blue-500/20'
  }
  if (act.includes('DELETE') || act.includes('BAN')) {
    return 'bg-rose-500/10 text-rose-600 dark:text-rose-400 border-rose-500/20'
  }
  if (act.includes('CREATE') || act.includes('ADD') || act.includes('APPROVE') || act.includes('UNBAN')) {
    return 'bg-emerald-500/10 text-emerald-600 dark:text-emerald-400 border-emerald-500/20'
  }
  if (act.includes('UPDATE') || act.includes('STATUS')) {
    return 'bg-amber-500/10 text-amber-600 dark:text-amber-400 border-amber-500/20'
  }
  return 'bg-purple-500/10 text-purple-600 dark:text-purple-400 border-purple-500/20'
}

function formatDate(iso: string) {
  try {
    const d = new Date(iso)
    return {
      date: d.toLocaleDateString(),
      time: d.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit', second: '2-digit' }),
    }
  } catch {
    return { date: iso, time: '' }
  }
}

onMounted(() => {
  fetchLogs(1)
})
</script>

<template>
  <div class="space-y-6">
    <!-- Header -->
    <div class="flex flex-col gap-4 sm:flex-row sm:items-center sm:justify-between">
      <div class="flex items-center gap-3">
        <span class="flex h-11 w-11 items-center justify-center rounded-2xl bg-amber-500/10 text-amber-500 border border-amber-500/20">
          <Shield class="h-6 w-6" />
        </span>
        <div>
          <h1 class="text-2xl font-bold tracking-tight text-neutral-900 dark:text-neutral-100">Audit Logs</h1>
          <p class="text-sm text-neutral-500 dark:text-neutral-400">
            System-wide audit trail of security, administration, inventory, and user events
          </p>
        </div>
      </div>
      <button
        type="button"
        :disabled="loading"
        class="inline-flex items-center gap-2 rounded-xl border border-neutral-300 dark:border-neutral-700 bg-white dark:bg-neutral-800 px-4 py-2.5 text-sm font-semibold text-neutral-700 dark:text-neutral-200 shadow-xs transition hover:bg-neutral-50 dark:hover:bg-neutral-700/50"
        @click="fetchLogs(page)"
      >
        <RefreshCw class="h-4 w-4" :class="{ 'animate-spin text-amber-500': loading }" />
        Refresh
      </button>
    </div>

    <!-- Error message -->
    <div v-if="error" class="rounded-xl border border-rose-200 dark:border-rose-900 bg-rose-50 dark:bg-rose-950/30 p-4 text-sm text-rose-700 dark:text-rose-300">
      {{ error }}
    </div>

    <!-- Stats summary -->
    <div class="grid grid-cols-1 gap-4 sm:grid-cols-3">
      <div class="rounded-2xl border border-neutral-200 dark:border-neutral-800 bg-white dark:bg-neutral-900 p-5 shadow-xs">
        <div class="flex items-center justify-between">
          <span class="text-xs font-semibold uppercase tracking-wider text-neutral-400">Total Entries</span>
          <Activity class="h-5 w-5 text-amber-500" />
        </div>
        <p class="mt-3 text-3xl font-bold text-neutral-900 dark:text-neutral-100">{{ stats.total_logs }}</p>
        <p class="mt-1 text-xs text-neutral-400">Recorded audit events</p>
      </div>

      <div class="rounded-2xl border border-neutral-200 dark:border-neutral-800 bg-white dark:bg-neutral-900 p-5 shadow-xs">
        <div class="flex items-center justify-between">
          <span class="text-xs font-semibold uppercase tracking-wider text-neutral-400">Today's Activity</span>
          <Clock class="h-5 w-5 text-emerald-500" />
        </div>
        <p class="mt-3 text-3xl font-bold text-neutral-900 dark:text-neutral-100">{{ stats.today_logs }}</p>
        <p class="mt-1 text-xs text-neutral-400">Logged since midnight UTC</p>
      </div>

      <div class="rounded-2xl border border-neutral-200 dark:border-neutral-800 bg-white dark:bg-neutral-900 p-5 shadow-xs">
        <div class="flex items-center justify-between">
          <span class="text-xs font-semibold uppercase tracking-wider text-neutral-400">Showing</span>
          <FileText class="h-5 w-5 text-blue-500" />
        </div>
        <p class="mt-3 text-3xl font-bold text-neutral-900 dark:text-neutral-100">{{ logs.length }}</p>
        <p class="mt-1 text-xs text-neutral-400">Entries on current page</p>
      </div>
    </div>

    <!-- Filter toolbar -->
    <div class="rounded-2xl border border-neutral-200 dark:border-neutral-800 bg-white dark:bg-neutral-900 p-4 shadow-xs">
      <form class="flex flex-col gap-3 md:flex-row md:items-center" @submit.prevent="handleSearch">
        <div class="relative flex-1">
          <Search class="absolute left-3.5 top-1/2 h-4 w-4 -translate-y-1/2 text-neutral-400" />
          <input
            v-model="search"
            type="text"
            placeholder="Search descriptions, actions, users, IPs..."
            class="w-full rounded-xl border border-neutral-300 dark:border-neutral-700 bg-transparent py-2 pl-10 pr-4 text-sm text-neutral-900 dark:text-neutral-100 focus:border-amber-500 focus:outline-hidden focus:ring-2 focus:ring-amber-500/20"
          />
        </div>

        <div class="flex flex-wrap items-center gap-2">
          <div class="flex items-center gap-1.5 rounded-xl border border-neutral-300 dark:border-neutral-700 bg-neutral-50 dark:bg-neutral-800 px-3 py-1.5">
            <Filter class="h-3.5 w-3.5 text-neutral-400" />
            <select
              v-model="actionFilter"
              class="bg-transparent text-xs font-medium text-neutral-700 dark:text-neutral-200 focus:outline-hidden"
            >
              <option value="">All Actions</option>
              <option value="AUTH_LOGIN">AUTH_LOGIN</option>
              <option value="AUTH_LOGOUT">AUTH_LOGOUT</option>
              <option value="USER_CREATE_STAFF">USER_CREATE_STAFF</option>
              <option value="USER_DELETE_STAFF">USER_DELETE_STAFF</option>
              <option value="USER_BAN">USER_BAN</option>
              <option value="USER_UNBAN">USER_UNBAN</option>
            </select>
          </div>

          <div class="flex items-center gap-1.5 rounded-xl border border-neutral-300 dark:border-neutral-700 bg-neutral-50 dark:bg-neutral-800 px-3 py-1.5">
            <User class="h-3.5 w-3.5 text-neutral-400" />
            <select
              v-model="roleFilter"
              class="bg-transparent text-xs font-medium text-neutral-700 dark:text-neutral-200 focus:outline-hidden"
            >
              <option value="">All Roles</option>
              <option value="admin">Admin</option>
              <option value="staff">Staff</option>
              <option value="customer">Customer</option>
              <option value="system">System</option>
            </select>
          </div>

          <button
            type="submit"
            class="rounded-xl bg-amber-500 px-4 py-2 text-sm font-semibold text-neutral-950 shadow-xs hover:bg-amber-400"
          >
            Filter
          </button>
        </div>
      </form>
    </div>

    <!-- Table -->
    <div class="overflow-hidden rounded-2xl border border-neutral-200 dark:border-neutral-800 bg-white dark:bg-neutral-900 shadow-xs">
      <div class="overflow-x-auto">
        <table class="w-full text-left text-sm">
          <thead class="border-b border-neutral-200 dark:border-neutral-800 bg-neutral-50/75 dark:bg-neutral-800/50 text-xs font-semibold uppercase tracking-wider text-neutral-500 dark:text-neutral-400">
            <tr>
              <th scope="col" class="px-6 py-4">Timestamp</th>
              <th scope="col" class="px-6 py-4">Actor</th>
              <th scope="col" class="px-6 py-4">Action</th>
              <th scope="col" class="px-6 py-4">Description</th>
              <th scope="col" class="px-6 py-4">IP Address</th>
              <th scope="col" class="px-6 py-4 text-right">Details</th>
            </tr>
          </thead>
          <tbody class="divide-y divide-neutral-100 dark:divide-neutral-800">
            <tr v-if="loading">
              <td colspan="6" class="py-12 text-center text-neutral-500">
                <LocalLoader />
                <p class="mt-2 text-sm">Loading audit logs...</p>
              </td>
            </tr>
            <tr v-else-if="logs.length === 0">
              <td colspan="6" class="py-12 text-center text-neutral-500 dark:text-neutral-400">
                <Shield class="mx-auto h-8 w-8 text-neutral-400" />
                <p class="mt-2 text-sm font-medium text-neutral-700 dark:text-neutral-300">No audit logs found</p>
                <p class="text-xs text-neutral-400">Try adjusting your filter or search query</p>
              </td>
            </tr>
            <tr v-for="log in logs" :key="log.id" class="transition-colors hover:bg-neutral-50/75 dark:hover:bg-neutral-800/40">
              <td class="whitespace-nowrap px-6 py-4 text-xs text-neutral-500 dark:text-neutral-400">
                <div class="flex items-center gap-1.5 font-medium text-neutral-900 dark:text-neutral-100">
                  <Calendar class="h-3.5 w-3.5 text-neutral-400" />
                  {{ formatDate(log.created_at).date }}
                </div>
                <div class="text-[11px] text-neutral-400">
                  {{ formatDate(log.created_at).time }}
                </div>
              </td>
              <td class="whitespace-nowrap px-6 py-4">
                <div class="font-semibold text-neutral-900 dark:text-neutral-100">{{ log.user_name || 'System' }}</div>
                <span class="inline-flex items-center rounded-md bg-neutral-100 dark:bg-neutral-800 px-1.5 py-0.5 text-[10px] font-medium text-neutral-600 dark:text-neutral-300">
                  {{ log.user_role || 'System' }}
                </span>
              </td>
              <td class="whitespace-nowrap px-6 py-4">
                <span
                  class="inline-flex items-center rounded-lg border px-2.5 py-1 text-xs font-semibold"
                  :class="getActionBadgeClass(log.action)"
                >
                  {{ log.action }}
                </span>
              </td>
              <td class="max-w-md px-6 py-4">
                <p class="truncate font-medium text-neutral-800 dark:text-neutral-200" :title="log.description">
                  {{ log.description }}
                </p>
              </td>
              <td class="whitespace-nowrap px-6 py-4 text-xs font-mono text-neutral-500 dark:text-neutral-400">
                {{ log.ip_address || '-' }}
              </td>
              <td class="whitespace-nowrap px-6 py-4 text-right">
                <button
                  type="button"
                  class="inline-flex items-center gap-1 rounded-lg border border-neutral-200 dark:border-neutral-700 px-2.5 py-1.5 text-xs font-medium text-neutral-700 dark:text-neutral-300 hover:bg-neutral-100 dark:hover:bg-neutral-800"
                  @click="selectedLog = log"
                >
                  <Eye class="h-3.5 w-3.5" />
                  Inspect
                </button>
              </td>
            </tr>
          </tbody>
        </table>
      </div>

      <!-- Pagination -->
      <div v-if="pagination.last_page > 1" class="flex items-center justify-between border-t border-neutral-200 dark:border-neutral-800 bg-neutral-50/50 dark:bg-neutral-800/30 px-6 py-3">
        <span class="text-xs text-neutral-500 dark:text-neutral-400">
          Page <span class="font-semibold text-neutral-900 dark:text-neutral-100">{{ pagination.current_page }}</span> of
          <span class="font-semibold text-neutral-900 dark:text-neutral-100">{{ pagination.last_page }}</span> ({{ pagination.total }} entries)
        </span>
        <div class="flex items-center gap-2">
          <button
            type="button"
            :disabled="pagination.current_page <= 1"
            class="inline-flex items-center gap-1 rounded-lg border border-neutral-300 dark:border-neutral-700 bg-white dark:bg-neutral-800 px-3 py-1.5 text-xs font-medium text-neutral-700 dark:text-neutral-200 shadow-xs disabled:opacity-40 hover:bg-neutral-50 dark:hover:bg-neutral-700"
            @click="page = Math.max(1, page - 1); fetchLogs(page)"
          >
            <ChevronLeft class="h-3.5 w-3.5" /> Previous
          </button>
          <button
            type="button"
            :disabled="pagination.current_page >= pagination.last_page"
            class="inline-flex items-center gap-1 rounded-lg border border-neutral-300 dark:border-neutral-700 bg-white dark:bg-neutral-800 px-3 py-1.5 text-xs font-medium text-neutral-700 dark:text-neutral-200 shadow-xs disabled:opacity-40 hover:bg-neutral-50 dark:hover:bg-neutral-700"
            @click="page = Math.min(pagination.last_page, page + 1); fetchLogs(page)"
          >
            Next <ChevronRight class="h-3.5 w-3.5" />
          </button>
        </div>
      </div>
    </div>

    <!-- Inspect Modal -->
    <div
      v-if="selectedLog"
      class="fixed inset-0 z-50 flex items-center justify-center p-4 bg-black/50 backdrop-blur-xs"
    >
      <div class="relative w-full max-w-2xl rounded-2xl border border-neutral-200 dark:border-neutral-800 bg-white dark:bg-neutral-900 p-6 shadow-2xl">
        <div class="flex items-start justify-between border-b border-neutral-100 dark:border-neutral-800 pb-4">
          <div class="flex items-center gap-3">
            <span class="flex h-10 w-10 items-center justify-center rounded-xl bg-amber-500/10 text-amber-500">
              <Shield class="h-5 w-5" />
            </span>
            <div>
              <h3 class="text-lg font-bold text-neutral-900 dark:text-neutral-100">Audit Entry {{ selectedLog.id }}</h3>
              <p class="text-xs text-neutral-500 dark:text-neutral-400">
                {{ formatDate(selectedLog.created_at).date }} {{ formatDate(selectedLog.created_at).time }}
              </p>
            </div>
          </div>
          <button
            type="button"
            class="rounded-lg p-1 text-neutral-400 hover:bg-neutral-100 dark:hover:bg-neutral-800 hover:text-neutral-600"
            @click="selectedLog = null"
          >
            <X class="h-5 w-5" />
          </button>
        </div>

        <div class="mt-4 space-y-4 max-h-[70vh] overflow-y-auto pr-1">
          <div class="grid grid-cols-2 gap-4 text-xs">
            <div class="rounded-xl border border-neutral-100 dark:border-neutral-800 bg-neutral-50 dark:bg-neutral-800/50 p-3">
              <span class="font-semibold text-neutral-400 uppercase">Actor</span>
              <p class="mt-1 font-bold text-neutral-900 dark:text-neutral-100">{{ selectedLog.user_name || 'System' }}</p>
              <p class="text-neutral-500 dark:text-neutral-400">{{ selectedLog.user_role || 'System' }}</p>
            </div>
            <div class="rounded-xl border border-neutral-100 dark:border-neutral-800 bg-neutral-50 dark:bg-neutral-800/50 p-3">
              <span class="font-semibold text-neutral-400 uppercase">Action</span>
              <p class="mt-1">
                <span
                  class="inline-flex items-center rounded-md border px-2 py-0.5 text-xs font-bold"
                  :class="getActionBadgeClass(selectedLog.action)"
                >
                  {{ selectedLog.action }}
                </span>
              </p>
            </div>
          </div>

          <div>
            <label class="text-xs font-semibold uppercase text-neutral-400">Description</label>
            <p class="mt-1 rounded-xl border border-neutral-100 dark:border-neutral-800 bg-neutral-50 dark:bg-neutral-800/30 p-3 text-sm text-neutral-800 dark:text-neutral-200">
              {{ selectedLog.description }}
            </p>
          </div>

          <div v-if="selectedLog.auditable_type">
            <label class="text-xs font-semibold uppercase text-neutral-400">Target Resource</label>
            <div class="mt-1 rounded-xl border border-neutral-100 dark:border-neutral-800 bg-neutral-50 dark:bg-neutral-800/30 p-3 text-xs font-mono text-neutral-700 dark:text-neutral-300">
              {{ selectedLog.auditable_type }} #{{ selectedLog.auditable_id }}
            </div>
          </div>

          <div v-if="selectedLog.properties && Object.keys(selectedLog.properties).length > 0">
            <label class="text-xs font-semibold uppercase text-neutral-400">Metadata / Properties</label>
            <pre class="mt-1 overflow-x-auto rounded-xl border border-neutral-200 dark:border-neutral-700 bg-neutral-950 p-3 text-xs text-amber-400">
{{ JSON.stringify(selectedLog.properties, null, 2) }}
            </pre>
          </div>

          <div class="border-t border-neutral-100 dark:border-neutral-800 pt-3 text-xs text-neutral-500 space-y-1">
            <div class="flex items-center gap-1.5">
              <Laptop class="h-3.5 w-3.5" />
              <span>IP: <code class="font-mono text-neutral-800 dark:text-neutral-200">{{ selectedLog.ip_address }}</code></span>
            </div>
            <div class="truncate" :title="selectedLog.user_agent || ''">
              Agent: <code class="font-mono text-neutral-700 dark:text-neutral-300">{{ selectedLog.user_agent }}</code>
            </div>
          </div>
        </div>

        <div class="mt-5 border-t border-neutral-100 dark:border-neutral-800 pt-4 text-right">
          <button
            type="button"
            class="rounded-xl bg-neutral-100 dark:bg-neutral-800 px-4 py-2 text-xs font-semibold text-neutral-700 dark:text-neutral-200 hover:bg-neutral-200 dark:hover:bg-neutral-700"
            @click="selectedLog = null"
          >
            Close
          </button>
        </div>
      </div>
    </div>
  </div>
</template>
