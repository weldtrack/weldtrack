<script setup lang="ts">
import { computed, onMounted, reactive, ref } from 'vue'
import LocalLoader from '../../../../components/ui/LocalLoader.vue'
import ModalShell from '../../../../components/ui/ModalShell.vue'
import { useCustomerAddressesStore } from '../../../../stores/customerAddresses'
import { type CustomerAddressItem } from '../../../../types/customerAddresses'
import { Plus, MapPin, Check, Edit2, Trash2, Home, Building2, Map, Globe } from 'lucide-vue-next'

const addressesStore = useCustomerAddressesStore()

const addresses = computed(() => addressesStore.addresses)
const activeAddress = computed(() => addressesStore.activeAddress)
const isDialogOpen = ref(false)
const isSubmitting = ref(false)
const editingAddressId = ref<string | null>(null)

const formData = reactive({
  label: '',
  country: 'PH',
  region: 'Bicol Region (Region V)',
  province: '',
  municipality: '',
  barangay: '',
  house: '',
  isActive: false,
})

const isLoading = ref(true)

onMounted(async () => {
  isLoading.value = true
  try {
    await addressesStore.fetchMyAddresses()
  } finally {
    isLoading.value = false
  }
})

function resetForm() {
  editingAddressId.value = null
  formData.label = ''
  formData.country = 'PH'
  formData.region = 'Bicol Region (Region V)'
  formData.province = ''
  formData.municipality = ''
  formData.barangay = ''
  formData.house = ''
  formData.isActive = !addresses.value.length
}

function openCreateDialog() {
  resetForm()
  isDialogOpen.value = true
}

function openEditDialog(address: CustomerAddressItem) {
  editingAddressId.value = address.id
  formData.label = address.label
  formData.country = address.country
  formData.region = address.region
  formData.province = address.province
  formData.municipality = address.municipality
  formData.barangay = address.barangay
  formData.house = address.house
  formData.isActive = address.isActive
  isDialogOpen.value = true
}

function closeDialog() {
  isDialogOpen.value = false
  resetForm()
}

async function submitAddress() {
  isSubmitting.value = true
  try {
    const payload = {
      label: formData.label,
      country: formData.country,
      region: formData.region,
      province: formData.province,
      municipality: formData.municipality,
      barangay: formData.barangay,
      house: formData.house,
      isActive: formData.isActive,
    }

    if (editingAddressId.value) {
      await addressesStore.updateAddress(editingAddressId.value, payload)
    } else {
      await addressesStore.createAddress(payload)
    }

    closeDialog()
  } finally {
    isSubmitting.value = false
  }
}

async function activateAddress(id: string) {
  await addressesStore.activateAddress(id)
}

async function removeAddress(id: string) {
  await addressesStore.deleteAddress(id)
}
</script>

<template>
  <section class="space-y-8 relative">
    <LocalLoader v-if="isLoading" />
    <div class="flex flex-col gap-4 lg:flex-row lg:items-center lg:justify-between">
      <div class="flex items-start gap-3">
        <div class="flex h-12 w-12 items-center justify-center rounded-xl bg-linear-to-br from-sky-100 to-sky-50 ring-1 ring-sky-200">
          <MapPin class="dashboard-view-icon h-6 w-6 text-sky-600 dark:text-sky-400" />
        </div>
        <div>
          <h3 class="text-2xl font-bold text-gray-900">My Addresses</h3>
          <p class="mt-1 text-sm text-gray-500">Manage and set your delivery locations</p>
        </div>
      </div>

      <button
        type="button"
        class="inline-flex items-center justify-center gap-2 rounded-lg bg-linear-to-r from-sky-600 to-sky-700 px-5 py-3 font-semibold text-white shadow-md shadow-sky-500/20 transition-all hover:shadow-lg hover:shadow-sky-500/30 active:scale-95"
        @click="openCreateDialog"
      >
        <Plus class="h-5 w-5" />
        Add Address
      </button>
    </div>

    <div v-if="activeAddress" class="rounded-2xl border border-sky-200/50 bg-linear-to-br from-sky-50 to-sky-50/50 p-6 shadow-sm">
      <div class="flex items-start gap-3">
        <div class="flex h-10 w-10 items-center justify-center rounded-lg bg-sky-100 ring-1 ring-sky-200">
          <Check class="dashboard-view-icon h-5 w-5 text-sky-600 dark:text-sky-400" />
        </div>
        <div class="flex-1">
          <p class="text-xs font-bold uppercase tracking-widest text-sky-600">✓ Active Address</p>
          <h4 class="mt-2 text-lg font-bold uppercase text-sky-950">{{ activeAddress.label }}</h4>
          <div class="mt-3 space-y-2">
            <div v-if="activeAddress.house" class="flex items-center gap-2 text-sm text-sky-800">
              <Home class="h-3.5 w-3.5 opacity-70" />
              <span>{{ activeAddress.house }}</span>
            </div>
            <div v-if="activeAddress.barangay" class="flex items-center gap-2 text-sm text-sky-800">
              <Building2 class="h-3.5 w-3.5 opacity-70" />
              <span>{{ activeAddress.barangay }}</span>
            </div>
            <div v-if="activeAddress.municipality" class="flex items-center gap-2 text-sm text-sky-800">
              <Map class="h-3.5 w-3.5 opacity-70" />
              <span>{{ activeAddress.municipality }}</span>
            </div>
            <div v-if="activeAddress.province" class="flex items-center gap-2 text-sm text-sky-800">
              <Map class="h-3.5 w-3.5 opacity-70" />
              <span>{{ activeAddress.province }}</span>
            </div>
            <div v-if="activeAddress.region" class="flex items-center gap-2 text-sm text-sky-800">
              <Globe class="h-3.5 w-3.5 opacity-70" />
              <span>{{ activeAddress.region }}</span>
            </div>
            <div v-if="activeAddress.country" class="flex items-center gap-2 text-sm text-sky-800">
              <Globe class="h-3.5 w-3.5 opacity-70" />
              <span>{{ activeAddress.country }}</span>
            </div>
          </div>
        </div>
      </div>
    </div>

    <div v-if="!addresses.length" class="rounded-2xl border-2 border-dashed border-slate-300 bg-linear-to-br from-sky-50 to-sky-50/50 p-12 text-center">
      <div class="mx-auto flex h-16 w-16 items-center justify-center rounded-full bg-sky-100">
        <MapPin class="dashboard-view-icon h-8 w-8 text-sky-600 dark:text-sky-400" />
      </div>
      <p class="mt-4 text-base font-semibold text-slate-900">No saved addresses yet</p>
      <p class="mt-2 text-sm text-slate-600">Add your first address so new bookings can use it automatically.</p>
      <button
        type="button"
        class="mt-5 inline-flex items-center justify-center gap-2 rounded-lg bg-blue-600 px-4 py-2 text-sm font-semibold text-white transition-colors hover:bg-blue-700"
        @click="openCreateDialog"
      >
        <Plus class="h-4 w-4" />
        Add Your First Address
      </button>
    </div>

    <div v-else class="grid gap-5 md:grid-cols-2 lg:grid-cols-3">
      <article
        v-for="address in addresses"
        :key="address.id"
        class="group relative overflow-hidden rounded-2xl border bg-white p-6 shadow-sm transition-all duration-300 hover:shadow-md"
        :class="address.isActive ? 'border-sky-300 ring-1 ring-sky-300' : 'border-slate-200 hover:border-slate-300'"
      >
        <div v-if="address.isActive" class="absolute left-0 top-0 h-full w-1.5 bg-sky-500"></div>

        <div class="flex items-start gap-4">
          <div class="shrink-0">
            <div :class="['h-12 w-12 flex items-center justify-center rounded-xl transition-colors', address.isActive ? 'bg-sky-100 ring-1 ring-sky-200' : 'bg-slate-100 ring-1 ring-slate-200']">
              <MapPin :class="['h-6 w-6', address.isActive ? 'text-sky-600 dark:text-sky-400' : 'text-slate-400 dark:text-slate-400']" />
            </div>
          </div>

          <div class="flex-1 min-w-0">
            <div class="flex items-center justify-between gap-2">
              <h4 class="truncate text-base font-bold uppercase text-slate-900">{{ address.label }}</h4>
              <span
                v-if="address.isActive"
                class="inline-flex items-center gap-1 rounded-full bg-sky-100 px-2 py-0.5 text-[10px] font-bold uppercase tracking-wider text-sky-700 ring-1 ring-inset ring-sky-200"
              >
                <Check class="h-3 w-3" />
                Active
              </span>
            </div>
            <div class="mt-3 space-y-1.5">
              <div v-if="address.house" class="flex items-center gap-2 text-xs text-slate-600">
                <Home class="h-3 w-3 opacity-60" />
                <span class="truncate">{{ address.house }}</span>
              </div>
              <div v-if="address.barangay" class="flex items-center gap-2 text-xs text-slate-600">
                <Building2 class="h-3 w-3 opacity-60" />
                <span class="truncate">{{ address.barangay }}</span>
              </div>
              <div v-if="address.municipality" class="flex items-center gap-2 text-xs text-slate-600">
                <Map class="h-3 w-3 opacity-60" />
                <span class="truncate">{{ address.municipality }}</span>
              </div>
              <div v-if="address.province" class="flex items-center gap-2 text-xs text-slate-600">
                <Map class="h-3 w-3 opacity-60" />
                <span class="truncate">{{ address.province }}</span>
              </div>
              <div v-if="address.region" class="flex items-center gap-2 text-xs text-slate-600">
                <Globe class="h-3 w-3 opacity-60" />
                <span class="truncate">{{ address.region }}</span>
              </div>
              <div v-if="address.country" class="flex items-center gap-2 text-xs text-slate-600">
                <Globe class="h-3 w-3 opacity-60" />
                <span class="truncate">{{ address.country }}</span>
              </div>
            </div>
          </div>
        </div>

        <div class="mt-6 flex items-center gap-2 border-t border-slate-100 pt-4">
          <button
            v-if="!address.isActive"
            type="button"
            class="flex-1 inline-flex items-center justify-center gap-2 rounded-lg bg-sky-600 px-3 py-2 text-sm font-semibold text-white transition-all hover:bg-sky-700 active:scale-95 shadow-sm shadow-sky-200"
            @click="activateAddress(address.id)"
            title="Set as active address"
          >
            <Check class="h-4 w-4" />
            Set Active
          </button>
          <button
            type="button"
            class="inline-flex items-center justify-center rounded-lg border border-slate-200 px-3 py-2 text-sm font-semibold text-slate-700 transition-all hover:bg-slate-50 active:scale-95"
            @click="openEditDialog(address)"
            title="Edit this address"
          >
            <Edit2 class="h-4 w-4" />
          </button>
          <button
            type="button"
            class="inline-flex items-center justify-center rounded-lg border border-red-100 px-3 py-2 text-sm font-semibold text-red-600 transition-all hover:bg-red-50 active:scale-95"
            @click="removeAddress(address.id)"
            title="Delete this address"
          >
            <Trash2 class="h-4 w-4" />
          </button>
        </div>
      </article>
    </div>

    <ModalShell
      :show="isDialogOpen"
      :title="editingAddressId ? 'Edit Address' : 'Add Address'"
      subtitle="Customer address book"
      tone="green"
      size="lg"
      @close="closeDialog"
    >
      <form class="space-y-5" @submit.prevent="submitAddress">
        <div class="grid gap-4 sm:grid-cols-2">
          <div>
            <label class="block text-sm font-semibold text-gray-700" for="address-label">Label *</label>
            <input id="address-label" v-model="formData.label" type="text" required placeholder="e.g., Home, Shop, Office" class="mt-2 w-full rounded-xl border border-slate-200 bg-white px-4 py-3 text-sm shadow-sm transition focus:border-blue-500 focus:ring-2 focus:ring-blue-200" />
          </div>
          <div>
            <label class="block text-sm font-semibold text-gray-700" for="address-house">House / Street *</label>
            <input id="address-house" v-model="formData.house" type="text" required placeholder="e.g., 123 Main St" class="mt-2 w-full rounded-xl border border-slate-200 bg-white px-4 py-3 text-sm shadow-sm transition focus:border-blue-500 focus:ring-2 focus:ring-blue-200" />
          </div>
          <div>
            <label class="block text-sm font-semibold text-gray-700" for="address-barangay">Barangay *</label>
            <input id="address-barangay" v-model="formData.barangay" type="text" required class="mt-2 w-full rounded-xl border border-slate-200 bg-white px-4 py-3 text-sm shadow-sm transition focus:border-blue-500 focus:ring-2 focus:ring-blue-200" />
          </div>
          <div>
            <label class="block text-sm font-semibold text-gray-700" for="address-municipality">Municipality *</label>
            <input id="address-municipality" v-model="formData.municipality" type="text" required class="mt-2 w-full rounded-xl border border-slate-200 bg-white px-4 py-3 text-sm shadow-sm transition focus:border-blue-500 focus:ring-2 focus:ring-blue-200" />
          </div>
          <div>
            <label class="block text-sm font-semibold text-gray-700" for="address-province">Province *</label>
            <input id="address-province" v-model="formData.province" type="text" required class="mt-2 w-full rounded-xl border border-slate-200 bg-white px-4 py-3 text-sm shadow-sm transition focus:border-blue-500 focus:ring-2 focus:ring-blue-200" />
          </div>
          <div>
            <label class="block text-sm font-semibold text-gray-700" for="address-country">Country *</label>
            <input id="address-country" v-model="formData.country" type="text" required class="mt-2 w-full rounded-xl border border-slate-200 bg-slate-100 px-4 py-3 text-sm text-slate-600 shadow-sm" disabled />
          </div>
          <div class="sm:col-span-2">
            <label class="block text-sm font-semibold text-gray-700" for="address-region">Region *</label>
            <input id="address-region" v-model="formData.region" type="text" required class="mt-2 w-full rounded-xl border border-slate-200 bg-slate-100 px-4 py-3 text-sm text-slate-600 shadow-sm" disabled />
          </div>
        </div>

        <label class="flex items-center gap-3 rounded-xl border border-blue-200 bg-blue-50 px-4 py-3 text-sm text-blue-900 transition cursor-pointer hover:bg-blue-100">
          <input v-model="formData.isActive" type="checkbox" class="h-4 w-4 rounded border-blue-300 text-blue-600" />
          <span class="font-medium">Set this as the active address for new bookings</span>
        </label>

        <div class="flex justify-end gap-3 border-t border-slate-100 pt-5">
          <button type="button" class="rounded-lg border border-slate-300 px-4 py-2.5 text-sm font-semibold text-slate-700 transition-all hover:bg-slate-50 active:scale-95" @click="closeDialog">
            Cancel
          </button>
          <button type="submit" :disabled="isSubmitting" class="rounded-lg bg-linear-to-r from-blue-600 to-blue-700 px-4 py-2.5 text-sm font-semibold text-white shadow-md shadow-blue-500/20 transition-all hover:shadow-lg active:scale-95 disabled:cursor-not-allowed disabled:opacity-60">
            {{ isSubmitting ? 'Saving...' : editingAddressId ? 'Save Changes' : 'Save Address' }}
          </button>
        </div>
      </form>
    </ModalShell>
  </section>
</template>
