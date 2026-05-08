<script setup lang="ts">
import { computed, reactive, ref } from 'vue'
import { useBookingsStore, type BookingItem, type BookingStatus } from '../../../stores/bookings'
import { useInventoryStore } from '../../../stores/inventory'
import { useModalStore } from '../../../stores/modal'
import ModalShell from '../../../components/ui/ModalShell.vue'
import { getLaborPrice } from '../../../constants/pricing'

const bookingsStore = useBookingsStore()
const inventoryStore = useInventoryStore()
const modalStore = useModalStore()
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
const isCancelModalOpen = ref(false)
const cancelForm = reactive({
  reason: '',
})

function getLaborPriceFor(type: string) {
  return getLaborPrice(type)
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
  // Refetch movements to show newly submitted staff materials
  inventoryStore.fetchMovements().then(() => loadMaterialsForBooking())
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
  
  // Check if staff has recorded materials
  if (!hasStaffMaterialSubmission(selectedBooking.value.id)) {
    // Show modal asking to confirm completion without materials
    modalStore.open({
      title: 'No materials recorded',
      message: 'Staff has not submitted any recorded materials for this booking. Are you sure you want to complete it without material records?',
      variant: 'warning',
      confirmLabel: 'Complete Anyway',
      cancelLabel: 'Cancel',
      onConfirm: () => completeBookingForce(),
    })
    return
  }
  
  completeBookingForce()
}

async function completeBookingForce() {
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
  
  // eslint-disable-next-line no-console
  console.debug('Loading materials for booking:', bookingId)
  
  try {
    const remote = await bookingsStore.getBooking(bookingId)
    if (remote && Array.isArray(remote.materials)) {
      const total = remote.materials.reduce((acc, line) => {
        const subtotal = Number(line.subtotal ?? 0)
        if (subtotal > 0) return acc + subtotal
        return acc + Number(line.unitPrice ?? 0) * Number(line.qty ?? 0)
      }, 0)

      if (total > 0) {
        completionForm.materialCost = String(total)
        // eslint-disable-next-line no-console
        console.debug('Loaded from booking.materials:', total)
        return
      }
    }
  } catch (err) {
    // eslint-disable-next-line no-console
    console.error('Error fetching booking:', err)
  }

  // Fallback: load from stock movements
  await inventoryStore.fetchMovements({ bookingId })
  const movements = inventoryStore.getMovementsForBooking(bookingId)
  // eslint-disable-next-line no-console
  console.debug('Found stock movements for booking:', movements)
  
  let total = 0
  movements.forEach((m) => {
    if (m.type === 'stock-out') {
      const item = inventoryStore.items.find((it) => it.id === m.itemId)
      if (item) {
        const lineTotal = m.quantity * item.unitPrice
        total += lineTotal
        // eslint-disable-next-line no-console
        console.debug(`  ${item.name}: ${m.quantity} × ${item.unitPrice} = ${lineTotal}`)
      }
    }
  })
  completionForm.materialCost = String(total)
  // eslint-disable-next-line no-console
  console.debug('Calculated material total:', total)
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
                <p>Labor: ₱{{ getLaborPriceFor(booking.projectType).toLocaleString('en-PH', { minimumFractionDigits: 2 }) }}</p>
                <p>Material: <span v-if="booking.materialCost != null">₱{{ booking.materialCost.toLocaleString('en-PH', { minimumFractionDigits: 2 }) }}</span><span v-else class="text-gray-500">After completion</span></p>
                <p class="font-semibold">Total: ₱{{ (getLaborPriceFor(booking.projectType) + (booking.materialCost ?? 0)).toLocaleString('en-PH', { minimumFractionDigits: 2 }) }}</p>
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

    <ModalShell
      :show="isApprovalModalOpen"
      title="Approve Booking"
      subtitle="Review booking details"
      tone="blue"
      size="xl"
      @close="closeApprovalModal"
    >
      <div v-if="selectedBooking" class="mb-5 rounded-2xl border border-slate-200 bg-slate-50 p-4 text-sm text-slate-700">
        <p><span class="font-semibold text-slate-900">Email:</span> {{ selectedBooking.email }}</p>
        <p><span class="font-semibold text-slate-900">Service:</span> {{ selectedBooking.projectType }}</p>
        <p><span class="font-semibold text-slate-900">Contact:</span> {{ selectedBooking.phone }}</p>
        <div v-if="selectedBooking.beforeImages?.length || selectedBooking.afterImages?.length" class="mt-3">
          <p class="font-semibold text-slate-900">Field Images</p>
          <div class="mt-2 grid grid-cols-2 gap-2">
            <div v-if="selectedBooking.beforeImages?.length">
              <p class="text-xs text-slate-600">Before</p>
              <div class="mt-1 flex flex-wrap gap-2">
                <a v-for="(img, idx) in selectedBooking.beforeImages" :key="`before-${idx}`" :href="img" target="_blank" rel="noreferrer">
                  <img :src="img" class="h-20 w-28 rounded-xl border border-slate-200 object-cover shadow-sm" />
                </a>
              </div>
            </div>

            <div v-if="selectedBooking.afterImages?.length">
              <p class="text-xs text-slate-600">After</p>
              <div class="mt-1 flex flex-wrap gap-2">
                <a v-for="(img, idx) in selectedBooking.afterImages" :key="`after-${idx}`" :href="img" target="_blank" rel="noreferrer">
                  <img :src="img" class="h-20 w-28 rounded-xl border border-slate-200 object-cover shadow-sm" />
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
            class="mt-1 w-full rounded-xl border border-slate-200 bg-slate-50 px-4 py-3 shadow-sm outline-none transition focus:border-blue-500 focus:ring-2 focus:ring-blue-200"
          />
        </div>
      </div>

      <template #footer>
        <button type="button" class="rounded-xl border border-slate-200 bg-white px-4 py-3 font-semibold text-slate-700 shadow-sm hover:bg-slate-50" @click="closeApprovalModal">
          Cancel
        </button>
        <button type="button" class="rounded-xl bg-linear-to-r from-blue-600 to-sky-600 px-4 py-3 font-semibold text-white shadow-lg shadow-blue-600/20 hover:from-blue-700 hover:to-sky-700" @click="confirmApproval">
          Approve Booking
        </button>
      </template>
    </ModalShell>

    <ModalShell
      :show="isCompleteModalOpen"
      title="Complete Booking"
      subtitle="Finalize costs and status"
      tone="green"
      size="lg"
      @close="closeCompleteModal"
    >
      <div v-if="selectedBooking" class="mb-5 rounded-2xl border border-slate-200 bg-slate-50 p-4 text-sm text-slate-700">
        <p><span class="font-semibold text-slate-900">Email:</span> {{ selectedBooking.email }}</p>
        <p><span class="font-semibold text-slate-900">Service:</span> {{ selectedBooking.projectType }}</p>
        <p><span class="font-semibold text-slate-900">Contact:</span> {{ selectedBooking.phone }}</p>
      </div>

      <div v-if="selectedBooking && (selectedBooking.beforeImages?.length || selectedBooking.afterImages?.length)" class="mb-4 rounded-2xl border border-slate-200 bg-slate-50 p-4 text-sm text-slate-700">
        <p class="font-semibold text-slate-900">Field Images</p>
        <div class="mt-2 grid grid-cols-2 gap-2">
          <div v-if="selectedBooking.beforeImages?.length">
            <p class="text-xs text-slate-600">Before</p>
            <div class="mt-1 flex flex-wrap gap-2">
              <a v-for="(img, idx) in selectedBooking.beforeImages" :key="`c-before-${idx}`" :href="img" target="_blank" rel="noreferrer">
                <img :src="img" class="h-20 w-28 rounded-xl border border-slate-200 object-cover shadow-sm" />
              </a>
            </div>
          </div>
          <div v-if="selectedBooking.afterImages?.length">
            <p class="text-xs text-slate-600">After</p>
            <div class="mt-1 flex flex-wrap gap-2">
              <a v-for="(img, idx) in selectedBooking.afterImages" :key="`c-after-${idx}`" :href="img" target="_blank" rel="noreferrer">
                <img :src="img" class="h-20 w-28 rounded-xl border border-slate-200 object-cover shadow-sm" />
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

        <div v-if="selectedBooking && !hasStaffMaterialSubmission(selectedBooking.id)" class="rounded-xl border border-amber-200 bg-amber-50 px-3 py-2 text-sm font-medium text-amber-800">
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
              class="mt-1 w-full rounded-xl border border-slate-200 bg-slate-50 px-4 py-3 shadow-sm outline-none transition focus:border-blue-500 focus:ring-2 focus:ring-blue-200"
            />
            <button type="button" class="mt-1 rounded-xl bg-amber-100 px-3 py-2 font-semibold text-amber-800 hover:bg-amber-200" @click="loadMaterialsForBooking">Load from recorded materials</button>
          </div>
        </div>

        <div>
          <p class="text-sm text-gray-600">Total Price</p>
          <p class="mt-1 text-lg font-medium text-gray-900">₱{{ computedCompletionTotal.toLocaleString('en-PH', { minimumFractionDigits: 2 }) }}</p>
        </div>
      </div>

      <template #footer>
        <button type="button" class="rounded-xl border border-slate-200 bg-white px-4 py-3 font-semibold text-slate-700 shadow-sm hover:bg-slate-50" @click="closeCompleteModal">
          Cancel
        </button>
        <button type="button" class="rounded-xl bg-linear-to-r from-green-600 to-emerald-600 px-4 py-3 font-semibold text-white shadow-lg shadow-green-600/20 hover:from-green-700 hover:to-emerald-700" @click="confirmComplete">
          Mark Completed
        </button>
      </template>
    </ModalShell>

    <ModalShell
      :show="isCancelModalOpen"
      title="Cancel Booking"
      subtitle="Provide a cancellation reason"
      tone="red"
      size="lg"
      @close="closeCancelModal"
    >
      <div class="space-y-4">
        <div>
          <label class="block text-sm font-medium text-gray-700" for="cancelReason">Cancel Reason</label>
          <textarea
            id="cancelReason"
            v-model="cancelForm.reason"
            rows="4"
            placeholder="Enter cancellation reason..."
            class="mt-1 w-full rounded-xl border border-slate-200 bg-slate-50 px-4 py-3 shadow-sm outline-none transition focus:border-red-500 focus:ring-2 focus:ring-red-200"
          />
        </div>
      </div>

      <template #footer>
        <button type="button" class="rounded-xl border border-slate-200 bg-white px-4 py-3 font-semibold text-slate-700 shadow-sm hover:bg-slate-50" @click="closeCancelModal">
          Back
        </button>
        <button type="button" class="rounded-xl bg-linear-to-r from-red-600 to-rose-600 px-4 py-3 font-semibold text-white shadow-lg shadow-red-600/20 disabled:cursor-not-allowed disabled:opacity-50" :disabled="!cancelForm.reason.trim()" @click="cancelBookingAsAdmin">
          Confirm Cancel
        </button>
      </template>
    </ModalShell>
  </section>
</template>
