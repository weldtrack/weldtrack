<script setup lang="ts">
import InfoTooltip from '../../../../components/ui/InfoTooltip.vue'
import { computed, onMounted, reactive, ref } from 'vue'
import { Briefcase, ImagePlus, Info, LoaderCircle } from 'lucide-vue-next'
import api from '../../../../api/api'
import { useModalStore } from '../../../../stores/modal'
import LocalLoader from '../../../../components/ui/LocalLoader.vue'
import { resolveImageUrl, uploadImage } from '../../../../services/images'

import { formatServicePricing } from '../../../../services/servicePricing'

interface Service {
  id: string
  name: string
  description: string | null
  pricing_type: 'hourly' | 'fixed' | 'hybrid'
  price_fixed: number
  price_hour: number
  image_url: string | null
  created_at: string
  updated_at: string
}

interface FormData {
  name: string
  description: string
  pricing_type: 'hourly' | 'fixed' | 'hybrid'
  price_fixed: string
  price_hour: string
  image_url: string
}

const modalStore = useModalStore()
const services = ref<Service[]>([])
const loading = ref(false)
const isDialogOpen = ref(false)
const editingId = ref<string | null>(null)
const isSubmitting = ref(false)
const formError = ref('')
const searchTerm = ref('')
const fileInputRef = ref<HTMLInputElement | null>(null)
const imagePreview = ref<string | null>(null)
const formData = reactive<FormData>({
  name: '',
  description: '',
  pricing_type: 'hourly',
  price_fixed: '0',
  price_hour: '0',
  image_url: '',
})

const sortBy = ref<'latest' | 'oldest' | 'az'>('latest')

const filteredServices = computed(() => {
  let list = [...services.value]
  const query = searchTerm.value.trim().toLowerCase()
  if (query) {
    list = list.filter(
      (service) =>
        service.name.toLowerCase().includes(query) ||
        (service.description?.toLowerCase().includes(query) ?? false),
    )
  }

  return list.sort((a, b) => {
    if (sortBy.value === 'az') {
      return a.name.localeCompare(b.name)
    }
    const timeA = a.created_at ? new Date(a.created_at).getTime() : 0
    const timeB = b.created_at ? new Date(b.created_at).getTime() : 0
    if (timeA && timeB && timeA !== timeB) {
      return sortBy.value === 'oldest' ? timeA - timeB : timeB - timeA
    }
    return sortBy.value === 'oldest' ? String(a.id).localeCompare(String(b.id)) : String(b.id).localeCompare(String(a.id))
  })
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
  formError.value = ''
  formData.name = ''
  formData.description = ''
  formData.pricing_type = 'hourly'
  formData.price_fixed = '0'
  formData.price_hour = '0'
  formData.image_url = ''
  imagePreview.value = null
  if (fileInputRef.value) fileInputRef.value.value = ''
}

function triggerFileInput() {
  fileInputRef.value?.click()
}

async function handleFileInput(event: Event) {
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

  imagePreview.value = URL.createObjectURL(file)
  try {
    formData.image_url = await uploadImage(file, 'services')
    imagePreview.value = resolveImageUrl(formData.image_url)
  } catch (err: any) {
    formData.image_url = ''
    imagePreview.value = null
    modalStore.open({
      title: 'Image upload failed',
      message: err.response?.data?.detail || 'The service image could not be uploaded.',
      variant: 'error',
    })
  }
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
  formData.pricing_type = service.pricing_type || 'hourly'
  formData.price_fixed = String(service.price_fixed ?? 0)
  formData.price_hour = String(service.price_hour ?? 0)
  formData.image_url = service.image_url || ''
  imagePreview.value = resolveImageUrl(service.image_url)
  isDialogOpen.value = true
}

function closeDialog() {
  isDialogOpen.value = false
  editingId.value = null
  resetForm()
}

async function saveService() {
  if (!formData.name.trim()) {
    formError.value = 'Enter a service name before continuing.'
    return
  }

  const priceFixed = Number(formData.price_fixed)
  const priceHour = Number(formData.price_hour)

  if (formData.pricing_type === 'fixed' || formData.pricing_type === 'hybrid') {
    if (isNaN(priceFixed) || priceFixed < 0) {
      formError.value = 'Enter a valid fixed price of zero or more.'
      return
    }
  }

  if (formData.pricing_type === 'hourly' || formData.pricing_type === 'hybrid') {
    if (isNaN(priceHour) || priceHour < 0) {
      formError.value = 'Enter a valid hourly labor price of zero or more.'
      return
    }
  }

  isSubmitting.value = true
  formError.value = ''
  try {
    const payload = {
      name: formData.name.trim(),
      description: formData.description.trim() || null,
      pricing_type: formData.pricing_type,
      price_fixed: formData.pricing_type === 'hourly' ? 0 : priceFixed,
      price_hour: formData.pricing_type === 'fixed' ? 0 : priceHour,
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
    formError.value = err.response?.data?.detail || 'The service could not be saved. Please try again.'
  } finally {
    isSubmitting.value = false
  }
}

function deleteService(id: string, name: string) {
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


function formatDate(value: string) {
  return new Date(value).toLocaleDateString('en-PH', {
    year: 'numeric',
    month: 'short',
    day: '2-digit',
  })
}
</script>

<template>
  <section class="relative space-y-6">
    <LocalLoader v-if="loading" />
    
    <!-- List View -->
    <template v-if="!isDialogOpen">
      <div class="flex flex-col gap-4 lg:flex-row lg:items-center lg:justify-between">
        <div class="flex items-start gap-3">
          <div class="flex h-12 w-12 items-center justify-center">
            <Briefcase class="dashboard-view-icon h-6 w-6 text-sky-600 dark:text-sky-400" />
          </div>
          <div>
            <h3 class="text-2xl font-semibold text-slate-900 dark:text-slate-100">Services Management</h3>
            <p class="text-sm text-slate-600 dark:text-slate-400">Manage all services offered by your business</p>
          </div>
        </div>
        <button
          @click="openAddDialog"
          class="inline-flex items-center justify-center gap-2 rounded-xl bg-sky-600 px-4 py-2.5 text-sm font-semibold text-white shadow-xs transition-colors hover:bg-sky-700 dark:bg-sky-600 dark:hover:bg-sky-500 shrink-0"
        >
          <svg class="h-4 w-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 4v16m8-8H4" />
          </svg>
          <span>Add Service</span>
        </button>
      </div>

      <!-- Search and Sort Box Card -->
      <div class="rounded-2xl border border-slate-200 bg-white p-4 shadow-xs dark:border-slate-800 dark:bg-slate-900">
        <div class="flex flex-col gap-3 sm:flex-row sm:items-center sm:justify-between">
          <div class="relative flex-1 max-w-md">
            <svg class="absolute left-3.5 top-1/2 h-4 w-4 -translate-y-1/2 text-slate-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M21 21l-4.35-4.35M11 18a7 7 0 100-14 7 7 0 000 14z" />
            </svg>
            <input
              v-model="searchTerm"
              type="text"
              placeholder="Search services..."
              class="w-full rounded-xl border border-slate-200 bg-slate-50 py-2.5 pl-10 pr-4 text-sm text-slate-900 outline-none transition focus:border-sky-500 focus:bg-white dark:border-slate-800 dark:bg-slate-950 dark:text-slate-100 dark:focus:border-sky-500"
            />
          </div>

          <!-- Sort by dropdown -->
          <div class="flex items-center gap-2 shrink-0">
            <label class="text-xs font-semibold text-slate-500 dark:text-slate-400 whitespace-nowrap">Sort by:</label>
            <select
              v-model="sortBy"
              class="rounded-xl border border-slate-200 bg-slate-50 px-3 py-2 text-xs font-semibold text-slate-800 outline-none transition focus:border-sky-500 focus:bg-white dark:border-slate-800 dark:bg-slate-950 dark:text-slate-200 dark:focus:border-sky-500"
            >
              <option value="latest">Date Latest</option>
              <option value="oldest">Date Oldest</option>
              <option value="az">A to Z</option>
            </select>
          </div>
        </div>
      </div>

      <!-- Services Table Container -->
      <div v-if="loading" class="rounded-2xl border border-slate-200 bg-white p-8 text-center dark:border-slate-800 dark:bg-slate-900">
        <p class="text-slate-600 dark:text-slate-400">Loading services...</p>
      </div>

      <div v-else-if="filteredServices.length === 0" class="rounded-2xl border border-slate-200 bg-white p-8 text-center dark:border-slate-800 dark:bg-slate-900">
        <p class="text-slate-600 dark:text-slate-400">{{ searchTerm ? 'No matching services found.' : 'No services yet. Add one to get started!' }}</p>
      </div>

      <div v-else class="overflow-hidden rounded-2xl border border-slate-200 bg-white shadow-xs dark:border-slate-800 dark:bg-slate-900">
        <div class="overflow-x-auto">
          <table class="w-full min-w-[800px] divide-y divide-slate-100 dark:divide-slate-800">
            <thead class="bg-slate-50 dark:bg-slate-800/80">
              <tr class="text-left">
                <th class="px-6 py-4 text-xs font-bold uppercase tracking-wider text-slate-500 dark:text-slate-400">Image</th>
                <th class="px-6 py-4 text-xs font-bold uppercase tracking-wider text-slate-500 dark:text-slate-400">Service Name</th>
                <th class="px-6 py-4 text-xs font-bold uppercase tracking-wider text-slate-500 dark:text-slate-400">Description</th>
                <th class="px-6 py-4 text-xs font-bold uppercase tracking-wider text-slate-500 dark:text-slate-400">Labor Price per Hour</th>
                <th class="px-6 py-4 text-xs font-bold uppercase tracking-wider text-slate-500 dark:text-slate-400">Created</th>
                <th class="px-6 py-4 text-xs font-bold uppercase tracking-wider text-slate-500 dark:text-slate-400 text-right sticky right-0 z-10 bg-slate-50 dark:bg-slate-800 shadow-[-12px_0_15px_-4px_rgba(0,0,0,0.05)]">Actions</th>
              </tr>
            </thead>
            <tbody class="divide-y divide-slate-100 dark:divide-slate-800 bg-transparent">
              <tr v-for="service in filteredServices" :key="service.id" class="transition-colors hover:bg-slate-50/50 dark:hover:bg-slate-800/50 group">
                <td class="px-6 py-4 whitespace-nowrap">
                  <div class="flex h-14 w-14 items-center justify-center overflow-hidden rounded-lg border border-gray-200 bg-gray-100 shadow-xs">
                    <img
                      v-if="service.image_url"
                      :src="resolveImageUrl(service.image_url)"
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
                <td class="px-6 py-4 whitespace-nowrap">
                  <div class="flex flex-col">
                    <span class="font-semibold text-gray-900 dark:text-gray-100">{{ formatServicePricing(service) }}</span>
                    <span class="text-[11px] font-bold uppercase tracking-wider text-sky-600 dark:text-sky-400">{{ service.pricing_type || 'hourly' }}</span>
                  </div>
                </td>
                <td class="px-6 py-4 text-sm text-gray-600 whitespace-nowrap">{{ formatDate(service.created_at) }}</td>
                <td class="px-6 py-4 whitespace-nowrap sticky right-0 z-10 bg-white dark:bg-slate-900 group-hover:bg-slate-50 dark:group-hover:bg-slate-800 shadow-[-12px_0_15px_-4px_rgba(0,0,0,0.05)]">
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
    </template>

    <!-- Form View -->
    <template v-else>
      <div class="overflow-hidden rounded-3xl border border-slate-200 bg-white shadow-xl shadow-slate-200/40 dark:border-slate-800 dark:bg-slate-900 dark:shadow-black/20">
        <div class="flex items-center justify-between border-b border-slate-200 bg-linear-to-r from-sky-50 via-white to-cyan-50 px-6 py-6 dark:border-slate-800 dark:from-slate-900 dark:via-slate-900 dark:to-sky-950/40 sm:px-8">
          <div class="flex items-center gap-4">
            <div class="flex h-12 w-12 items-center justify-center rounded-2xl bg-sky-600 text-white shadow-lg shadow-sky-600/20"><Briefcase class="h-5 w-5" /></div>
            <div>
            <h3 class="text-xl font-bold text-slate-900 dark:text-white">
              {{ editingId ? 'Edit Service' : 'Add New Service' }}
            </h3>
            <p class="text-sm text-slate-500 mt-1 dark:text-slate-400">Create a polished listing for your service catalogue</p>
            </div>
          </div>
          <button 
            @click="closeDialog" 
            class="rounded-xl border border-slate-200 bg-white px-4 py-2 text-sm font-semibold text-slate-600 shadow-sm transition hover:bg-slate-50 hover:text-slate-900 dark:border-slate-700 dark:bg-slate-800 dark:text-slate-300 dark:hover:bg-slate-700"
          >
            Cancel
          </button>
        </div>

        <div class="p-6 sm:p-8">
          <form id="service-form" class="mx-auto max-w-5xl space-y-7" @submit.prevent="saveService">
            <div class="flex gap-3 rounded-2xl border border-sky-200 bg-sky-50 p-4 text-sm leading-6 text-sky-900 dark:border-sky-900/50 dark:bg-sky-950/40 dark:text-sky-200">
              <Info class="mt-0.5 h-4 w-4 shrink-0" />
              <p>This information appears in the customer service catalogue. Use a clear name, useful description, and accurate labor price per hour.</p>
            </div>
            <div class="rounded-2xl border border-slate-200 bg-slate-50/70 p-5 dark:border-slate-800 dark:bg-slate-950/40">
              <label class="flex items-center text-sm font-semibold text-gray-700 mb-1.5">Service Name <span class="text-red-500">*</span><InfoTooltip text="Please provide the service name." /></label>
              <input
                v-model="formData.name"
                type="text"
                class="w-full rounded-xl border border-slate-200 bg-white px-4 py-3.5 shadow-sm outline-none transition focus:border-sky-500 focus:ring-4 focus:ring-sky-500/10 dark:border-slate-700 dark:bg-slate-900 dark:text-white"
                required
                autocomplete="off"
                placeholder="e.g. Steel gate fabrication"
              />
            </div>

            <div class="rounded-2xl border border-slate-200 bg-slate-50/70 p-5 dark:border-slate-800 dark:bg-slate-950/40">
              <div class="flex items-center justify-between gap-4 mb-1.5">
                <label class="flex items-center text-sm font-semibold text-gray-700">Description<InfoTooltip text="Please provide the description." /></label>
                <span class="text-xs text-gray-500">{{ formData.description.length }}/500</span>
              </div>
              <textarea
                v-model="formData.description"
                rows="3"
                maxlength="500"
                class="w-full rounded-xl border border-slate-200 bg-white px-4 py-3.5 shadow-sm outline-none transition focus:border-sky-500 focus:ring-4 focus:ring-sky-500/10 dark:border-slate-700 dark:bg-slate-900 dark:text-white"
                placeholder="Describe what is included and what customers should expect."
              ></textarea>
            </div>

            <!-- Pricing Model Selector -->
            <div class="rounded-2xl border border-slate-200 bg-slate-50/70 p-5 dark:border-slate-800 dark:bg-slate-950/40">
              <label class="flex items-center text-sm font-semibold text-gray-700 dark:text-gray-200 mb-1.5">
                Pricing Model <span class="text-red-500">*</span>
                <InfoTooltip text="Choose whether this service has an hourly rate, a fixed flat fee, or a hybrid base fee + hourly rate." />
              </label>
              <select
                v-model="formData.pricing_type"
                class="w-full rounded-xl border border-slate-200 bg-white px-4 py-3.5 shadow-sm outline-none transition focus:border-sky-500 focus:ring-4 focus:ring-sky-500/10 dark:border-slate-700 dark:bg-slate-900 dark:text-white"
              >
                <option value="hourly">Hourly Rate Only (₱ / hour)</option>
                <option value="fixed">Fixed Price (Flat ₱ fee)</option>
                <option value="hybrid">Hybrid (Base Fee + Hourly Rate)</option>
              </select>
            </div>

            <!-- Price Inputs based on Model -->
            <div class="grid grid-cols-1 gap-5" :class="formData.pricing_type === 'hybrid' ? 'sm:grid-cols-2' : ''">
              <div
                v-if="formData.pricing_type === 'fixed' || formData.pricing_type === 'hybrid'"
                class="rounded-2xl border border-slate-200 bg-slate-50/70 p-5 dark:border-slate-800 dark:bg-slate-950/40"
              >
                <label class="flex items-center text-sm font-semibold text-gray-700 dark:text-gray-200 mb-1.5">
                  {{ formData.pricing_type === 'hybrid' ? 'Base / Call-out Fee (₱)' : 'Fixed Price (₱)' }} <span class="text-red-500">*</span>
                  <InfoTooltip text="Fixed flat fee charged for this service." />
                </label>
                <input
                  v-model="formData.price_fixed"
                  type="number"
                  step="0.01"
                  min="0"
                  required
                  class="w-full rounded-xl border border-slate-200 bg-white px-4 py-3.5 shadow-sm outline-none transition focus:border-sky-500 focus:ring-4 focus:ring-sky-500/10 dark:border-slate-700 dark:bg-slate-900 dark:text-white"
                  placeholder="0"
                />
              </div>

              <div
                v-if="formData.pricing_type === 'hourly' || formData.pricing_type === 'hybrid'"
                class="rounded-2xl border border-slate-200 bg-slate-50/70 p-5 dark:border-slate-800 dark:bg-slate-950/40"
              >
                <label class="flex items-center text-sm font-semibold text-gray-700 dark:text-gray-200 mb-1.5">
                  Labor Price per Hour (₱/hr) <span class="text-red-500">*</span>
                  <InfoTooltip text="Hourly rate multiplied by labor hours." />
                </label>
                <input
                  v-model="formData.price_hour"
                  type="number"
                  step="0.01"
                  min="0"
                  required
                  class="w-full rounded-xl border border-slate-200 bg-white px-4 py-3.5 shadow-sm outline-none transition focus:border-sky-500 focus:ring-4 focus:ring-sky-500/10 dark:border-slate-700 dark:bg-slate-900 dark:text-white"
                  placeholder="0"
                />
              </div>
            </div>

            <!-- Service Image Upload -->
            <div class="rounded-2xl border border-slate-200 bg-slate-50/70 p-5 dark:border-slate-800 dark:bg-slate-950/40">
              <label class="flex items-center text-sm font-semibold text-gray-700 dark:text-gray-200 mb-1.5">Service Image<InfoTooltip text="Please provide the service image." /></label>
              <button
                type="button"
                @click="triggerFileInput"
                class="w-full rounded-xl border border-dashed border-sky-300 bg-white px-4 py-3.5 font-semibold text-sky-700 shadow-sm outline-none transition hover:border-sky-500 hover:bg-sky-50 focus:ring-4 focus:ring-sky-500/10 dark:border-sky-800 dark:bg-slate-900 dark:text-sky-300"
              >
                <ImagePlus class="mr-2 inline h-4 w-4" />
                {{ imagePreview ? 'Replace Image' : 'Choose Image' }}
              </button>
              <input
                ref="fileInputRef"
                type="file"
                accept="image/*"
                class="hidden"
                @change="handleFileInput"
              />
            </div>

            <div v-if="imagePreview" class="overflow-hidden rounded-2xl border border-slate-200 bg-slate-50 p-3 shadow-inner dark:border-slate-800 dark:bg-slate-950">
              <img :src="imagePreview" :alt="formData.name || 'Service image preview'" class="h-64 w-full rounded-xl object-cover" />
              <p class="mt-2 text-xs text-gray-500">Preview · JPG, PNG, GIF or WebP · maximum 5 MB</p>
            </div>
            <p v-else class="rounded-xl border border-dashed border-slate-300 p-5 text-center text-sm text-gray-500">Add a landscape image to make this service easier to recognize.</p>
            <div v-if="formError" role="alert" class="rounded-xl border border-red-200 bg-red-50 p-3 text-sm text-red-800">{{ formError }}</div>

            <div class="flex justify-end gap-3 pt-4 border-t border-slate-100 mt-8">
              <button
                type="button"
                class="rounded-xl border border-slate-200 bg-white px-5 py-2.5 font-semibold text-slate-700 shadow-sm hover:bg-slate-50 disabled:opacity-50 disabled:cursor-not-allowed transition-colors"
                :disabled="isSubmitting"
                @click="closeDialog"
              >
                Cancel
              </button>
              <button
                type="submit"
                class="inline-flex min-w-40 items-center justify-center gap-2 rounded-xl bg-linear-to-r from-blue-600 to-blue-700 px-6 py-2.5 font-semibold text-white shadow-md shadow-blue-500/20 hover:from-blue-700 hover:to-blue-800 disabled:opacity-50 disabled:cursor-not-allowed transition-all"
                :disabled="isSubmitting"
              >
                <LoaderCircle v-if="isSubmitting" class="h-4 w-4 animate-spin" />
                <span>{{ isSubmitting ? (editingId ? 'Updating...' : 'Adding...') : (editingId ? 'Update' : 'Add') }} Service</span>
              </button>
            </div>
          </form>
        </div>
      </div>
    </template>
  </section>
</template>
