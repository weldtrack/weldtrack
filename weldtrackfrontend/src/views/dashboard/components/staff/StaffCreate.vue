<script setup lang="ts">
import InfoTooltip from '../../../../components/ui/InfoTooltip.vue'
import LocalLoader from '../../../../components/ui/LocalLoader.vue'
import { onMounted, reactive, ref } from 'vue'
import api from '../../../../api/api'
import { getUserFriendlyApiError } from '../../../../services/errorMessage'
import ModalShell from '../../../../components/ui/ModalShell.vue'
import { User } from 'lucide-vue-next'
import { resolveImageUrl } from '../../../../services/images'

interface StaffMember {
  id: string
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

const getImageUrl = resolveImageUrl;

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
  <section class="space-y-6 relative">
    <LocalLoader v-if="isLoading" />
    
    <!-- Header -->
    <div class="flex items-start gap-3">
      <div class="flex h-12 w-12 items-center justify-center">
        <User class="dashboard-view-icon h-6 w-6 text-sky-600 dark:text-sky-400" />
      </div>
      <div>
        <h3 class="text-2xl font-semibold text-gray-900">Create Staff Account</h3>
        <p class="text-sm text-gray-600">Create a staff account directly (no verification required).</p>
      </div>
    </div>

    <!-- Form Section -->
    <div class="rounded-xl border border-slate-200 bg-white shadow-sm dark:border-slate-800 dark:bg-slate-900">
      <div class="border-b border-slate-100 px-6 py-5 flex items-center justify-between bg-transparent">
        <div>
          <h3 class="text-xl font-bold text-slate-900">Account Details</h3>
          <p class="text-sm text-slate-500 mt-1">Set up new staff login credentials</p>
        </div>
      </div>

      <div class="p-6">
        <div v-if="createStaffError" class="mb-4 rounded-xl border border-red-200 bg-red-50 p-4 text-sm text-red-700">
          {{ createStaffError }}
        </div>
        <div v-if="createStaffSuccess" class="mb-4 rounded-xl border border-green-200 bg-green-50 p-4 text-sm text-green-700">
          {{ createStaffSuccess }}
        </div>

        <form @submit.prevent="submitCreateStaff" class="space-y-5 max-w-4xl">
          <div>
            <label class="flex items-center text-sm font-semibold text-gray-700 mb-1.5" for="create-staff-email">
              Email Address <span class="text-red-500 ml-1">*</span>
              <InfoTooltip text="Enter the official work email address for the staff member." />
            </label>
            <input
              id="create-staff-email"
              v-model="createStaffForm.email"
              type="email"
              required
              placeholder="staff@example.com"
              class="w-full rounded-xl border border-slate-200 bg-white px-4 py-3 shadow-sm outline-none transition focus:border-sky-500 focus:ring-2 focus:ring-sky-200"
            />
          </div>

          <div class="grid grid-cols-1 gap-5 sm:grid-cols-2">
            <div>
              <label class="flex items-center text-sm font-semibold text-gray-700 mb-1.5" for="create-staff-password">
                Password <span class="text-red-500 ml-1">*</span>
                <InfoTooltip text="Must be at least 8 characters long." />
              </label>
              <input
                id="create-staff-password"
                v-model="createStaffForm.password"
                type="password"
                required
                placeholder="••••••••"
                class="w-full rounded-xl border border-slate-200 bg-white px-4 py-3 shadow-sm outline-none transition focus:border-sky-500 focus:ring-2 focus:ring-sky-200"
              />
            </div>

            <div>
              <label class="flex items-center text-sm font-semibold text-gray-700 mb-1.5" for="create-staff-confirm-password">
                Confirm Password <span class="text-red-500 ml-1">*</span>
                <InfoTooltip text="Re-enter the password to verify." />
              </label>
              <input
                id="create-staff-confirm-password"
                v-model="createStaffForm.confirmPassword"
                type="password"
                required
                placeholder="••••••••"
                class="w-full rounded-xl border border-slate-200 bg-white px-4 py-3 shadow-sm outline-none transition focus:border-sky-500 focus:ring-2 focus:ring-sky-200"
              />
            </div>
          </div>

          <label class="flex items-center gap-3 rounded-xl border border-slate-200 bg-slate-50 p-4 text-sm text-slate-700 cursor-pointer hover:bg-slate-100/80 transition-colors">
            <input
              v-model="createStaffForm.confirm"
              type="checkbox"
              class="h-4 w-4 rounded border-slate-300 text-sky-600 focus:ring-sky-500"
            />
            <span class="font-medium">I confirm that this staff account creation is authorized.</span>
            <InfoTooltip text="Confirmation check required before creating account." />
          </label>

          <div class="flex justify-end pt-2 border-t border-slate-100 mt-6">
            <button
              type="submit"
              :disabled="creatingStaff"
              class="inline-flex min-w-40 items-center justify-center gap-2 rounded-xl bg-linear-to-r from-sky-600 to-sky-700 px-6 py-2.5 font-semibold text-white shadow-md shadow-sky-600/20 hover:from-sky-700 hover:to-sky-800 disabled:opacity-50 disabled:cursor-not-allowed transition-all"
            >
              {{ creatingStaff ? 'Creating Account...' : 'Create Staff Account' }}
            </button>
          </div>
        </form>
      </div>
    </div>

    <!-- Staff Profile Cards List -->
    <div class="space-y-4">
      <div class="flex items-center justify-between">
        <div>
          <h3 class="text-xl font-bold text-slate-900">Staff Members</h3>
          <p class="text-sm text-slate-500">Currently active staff accounts in the system</p>
        </div>
        <span class="inline-flex items-center rounded-full bg-sky-50 px-3 py-1 text-xs font-bold text-sky-700 ring-1 ring-inset ring-sky-600/20">
          {{ staffList.length }} Staff {{ staffList.length === 1 ? 'Member' : 'Members' }}
        </span>
      </div>

      <div v-if="staffList.length === 0" class="rounded-xl border border-slate-200 bg-white p-8 text-center text-sm text-slate-500">
        No staff members found. Create one above to get started.
      </div>

      <div v-else class="grid grid-cols-1 gap-5 sm:grid-cols-2 lg:grid-cols-3">
        <div
          v-for="staff in staffList"
          :key="staff.id"
          class="group relative flex flex-col justify-between rounded-2xl border border-slate-200 bg-white p-5 shadow-xs transition-all duration-200 hover:border-slate-300 hover:shadow-md"
        >
          <!-- Top Badge & Avatar -->
          <div>
            <div class="flex items-start justify-between mb-4">
              <div class="relative flex h-14 w-14 shrink-0 items-center justify-center rounded-2xl border border-slate-200 bg-linear-to-br from-slate-50 to-slate-100 shadow-xs overflow-hidden">
                <img v-if="staff.profile_image" :src="getImageUrl(staff.profile_image)" :alt="staff.email" class="h-full w-full object-cover" />
                <span v-else class="text-xl font-bold text-sky-700">{{ staff.email.slice(0, 1).toUpperCase() }}</span>
              </div>
              <span class="inline-flex items-center rounded-full bg-slate-100 px-2.5 py-1 text-[11px] font-bold text-slate-600 tracking-wider uppercase">
                Staff
              </span>
            </div>

            <!-- Profile Info -->
            <div class="space-y-1">
              <h4 class="truncate text-base font-bold text-slate-900" :title="staff.email">{{ staff.email }}</h4>
              <p class="truncate text-xs font-medium text-slate-500">
                {{ staff.mobile_phone || 'No phone recorded' }}
              </p>
            </div>
          </div>

          <!-- Footer Metadata & Action -->
          <div class="mt-5 pt-4 border-t border-slate-100 flex items-center justify-between text-xs text-slate-500">
            <div>
              <span class="block text-[10px] uppercase tracking-wider font-semibold text-slate-400">Joined</span>
              <span class="font-medium text-slate-700">
                {{ new Date(staff.created_at).toLocaleDateString('en-PH', { year: 'numeric', month: 'short', day: 'numeric' }) }}
              </span>
            </div>
            <button
              type="button"
              @click="openDeleteModal(staff)"
              class="rounded-lg border border-red-200 bg-red-50 px-3 py-1.5 text-xs font-semibold text-red-600 transition-colors hover:bg-red-100 hover:border-red-300"
            >
              Delete
            </button>
          </div>
        </div>
      </div>
    </div>

    <!-- Delete Confirmation Modal -->
    <ModalShell
      :show="showDeleteModal"
      title="Delete Staff Member"
      subtitle="Confirm account removal"
      tone="red"
      size="lg"
      @close="closeDeleteModal"
    >
      <div class="space-y-4">
        <p class="text-slate-700">
          Are you sure you want to delete <strong>{{ selectedStaffToDelete?.email }}</strong>? This action cannot be undone.
        </p>
        <div v-if="deleteError" class="rounded-lg border border-red-200 bg-red-50 px-3 py-2 text-sm text-red-700">
          {{ deleteError }}
        </div>
      </div>

      <template #footer>
        <button
          type="button"
          class="rounded-lg border border-slate-300 bg-white px-4 py-2 font-semibold text-slate-700 hover:bg-slate-50"
          @click="closeDeleteModal"
        >
          Cancel
        </button>
        <button
          type="button"
          :disabled="isDeleting"
          class="rounded-lg bg-red-600 px-4 py-2 font-semibold text-white hover:bg-red-700 disabled:opacity-60"
          @click="confirmDeleteStaff"
        >
          {{ isDeleting ? 'Deleting...' : 'Delete Staff' }}
        </button>
      </template>
    </ModalShell>
  </section>
</template>
