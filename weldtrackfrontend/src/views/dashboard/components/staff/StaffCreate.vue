<script setup lang="ts">
import InfoTooltip from '../../../../components/ui/InfoTooltip.vue'
import LocalLoader from '../../../../components/ui/LocalLoader.vue'
import { onMounted, reactive, ref } from 'vue'
import api from '../../../../api/api'
import { getUserFriendlyApiError } from '../../../../services/errorMessage'
import ModalShell from '../../../../components/ui/ModalShell.vue'
import { CalendarDays, Eye, EyeOff, Phone, ShieldCheck, Trash2, User } from 'lucide-vue-next'
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
const showPassword = ref(false)
const showConfirmPassword = ref(false)

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
              <div class="relative">
              <input
                id="create-staff-password"
                v-model="createStaffForm.password"
                :type="showPassword ? 'text' : 'password'"
                required
                placeholder="••••••••"
                class="w-full rounded-xl border border-slate-200 bg-white px-4 py-3 pr-12 shadow-sm outline-none transition focus:border-sky-500 focus:ring-2 focus:ring-sky-200"
              />
              <button type="button" class="absolute inset-y-0 right-0 flex w-12 items-center justify-center text-slate-400 transition-colors hover:text-sky-600 focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-inset focus-visible:ring-sky-500" :aria-label="showPassword ? 'Hide password' : 'Show password'" :aria-pressed="showPassword" @click="showPassword = !showPassword">
                <EyeOff v-if="showPassword" class="h-5 w-5" aria-hidden="true" />
                <Eye v-else class="h-5 w-5" aria-hidden="true" />
              </button>
              </div>
            </div>

            <div>
              <label class="flex items-center text-sm font-semibold text-gray-700 mb-1.5" for="create-staff-confirm-password">
                Confirm Password <span class="text-red-500 ml-1">*</span>
                <InfoTooltip text="Re-enter the password to verify." />
              </label>
              <div class="relative">
              <input
                id="create-staff-confirm-password"
                v-model="createStaffForm.confirmPassword"
                :type="showConfirmPassword ? 'text' : 'password'"
                required
                placeholder="••••••••"
                class="w-full rounded-xl border border-slate-200 bg-white px-4 py-3 pr-12 shadow-sm outline-none transition focus:border-sky-500 focus:ring-2 focus:ring-sky-200"
              />
              <button type="button" class="absolute inset-y-0 right-0 flex w-12 items-center justify-center text-slate-400 transition-colors hover:text-sky-600 focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-inset focus-visible:ring-sky-500" :aria-label="showConfirmPassword ? 'Hide confirmed password' : 'Show confirmed password'" :aria-pressed="showConfirmPassword" @click="showConfirmPassword = !showConfirmPassword">
                <EyeOff v-if="showConfirmPassword" class="h-5 w-5" aria-hidden="true" />
                <Eye v-else class="h-5 w-5" aria-hidden="true" />
              </button>
              </div>
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
          class="group relative flex min-w-0 flex-col overflow-hidden rounded-2xl border border-slate-200 bg-white shadow-sm transition-all duration-300 hover:-translate-y-1 hover:border-sky-200 hover:shadow-xl hover:shadow-sky-900/10 dark:border-slate-800 dark:bg-slate-900 dark:hover:border-sky-800"
        >
          <!-- Profile-style color header -->
          <div class="relative h-24 overflow-hidden bg-linear-to-br from-sky-500 via-blue-600 to-indigo-700 dark:from-sky-800 dark:via-blue-900 dark:to-indigo-950">
            <div class="absolute -right-8 -top-10 h-28 w-28 rounded-full border border-white/15 bg-white/10"></div>
            <div class="absolute -bottom-12 left-8 h-24 w-24 rounded-full bg-cyan-300/15 blur-xl"></div>
            <span class="absolute right-4 top-4 inline-flex items-center gap-1.5 rounded-full border border-white/20 bg-slate-950/20 px-2.5 py-1 text-[10px] font-bold uppercase tracking-[0.14em] text-white backdrop-blur-sm">
              <ShieldCheck class="h-3.5 w-3.5 text-sky-200" /> Staff account
            </span>
          </div>

          <div class="relative flex flex-1 flex-col px-5 pb-5">
            <div class="-mt-10 mb-4">
              <div class="relative flex h-20 w-20 shrink-0 items-center justify-center overflow-hidden rounded-2xl border-4 border-white bg-linear-to-br from-sky-50 to-slate-100 shadow-lg dark:border-slate-900 dark:from-slate-700 dark:to-slate-800">
                <img v-if="staff.profile_image" :src="getImageUrl(staff.profile_image)" :alt="staff.email" class="h-full w-full object-cover" />
                <span v-else class="text-2xl font-black text-sky-700 dark:text-sky-300">{{ staff.email.slice(0, 1).toUpperCase() }}</span>
              </div>
            </div>

            <div class="min-w-0">
              <p class="text-[10px] font-bold uppercase tracking-[0.16em] text-sky-600 dark:text-sky-400">WeldTrack team member</p>
              <h4 class="mt-1 truncate text-base font-bold text-slate-900 dark:text-white" :title="staff.email">{{ staff.email }}</h4>
            </div>

            <div class="mt-5 space-y-2.5 rounded-xl border border-slate-100 bg-slate-50/80 p-3.5 text-xs dark:border-slate-800 dark:bg-slate-800/50">
              <div class="flex items-center gap-2.5 text-slate-600 dark:text-slate-300">
                <Phone class="h-4 w-4 shrink-0 text-sky-600 dark:text-sky-400" />
                <span class="truncate font-medium">{{ staff.mobile_phone || 'No phone number added' }}</span>
              </div>
              <div class="flex items-center gap-2.5 text-slate-600 dark:text-slate-300">
                <CalendarDays class="h-4 w-4 shrink-0 text-sky-600 dark:text-sky-400" />
                <span><span class="text-slate-400">Joined</span> · {{ new Date(staff.created_at).toLocaleDateString('en-PH', { year: 'numeric', month: 'short', day: 'numeric' }) }}</span>
              </div>
            </div>

            <button
              type="button"
              @click="openDeleteModal(staff)"
              class="mt-4 inline-flex w-full items-center justify-center gap-2 rounded-xl border border-red-200 bg-white px-3 py-2.5 text-xs font-bold text-red-600 transition-colors hover:border-red-300 hover:bg-red-50 dark:border-red-900/60 dark:bg-slate-900 dark:text-red-400 dark:hover:bg-red-950/30"
            >
              <Trash2 class="h-3.5 w-3.5" /> Remove Staff Account
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
