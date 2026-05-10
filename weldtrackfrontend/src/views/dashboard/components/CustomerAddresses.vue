<script setup lang="ts">
import { computed, onMounted, reactive, ref } from 'vue'
import ModalShell from '../../../components/ui/ModalShell.vue'
import { useCustomerAddressesStore, type CustomerAddressItem } from '../../../stores/customerAddresses'

const addressesStore = useCustomerAddressesStore()

const addresses = computed(() => addressesStore.addresses)
const activeAddress = computed(() => addressesStore.activeAddress)
const isDialogOpen = ref(false)
const isSubmitting = ref(false)
const editingAddressId = ref<number | null>(null)

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

onMounted(() => {
  addressesStore.fetchMyAddresses()
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

async function activateAddress(id: number) {
  await addressesStore.activateAddress(id)
}

async function removeAddress(id: number) {
  await addressesStore.deleteAddress(id)
}

function formatAddress(address: CustomerAddressItem) {
  return [address.house, address.barangay, address.municipality, address.province, address.region, address.country]
    .filter(Boolean)
    .join(', ')
}
</script>

<template>
  <section class="space-y-6">
    <div class="flex flex-col gap-4 lg:flex-row lg:items-center lg:justify-between">
      <div>
        <h3 class="mb-1 text-2xl font-semibold text-gray-900">My Addresses</h3>
        <p class="text-sm text-gray-600">Save multiple addresses and choose which one is active for new bookings.</p>
      </div>

      <button
        type="button"
        class="inline-flex items-center justify-center rounded-lg bg-blue-600 px-4 py-3 font-semibold text-white transition-colors hover:bg-blue-700"
        @click="openCreateDialog"
      >
        Add Address
      </button>
    </div>

    <div v-if="activeAddress" class="rounded-xl border border-emerald-200 bg-emerald-50 p-5">
      <p class="text-xs font-semibold uppercase tracking-[0.2em] text-emerald-700">Active Address</p>
      <h4 class="mt-2 text-lg font-semibold text-emerald-950">{{ activeAddress.label }}</h4>
      <p class="mt-1 text-sm text-emerald-900">{{ formatAddress(activeAddress) }}</p>
    </div>

    <div v-if="!addresses.length" class="rounded-xl border border-dashed border-slate-300 bg-white p-10 text-center">
      <p class="text-base font-medium text-slate-900">No saved addresses yet</p>
      <p class="mt-2 text-sm text-slate-600">Add your first address so new bookings can use it automatically.</p>
    </div>

    <div v-else class="grid gap-4 md:grid-cols-2">
      <article
        v-for="address in addresses"
        :key="address.id"
        class="rounded-xl border bg-white p-5 shadow-sm"
        :class="address.isActive ? 'border-emerald-200 ring-1 ring-emerald-200' : 'border-slate-200'"
      >
        <div class="flex items-start justify-between gap-4">
          <div>
            <div class="flex items-center gap-2">
              <h4 class="text-lg font-semibold text-slate-900">{{ address.label }}</h4>
              <span
                v-if="address.isActive"
                class="rounded-full bg-emerald-100 px-2.5 py-1 text-xs font-semibold text-emerald-800"
              >
                Active
              </span>
            </div>
            <p class="mt-2 text-sm leading-6 text-slate-600">{{ formatAddress(address) }}</p>
          </div>
        </div>

        <div class="mt-5 flex flex-wrap gap-3">
          <button
            v-if="!address.isActive"
            type="button"
            class="rounded-lg bg-emerald-600 px-4 py-2 text-sm font-semibold text-white transition-colors hover:bg-emerald-700"
            @click="activateAddress(address.id)"
          >
            Set Active
          </button>
          <button
            type="button"
            class="rounded-lg border border-slate-300 px-4 py-2 text-sm font-semibold text-slate-700 transition-colors hover:bg-slate-100"
            @click="openEditDialog(address)"
          >
            Edit
          </button>
          <button
            type="button"
            class="rounded-lg border border-red-200 px-4 py-2 text-sm font-semibold text-red-700 transition-colors hover:bg-red-50"
            @click="removeAddress(address.id)"
          >
            Delete
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
      <form class="space-y-4" @submit.prevent="submitAddress">
        <div class="grid gap-4 sm:grid-cols-2">
          <div>
            <label class="block text-sm font-medium text-gray-700" for="address-label">Label</label>
            <input id="address-label" v-model="formData.label" type="text" required class="mt-1 w-full rounded-xl border border-slate-200 bg-slate-50 px-4 py-3 shadow-sm" placeholder="Home, Shop, Office" />
          </div>
          <div>
            <label class="block text-sm font-medium text-gray-700" for="address-house">House / Street</label>
            <input id="address-house" v-model="formData.house" type="text" required class="mt-1 w-full rounded-xl border border-slate-200 bg-slate-50 px-4 py-3 shadow-sm" />
          </div>
          <div>
            <label class="block text-sm font-medium text-gray-700" for="address-barangay">Barangay</label>
            <input id="address-barangay" v-model="formData.barangay" type="text" required class="mt-1 w-full rounded-xl border border-slate-200 bg-slate-50 px-4 py-3 shadow-sm" />
          </div>
          <div>
            <label class="block text-sm font-medium text-gray-700" for="address-municipality">Municipality</label>
            <input id="address-municipality" v-model="formData.municipality" type="text" required class="mt-1 w-full rounded-xl border border-slate-200 bg-slate-50 px-4 py-3 shadow-sm" />
          </div>
          <div>
            <label class="block text-sm font-medium text-gray-700" for="address-province">Province</label>
            <input id="address-province" v-model="formData.province" type="text" required class="mt-1 w-full rounded-xl border border-slate-200 bg-slate-50 px-4 py-3 shadow-sm" />
          </div>
          <div>
            <label class="block text-sm font-medium text-gray-700" for="address-country">Country</label>
            <input id="address-country" v-model="formData.country" type="text" required class="mt-1 w-full rounded-xl border border-slate-200 bg-slate-100 px-4 py-3 text-slate-600 shadow-sm" />
          </div>
          <div class="sm:col-span-2">
            <label class="block text-sm font-medium text-gray-700" for="address-region">Region</label>
            <input id="address-region" v-model="formData.region" type="text" required class="mt-1 w-full rounded-xl border border-slate-200 bg-slate-100 px-4 py-3 text-slate-600 shadow-sm" />
          </div>
        </div>

        <label class="flex items-center gap-3 rounded-xl border border-slate-200 bg-slate-50 px-4 py-3 text-sm text-slate-700">
          <input v-model="formData.isActive" type="checkbox" class="h-4 w-4 rounded border-slate-300 text-blue-600" />
          Set this as the active address for new bookings
        </label>

        <div class="flex justify-end gap-3 pt-2">
          <button type="button" class="rounded-lg border border-slate-300 px-4 py-2 text-sm font-semibold text-slate-700 hover:bg-slate-100" @click="closeDialog">
            Cancel
          </button>
          <button type="submit" :disabled="isSubmitting" class="rounded-lg bg-blue-600 px-4 py-2 text-sm font-semibold text-white hover:bg-blue-700 disabled:cursor-not-allowed disabled:opacity-60">
            {{ isSubmitting ? 'Saving...' : editingAddressId ? 'Save Changes' : 'Save Address' }}
          </button>
        </div>
      </form>
    </ModalShell>
  </section>
</template>
