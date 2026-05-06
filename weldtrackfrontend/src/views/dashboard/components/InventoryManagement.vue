<script setup lang="ts">
import { computed, reactive, ref } from 'vue'
import { useInventoryStore, type InventoryItem } from '../../../stores/inventory'

const store = useInventoryStore()

const isDialogOpen = ref(false)
const isStockModalOpen = ref(false)
const editingItem = ref<InventoryItem | null>(null)
const selectedItems = ref<Set<string>>(new Set())
const selectedStockAdjustment = ref<number | null>(null)
const searchTerm = ref('')
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

function resetForm() {
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
  formData.dateAdded = item.dateAdded
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
    window.alert('Please select at least one item')
    return
  }
  selectedStockAdjustment.value = null
  isStockModalOpen.value = true
}

function closeStockModal() {
  isStockModalOpen.value = false
  selectedStockAdjustment.value = null
}

function applyStockAdjustment() {
  if (selectedStockAdjustment.value === null) {
    window.alert('Please select a quantity')
    return
  }

  const adjustment = selectedStockAdjustment.value
  selectedItems.value.forEach((itemId) => store.stockIn(itemId, adjustment))
  selectedItems.value.clear()
  closeStockModal()
}

function handleSubmit() {
  const payload = {
    name: formData.name,
    quantity: editingItem.value?.quantity || 0,
    unitPrice: Number.parseFloat(formData.unitPrice) || 0,
    supplier: formData.supplier,
    dateAdded: formData.dateAdded,
    lowStockThreshold: Number.parseInt(formData.lowStockThreshold, 10) || 0,
  }

  if (editingItem.value) {
    store.updateItem(editingItem.value.id, payload)
  } else {
    store.addItem(payload)
  }

  closeDialog()
}

function handleDelete(id: string) {
  if (window.confirm('Are you sure you want to delete this item?')) store.deleteItem(id)
}

function formatCurrency(value: number) {
  return `₱${value.toLocaleString('en-PH', { minimumFractionDigits: 2 })}`
}
</script>

<template>
  <section class="space-y-6 rounded-lg border border-gray-200 bg-white p-6">
    <div class="flex flex-col gap-4 lg:flex-row lg:items-center lg:justify-between">
      <div>
        <h3 class="mb-1 text-2xl font-semibold text-gray-900">Inventory Management</h3>
        <p class="text-sm text-gray-600">Manage materials, stock levels, and supplier records.</p>
      </div>

      <button
        type="button"
        class="inline-flex items-center justify-center rounded-lg bg-blue-600 px-4 py-3 font-semibold text-white transition-colors hover:bg-blue-700"
        @click="openAddDialog"
      >
        <svg class="mr-2 h-5 w-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 4v16m8-8H4" />
        </svg>
        Add Material
      </button>
    </div>

    <div class="grid grid-cols-1 gap-4 sm:grid-cols-3">
      <div class="rounded-lg bg-blue-50 p-4">
        <p class="text-xs uppercase tracking-wide text-blue-600">Total Items</p>
        <p class="mt-1 text-2xl font-bold text-gray-900">{{ totalItems }}</p>
      </div>
      <div class="rounded-lg bg-amber-50 p-4">
        <p class="text-xs uppercase tracking-wide text-amber-600">Low Stock</p>
        <p class="mt-1 text-2xl font-bold text-gray-900">{{ lowStockCount }}</p>
      </div>
      <div class="rounded-lg bg-emerald-50 p-4">
        <p class="text-xs uppercase tracking-wide text-emerald-600">Suppliers</p>
        <p class="mt-1 text-2xl font-bold text-gray-900">{{ supplierCount }}</p>
      </div>
    </div>

    <div class="rounded-lg border border-gray-200 p-4">
      <input
        v-model="searchTerm"
        type="text"
        placeholder="Search materials or suppliers..."
        class="w-full rounded-lg border border-gray-300 bg-gray-50 px-4 py-3 outline-none transition focus:border-blue-500 focus:ring-2 focus:ring-blue-200 lg:max-w-md"
      />
    </div>

    <div v-if="selectedCount > 0" class="flex items-center justify-between rounded-lg border border-blue-200 bg-blue-50 p-4">
      <div>
        <p class="font-semibold text-blue-900">{{ selectedCount }} item(s) selected</p>
      </div>
      <button
        type="button"
        class="rounded-lg bg-green-600 px-4 py-2 font-semibold text-white transition-colors hover:bg-green-700"
        @click="openStockModal"
      >
        Stock In
      </button>
    </div>

    <div class="overflow-hidden rounded-lg border border-gray-200">
      <div class="overflow-x-auto">
        <table class="w-full min-w-275">
          <thead class="bg-gray-50">
            <tr class="border-b border-gray-200 text-left">
              <th class="px-6 py-4 text-gray-700">
                <input
                  type="checkbox"
                  :checked="allSelected"
                  class="h-4 w-4 cursor-pointer rounded border-gray-300"
                  @change="toggleSelectAll"
                />
              </th>
              <th class="px-6 py-4 text-gray-700">Material Name</th>
              <th class="px-6 py-4 text-gray-700">Quantity</th>
              <th class="px-6 py-4 text-gray-700">Unit Price</th>
              <th class="px-6 py-4 text-gray-700">Total Value</th>
              <th class="px-6 py-4 text-gray-700">Supplier</th>
              <th class="px-6 py-4 text-gray-700">Date Added</th>
              <th class="px-6 py-4 text-gray-700">Status</th>
              <th class="px-6 py-4 text-gray-700">Actions</th>
            </tr>
          </thead>
          <tbody>
            <tr v-for="item in filteredInventory" :key="item.id" class="border-b border-gray-100 hover:bg-gray-50">
              <td class="px-6 py-4">
                <input
                  type="checkbox"
                  :checked="selectedItems.has(item.id)"
                  class="h-4 w-4 cursor-pointer rounded border-gray-300"
                  @change="toggleItemSelection(item.id)"
                />
              </td>
              <td class="px-6 py-4 text-gray-900">{{ item.name }}</td>
              <td class="px-6 py-4 text-gray-700">{{ item.quantity }}</td>
              <td class="px-6 py-4 text-gray-700">{{ formatCurrency(item.unitPrice) }}</td>
              <td class="px-6 py-4 text-gray-900">{{ formatCurrency(item.quantity * item.unitPrice) }}</td>
              <td class="px-6 py-4 text-gray-700">{{ item.supplier }}</td>
              <td class="px-6 py-4 text-gray-700">{{ item.dateAdded }}</td>
              <td class="px-6 py-4">
                <span
                  v-if="item.quantity <= item.lowStockThreshold"
                  class="inline-flex items-center rounded-full bg-orange-100 px-3 py-1 text-orange-800"
                >
                  <svg class="mr-1 h-4 w-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-3L13.732 4c-.77-1.333-2.694-1.333-3.464 0L3.34 16c-.77 1.333.192 3 1.732 3z" />
                  </svg>
                  Low Stock
                </span>
                <span v-else class="inline-flex items-center rounded-full bg-green-100 px-3 py-1 text-green-800">
                  In Stock
                </span>
              </td>
              <td class="px-6 py-4">
                <div class="flex gap-2">
                  <button type="button" class="text-blue-600 transition-colors hover:text-blue-800" @click="openEditDialog(item)">
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

    <div
      v-if="isDialogOpen"
      class="fixed inset-0 z-50 flex items-center justify-center bg-black/50 p-4"
      @click.self="closeDialog"
    >
      <div class="w-full max-w-md rounded-2xl bg-white p-6 shadow-2xl">
        <div class="mb-5">
          <h4 class="text-lg font-semibold text-gray-900">
            {{ editingItem ? 'Edit Material' : 'Add New Material' }}
          </h4>
        </div>

        <form class="space-y-4" @submit.prevent="handleSubmit">
          <div>
            <label class="block text-sm font-medium text-gray-700" for="name">Material Name</label>
            <input
              id="name"
              v-model="formData.name"
              required
              class="mt-1 w-full rounded-lg border border-gray-300 bg-gray-50 px-4 py-3 outline-none transition focus:border-blue-500 focus:ring-2 focus:ring-blue-200"
            />
          </div>

          <div class="grid grid-cols-1 gap-4 sm:grid-cols-2">
            <div>
              <label class="block text-sm font-medium text-gray-700" for="unitPrice">Unit Price (₱)</label>
              <input
                id="unitPrice"
                v-model="formData.unitPrice"
                type="number"
                step="0.01"
                min="0"
                required
                class="mt-1 w-full rounded-lg border border-gray-300 bg-gray-50 px-4 py-3 outline-none transition focus:border-blue-500 focus:ring-2 focus:ring-blue-200"
              />
            </div>

            <div>
              <label class="block text-sm font-medium text-gray-700" for="supplier">Supplier</label>
              <input
                id="supplier"
                v-model="formData.supplier"
                required
                class="mt-1 w-full rounded-lg border border-gray-300 bg-gray-50 px-4 py-3 outline-none transition focus:border-blue-500 focus:ring-2 focus:ring-blue-200"
              />
            </div>
          </div>

          <div class="grid grid-cols-1 gap-4 sm:grid-cols-2">
            <div>
              <label class="block text-sm font-medium text-gray-700" for="dateAdded">Date Added</label>
              <input
                id="dateAdded"
                v-model="formData.dateAdded"
                type="date"
                required
                class="mt-1 w-full rounded-lg border border-gray-300 bg-gray-50 px-4 py-3 outline-none transition focus:border-blue-500 focus:ring-2 focus:ring-blue-200"
              />
            </div>

            <div>
              <label class="block text-sm font-medium text-gray-700" for="lowStockThreshold">Low Stock Alert</label>
              <input
                id="lowStockThreshold"
                v-model="formData.lowStockThreshold"
                type="number"
                min="0"
                required
                class="mt-1 w-full rounded-lg border border-gray-300 bg-gray-50 px-4 py-3 outline-none transition focus:border-blue-500 focus:ring-2 focus:ring-blue-200"
              />
            </div>
          </div>

          <div class="flex gap-3 pt-2">
            <button type="button" class="flex-1 rounded-lg border border-gray-300 px-4 py-3 font-semibold text-gray-700 hover:bg-gray-50" @click="closeDialog">
              Cancel
            </button>
            <button type="submit" class="flex-1 rounded-lg bg-blue-600 px-4 py-3 font-semibold text-white hover:bg-blue-700">
              {{ editingItem ? 'Update' : 'Add' }} Material
            </button>
          </div>
        </form>
      </div>
    </div>

    <div
      v-if="isStockModalOpen"
      class="fixed inset-0 z-50 flex items-center justify-center bg-black/50 p-4"
      @click.self="closeStockModal"
    >
      <div class="w-full max-w-md rounded-2xl bg-white p-6 shadow-2xl">
        <div class="mb-5">
          <h4 class="text-lg font-semibold text-gray-900">
            Add Stock to {{ selectedCount }} item(s)
          </h4>
        </div>

        <div class="space-y-4">
          <div>
            <label class="mb-3 block text-sm font-medium text-gray-700">Select Quantity to Add</label>
            <div class="flex flex-wrap gap-2">
              <button
                v-for="qty in [5, 10, 20, 50]"
                :key="qty"
                type="button"
                :class="[
                  'rounded-lg border px-4 py-2 font-semibold transition-colors',
                  selectedStockAdjustment === qty
                    ? 'border-green-600 bg-green-100 text-green-800'
                    : 'border-gray-300 bg-gray-50 text-gray-700 hover:bg-gray-100',
                ]"
                @click="selectedStockAdjustment = qty"
              >
                +{{ qty }}
              </button>
            </div>
          </div>

          <div>
            <label class="block text-sm font-medium text-gray-700" for="manual-qty">Or Enter Manually</label>
            <input
              id="manual-qty"
              type="number"
              min="1"
              placeholder="Enter custom quantity"
              class="mt-2 w-full rounded-lg border border-gray-300 bg-gray-50 px-4 py-3 outline-none transition focus:border-green-500 focus:ring-2 focus:ring-green-200"
              @input="(e) => selectedStockAdjustment = Number((e.target as HTMLInputElement).value) || null"
            />
          </div>

          <div v-if="selectedStockAdjustment !== null" class="rounded border border-green-200 bg-green-50 p-3">
            <p class="text-sm text-green-600">
              Will add {{ selectedStockAdjustment }} unit(s) to each selected item
            </p>
          </div>

          <div class="flex gap-3 pt-2">
            <button
              type="button"
              class="flex-1 rounded-lg border border-gray-300 px-4 py-3 font-semibold text-gray-700 hover:bg-gray-50"
              @click="closeStockModal"
            >
              Cancel
            </button>
            <button
              type="button"
              class="flex-1 rounded-lg bg-green-600 px-4 py-3 font-semibold text-white hover:bg-green-700"
              @click="applyStockAdjustment"
            >
              Apply
            </button>
          </div>
        </div>
      </div>
    </div>

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
            <p class="text-sm text-gray-600">{{ movement.timestamp }}</p>
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
