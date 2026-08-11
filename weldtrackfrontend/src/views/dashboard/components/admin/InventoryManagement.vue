<script setup lang="ts">
import { computed, onMounted, reactive, ref } from 'vue'
import { Archive, Info, LoaderCircle, PackagePlus } from 'lucide-vue-next'
import { useInventoryStore } from '../../../../stores/inventory'
import { type InventoryItem } from '../../../../types/inventory'
import { useModalStore } from '../../../../stores/modal'
import ModalShell from '../../../../components/ui/ModalShell.vue'
import LocalLoader from '../../../../components/ui/LocalLoader.vue'

const store = useInventoryStore()
const modalStore = useModalStore()

const isDialogOpen = ref(false)
const isStockModalOpen = ref(false)
const editingItem = ref<InventoryItem | null>(null)
const selectedItems = ref<Set<string>>(new Set())
const selectedStockAdjustment = ref<number | null>(null)
const searchTerm = ref('')
const isSubmitting = ref(false)
const isStockSubmitting = ref(false)
const formError = ref('')
const stockError = ref('')
const formData = reactive({
  name: '',
  unitPrice: '',
  supplier: '',
  dateAdded: new Date().toISOString().split('T')[0],
  lowStockThreshold: '10',
})

const filteredInventory = computed(() => {
  const query = searchTerm.value.trim().toLowerCase()
  if (!query) return store.items
  return store.items.filter((item) => item.name.toLowerCase().includes(query) || item.supplier.toLowerCase().includes(query))
})

const totalItems = computed(() => store.items.reduce((sum, item) => sum + item.quantity, 0))
const lowStockCount = computed(() => store.items.filter((item) => item.quantity <= item.lowStockThreshold).length)
const supplierCount = computed(() => new Set(store.items.map((item) => item.supplier)).size)
const selectedCount = computed(() => selectedItems.value.size)
const allSelected = computed(() => selectedCount.value === filteredInventory.value.length && filteredInventory.value.length > 0)
const selectedInventoryItems = computed(() => store.items.filter((item) => selectedItems.value.has(item.id)))

const isLoading = ref(true)

onMounted(async () => {
  isLoading.value = true
  try {
    await Promise.all([store.fetchInventory(), store.fetchMovements()])
  } finally {
    isLoading.value = false
  }
})

function resetForm() {
  formError.value = ''
  formData.name = ''
  formData.unitPrice = ''
  formData.supplier = ''
  formData.dateAdded = new Date().toISOString().split('T')[0]
  formData.lowStockThreshold = '10'
}

function openAddDialog() {
  editingItem.value = null
  resetForm()
  isDialogOpen.value = true
}

function openEditDialog(item: InventoryItem) {
  editingItem.value = item
  formData.name = item.name
  formData.unitPrice = String(item.unitPrice)
  formData.supplier = item.supplier
  // Always reset to current system date when opening edit state
  formData.dateAdded = new Date().toISOString().split('T')[0]
  formData.lowStockThreshold = String(item.lowStockThreshold)
  isDialogOpen.value = true
}

function closeDialog() {
  isDialogOpen.value = false
  editingItem.value = null
  resetForm()
}

function toggleItemSelection(id: string) {
  if (selectedItems.value.has(id)) selectedItems.value.delete(id)
  else selectedItems.value.add(id)
}

function toggleSelectAll() {
  if (allSelected.value) selectedItems.value.clear()
  else filteredInventory.value.forEach((item) => selectedItems.value.add(item.id))
}

function openStockModal() {
  if (selectedItems.value.size === 0) {
    modalStore.open({
      title: 'No items selected',
      message: 'Please select at least one item before adding stock.',
      variant: 'warning',
    })
    return
  }
  selectedStockAdjustment.value = null
  stockError.value = ''
  isStockModalOpen.value = true
}

function closeStockModal() {
  if (isStockSubmitting.value) return
  isStockModalOpen.value = false
  selectedStockAdjustment.value = null
}

async function applyStockAdjustment() {
  if (selectedStockAdjustment.value === null) {
    stockError.value = 'Select or enter a quantity before continuing.'
    return
  }

  isStockSubmitting.value = true
  stockError.value = ''
  const adjustment = selectedStockAdjustment.value
  try {
    for (const item of selectedInventoryItems.value) {
      await store.updateItem(item.id, { quantity: item.quantity + adjustment })
    }
    await store.fetchMovements()
    selectedItems.value.clear()
    isStockModalOpen.value = false
    selectedStockAdjustment.value = null
  } catch (error: any) {
    stockError.value = error?.response?.data?.detail || 'Stock could not be updated. Please try again.'
  } finally {
    isStockSubmitting.value = false
  }
}

async function handleSubmit() {
  if (!formData.name.trim() || !formData.supplier.trim()) {
    formError.value = 'Material name and supplier are required.'
    return
  }
  isSubmitting.value = true
  formError.value = ''
  try {
    const currentDateString = new Date().toISOString().split('T')[0]

    if (editingItem.value) {
      await store.updateItem(editingItem.value.id, {
        name: formData.name,
        quantity: editingItem.value.quantity,
        unitPrice: Number.parseFloat(formData.unitPrice) || 0,
        supplier: formData.supplier,
        lowStockThreshold: Number.parseInt(formData.lowStockThreshold, 10) || 0,
        dateAdded: editingItem.value.dateAdded,
      })
    } else {
      await store.addItem({
        name: formData.name,
        quantity: 0,
        unitPrice: Number.parseFloat(formData.unitPrice) || 0,
        supplier: formData.supplier,
        lowStockThreshold: Number.parseInt(formData.lowStockThreshold, 10) || 0,
        dateAdded: currentDateString,
      })
    }

    closeDialog()
  } catch (error: any) {
    formError.value = error?.response?.data?.detail || 'The material could not be saved. Please try again.'
  } finally {
    isSubmitting.value = false
  }
}

async function handleDelete(id: string) {
  modalStore.open({
    title: 'Delete material?',
    message: 'This action will permanently remove the item from inventory.',
    variant: 'error',
    confirmLabel: 'Delete',
    cancelLabel: 'Cancel',
    onConfirm: () => store.deleteItem(id),
  })
}

function formatCurrency(value: number) {
  return `₱${value.toLocaleString('en-PH', { minimumFractionDigits: 2 })}`
}

function formatDate(value?: string) {
  if (!value) return '-'
  const d = new Date(value)
  if (Number.isNaN(d.getTime())) return '-'
  return d.toLocaleDateString('en-PH', {
    year: 'numeric',
    month: 'short',
    day: '2-digit',
  })
}

function formatDateTime(value?: string) {
  if (!value) return '-'
  const d = new Date(value)
  if (Number.isNaN(d.getTime())) return '-'
  return d.toLocaleString('en-PH', {
    year: 'numeric',
    month: 'short',
    day: '2-digit',
    hour: '2-digit',
    minute: '2-digit',
  })
}
</script>

<template>
  <section class="relative space-y-6">
    <LocalLoader v-if="isLoading" />
    <div class="flex flex-col gap-4 lg:flex-row lg:items-center lg:justify-between">
      <div class="flex items-start gap-3">
        <div class="flex h-10 w-10 items-center justify-center rounded-lg bg-linear-to-br from-sky-50 to-sky-100 ring-1 ring-sky-100">
          <Archive class="dashboard-view-icon h-5 w-5 text-sky-600 dark:text-sky-400" />
        </div>
        <div>
          <h3 class="mb-1 text-2xl font-semibold text-gray-900">Inventory Management</h3>
          <p class="text-sm text-gray-600">Manage materials, stock levels, and supplier records.</p>
        </div>
      </div>
      <button
        type="button"
        class="inline-flex items-center justify-center rounded-lg bg-sky-600 px-4 py-3 font-semibold text-white transition-colors hover:bg-sky-700"
        @click="openAddDialog"
      >
        <svg class="mr-2 h-5 w-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 4v16m8-8H4" />
        </svg>
        Add Material
      </button>
    </div>

    <div class="grid grid-cols-1 gap-4 sm:grid-cols-3">
      <div class="rounded-lg bg-sky-50 p-4">
        <p class="text-xs uppercase tracking-wide text-sky-600">Total Items</p>
        <p class="mt-1 text-2xl font-bold text-gray-900">{{ totalItems }}</p>
      </div>
      <div class="rounded-lg bg-sky-50 p-4">
        <p class="text-xs uppercase tracking-wide text-sky-600">Low Stock</p>
        <p class="mt-1 text-2xl font-bold text-gray-900">{{ lowStockCount }}</p>
      </div>
      <div class="rounded-lg bg-sky-50 p-4">
        <p class="text-xs uppercase tracking-wide text-sky-600">Suppliers</p>
        <p class="mt-1 text-2xl font-bold text-gray-900">{{ supplierCount }}</p>
      </div>
    </div>

    <div class="rounded-lg border border-gray-200 bg-white p-4">
      <input
        v-model="searchTerm"
        type="text"
        placeholder="Search materials or suppliers..."
        class="w-full rounded-lg border border-gray-300 bg-gray-50 px-4 py-3 outline-none transition focus:border-sky-500 focus:ring-2 focus:ring-sky-200 lg:max-w-md"
      />
    </div>

    <div v-if="selectedCount > 0" class="flex items-center justify-between rounded-lg border border-sky-200 bg-sky-50 p-4">
      <div>
        <p class="font-semibold text-sky-900">{{ selectedCount }} item(s) selected</p>
      </div>
      <button
        type="button"
        class="rounded-lg bg-sky-600 px-4 py-2 font-semibold text-white transition-colors hover:bg-sky-700"
        @click="openStockModal"
      >
        Stock In
      </button>
    </div>

    <div class="overflow-hidden rounded-xl border border-gray-200 bg-white">
      <div class="overflow-x-auto">
        <table class="w-full min-w-[1100px] divide-y divide-gray-200">
          <thead class="bg-gray-50/70">
            <tr class="text-left">
              <th class="w-12 px-6 py-4 text-xs font-bold uppercase tracking-wider text-gray-500">
                <input
                  type="checkbox"
                  :checked="allSelected"
                  class="h-4 w-4 cursor-pointer rounded border-gray-300 text-sky-600 focus:ring-sky-500"
                  @change="toggleSelectAll"
                />
              </th>
              <th class="px-6 py-4 text-xs font-bold uppercase tracking-wider text-gray-500">Material Name</th>
              <th class="px-6 py-4 text-xs font-bold uppercase tracking-wider text-gray-500">Quantity</th>
              <th class="px-6 py-4 text-xs font-bold uppercase tracking-wider text-gray-500">Unit Price</th>
              <th class="px-6 py-4 text-xs font-bold uppercase tracking-wider text-gray-500">Total Value</th>
              <th class="px-6 py-4 text-xs font-bold uppercase tracking-wider text-gray-500">Supplier</th>
              <th class="px-6 py-4 text-xs font-bold uppercase tracking-wider text-gray-500">Date Added</th>
              <th class="px-6 py-4 text-xs font-bold uppercase tracking-wider text-gray-500">Status</th>
              <th class="px-6 py-4 text-xs font-bold uppercase tracking-wider text-gray-500 text-right">Actions</th>
            </tr>
          </thead>
          <tbody class="divide-y divide-gray-100 bg-white">
            <tr v-for="item in filteredInventory" :key="item.id" class="transition-colors hover:bg-slate-50/80">
              <td class="px-6 py-4 whitespace-nowrap">
                <input
                  type="checkbox"
                  :checked="selectedItems.has(item.id)"
                  class="h-4 w-4 cursor-pointer rounded border-gray-300 text-sky-600 focus:ring-sky-500"
                  @change="toggleItemSelection(item.id)"
                />
              </td>
              <td class="px-6 py-4 font-semibold text-gray-900 whitespace-nowrap">{{ item.name }}</td>
              <td class="px-6 py-4 text-gray-700 whitespace-nowrap">{{ item.quantity }}</td>
              <td class="px-6 py-4 text-gray-700 whitespace-nowrap">{{ formatCurrency(item.unitPrice) }}</td>
              <td class="px-6 py-4 font-semibold text-gray-900 whitespace-nowrap">{{ formatCurrency(item.quantity * item.unitPrice) }}</td>
              <td class="px-6 py-4 text-gray-700 whitespace-nowrap">{{ item.supplier }}</td>
              <td class="px-6 py-4 text-gray-600 whitespace-nowrap">{{ formatDate(item.dateAdded) }}</td>
              <td class="px-6 py-4 whitespace-nowrap">
                <span
                  v-if="item.quantity <= item.lowStockThreshold"
                  class="inline-flex items-center rounded-full bg-orange-50 px-2.5 py-1 text-xs font-semibold text-orange-700 ring-1 ring-inset ring-orange-600/10 whitespace-nowrap"
                >
                  <svg class="mr-1 h-3.5 w-3.5 text-orange-500" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-3L13.732 4c-.77-1.333-2.694-1.333-3.464 0L3.34 16c-.77 1.333.192 3 1.732 3z" />
                  </svg>
                  Low Stock
                </span>
                <span v-else class="inline-flex items-center rounded-full bg-green-50 px-2.5 py-1 text-xs font-semibold text-green-700 ring-1 ring-inset ring-green-600/20 whitespace-nowrap">
                  In Stock
                </span>
              </td>
              <td class="px-6 py-4 whitespace-nowrap">
                <div class="flex gap-3 justify-end">
                  <button type="button" class="text-sky-600 transition-colors hover:text-sky-800" @click="openEditDialog(item)">
                    <svg class="h-5 w-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M11 5H6a2 2 0 00-2 2v11a2 2 0 002 2h11a2 2 0 002-2v-5m-1.414-9.414a2 2 0 112.828 2.828L11.828 15H9v-2.828l8.586-8.586z" />
                    </svg>
                  </button>
                  <button type="button" class="text-red-600 transition-colors hover:text-red-800" @click="handleDelete(item.id)">
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

    <ModalShell
      :show="isDialogOpen"
      :title="editingItem ? 'Edit Material' : 'Add New Material'"
      subtitle="Inventory record"
      tone="blue"
      size="lg"
      @close="closeDialog"
    >
      <form id="inventory-item-form" class="space-y-5" @submit.prevent="handleSubmit">
          <div class="flex gap-3 rounded-xl border border-blue-200 bg-blue-50 p-4 text-sm text-blue-800">
            <Info class="mt-0.5 h-4 w-4 shrink-0" />
            <p>Create the material record first, then select it from the inventory table to add its opening stock.</p>
          </div>
          <div>
            <label class="block text-sm font-semibold text-gray-700" for="name">Material Name <span class="text-red-500">*</span></label>
            <input
              id="name"
              v-model="formData.name"
              required
              autocomplete="off"
              placeholder="e.g. Welding rod E6013"
              class="mt-1 w-full rounded-xl border border-slate-200 bg-slate-50 px-4 py-3 shadow-sm outline-none transition focus:border-blue-500 focus:ring-2 focus:ring-blue-200"
            />
          </div>

          <div class="grid grid-cols-1 gap-4 sm:grid-cols-2">
            <div>
              <label class="block text-sm font-semibold text-gray-700" for="unitPrice">Unit Price <span class="text-red-500">*</span></label>
              <input
                id="unitPrice"
                v-model="formData.unitPrice"
                type="number"
                step="0.01"
                min="0"
                required
                placeholder="0.00"
                class="mt-1 w-full rounded-xl border border-slate-200 bg-slate-50 px-4 py-3 shadow-sm outline-none transition focus:border-blue-500 focus:ring-2 focus:ring-blue-200"
              />
            </div>

            <div>
              <label class="block text-sm font-semibold text-gray-700" for="supplier">Supplier <span class="text-red-500">*</span></label>
              <input
                id="supplier"
                v-model="formData.supplier"
                required
                autocomplete="off"
                placeholder="Supplier or store name"
                class="mt-1 w-full rounded-xl border border-slate-200 bg-slate-50 px-4 py-3 shadow-sm outline-none transition focus:border-blue-500 focus:ring-2 focus:ring-blue-200"
              />
            </div>
          </div>

          <div class="grid grid-cols-1 gap-4 sm:grid-cols-2">
            <div>
              <label class="block text-sm font-semibold text-gray-700" for="dateAdded">
                {{ editingItem ? 'Date Updated' : 'Date Added' }}
              </label>
              <input
                id="dateAdded"
                v-model="formData.dateAdded"
                type="date"
                disabled
                class="mt-1 w-full rounded-xl border border-slate-200 bg-slate-100 cursor-not-allowed px-4 py-3 shadow-sm outline-none transition text-gray-500"
              />
            </div>

            <div>
              <label class="block text-sm font-semibold text-gray-700" for="lowStockThreshold">Low Stock Alert</label>
              <input
                id="lowStockThreshold"
                v-model="formData.lowStockThreshold"
                type="number"
                min="0"
                required
                placeholder="10"
                class="mt-1 w-full rounded-xl border border-slate-200 bg-slate-50 px-4 py-3 shadow-sm outline-none transition focus:border-sky-500 focus:ring-2 focus:ring-sky-200"
              />
            </div>
          </div>

          <div class="rounded-xl bg-slate-50 p-4 text-sm text-gray-600"><strong class="text-gray-800">Low-stock alert:</strong> the material will be flagged whenever its available quantity reaches this threshold.</div>
          <div v-if="formError" role="alert" class="rounded-xl border border-red-200 bg-red-50 p-3 text-sm text-red-800">{{ formError }}</div>
      </form>
      <template #footer>
            <button type="button" class="rounded-xl border border-slate-200 bg-white px-5 py-3 font-semibold text-slate-700 shadow-sm hover:bg-slate-50 disabled:opacity-50 disabled:cursor-not-allowed" :disabled="isSubmitting" @click="closeDialog">
              Cancel
            </button>
            <button form="inventory-item-form" type="submit" class="inline-flex min-w-40 items-center justify-center gap-2 rounded-xl bg-linear-to-r from-sky-600 to-sky-700 px-5 py-3 font-semibold text-white shadow-lg shadow-sky-600/20 hover:from-sky-700 hover:to-sky-800 disabled:opacity-50 disabled:cursor-not-allowed" :disabled="isSubmitting">
              <LoaderCircle v-if="isSubmitting" class="h-4 w-4 animate-spin" />
              <span>{{ isSubmitting ? (editingItem ? 'Updating...' : 'Adding...') : (editingItem ? 'Update' : 'Add') }} Material</span>
            </button>
      </template>
    </ModalShell>

    <ModalShell
      :show="isStockModalOpen"
      title="Stock In"
      subtitle="Bulk stock adjustment"
      tone="green"
      size="md"
      @close="closeStockModal"
    >
      <div class="space-y-5">
          <div class="flex items-start gap-3 rounded-xl border border-emerald-200 bg-emerald-50 p-4">
            <PackagePlus class="mt-0.5 h-5 w-5 shrink-0 text-emerald-700" />
            <div><p class="font-semibold text-emerald-900">{{ selectedCount }} material{{ selectedCount === 1 ? '' : 's' }} selected</p><p class="mt-1 text-sm text-emerald-700">The quantity you choose will be added to every selected material.</p></div>
          </div>

          <div class="max-h-32 overflow-y-auto rounded-xl border border-slate-200 bg-slate-50 p-3">
            <div v-for="item in selectedInventoryItems" :key="item.id" class="flex items-center justify-between gap-4 py-1.5 text-sm"><span class="truncate font-medium text-gray-800">{{ item.name }}</span><span class="shrink-0 text-gray-500">Current: {{ item.quantity }}</span></div>
          </div>
          <div>
            <label class="mb-3 block text-sm font-semibold text-gray-700">Quick quantity</label>
            <div class="grid grid-cols-4 gap-2">
              <button
                v-for="qty in [5, 10, 20, 50]"
                :key="qty"
                type="button"
                :class="[
                  'rounded-xl border px-3 py-3 font-semibold transition-all',
                  selectedStockAdjustment === qty
                    ? 'border-green-600 bg-green-100 text-green-800 shadow-sm'
                    : 'border-slate-200 bg-white text-slate-700 hover:bg-slate-50',
                ]"
                @click="selectedStockAdjustment = qty"
              >
                +{{ qty }}
              </button>
            </div>
          </div>

          <div>
            <label class="block text-sm font-semibold text-gray-700" for="manual-qty">Custom quantity</label>
            <input
              id="manual-qty"
              type="number"
              min="1"
              placeholder="Enter custom quantity"
              class="mt-2 w-full rounded-xl border border-gray-300 bg-gray-50 px-4 py-3 outline-none transition focus:border-green-500 focus:ring-2 focus:ring-green-200"
              @input="(e) => selectedStockAdjustment = Number((e.target as HTMLInputElement).value) || null"
            />
          </div>

          <div v-if="selectedStockAdjustment !== null" class="rounded-xl border border-green-200 bg-green-50 p-4">
            <p class="font-semibold text-green-800">+{{ selectedStockAdjustment }} each · {{ selectedStockAdjustment * selectedCount }} total units</p>
            <p class="mt-1 text-sm text-green-700">Review the selected materials above before applying.</p>
          </div>
          <div v-if="stockError" role="alert" class="rounded-xl border border-red-200 bg-red-50 p-3 text-sm text-red-800">{{ stockError }}</div>
      </div>
      <template #footer>
            <button
              type="button"
              class="rounded-xl border border-slate-200 bg-white px-5 py-3 font-semibold text-slate-700 shadow-sm hover:bg-slate-50 disabled:opacity-50"
              :disabled="isStockSubmitting"
              @click="closeStockModal"
            >
              Cancel
            </button>
            <button
              type="button"
              class="inline-flex min-w-40 items-center justify-center gap-2 rounded-xl bg-linear-to-r from-green-600 to-emerald-600 px-5 py-3 font-semibold text-white shadow-lg shadow-green-600/20 hover:from-green-700 hover:to-emerald-700 disabled:opacity-50"
              :disabled="isStockSubmitting || selectedStockAdjustment === null"
              @click="applyStockAdjustment"
            >
              <LoaderCircle v-if="isStockSubmitting" class="h-4 w-4 animate-spin" />
              {{ isStockSubmitting ? 'Updating…' : 'Apply Stock' }}
            </button>
      </template>
    </ModalShell>

    <div class="rounded-lg border border-gray-200 bg-white p-6">
      <h3 class="mb-4 text-lg font-semibold text-gray-900">Stock Movement Log</h3>
      <div class="max-h-80 space-y-2 overflow-y-auto">
        <div v-if="store.movements.length === 0" class="py-8 text-center text-gray-500">
          No stock movements yet
        </div>
        <div
          v-for="movement in store.movements"
          :key="movement.id"
          class="flex items-center justify-between rounded-lg border border-gray-200 p-3 hover:bg-gray-50"
        >
          <div>
            <p class="font-medium text-gray-900">{{ movement.itemName }}</p>
            <p class="text-sm text-gray-600">{{ formatDateTime(movement.timestamp) }}</p>
            <p v-if="movement.teamEmails.length" class="text-xs text-gray-500">
              Team: {{ movement.teamEmails.join(', ') }}
            </p>
          </div>
          <span
            :class="[
              'inline-flex items-center rounded-full px-3 py-1 text-sm font-semibold',
              movement.type === 'stock-in' ? 'bg-green-100 text-green-800' : 'bg-red-100 text-red-800',
            ]"
          >
            {{ movement.type === 'stock-in' ? '+' : '-' }}{{ movement.quantity }}
          </span>
        </div>
      </div>
    </div>
  </section>
</template>
