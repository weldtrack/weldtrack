<script setup lang="ts">
import { computed, onMounted, reactive, ref } from 'vue'
import { useAdminSectionStore } from '../../../stores/adminSection'
import { useAuthStore } from '../../../stores/auth'
import { useStaffTasksStore } from '../../../stores/staffTasks'
import api from '../../../services/api'
import ModalShell from '../../../components/ui/ModalShell.vue'
import StaffAttendance from './StaffAttendance.vue'
import StaffTasks from './StaffTasks.vue'

type StaffTab = 'attendance' | 'tasks' | 'contributions' | 'create'

interface StaffMember {
  id: number
  email: string
  role: string
  created_at: string
}

const adminSectionStore = useAdminSectionStore()

const activeTab = computed<StaffTab>({
  get() {
    const s = adminSectionStore.section
    if (s === 'staff-attendance') return 'attendance'
    if (s === 'staff-tasks') return 'tasks'
    if (s === 'staff-contributions') return 'contributions'
    if (s === 'staff-create') return 'create'
    return 'attendance'
  },
  set(val: StaffTab) {
    if (val === 'attendance') adminSectionStore.setSection('staff-attendance')
    else if (val === 'tasks') adminSectionStore.setSection('staff-tasks')
    else if (val === 'contributions') adminSectionStore.setSection('staff-contributions')
    else if (val === 'create') adminSectionStore.setSection('staff-create')
  },
})
const authStore = useAuthStore()
const staffTasksStore = useStaffTasksStore()
const isAdmin = computed(() => authStore.role === 'admin')

// Create staff form (admin only) — moved into its own tab
const createStaffForm = reactive({ email: '', password: '', confirm: '' })
const creatingStaff = ref(false)
const createStaffError = ref('')
const createStaffSuccess = ref('')

// Staff list and delete
const staffList = ref<StaffMember[]>([])
const showDeleteModal = ref(false)
const selectedStaffToDelete = ref<StaffMember | null>(null)
const deleteError = ref('')
const isDeleting = ref(false)

async function fetchStaffList() {
  try {
    const { data } = await api.get('/auth/staff')
    staffList.value = Array.isArray(data) ? data : []
  } catch (err) {
    console.error('Failed to fetch staff list:', err)
    staffList.value = []
  }
}

async function submitCreateStaff() {
  createStaffError.value = ''
  createStaffSuccess.value = ''

  if (!createStaffForm.email || !createStaffForm.password || !createStaffForm.confirm) {
    createStaffError.value = 'Email, password, and confirmation are required.'
    return
  }

  if (createStaffForm.password !== createStaffForm.confirm) {
    createStaffError.value = 'Passwords do not match.'
    return
  }

  creatingStaff.value = true
  try {
    // Call admin endpoint to create staff directly (no verification code)
    const { data } = await api.post('/auth/admin/create-staff', {
      email: createStaffForm.email,
      password: createStaffForm.password,
    })

    if (data && data.success) {
      createStaffSuccess.value = 'Staff account created successfully.'
      createStaffForm.email = ''
      createStaffForm.password = ''
      createStaffForm.confirm = ''
      await fetchStaffList()
    } else {
      createStaffError.value = data?.message || 'Unable to create staff account.'
    }
  } catch (err) {
    createStaffError.value = (err as Error).message || 'Unable to create staff account.'
  } finally {
    creatingStaff.value = false
  }
}

function openDeleteModal(staff: StaffMember) {
  selectedStaffToDelete.value = staff
  deleteError.value = ''
  showDeleteModal.value = true
}

function closeDeleteModal() {
  showDeleteModal.value = false
  selectedStaffToDelete.value = null
  deleteError.value = ''
}

async function confirmDeleteStaff() {
  if (!selectedStaffToDelete.value) return

  isDeleting.value = true
  deleteError.value = ''

  try {
    await api.delete(`/auth/staff/${selectedStaffToDelete.value.id}`)
    await fetchStaffList()
    closeDeleteModal()
  } catch (err) {
    deleteError.value = (err as Error).message || 'Failed to delete staff member.'
    isDeleting.value = false
  }
}

const currentUserId = ref('')

function getStaffLabel(staffId: string) {
  return authStore.getStaffLabel(staffId, staffId ? `Staff #${staffId}` : '')
}

const completedContributions = computed(() => {
  const doneTasks = staffTasksStore.tasks.filter((t) => {
    if (t.status !== 'done') return false
    if (isAdmin.value) return true
    if (Array.isArray(t.assignedStaffIds)) return t.assignedStaffIds.includes(currentUserId.value)
    return false
  })

  const byProject: Record<
    string,
    { projectName: string; doneCount: number; lastDoneAt: string; contributors: string[] }
  > = {}

  doneTasks.forEach((t) => {
    const existing = byProject[t.projectName]
    const contributorNames = (t.assignedStaffIds || []).map((id) => getStaffLabel(id))

    if (!existing) {
      byProject[t.projectName] = {
        projectName: t.projectName,
        doneCount: 1,
        lastDoneAt: t.assignedAt,
        contributors: [...contributorNames],
      }
    } else {
      existing.doneCount += 1
      if (new Date(t.assignedAt) > new Date(existing.lastDoneAt)) existing.lastDoneAt = t.assignedAt
      contributorNames.forEach((name) => {
        if (!existing.contributors.includes(name)) existing.contributors.push(name)
      })
    }
  })

  return Object.values(byProject).sort((a, b) => {
    return new Date(b.lastDoneAt).getTime() - new Date(a.lastDoneAt).getTime()
  })
})

function isCurrentUserContributor(name: string) {
  if (isAdmin.value) return false
  const currentName = currentUserId.value ? getStaffLabel(currentUserId.value) : ''
  return Boolean(currentName && name === currentName)
}

// Note: `activeTab` is computed and syncs with `adminSectionStore.section`

onMounted(() => {
  Promise.all([
    staffTasksStore.fetchTasks(),
    authStore.fetchStaffDirectory(),
    api.get('/auth/me').then(({ data }) => {
      currentUserId.value = String(data?.id ?? '')
    }),
    fetchStaffList(),
  ])
})


</script>

<template>
  <section class="space-y-4">
    <div>
      

      <div class="inline-flex rounded-lg border border-gray-200 bg-white p-1">
      <button
        type="button"
        class="rounded-md px-4 py-2 text-sm font-semibold transition-colors"
        :class="activeTab === 'attendance' ? 'bg-blue-600 text-white' : 'text-gray-700 hover:bg-gray-100'"
        @click="activeTab = 'attendance'"
      >
        Attendance
      </button>
      <button
        type="button"
        class="rounded-md px-4 py-2 text-sm font-semibold transition-colors"
        :class="activeTab === 'tasks' ? 'bg-blue-600 text-white' : 'text-gray-700 hover:bg-gray-100'"
        @click="activeTab = 'tasks'"
      >
        Tasks
      </button>
      <button
        type="button"
        class="rounded-md px-4 py-2 text-sm font-semibold transition-colors"
        :class="activeTab === 'contributions' ? 'bg-blue-600 text-white' : 'text-gray-700 hover:bg-gray-100'"
        @click="activeTab = 'contributions'"
      >
        Contributions
      </button>
      <button
        v-if="isAdmin"
        type="button"
        class="rounded-md px-4 py-2 text-sm font-semibold transition-colors"
        :class="activeTab === 'create' ? 'bg-green-600 text-white' : 'text-gray-700 hover:bg-gray-100'"
        @click="activeTab = 'create'"
      >
        Create Staff
      </button>
      
    </div>
    </div>

    <StaffAttendance v-if="activeTab === 'attendance'" />
    <StaffTasks v-else-if="activeTab === 'tasks'" />

    <section v-else-if="activeTab === 'create'" class="space-y-4">
      <div class="rounded-lg border border-gray-200 bg-white p-4">
        <h3 class="mb-2 text-lg font-semibold text-gray-900">Create Staff Account</h3>
        <p class="mb-3 text-sm text-gray-600">Create a staff account directly (no verification required).</p>

        <div v-if="createStaffError" class="mb-3 rounded-xl border border-red-200 bg-red-50 px-4 py-2 text-sm text-red-700">{{ createStaffError }}</div>
        <div v-if="createStaffSuccess" class="mb-3 rounded-xl border border-green-200 bg-green-50 px-4 py-2 text-sm text-green-700">{{ createStaffSuccess }}</div>

        <div class="grid grid-cols-1 gap-3 sm:grid-cols-3">
          <input v-model="createStaffForm.email" type="email" placeholder="staff@example.com" class="col-span-3 rounded-xl border border-gray-300 bg-gray-50 px-3 py-2" />
          <input v-model="createStaffForm.password" type="password" placeholder="Password" class="rounded-xl border border-gray-300 bg-gray-50 px-3 py-2" />
          <input v-model="createStaffForm.confirm" type="password" placeholder="Confirm" class="rounded-xl border border-gray-300 bg-gray-50 px-3 py-2" />
          <button :disabled="creatingStaff" @click="submitCreateStaff" class="col-span-3 mt-1 h-10 rounded-xl bg-green-600 text-white font-semibold hover:bg-green-700 disabled:opacity-60">{{ creatingStaff ? 'Creating...' : 'Create Staff' }}</button>
        </div>
      </div>

      <!-- Staff List -->
      <div class="rounded-lg border border-gray-200 bg-white p-4">
        <h3 class="mb-4 text-lg font-semibold text-gray-900">Staff Members</h3>

        <div v-if="staffList.length === 0" class="rounded-lg bg-gray-50 p-4 text-center text-sm text-gray-500">
          No staff members yet.
        </div>

        <div v-else class="space-y-2">
          <div v-for="staff in staffList" :key="staff.id" class="flex items-center justify-between rounded-lg bg-gray-50 p-3">
            <div class="flex-1">
              <p class="font-semibold text-gray-900">{{ staff.email }}</p>
              <p class="text-xs text-gray-600">
                Created: {{ new Date(staff.created_at).toLocaleDateString('en-PH') }}
              </p>
            </div>
            <button
              type="button"
              @click="openDeleteModal(staff)"
              class="ml-3 rounded-lg border border-red-300 px-3 py-1.5 text-sm font-semibold text-red-600 transition-colors hover:bg-red-50"
            >
              Delete
            </button>
          </div>
        </div>
      </div>
    </section>

    <section v-else-if="activeTab === 'contributions'" class="space-y-4">
      <div>
        <h3 class="mb-1 text-2xl font-semibold text-gray-900">
          {{ isAdmin ? 'Team Contributions' : 'My Contributions' }}
        </h3>
        <p class="text-sm text-gray-600">
          {{ isAdmin ? 'Completed tasks from all staff members' : "Projects you've completed tasks on" }}
        </p>
      </div>

      <div v-if="completedContributions.length === 0" class="rounded-lg bg-gray-50 p-4 text-sm text-gray-500">
        No completed tasks yet.
      </div>

      <div v-else class="space-y-3">
        <div v-for="proj in completedContributions" :key="proj.projectName" class="rounded-lg border border-gray-200 bg-white p-4">
          <div class="flex items-center justify-between">
            <div>
              <p class="font-semibold text-gray-900">{{ proj.projectName }}</p>
              <p class="text-sm text-gray-600">Completed tasks: {{ proj.doneCount }}</p>
              <div class="mt-1 flex flex-wrap gap-2">
                <span
                  v-for="name in proj.contributors"
                  :key="`${proj.projectName}-${name}`"
                  class="rounded-full px-2 py-0.5 text-xs"
                  :class="isCurrentUserContributor(name) ? 'bg-blue-100 font-semibold text-blue-700' : 'bg-gray-100 text-gray-600'"
                >
                  {{ name }}
                  <span v-if="isCurrentUserContributor(name)">(You)</span>
                </span>
              </div>
            </div>
            <p class="text-sm text-gray-500">Last: {{ new Date(proj.lastDoneAt).toLocaleDateString('en-PH') }}</p>
          </div>
        </div>
      </div>
    </section>

    <!-- Delete Staff Modal -->
    <ModalShell
      :show="showDeleteModal"
      title="Delete Staff Member"
      subtitle="Confirm deletion"
      tone="red"
      size="lg"
      @close="closeDeleteModal"
    >
      <div class="space-y-4">
        <p class="text-gray-700">
          Are you sure you want to delete <strong>{{ selectedStaffToDelete?.email }}</strong>? This action cannot be undone.
        </p>
        <div v-if="deleteError" class="rounded-lg border border-red-200 bg-red-50 px-3 py-2 text-sm text-red-700">
          {{ deleteError }}
        </div>
      </div>

      <template #footer>
        <button type="button" class="rounded-lg border border-gray-300 bg-white px-4 py-2 font-semibold text-gray-700 hover:bg-gray-50" @click="closeDeleteModal">
          Cancel
        </button>
        <button
          type="button"
          :disabled="isDeleting"
          class="rounded-lg bg-red-600 px-4 py-2 font-semibold text-white hover:bg-red-700 disabled:opacity-60"
          @click="confirmDeleteStaff"
        >
          {{ isDeleting ? 'Deleting...' : 'Delete' }}
        </button>
      </template>
    </ModalShell>
  </section>
</template>
