<script setup lang="ts">
import LocalLoader from '../../../../components/ui/LocalLoader.vue'
import { onMounted, reactive, ref } from 'vue'
import api from '../../../../api/api'
import { getUserFriendlyApiError } from '../../../../services/errorMessage'
import ModalShell from '../../../../components/ui/ModalShell.vue'
import { User } from 'lucide-vue-next'

interface StaffMember {
  id: number
  email: string
  role: string
  created_at: string
  mobile_phone: string | null
  profile_image: string | null
}

const createStaffForm = reactive({ email: '', password: '', confirmPassword: '', confirm: false })
const creatingStaff = ref(false)
const createStaffError = ref('')
const createStaffSuccess = ref('')

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
    createStaffError.value = getUserFriendlyApiError(err)
    staffList.value = []
  }
}

async function submitCreateStaff() {
  createStaffError.value = ''
  createStaffSuccess.value = ''

  if (!createStaffForm.email || !createStaffForm.password || !createStaffForm.confirmPassword || !createStaffForm.confirm) {
    createStaffError.value = 'Email, password, confirmation, and acknowledgement are required.'
    return
  }

  if (createStaffForm.password !== createStaffForm.confirmPassword) {
    createStaffError.value = 'Passwords do not match.'
    return
  }

  if (createStaffForm.password.length < 8) {
    createStaffError.value = 'Password must be at least 8 characters long.'
    return
  }

  creatingStaff.value = true
  try {
    const { data } = await api.post('/auth/admin/create-staff', {
      email: createStaffForm.email,
      password: createStaffForm.password,
    })

    if (data && data.success) {
      createStaffSuccess.value = 'Staff account created successfully.'
      createStaffForm.email = ''
      createStaffForm.password = ''
      createStaffForm.confirmPassword = ''
      createStaffForm.confirm = false
      await fetchStaffList()
    } else {
      createStaffError.value = data?.message || 'Unable to create staff account.'
    }
  } catch (err) {
    createStaffError.value = getUserFriendlyApiError(err, 'Unable to create staff account.')
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
    deleteError.value = getUserFriendlyApiError(err, 'Failed to delete staff member.')
    isDeleting.value = false
  }
}

const getImageUrl = (url?: string | null) => {
  if (!url) return '';
  // If it's a data URI, return as is
  if (url.startsWith('data:')) return url;
  // Otherwise, handle as API path
  const cleanUrl = url.replace('/api', '');
  return `${import.meta.env.VITE_API_BASE_URL}${cleanUrl}`;
};

const isLoading = ref(true)

onMounted(async () => {
  isLoading.value = true
  try {
    await fetchStaffList()
  } finally {
    isLoading.value = false
  }
})
</script>

<template>
  <section class="space-y-4 relative">
    <LocalLoader v-if="isLoading" />
    <div class="rounded-lg border border-gray-200 bg-white p-4">
      <div class="flex items-start gap-3 pb-4">
        <div
          class="flex h-12 w-12 items-center justify-center rounded-lg bg-linear-to-br from-sky-50 to-sky ring-1 ring-sky-100">
          <User class="dashboard-view-icon h-6 w-6 text-sky-600 dark:text-sky-400" />
        </div>
        <div>
          <h3 class="mb-1 text-2xl font-semibold text-gray-900">Create Staff Account</h3>
          <p class="text-sm text-gray-600">Create a staff account directly (no verification required).</p>
        </div>
      </div>
      <div v-if="createStaffError"
        class="mb-3 rounded-xl border border-red-200 bg-red-50 px-4 py-2 text-sm text-red-700">{{ createStaffError }}
      </div>
      <div v-if="createStaffSuccess"
        class="mb-3 rounded-xl border border-green-200 bg-green-50 px-4 py-2 text-sm text-green-700">{{
          createStaffSuccess }}</div>

      <div class="grid grid-cols-1 gap-3 sm:grid-cols-2">
        <input v-model="createStaffForm.email" type="email" placeholder="staff@example.com"
          class="rounded-xl border border-gray-300 bg-gray-50 px-3 py-2 sm:col-span-2" />
        <div class="space-y-2 min-w-0">
          <label class="text-xs font-bold uppercase tracking-widest text-gray-500" for="create-staff-password">Create
            Password</label>
          <div class="group relative">
            <input v-model="createStaffForm.password" id="create-staff-password" type="password"
              placeholder="••••••••"
              class="min-w-0 w-full rounded-xl border border-gray-300 bg-gray-50 px-3 py-2 pr-11" />
            <div class="absolute inset-y-0 right-3 flex items-center">
              <div
                class="relative flex h-5 w-5 cursor-help items-center justify-center rounded-full border border-gray-300 bg-white text-[11px] font-black text-gray-500 shadow-sm transition group-hover:border-green-500 group-hover:text-green-700 group-focus-within:border-green-500 group-focus-within:text-green-700">
                !
                <div
                  class="pointer-events-none absolute right-0 top-full z-20 mt-2 w-52 rounded-xl border border-gray-200 bg-white px-3 py-2 text-left text-[11px] leading-snug text-gray-700 opacity-0 shadow-2xl transition group-hover:opacity-100 group-focus-within:opacity-100">
                  Password must be 8+ characters and include 1 uppercase letter and 1 number.
                </div>
              </div>
            </div>
          </div>
        </div>
        <div class="space-y-2 min-w-0">
          <label class="text-xs font-bold uppercase tracking-widest text-gray-500"
            for="create-staff-confirm-password">Confirm Password</label>
          <input v-model="createStaffForm.confirmPassword" id="create-staff-confirm-password" type="password"
            placeholder="••••••••" class="min-w-0 w-full rounded-xl border border-gray-300 bg-gray-50 px-3 py-2" />
        </div>
        <label
          class="flex min-w-0 items-start gap-3 rounded-xl border border-gray-300 bg-gray-50 px-3 py-3 text-sm text-gray-700 sm:col-span-2">
          <input v-model="createStaffForm.confirm" type="checkbox"
            class="mt-0.5 h-4 w-4 rounded border-gray-300 text-green-600 focus:ring-green-500" />
          <span>I confirm this account creation.</span>
        </label>
        <button :disabled="creatingStaff" @click="submitCreateStaff"
          class="mt-1 h-10 rounded-xl bg-green-600 px-4 font-semibold text-white hover:bg-green-700 disabled:opacity-60 sm:col-span-2">{{
            creatingStaff ? 'Creating...' : 'Create Staff' }}</button>
      </div>
    </div>

    <div class="rounded-lg border border-gray-200 bg-white p-4">
      <div class="mb-4 flex items-center justify-between">
        <h3 class="text-lg font-semibold text-gray-900">Staff Members</h3>
        <span class="rounded-full bg-gray-100 px-3 py-1 text-xs font-semibold text-gray-600">
          {{ staffList.length }} Staff
        </span>
      </div>

      <div v-if="staffList.length === 0" class="rounded-lg bg-gray-50 p-4 text-center text-sm text-gray-500">
        No staff members yet.
      </div>

      <div v-else class="grid grid-cols-1 gap-4 sm:grid-cols-2">
        <div v-for="staff in staffList" :key="staff.id"
          class="flex items-center gap-4 rounded-xl border border-gray-100 bg-white p-4 shadow-sm transition-shadow hover:shadow-md">
          <div class="flex h-12 w-12 items-center justify-center rounded-full bg-slate-200 overflow-hidden border border-slate-300">
            <img v-if="staff.profile_image" :src="getImageUrl(staff.profile_image)" :alt="staff.email" class="h-full w-full object-cover" />
            <span v-else class="text-lg font-semibold text-slate-600">{{ staff.email.slice(0, 1).toUpperCase() }}</span>
          </div>
          <div class="flex-1 min-w-0">
            <p class="truncate font-semibold text-gray-900">{{ staff.email }}</p>
            <p class="truncate text-sm text-gray-600">{{ staff.mobile_phone || 'No phone' }}</p>
            <p class="text-xs text-gray-500">
              Joined: {{ new Date(staff.created_at).toLocaleDateString('en-PH', { year: 'numeric', month: 'short', day: 'numeric' }) }}
            </p>
          </div>
          <button type="button" @click="openDeleteModal(staff)"
            class="rounded-lg border border-red-200 px-3 py-1.5 text-xs font-semibold text-red-600 transition-colors hover:bg-red-50 hover:border-red-300">
            Delete
          </button>
        </div>
      </div>
    </div>

    <ModalShell :show="showDeleteModal" title="Delete Staff Member" subtitle="Confirm deletion" tone="red" size="lg"
      @close="closeDeleteModal">
      <div class="space-y-4">
        <p class="text-gray-700">
          Are you sure you want to delete <strong>{{ selectedStaffToDelete?.email }}</strong>? This action cannot be
          undone.
        </p>
        <div v-if="deleteError" class="rounded-lg border border-red-200 bg-red-50 px-3 py-2 text-sm text-red-700">
          {{ deleteError }}
        </div>
      </div>

      <template #footer>
        <button type="button"
          class="rounded-lg border border-gray-300 bg-white px-4 py-2 font-semibold text-gray-700 hover:bg-gray-50"
          @click="closeDeleteModal">
          Cancel
        </button>
        <button type="button" :disabled="isDeleting"
          class="rounded-lg bg-red-600 px-4 py-2 font-semibold text-white hover:bg-red-700 disabled:opacity-60"
          @click="confirmDeleteStaff">
          {{ isDeleting ? 'Deleting...' : 'Delete' }}
        </button>
      </template>
    </ModalShell>
  </section>
</template>
