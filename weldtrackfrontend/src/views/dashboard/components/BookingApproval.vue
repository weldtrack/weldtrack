<script setup lang="ts">
import { computed, reactive, ref } from 'vue'
import { useBookingsStore, type BookingItem, type BookingStatus } from '../../../stores/bookings'
import { useInventoryStore } from '../../../stores/inventory'

const bookingsStore = useBookingsStore()
const bookings = computed(() => bookingsStore.bookings)
const activeBookings = computed(() =>
  bookings.value.filter((booking) => booking.status === 'pending' || booking.status === 'confirmed'),
)

const pendingCount = computed(() => bookings.value.filter((booking) => booking.status === 'pending').length)
const confirmedCount = computed(() => bookings.value.filter((booking) => booking.status === 'confirmed').length)
const completedCount = computed(() => bookings.value.filter((booking) => booking.status === 'completed').length)

const isApprovalModalOpen = ref(false)
const selectedBooking = ref<BookingItem | null>(null)
const approvalForm = reactive({
  scheduleDate: '',
})
const isCompleteModalOpen = ref(false)
const completionForm = reactive({
  materialCost: '',
})
const inventoryStore = useInventoryStore()
const isCancelModalOpen = ref(false)
const cancelForm = reactive({
  reason: '',
})

// Fixed labor price per project type
const laborPriceMap: Record<string, number> = {
  'Gate Welding': 18000,
  'Metal Railings': 24500,
  'Steel Frame Construction': 32000,
  'Staircase Fabrication': 22000,
  'Metal Doors & Windows': 19500,
  'Pipe & Duct Welding': 15000,
  'Metal Shelving': 12000,
  'Automotive Welding': 25000,
  'Fence Installation': 16500,
  'Tank & Vessel Fabrication': 35000,
  'Repair & Maintenance': 9500,
  // Legacy project types for seed data
  'Steel Railing Installation': 24500,
  'Canopy Fabrication': 20000,
  'Metal Partition': 15800,
  'Gate Fabrication': 32000,
}

function getLaborPriceFor(type: string) {
  return laborPriceMap[type] || 0
}
// price is determined automatically on confirm; no UI helpers needed here

function getStatusLabel(status: BookingStatus) {
  switch (status) {
    case 'pending':
      return 'Pending'
    case 'confirmed':
      return 'Confirmed'
    case 'completed':
      return 'Completed'
    case 'cancelled':
      return 'Cancelled'
    default:
      return status
  }
}

function getStatusClass(status: BookingStatus) {
  switch (status) {
    case 'pending':
      return 'bg-yellow-100 text-yellow-800'
    case 'confirmed':
      return 'bg-blue-100 text-blue-800'
    case 'completed':
      return 'bg-green-100 text-green-800'
    case 'cancelled':
      return 'bg-red-100 text-red-800'
    default:
      return 'bg-gray-100 text-gray-700'
  }
}

function formatDate(value: string) {
  return new Date(value).toLocaleDateString('en-PH', {
    year: 'numeric',
    month: 'short',
    day: 'numeric',
  })
}

function openApprovalModal(booking: BookingItem) {
  selectedBooking.value = booking
  approvalForm.scheduleDate = String(booking.scheduleDate ?? booking.preferredDate ?? '')
  isApprovalModalOpen.value = true
}

function openCompleteModal(booking: BookingItem) {
  selectedBooking.value = booking
  completionForm.materialCost = booking.materialCost ? String(booking.materialCost) : ''
  isCompleteModalOpen.value = true
}

function closeCompleteModal() {
  isCompleteModalOpen.value = false
  selectedBooking.value = null
  completionForm.materialCost = ''
}

function closeApprovalModal() {
  isApprovalModalOpen.value = false
  selectedBooking.value = null
  approvalForm.scheduleDate = ''
  // approvalForm.estimatedCost = '' // Removed reference to estimatedCost
}

function openCancelModal(booking: BookingItem) {
  selectedBooking.value = booking
  cancelForm.reason = booking.cancelReason || ''
  isCancelModalOpen.value = true
}

function closeCancelModal() {
  isCancelModalOpen.value = false
  selectedBooking.value = null
  cancelForm.reason = ''
}

async function confirmApproval() {
  if (!selectedBooking.value) return
  const laborPrice = getLaborPriceFor(selectedBooking.value.projectType)
  const patch = {
    scheduleDate: approvalForm.scheduleDate,
    estimatedCost: laborPrice,
    status: 'confirmed' as BookingStatus,
  }

  await bookingsStore.updateBooking(selectedBooking.value.id, patch)

  console.log('Project auto-created from booking:', {
    bookingId: selectedBooking.value.id,
    customerEmail: selectedBooking.value.email,
    serviceType: selectedBooking.value.projectType,
    estimatedPrice: laborPrice,
    scheduleDate: approvalForm.scheduleDate,
  })

  closeApprovalModal()
}

async function cancelBookingAsAdmin() {
  if (!selectedBooking.value) return
  if (!cancelForm.reason.trim()) return
  const patch = {
    status: 'cancelled' as BookingStatus,
    cancelReason: cancelForm.reason.trim(),
    cancelledBy: 'admin' as const,
  }
  await bookingsStore.updateBooking(selectedBooking.value.id, patch)
  closeCancelModal()
}

const computedCompletionTotal = computed(() => {
  if (!selectedBooking.value) return 0
  const labor = getLaborPriceFor(selectedBooking.value.projectType)
  const mat = Number(completionForm.materialCost) || 0
  return labor + mat
})

async function confirmComplete() {
  if (!selectedBooking.value) return
  const labor = getLaborPriceFor(selectedBooking.value.projectType)
  const material = Number(completionForm.materialCost) || 0
  const patch = {
    status: 'completed' as BookingStatus,
    estimatedCost: labor,
    materialCost: material,
    totalPrice: labor + material,
  }

  await bookingsStore.updateBooking(selectedBooking.value.id, patch)

  console.log('Booking completed with totals:', {
    bookingId: selectedBooking.value.id,
    labor,
    material,
    total: labor + material,
  })

  closeCompleteModal()
}

async function loadMaterialsForBooking() {
  if (!selectedBooking.value) return
  const bookingId = Number(selectedBooking.value.id)
  try {
    const remote = await bookingsStore.getBooking(bookingId)
    if (remote && Array.isArray(remote.materials)) {
      const total = remote.materials.reduce((acc: number, m: any) => acc + (Number(m.unitPrice ?? 0) * Number(m.quantity ?? 0)), 0)
      completionForm.materialCost = String(total)
      return
    }
  } catch (err) {
    // ignore and fallback to local movements
  }

  const movements = inventoryStore.getMovementsForBooking(bookingId)
  let total = 0
  movements.forEach((m) => {
    if (m.type === 'stock-out') {
      const item = inventoryStore.items.find((it) => it.id === m.itemId)
      if (item) total += m.quantity * item.unitPrice
    }
  })
  completionForm.materialCost = String(total)
}

function hasStaffMaterialSubmission(bookingId: number) {
  const hasMovements = inventoryStore.getMovementsForBooking(bookingId).some((m) => m.type === 'stock-out')
  const booking = bookingsStore.bookings.find((b) => b.id === bookingId)
  const hasImages = Boolean(booking && ((booking.beforeImages && booking.beforeImages.length > 0) || (booking.afterImages && booking.afterImages.length > 0)))
  return hasMovements || hasImages
}
</script>

<template>
  <section class="space-y-6">
    <div class="flex flex-col gap-4 lg:flex-row lg:items-center lg:justify-between">
      <div>
        <h3 class="mb-1 text-2xl font-semibold text-gray-900">Booking Approval</h3>
        <p class="text-sm text-gray-600">Review customer requests and approve bookings</p>
      </div>
    </div>

    <div class="grid grid-cols-1 gap-4 md:grid-cols-3">
      <div class="rounded-lg border border-gray-200 bg-white p-4">
        <p class="text-sm text-gray-600">Pending</p>
        <p class="text-2xl text-gray-900">{{ pendingCount }}</p>
      </div>
      <div class="rounded-lg border border-gray-200 bg-white p-4">
        <p class="text-sm text-gray-600">Confirmed</p>
        <p class="text-2xl text-gray-900">{{ confirmedCount }}</p>
      </div>
      <div class="rounded-lg border border-gray-200 bg-white p-4">
        <p class="text-sm text-gray-600">Completed</p>
        <p class="text-2xl text-gray-900">{{ completedCount }}</p>
      </div>
    </div>

    <div class="overflow-hidden rounded-xl border border-gray-200 bg-white">
      <div class="overflow-x-auto">
      <table class="min-w-245 table-fixed divide-y divide-gray-200">
        <thead class="bg-gray-50">
          <tr>
            <th class="w-2/12 px-4 py-3 text-left text-sm font-semibold text-gray-700">Email/Contact No.</th>
            <th class="w-3/12 px-4 py-3 text-left text-sm font-semibold text-gray-700">Service</th>
            <th class="w-2/12 px-4 py-3 text-left text-sm font-semibold text-gray-700">Booked On</th>
            <th class="w-2/12 px-4 py-3 text-left text-sm font-semibold text-gray-700">Schedule</th>
            <th class="w-2/12 px-4 py-3 text-left text-sm font-semibold text-gray-700">Cost Summary</th>
            <th class="w-1/12 px-4 py-3 text-left text-sm font-semibold text-gray-700">Status</th>
            <th class="w-2/12 px-4 py-3 text-left text-sm font-semibold text-gray-700">Actions</th>
          </tr>
        </thead>
        <tbody class="divide-y divide-gray-200">
          <tr v-for="booking in activeBookings" :key="booking.id">
            <td class="px-4 py-3 font-medium text-gray-900 wrap-break-word">{{ booking.email }}<p class="text-xs text-gray-500">{{ booking.phone }}</p></td>
            <td class="px-4 py-3 text-gray-700 wrap-break-word">
              <div class="space-y-1">
                <p>{{ booking.projectType }}</p>
              </div>
            </td>
            <td class="px-4 py-3 text-gray-700">{{ formatDate(booking.createdDate ?? '') }}</td>
            <td class="px-4 py-3 text-gray-700">{{ booking.scheduleDate || 'Waiting for approval' }}</td>
            <td class="px-4 py-3 text-gray-900">
              <div class="space-y-1 text-sm">
                <p>Labor: ₱{{ (booking.estimatedCost ?? getLaborPriceFor(booking.projectType)).toLocaleString('en-PH', { minimumFractionDigits: 2 }) }}</p>
                <p>Material: <span v-if="booking.materialCost != null">₱{{ booking.materialCost.toLocaleString('en-PH', { minimumFractionDigits: 2 }) }}</span><span v-else class="text-gray-500">After completion</span></p>
                <p class="font-semibold">Total: ₱{{ ((booking.totalPrice != null ? booking.totalPrice : (getLaborPriceFor(booking.projectType) + (booking.materialCost ?? 0)))).toLocaleString('en-PH', { minimumFractionDigits: 2 }) }}</p>
                <p v-if="booking.status === 'confirmed' && !hasStaffMaterialSubmission(booking.id)" class="text-xs font-semibold text-amber-700">
                  Staff materials not submitted yet
                </p>
              </div>
            </td>
            <td class="px-4 py-3">
              <span class="rounded-full px-3 py-1 text-xs font-semibold" :class="getStatusClass(booking.status)">
                {{ getStatusLabel(booking.status) }}
              </span>
            </td>
            <td class="px-4 py-3">
              <div class="flex flex-wrap gap-2">
                <button
                  v-if="booking.status === 'pending'"
                  type="button"
                  class="rounded-lg bg-blue-600 px-3 py-2 text-sm font-semibold text-white hover:bg-blue-700"
                  @click="openApprovalModal(booking)"
                >
                  Approve
                </button>
                <button
                  v-if="booking.status === 'confirmed'"
                  type="button"
                  class="rounded-lg bg-green-600 px-3 py-2 text-sm font-semibold text-white hover:bg-green-700"
                  @click="openCompleteModal(booking)"
                >
                  Complete
                </button>
                <button
                  v-if="booking.status !== 'cancelled'"
                  type="button"
                  class="rounded-lg border border-red-300 px-3 py-2 text-sm font-semibold text-red-600 hover:bg-red-50"
                  @click="openCancelModal(booking)"
                >
                  Cancel
                </button>
              </div>
            </td>
          </tr>
        </tbody>
      </table>
      </div>
    </div>

    <div
      v-if="isApprovalModalOpen"
      class="fixed inset-0 z-50 flex items-center justify-center bg-black/50 p-4"
      @click.self="closeApprovalModal"
    >
      <div class="w-full max-w-xl rounded-2xl bg-white p-6 shadow-2xl">
        <h4 class="mb-4 text-lg font-semibold text-gray-900">Approve Booking</h4>

        <div v-if="selectedBooking" class="mb-5 rounded-lg border border-gray-200 bg-gray-50 p-4 text-sm text-gray-700">
          <p><span class="font-semibold">Email:</span> {{ selectedBooking.email }}</p>
          <p><span class="font-semibold">Service:</span> {{ selectedBooking.projectType }}</p>
          <p><span class="font-semibold">Contact:</span> {{ selectedBooking.phone }}</p>
          <div v-if="selectedBooking.beforeImages?.length || selectedBooking.afterImages?.length" class="mt-3">
            <p class="font-semibold">Field Images</p>
            <div class="mt-2 grid grid-cols-2 gap-2">
              <div v-if="selectedBooking.beforeImages?.length">
                <p class="text-xs text-gray-600">Before</p>
                <div class="flex flex-wrap gap-2 mt-1">
                  <a v-for="(img, idx) in selectedBooking.beforeImages" :key="`before-${idx}`" :href="img" target="_blank" rel="noreferrer">
                    <img :src="img" class="h-20 w-28 rounded-lg border object-cover" />
                  </a>
                </div>
              </div>

              <div v-if="selectedBooking.afterImages?.length">
                <p class="text-xs text-gray-600">After</p>
                <div class="flex flex-wrap gap-2 mt-1">
                  <a v-for="(img, idx) in selectedBooking.afterImages" :key="`after-${idx}`" :href="img" target="_blank" rel="noreferrer">
                    <img :src="img" class="h-20 w-28 rounded-lg border object-cover" />
                  </a>
                </div>
              </div>
            </div>
          </div>
        </div>

        <div class="space-y-4">
          <div>
            <label class="block text-sm font-medium text-gray-700" for="scheduleDate">Schedule Date</label>
            <input
              id="scheduleDate"
              v-model="approvalForm.scheduleDate"
              type="date"
              class="mt-1 w-full rounded-lg border border-gray-300 bg-gray-50 px-4 py-3 outline-none transition focus:border-blue-500 focus:ring-2 focus:ring-blue-200"
            />
          </div>

          <!-- Only schedule is required; price is auto-assigned on confirm -->
        </div>

        <div class="mt-6 flex justify-end gap-3">
          <button
            type="button"
            class="rounded-lg border border-gray-300 px-4 py-2 font-semibold text-gray-700 hover:bg-gray-50"
            @click="closeApprovalModal"
          >
            Cancel
          </button>
          <button
            type="button"
            class="rounded-lg bg-blue-600 px-4 py-2 font-semibold text-white hover:bg-blue-700"
            @click="confirmApproval"
          >
            Approve Booking
          </button>
        </div>
      </div>
    </div>
      
      <div
        v-if="isCompleteModalOpen"
        class="fixed inset-0 z-50 flex items-center justify-center bg-black/50 p-4"
        @click.self="closeCompleteModal"
      >
        <div class="w-full max-w-md rounded-2xl bg-white p-6 shadow-2xl">
          <h4 class="mb-4 text-lg font-semibold text-gray-900">Complete Booking</h4>

          <div v-if="selectedBooking" class="mb-5 rounded-lg border border-gray-200 bg-gray-50 p-4 text-sm text-gray-700">
            <p><span class="font-semibold">Email:</span> {{ selectedBooking.email }}</p>
            <p><span class="font-semibold">Service:</span> {{ selectedBooking.projectType }}</p>
            <p><span class="font-semibold">Contact:</span> {{ selectedBooking.phone }}</p>
          </div>

          <div v-if="selectedBooking && (selectedBooking.beforeImages?.length || selectedBooking.afterImages?.length)" class="mb-4 rounded-lg border border-gray-200 bg-gray-50 p-4 text-sm text-gray-700">
            <p class="font-semibold">Field Images</p>
            <div class="mt-2 grid grid-cols-2 gap-2">
              <div v-if="selectedBooking.beforeImages?.length">
                <p class="text-xs text-gray-600">Before</p>
                <div class="flex flex-wrap gap-2 mt-1">
                  <a v-for="(img, idx) in selectedBooking.beforeImages" :key="`c-before-${idx}`" :href="img" target="_blank" rel="noreferrer">
                    <img :src="img" class="h-20 w-28 rounded-lg border object-cover" />
                  </a>
                </div>
              </div>
              <div v-if="selectedBooking.afterImages?.length">
                <p class="text-xs text-gray-600">After</p>
                <div class="flex flex-wrap gap-2 mt-1">
                  <a v-for="(img, idx) in selectedBooking.afterImages" :key="`c-after-${idx}`" :href="img" target="_blank" rel="noreferrer">
                    <img :src="img" class="h-20 w-28 rounded-lg border object-cover" />
                  </a>
                </div>
              </div>
            </div>
          </div>

          <div class="space-y-4">
            <div>
              <p class="text-sm text-gray-600">Labor Cost (fixed)</p>
              <p class="mt-1 text-lg font-medium text-gray-900">₱{{ getLaborPriceFor(selectedBooking ? selectedBooking.projectType : '').toLocaleString('en-PH', { minimumFractionDigits: 2 }) }}</p>
            </div>

            <div
              v-if="selectedBooking && !hasStaffMaterialSubmission(selectedBooking.id)"
              class="rounded-lg border border-amber-200 bg-amber-50 px-3 py-2 text-sm font-medium text-amber-800"
            >
              Staff has not submitted materials for this booking yet.
            </div>

            <div>
              <label class="block text-sm font-medium text-gray-700" for="materialCost">Material Cost</label>
              <div class="flex gap-2">
                <input
                  id="materialCost"
                  v-model="completionForm.materialCost"
                  type="number"
                  min="0"
                  class="mt-1 w-full rounded-lg border border-gray-300 bg-gray-50 px-4 py-3 outline-none transition focus:border-blue-500 focus:ring-2 focus:ring-blue-200"
                />
                <button type="button" class="mt-1 rounded-lg bg-amber-100 px-3 py-2 font-semibold text-amber-700 hover:bg-amber-200" @click="loadMaterialsForBooking">Load from recorded materials</button>
              </div>
            </div>

            <div>
              <p class="text-sm text-gray-600">Total Price</p>
              <p class="mt-1 text-lg font-medium text-gray-900">₱{{ computedCompletionTotal.toLocaleString('en-PH', { minimumFractionDigits: 2 }) }}</p>
            </div>
          </div>

          <div class="mt-6 flex justify-end gap-3">
            <button
              type="button"
              class="rounded-lg border border-gray-300 px-4 py-2 font-semibold text-gray-700 hover:bg-gray-50"
              @click="closeCompleteModal"
            >
              Cancel
            </button>
            <button
              type="button"
              class="rounded-lg bg-green-600 px-4 py-2 font-semibold text-white hover:bg-green-700"
              @click="confirmComplete"
            >
              Mark Completed
            </button>
          </div>
        </div>
    </div>

    <div
      v-if="isCancelModalOpen"
      class="fixed inset-0 z-50 flex items-center justify-center bg-black/50 p-4"
      @click.self="closeCancelModal"
    >
      <div class="w-full max-w-xl rounded-2xl bg-white p-6 shadow-2xl">
        <h4 class="mb-4 text-lg font-semibold text-gray-900">Cancel Booking</h4>
        <div class="space-y-4">
          <div>
            <label class="block text-sm font-medium text-gray-700" for="cancelReason">Cancel Reason</label>
            <textarea
              id="cancelReason"
              v-model="cancelForm.reason"
              rows="4"
              placeholder="Enter cancellation reason..."
              class="mt-1 w-full rounded-lg border border-gray-300 bg-gray-50 px-4 py-3 outline-none transition focus:border-red-500 focus:ring-2 focus:ring-red-200"
            />
          </div>
          <div class="flex gap-3 pt-2">
            <button
              type="button"
              class="flex-1 rounded-lg border border-gray-300 px-4 py-2 font-semibold text-gray-700 hover:bg-gray-50"
              @click="closeCancelModal"
            >
              Back
            </button>
            <button
              type="button"
              class="flex-1 rounded-lg bg-red-600 px-4 py-2 font-semibold text-white hover:bg-red-700 disabled:cursor-not-allowed disabled:bg-red-300"
              :disabled="!cancelForm.reason.trim()"
              @click="cancelBookingAsAdmin"
            >
              Confirm Cancel
            </button>
          </div>
        </div>
      </div>
    </div>
  </section>
</template>
