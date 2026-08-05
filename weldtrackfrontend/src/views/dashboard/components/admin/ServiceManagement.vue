<script setup lang="ts">
import { computed, onMounted, reactive, ref } from 'vue'
import { Briefcase } from 'lucide-vue-next'
import api from '../../../../api/api'
import { useModalStore } from '../../../../stores/modal'
import ModalShell from '../../../../components/ui/ModalShell.vue'
import LocalLoader from '../../../../components/ui/LocalLoader.vue'

interface Service {
  id: number
  name: string
  description: string | null
  price: number
  image_url: string | null
  created_at: string
  updated_at: string
}

interface FormData {
  name: string
  description: string
  price: string
  image_url: string
}

const modalStore = useModalStore()
const services = ref<Service[]>([])
const loading = ref(false)
const isDialogOpen = ref(false)
const editingId = ref<number | null>(null)
const isSubmitting = ref(false)
const searchTerm = ref('')
const fileInputRef = ref<HTMLInputElement | null>(null)
const imagePreview = ref<string | null>(null)
const formData = reactive<FormData>({
  name: '',
  description: '',
  price: '',
  image_url: '',
})

const filteredServices = computed(() => {
  const query = searchTerm.value.trim().toLowerCase()
  if (!query) return services.value
  return services.value.filter(
    (service) =>
      service.name.toLowerCase().includes(query) ||
      (service.description?.toLowerCase().includes(query) ?? false),
  )
})

onMounted(() => {
  fetchServices()
})

async function fetchServices() {
  loading.value = true
  try {
    const response = await api.get('/services')
    services.value = response.data
  } catch (err: any) {
    modalStore.open({
      title: 'Error loading services',
      message: err.response?.data?.detail || 'Failed to load services',
      variant: 'error',
    })
  } finally {
    loading.value = false
  }
}

function resetForm() {
  formData.name = ''
  formData.description = ''
  formData.price = ''
  formData.image_url = ''
  imagePreview.value = null
  if (fileInputRef.value) fileInputRef.value.value = ''
}

function triggerFileInput() {
  fileInputRef.value?.click()
}

function handleFileInput(event: Event) {
  const input = event.target as HTMLInputElement
  const file = input.files?.[0]

  if (!file) return

  // Validate file is an image
  if (!file.type.startsWith('image/')) {
    modalStore.open({
      title: 'Invalid file type',
      message: 'Please select an image file (JPG, PNG, GIF, etc.)',
      variant: 'warning',
    })
    return
  }

  // Validate file size (max 5MB)
  if (file.size > 5 * 1024 * 1024) {
    modalStore.open({
      title: 'File too large',
      message: 'Please select an image smaller than 5MB',
      variant: 'warning',
    })
    return
  }

  // Convert to base64
  const reader = new FileReader()
  reader.onload = () => {
    const base64 = reader.result as string
    formData.image_url = base64
    imagePreview.value = base64
  }
  reader.readAsDataURL(file)
}

function openAddDialog() {
  editingId.value = null
  resetForm()
  isDialogOpen.value = true
}

function openEditDialog(service: Service) {
  editingId.value = service.id
  formData.name = service.name
  formData.description = service.description || ''
  formData.price = String(service.price)
  formData.image_url = service.image_url || ''
  imagePreview.value = service.image_url
  isDialogOpen.value = true
}

function closeDialog() {
  isDialogOpen.value = false
  editingId.value = null
  resetForm()
}

async function saveService() {
  if (!formData.name.trim()) {
    modalStore.open({
      title: 'Service name required',
      message: 'Please enter a service name',
      variant: 'warning',
    })
    return
  }

  const price = Number(formData.price)
  if (isNaN(price) || price < 0) {
    modalStore.open({
      title: 'Invalid price',
      message: 'Price must be a valid positive number',
      variant: 'warning',
    })
    return
  }

  isSubmitting.value = true
  try {
    const payload = {
      name: formData.name.trim(),
      description: formData.description.trim() || null,
      price,
      image_url: formData.image_url.trim() || null,
    }

    if (editingId.value) {
      await api.put(`/services/${editingId.value}`, payload)
    } else {
      await api.post('/services', payload)
    }

    closeDialog()
    await fetchServices()
  } catch (err: any) {
    modalStore.open({
      title: 'Error saving service',
      message: err.response?.data?.detail || 'Failed to save service',
      variant: 'error',
    })
  } finally {
    isSubmitting.value = false
  }
}

function deleteService(id: number, name: string) {
  modalStore.open({
    title: 'Delete service?',
    message: `Are you sure you want to delete "${name}"? This action cannot be undone.`,
    variant: 'error',
    confirmLabel: 'Delete',
    cancelLabel: 'Cancel',
    onConfirm: async () => {
      try {
        await api.delete(`/services/${id}`)
        await fetchServices()
      } catch (err: any) {
        modalStore.open({
          title: 'Error deleting service',
          message: err.response?.data?.detail || 'Failed to delete service',
          variant: 'error',
        })
      }
    },
  })
}

function formatCurrency(value: number) {
  return `₱${value.toLocaleString('en-PH', { minimumFractionDigits: 2 })}`
}

function formatDate(value: string) {
  return new Date(value).toLocaleDateString('en-PH', {
    year: 'numeric',
    month: 'short',
    day: '2-digit',
  })
}
</script>

<template>
  <section class="space-y-6 rounded-lg border border-gray-200 bg-white p-6 relative">
    <LocalLoader v-if="loading" />
    <div class="flex flex-col gap-4 lg:flex-row lg:items-center lg:justify-between">
      <div class="flex items-start gap-3">
        <div class="flex h-10 w-10 items-center justify-center rounded-lg bg-linear-to-br from-sky-50 to-sky ring-1 ring-sky-100">
          <Briefcase class="h-5 w-5 text-sky-600" />
        </div>
        <div>
          <h2 class="text-2xl font-semibold text-gray-900">Services Management</h2>
          <p class="mt-1 text-gray-600">Manage all services offered by your business</p>
        </div>
      </div>
      <button
        @click="openAddDialog"
        class="inline-flex items-center justify-center rounded-lg bg-blue-600 px-4 py-3 font-semibold text-white transition-colors hover:bg-blue-700"
      >
        <svg class="mr-2 h-5 w-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 4v16m8-8H4" />
        </svg>
        Add Service
      </button>
    </div>

    <div class="rounded-lg border border-gray-200 p-4">
      <input
        v-model="searchTerm"
        type="text"
        placeholder="Search services..."
        class="w-full rounded-lg border border-gray-300 bg-gray-50 px-4 py-3 outline-none transition focus:border-blue-500 focus:ring-2 focus:ring-blue-200 lg:max-w-md"
      />
    </div>

    <!-- Add/Edit Form Modal -->
    <ModalShell
      :show="isDialogOpen"
      :title="editingId ? 'Edit Service' : 'Add New Service'"
      subtitle="Service offering"
      tone="blue"
      size="md"
      @close="closeDialog"
    >
      <form class="space-y-4" @submit.prevent="saveService">
        <div>
          <label class="block text-sm font-medium text-gray-700">Service Name *</label>
          <input
            v-model="formData.name"
            type="text"
            class="mt-1 w-full rounded-xl border border-slate-200 bg-slate-50 px-4 py-3 shadow-sm outline-none transition focus:border-blue-500 focus:ring-2 focus:ring-blue-200"
            placeholder="e.g., Gate Welding"
          />
        </div>

        <div>
          <label class="block text-sm font-medium text-gray-700">Description</label>
          <textarea
            v-model="formData.description"
            rows="3"
            class="mt-1 w-full rounded-xl border border-slate-200 bg-slate-50 px-4 py-3 shadow-sm outline-none transition focus:border-blue-500 focus:ring-2 focus:ring-blue-200"
            placeholder="Service description"
          ></textarea>
        </div>

        <div class="grid grid-cols-1 gap-4 sm:grid-cols-2">
          <div>
            <label class="block text-sm font-medium text-gray-700">Labor Price (₱) /hour *</label>
            <input
              v-model="formData.price"
              type="number"
              step="0.01"
              min="0"
              class="mt-1 w-full rounded-xl border border-slate-200 bg-slate-50 px-4 py-3 shadow-sm outline-none transition focus:border-blue-500 focus:ring-2 focus:ring-blue-200"
              placeholder="0"
            />
          </div>

          <div>
            <label class="block text-sm font-medium text-gray-700">Service Image</label>
            <button
              type="button"
              @click="triggerFileInput"
              class="mt-1 w-full rounded-xl border border-slate-200 bg-slate-50 px-4 py-3 font-medium text-slate-700 shadow-sm outline-none transition hover:bg-slate-100 focus:border-blue-500 focus:ring-2 focus:ring-blue-200"
            >
              <svg class="mr-2 inline h-4 w-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 4v16m8-8H4" />
              </svg>
              Choose Image
            </button>
            <input
              ref="fileInputRef"
              type="file"
              accept="image/*"
              class="hidden"
              @change="handleFileInput"
            />
          </div>
        </div>

        <div v-if="imagePreview" class="rounded-lg border border-slate-200 bg-slate-50 p-4">
          <p class="mb-2 text-sm font-medium text-gray-700">Image Preview</p>
          <img :src="imagePreview" :alt="formData.name" class="h-48 w-full rounded-lg object-cover" />
        </div>

        <div class="flex gap-3 pt-2">
          <button
            type="button"
            class="flex-1 rounded-xl border border-slate-200 bg-white px-4 py-3 font-semibold text-slate-700 shadow-sm hover:bg-slate-50 disabled:opacity-50 disabled:cursor-not-allowed"
            :disabled="isSubmitting"
            @click="closeDialog"
          >
            Cancel
          </button>
          <button
            type="submit"
            class="flex-1 rounded-xl bg-linear-to-r from-blue-600 to-sky-600 px-4 py-3 font-semibold text-white shadow-lg shadow-blue-600/20 hover:from-blue-700 hover:to-sky-700 disabled:opacity-50 disabled:cursor-not-allowed inline-flex items-center justify-center gap-2"
            :disabled="isSubmitting"
          >
            <svg v-if="isSubmitting" class="h-4 w-4 animate-spin" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"></circle>
              <path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
            </svg>
            <span>{{ isSubmitting ? (editingId ? 'Updating...' : 'Adding...') : (editingId ? 'Update' : 'Add') }} Service</span>
          </button>
        </div>
      </form>
    </ModalShell>

    <!-- Services Table -->
    <div v-if="loading" class="rounded-lg border border-gray-200 bg-white p-8 text-center">
      <p class="text-gray-600">Loading services...</p>
    </div>

    <div v-else-if="filteredServices.length === 0" class="rounded-lg border border-gray-200 bg-white p-8 text-center">
      <p class="text-gray-600">{{ searchTerm ? 'No matching services found.' : 'No services yet. Add one to get started!' }}</p>
    </div>

    <div v-else class="overflow-hidden rounded-xl border border-gray-200">
      <div class="h-screen overflow-x-auto">
        <table class="w-full min-w-180 divide-y divide-gray-200">
          <thead class="bg-gray-50/70">
            <tr class="text-left">
              <th class="px-6 py-4 text-xs font-bold uppercase tracking-wider text-gray-500">Image</th>
              <th class="px-6 py-4 text-xs font-bold uppercase tracking-wider text-gray-500">Service Name</th>
              <th class="px-6 py-4 text-xs font-bold uppercase tracking-wider text-gray-500">Description</th>
              <th class="px-6 py-4 text-xs font-bold uppercase tracking-wider text-gray-500">Labor Price /hour</th>
              <th class="px-6 py-4 text-xs font-bold uppercase tracking-wider text-gray-500">Created</th>
              <th class="px-6 py-4 text-xs font-bold uppercase tracking-wider text-gray-500 text-right">Actions</th>
            </tr>
          </thead>
          <tbody class="divide-y divide-gray-100 bg-white">
            <tr v-for="service in filteredServices" :key="service.id" class="transition-colors hover:bg-slate-50/80">
              <td class="px-6 py-4 whitespace-nowrap">
                <div class="flex h-14 w-14 items-center justify-center overflow-hidden rounded-lg border border-gray-200 bg-gray-100 shadow-xs">
                  <img
                    v-if="service.image_url"
                    :src="service.image_url"
                    :alt="service.name"
                    class="h-full w-full object-cover"
                  />
                  <span v-else class="text-xs font-medium text-gray-500">No image</span>
                </div>
              </td>
              <td class="px-6 py-4 font-semibold text-gray-900 whitespace-nowrap">{{ service.name }}</td>
              <td class="px-6 py-4 text-sm text-gray-600">
                {{ service.description ? service.description.substring(0, 50) + (service.description.length > 50 ? '...' : '') : '-' }}
              </td>
              <td class="px-6 py-4 font-semibold text-gray-900 whitespace-nowrap">{{ formatCurrency(service.price) }}</td>
              <td class="px-6 py-4 text-sm text-gray-600 whitespace-nowrap">{{ formatDate(service.created_at) }}</td>
              <td class="px-6 py-4 whitespace-nowrap">
                <div class="flex gap-3 justify-end">
                  <button
                    @click="openEditDialog(service)"
                    class="text-sky-600 transition-colors hover:text-sky-800"
                  >
                    <svg class="h-5 w-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M11 5H6a2 2 0 00-2 2v11a2 2 0 002 2h11a2 2 0 002-2v-5m-1.414-9.414a2 2 0 112.828 2.828L11.828 15H9v-2.828l8.586-8.586z" />
                    </svg>
                  </button>
                  <button
                    @click="deleteService(service.id, service.name)"
                    class="text-red-600 transition-colors hover:text-red-800"
                  >
                    <svg class="h-5 w-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 7l-.867 12.142A2 2 0 0116.138 21H7.862a2 2 0 01-1.995-1.858L5 7m5 4v6m4-6v6m1-10V4a1 1 0 00-1-1h-4a1 1 0 00-1 1v3M4 7h16" />
                    </svg>
                  </button>
                </div>
              </td>
            </tr>
          </tbody>
        </table>
      </div>
    </div>
  </section>
</template>
