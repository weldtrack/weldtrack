<script setup lang="ts">
import InfoTooltip from '../../../../components/ui/InfoTooltip.vue'
import { computed, onMounted, reactive, ref } from 'vue'
import LocalLoader from '../../../../components/ui/LocalLoader.vue'
import { useCustomerAddressesStore } from '../../../../stores/customerAddresses'
import { type CustomerAddressItem } from '../../../../types/customerAddresses'
import { Plus, MapPin, Edit2, Trash2 } from 'lucide-vue-next'
import { getProvinces, getMunicipalities, getBarangays } from '../../../../data/phLocations'

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
  province: 'Sorsogon',
  municipality: '',
  barangay: '',
  house: '',
  isActive: false,
})

const provinceOptions = computed(() => getProvinces(formData.province))
const municipalityOptions = computed(() => getMunicipalities(formData.province, formData.municipality))
const barangayOptions = computed(() => getBarangays(formData.province, formData.municipality, formData.barangay))

function onProvinceChange() {
  formData.municipality = ''
  formData.barangay = ''
}

function onMunicipalityChange() {
  formData.barangay = ''
}

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
  formData.province = 'Sorsogon'
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
  <section class="space-y-6 relative">
    <LocalLoader v-if="isLoading" />
    
    <!-- List View -->
    <template v-if="!isDialogOpen">
      <!-- Header -->
      <div class="flex flex-col gap-4 sm:flex-row sm:items-center sm:justify-between">
        <div class="flex items-start gap-3">
          <div class="flex h-12 w-12 items-center justify-center">
            <MapPin class="dashboard-view-icon h-6 w-6 text-sky-600 dark:text-sky-400" />
          </div>
          <div>
            <h3 class="text-2xl font-semibold text-slate-900 dark:text-slate-100">My Addresses</h3>
            <p class="text-sm text-slate-600 dark:text-slate-400">Manage saved locations and active delivery addresses</p>
          </div>
        </div>

        <button
          type="button"
          class="inline-flex items-center justify-center gap-2 rounded-xl bg-sky-600 px-4 py-2.5 text-sm font-semibold text-white shadow-xs transition-colors hover:bg-sky-700 dark:bg-sky-600 dark:hover:bg-sky-500 shrink-0"
          @click="openCreateDialog"
        >
          <Plus class="h-4 w-4" />
          <span>Add Address</span>
        </button>
      </div>

      <!-- Active Address Summary Banner -->
      <div v-if="activeAddress" class="rounded-2xl border border-slate-200 bg-slate-50/80 p-6 shadow-xs dark:border-slate-800 dark:bg-slate-900">
        <div class="flex items-center justify-between gap-3 border-b border-slate-200 pb-3 dark:border-slate-800">
          <div class="flex items-center gap-2">
            <span class="relative flex h-2.5 w-2.5">
              <span class="absolute inline-flex h-full w-full animate-ping rounded-full bg-emerald-400 opacity-75"></span>
              <span class="relative inline-flex h-2.5 w-2.5 rounded-full bg-emerald-600 dark:bg-emerald-400"></span>
            </span>
            <span class="text-xs font-bold uppercase tracking-wider text-slate-700 dark:text-slate-300">Default Active Delivery Location</span>
          </div>
          <span class="rounded-full bg-emerald-50 border border-emerald-200 px-3 py-1 text-xs font-bold text-emerald-700 dark:bg-emerald-950/60 dark:border-emerald-800 dark:text-emerald-300">
            Selected for Bookings
          </span>
        </div>

        <div class="mt-4 min-w-0">
          <h4 class="text-lg font-extrabold text-slate-900 dark:text-slate-100 truncate" :title="activeAddress.label">{{ activeAddress.label }}</h4>
          <p class="mt-1 text-sm font-medium text-slate-700 dark:text-slate-300 break-words leading-relaxed">
            {{ [activeAddress.house, activeAddress.barangay, activeAddress.municipality, activeAddress.province, activeAddress.region, activeAddress.country].filter(Boolean).join(', ') }}
          </p>
        </div>
      </div>

      <!-- Empty State -->
      <div v-if="!addresses.length" class="rounded-2xl border border-slate-200 bg-white p-12 text-center dark:border-slate-800 dark:bg-slate-900">
        <MapPin class="mx-auto h-10 w-10 text-slate-400" />
        <h4 class="mt-3 text-base font-bold text-slate-900 dark:text-slate-100">No saved addresses yet</h4>
        <p class="mt-1 text-sm text-slate-500 dark:text-slate-400">Add an address to automatically pre-fill your project booking requests.</p>
        <button
          type="button"
          class="mt-5 inline-flex items-center justify-center gap-2 rounded-xl bg-sky-600 px-4 py-2.5 text-sm font-semibold text-white shadow-xs hover:bg-sky-700 dark:bg-sky-600 dark:hover:bg-sky-500"
          @click="openCreateDialog"
        >
          <Plus class="h-4 w-4" />
          <span>Add Address</span>
        </button>
      </div>

      <!-- Full-width address list -->
      <div v-else class="grid w-full grid-cols-1 gap-4">
        <article
          v-for="address in addresses"
          :key="address.id"
          class="min-w-0 overflow-hidden rounded-2xl border border-slate-200 bg-white shadow-sm transition duration-200 hover:border-slate-300 hover:shadow-md dark:border-slate-800 dark:bg-slate-900 dark:hover:border-slate-700"
        >
          <div class="p-4 sm:p-6">
            <div class="flex flex-col gap-4 border-b border-slate-100 pb-5 dark:border-slate-800 sm:flex-row sm:items-start sm:justify-between">
              <div class="flex min-w-0 items-start gap-3 sm:gap-4">
                <div class="flex h-11 w-11 shrink-0 items-center justify-center rounded-xl bg-slate-100 text-slate-600 ring-1 ring-inset ring-slate-200 dark:bg-slate-800 dark:text-slate-300 dark:ring-slate-700">
                  <MapPin class="h-5 w-5" />
                </div>
                <div class="min-w-0">
                  <p class="text-xs font-medium text-slate-400">Saved location</p>
                  <h4 class="mt-0.5 break-words text-lg font-semibold text-slate-900 dark:text-slate-100">{{ address.label }}</h4>
                  <p class="mt-1 break-words text-sm leading-relaxed text-slate-500 dark:text-slate-400">
                    {{ [address.house, address.barangay, address.municipality, address.province].filter(Boolean).join(', ') }}
                  </p>
                </div>
              </div>
              <span
                v-if="address.isActive"
                class="w-fit shrink-0 rounded-full bg-emerald-50 px-3 py-1 text-xs font-semibold text-emerald-700 ring-1 ring-inset ring-emerald-600/20 dark:bg-emerald-950/60 dark:text-emerald-300 dark:ring-emerald-800"
              >
                Active address
              </span>
              <span v-else class="w-fit shrink-0 rounded-full bg-slate-100 px-3 py-1 text-xs font-semibold text-slate-500 dark:bg-slate-800 dark:text-slate-400">
                Saved
              </span>
            </div>

            <dl class="mt-5 grid grid-cols-1 gap-3 sm:grid-cols-2 lg:grid-cols-4">
                <div v-if="address.barangay" class="min-w-0">
                  <dt class="text-xs text-slate-400">Barangay</dt>
                  <dd class="mt-1 break-words text-sm font-medium text-slate-700 dark:text-slate-300">{{ address.barangay }}</dd>
                </div>
                <div v-if="address.municipality" class="min-w-0">
                  <dt class="text-xs text-slate-400">Municipality / City</dt>
                  <dd class="mt-1 break-words text-sm font-medium text-slate-700 dark:text-slate-300">{{ address.municipality }}</dd>
                </div>
                <div v-if="address.province" class="min-w-0">
                  <dt class="text-xs text-slate-400">Province</dt>
                  <dd class="mt-1 break-words text-sm font-medium text-slate-700 dark:text-slate-300">{{ address.province }}</dd>
                </div>
                <div v-if="address.region" class="min-w-0">
                  <dt class="text-xs text-slate-400">Region</dt>
                  <dd class="mt-1 break-words text-sm font-medium text-slate-700 dark:text-slate-300">{{ address.region }}</dd>
                </div>
            </dl>
          </div>

          <!-- Actions Bar -->
          <div class="flex flex-col gap-3 border-t border-slate-200 bg-slate-50 px-4 py-4 dark:border-slate-800 dark:bg-slate-800/60 sm:flex-row sm:items-center sm:justify-between sm:px-6">
            <button
              v-if="!address.isActive"
              type="button"
              class="inline-flex w-full items-center justify-center rounded-xl border border-slate-200 bg-white px-4 py-2 text-sm font-semibold text-slate-700 transition hover:bg-slate-100 dark:border-slate-700 dark:bg-slate-900 dark:text-slate-200 dark:hover:bg-slate-700 sm:w-auto"
              @click="activateAddress(address.id)"
            >
              Set as Active
            </button>
            <span v-else class="text-xs font-medium text-slate-500 dark:text-slate-400">Used automatically for new bookings</span>

            <div class="grid grid-cols-2 gap-2 sm:flex">
              <button
                type="button"
                class="inline-flex items-center justify-center gap-2 rounded-xl px-3 py-2 text-sm font-medium text-slate-600 transition hover:bg-slate-200/70 hover:text-slate-900 dark:text-slate-300 dark:hover:bg-slate-700 dark:hover:text-white"
                @click="openEditDialog(address)"
                title="Edit address"
              >
                <Edit2 class="h-4 w-4" />
                <span>Edit</span>
              </button>
              <button
                type="button"
                class="inline-flex items-center justify-center gap-2 rounded-xl px-3 py-2 text-sm font-medium text-rose-600 transition hover:bg-rose-100 dark:text-rose-400 dark:hover:bg-rose-950/60"
                @click="removeAddress(address.id)"
                title="Delete address"
              >
                <Trash2 class="h-4 w-4" />
                <span>Delete</span>
              </button>
            </div>
          </div>
        </article>
      </div>
    </template>

    <!-- Inline Form View -->
    <template v-else>
      <div class="rounded-2xl border border-slate-200 bg-white shadow-xs dark:border-slate-800 dark:bg-slate-900 max-w-3xl mx-auto">
        <div class="border-b border-slate-100 px-6 py-5 flex items-center justify-between dark:border-slate-800">
          <div>
            <h3 class="text-xl font-bold text-slate-900 dark:text-slate-100">
              {{ editingAddressId ? 'Edit Address' : 'Add New Address' }}
            </h3>
            <p class="text-xs text-slate-500 dark:text-slate-400 mt-0.5">Enter your delivery location details.</p>
          </div>
          <button 
            @click="closeDialog" 
            class="text-sm font-semibold text-slate-500 hover:text-slate-800 dark:text-slate-400 dark:hover:text-slate-200 transition-colors"
          >
            Cancel
          </button>
        </div>

        <div class="p-6">
          <form class="space-y-5" @submit.prevent="submitAddress">
            <div class="grid gap-4 sm:grid-cols-2">
              <div>
                <label class="flex items-center text-sm font-semibold text-slate-700 dark:text-slate-300 mb-1.5" for="address-label">Label <span class="text-rose-500">*</span><InfoTooltip text="Please provide the label (e.g. Home, Office)." /></label>
                <input id="address-label" v-model="formData.label" type="text" required placeholder="e.g., Home, Office, Workshop" class="w-full rounded-xl border border-slate-200 bg-white px-4 py-2.5 text-sm text-slate-900 outline-none transition focus:border-sky-500 dark:border-slate-800 dark:bg-slate-950 dark:text-slate-100" />
              </div>
              <div>
                <label class="flex items-center text-sm font-semibold text-slate-700 dark:text-slate-300 mb-1.5" for="address-province">Province <span class="text-rose-500">*</span><InfoTooltip text="Select your province." /></label>
                <select id="address-province" v-model="formData.province" required @change="onProvinceChange" class="w-full rounded-xl border border-slate-200 bg-white px-4 py-2.5 text-sm text-slate-900 outline-none transition focus:border-sky-500 dark:border-slate-800 dark:bg-slate-950 dark:text-slate-100">
                  <option value="">Select Province</option>
                  <option v-for="prov in provinceOptions" :key="prov" :value="prov">{{ prov }}</option>
                </select>
              </div>
              <div>
                <label class="flex items-center text-sm font-semibold text-slate-700 dark:text-slate-300 mb-1.5" for="address-municipality">Municipality / City <span class="text-rose-500">*</span><InfoTooltip text="Select your municipality or city." /></label>
                <select id="address-municipality" v-model="formData.municipality" required :disabled="!formData.province" @change="onMunicipalityChange" class="w-full rounded-xl border border-slate-200 bg-white px-4 py-2.5 text-sm text-slate-900 outline-none transition focus:border-sky-500 disabled:opacity-50 dark:border-slate-800 dark:bg-slate-950 dark:text-slate-100">
                  <option value="">Select Municipality / City</option>
                  <option v-for="mun in municipalityOptions" :key="mun" :value="mun">{{ mun }}</option>
                </select>
              </div>
              <div>
                <label class="flex items-center text-sm font-semibold text-slate-700 dark:text-slate-300 mb-1.5" for="address-barangay">Barangay <span class="text-rose-500">*</span><InfoTooltip text="Select your barangay." /></label>
                <select id="address-barangay" v-model="formData.barangay" required :disabled="!formData.municipality" class="w-full rounded-xl border border-slate-200 bg-white px-4 py-2.5 text-sm text-slate-900 outline-none transition focus:border-sky-500 disabled:opacity-50 dark:border-slate-800 dark:bg-slate-950 dark:text-slate-100">
                  <option value="">Select Barangay</option>
                  <option v-for="brgy in barangayOptions" :key="brgy" :value="brgy">{{ brgy }}</option>
                </select>
              </div>
              <div class="sm:col-span-2">
                <label class="flex items-center text-sm font-semibold text-slate-700 dark:text-slate-300 mb-1.5" for="address-house">House / Street / Purok <span class="text-rose-500">*</span><InfoTooltip text="Please provide house, street, or purok." /></label>
                <input id="address-house" v-model="formData.house" type="text" required placeholder="e.g., Purok 2, 123 Main Street" class="w-full rounded-xl border border-slate-200 bg-white px-4 py-2.5 text-sm text-slate-900 outline-none transition focus:border-sky-500 dark:border-slate-800 dark:bg-slate-950 dark:text-slate-100" />
              </div>
              <div>
                <label class="flex items-center text-sm font-semibold text-slate-700 dark:text-slate-300 mb-1.5" for="address-country">Country<InfoTooltip text="Default country location." /></label>
                <input id="address-country" v-model="formData.country" type="text" required class="w-full rounded-xl border border-slate-200 bg-slate-50 px-4 py-2.5 text-sm text-slate-500 outline-none cursor-not-allowed dark:border-slate-800 dark:bg-slate-950 dark:text-slate-400" disabled />
              </div>
              <div>
                <label class="flex items-center text-sm font-semibold text-slate-700 dark:text-slate-300 mb-1.5" for="address-region">Region<InfoTooltip text="Default region location." /></label>
                <input id="address-region" v-model="formData.region" type="text" required class="w-full rounded-xl border border-slate-200 bg-slate-50 px-4 py-2.5 text-sm text-slate-500 outline-none cursor-not-allowed dark:border-slate-800 dark:bg-slate-950 dark:text-slate-400" disabled />
              </div>
            </div>

            <label class="flex items-center gap-3 rounded-xl border border-slate-200 bg-slate-50 p-4 text-xs font-semibold text-slate-800 dark:border-slate-800 dark:bg-slate-950 dark:text-slate-200 cursor-pointer">
              <input v-model="formData.isActive" type="checkbox" class="h-4 w-4 rounded border-slate-300 text-sky-600 focus:ring-sky-500 dark:border-slate-700 dark:bg-slate-900" />
              <span>Set as active delivery address for future project bookings</span>
            </label>

            <div class="flex justify-end gap-3 pt-4 border-t border-slate-100 dark:border-slate-800">
              <button type="button" class="rounded-xl border border-slate-200 bg-white px-5 py-2.5 text-sm font-semibold text-slate-700 shadow-xs hover:bg-slate-50 transition-colors dark:border-slate-700 dark:bg-slate-800 dark:text-slate-300 dark:hover:bg-slate-700" @click="closeDialog">
                Cancel
              </button>
              <button type="submit" :disabled="isSubmitting" class="rounded-xl bg-sky-600 px-6 py-2.5 text-sm font-semibold text-white shadow-xs hover:bg-sky-700 disabled:opacity-50 transition-all dark:bg-sky-600 dark:hover:bg-sky-500">
                {{ isSubmitting ? 'Saving...' : editingAddressId ? 'Save Changes' : 'Save Address' }}
              </button>
            </div>
          </form>
        </div>
      </div>
    </template>
  </section>
</template>
