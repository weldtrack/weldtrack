<script setup lang="ts">
import { computed, nextTick, onBeforeUnmount, onMounted, reactive, ref, watch } from 'vue'
import L from 'leaflet'
import 'leaflet/dist/leaflet.css'
import { Calendar, CheckCircle2, Clock3, MapPin, Pencil } from 'lucide-vue-next'
import LocalLoader from '../../../../components/ui/LocalLoader.vue'
import ModalShell from '../../../../components/ui/ModalShell.vue'
import { useAuthStore } from '../../../../stores/auth'
import {
  correctAttendance,
  fetchTodayAttendance,
  fetchTodayAttendanceState,
  submitAttendanceAction,
  toAttendanceRecord,
} from '../../../../api/attendance'
import { fetchAttendanceLocation, setAttendanceLocation } from '../../../../api/settings'
import { getUserFriendlyApiError } from '../../../../services/errorMessage'
import type { AttendanceAction, AttendanceRecord, AttendanceSite } from '../../../../types/attendance'

const authStore = useAuthStore()
const isAdmin = computed(() => authStore.role.trim().toLowerCase() === 'admin')
const isLoading = ref(true)
const isSubmitting = ref(false)
const actionError = ref('')
const attendanceRecords = ref<AttendanceRecord[]>([])
const attendanceDate = ref('')
const attendanceTimezone = ref('Asia/Manila')
const nextAction = ref<AttendanceAction | null>(null)
const nextActionAvailable = ref(false)
const nextActionAvailableAt = ref<string | null>(null)
const nextActionMessage = ref('')
let availabilityTimer: number | undefined

const myAttendance = computed(() => attendanceRecords.value[0])
const actionLabels: Record<AttendanceAction, string> = {
  'morning-in': 'Morning Time In',
  'morning-out': 'Morning Time Out',
  'afternoon-in': 'Afternoon Time In',
  'afternoon-out': 'Afternoon Time Out',
}
const nextActionLabel = computed(() => nextAction.value ? actionLabels[nextAction.value] : 'Attendance Completed')

function mapRecord(raw: Parameters<typeof toAttendanceRecord>[0]) {
  return toAttendanceRecord(raw, (email, fallback) => authStore.getStaffLabel(email, fallback))
}

async function loadAttendance() {
  actionError.value = ''
  if (isAdmin.value) {
    const raw = await fetchTodayAttendance()
    attendanceRecords.value = raw.map(mapRecord)
    return
  }
  const state = await fetchTodayAttendanceState()
  attendanceDate.value = state.attendance_date
  attendanceTimezone.value = state.timezone
  nextAction.value = state.next_action
  nextActionAvailable.value = state.next_action_available
  nextActionAvailableAt.value = state.next_action_available_at
  nextActionMessage.value = state.next_action_message
  attendanceRecords.value = state.record ? [mapRecord(state.record)] : []
  scheduleAvailabilityRefresh()
}

function scheduleAvailabilityRefresh() {
  if (availabilityTimer) window.clearTimeout(availabilityTimer)
  availabilityTimer = undefined
  if (isAdmin.value || nextActionAvailable.value || !nextActionAvailableAt.value) return
  const delay = new Date(nextActionAvailableAt.value).getTime() - Date.now()
  if (delay <= 0) return
  availabilityTimer = window.setTimeout(() => { void loadAttendance() }, Math.min(delay + 500, 2_147_000_000))
}

const attendedToday = computed(() => attendanceRecords.value.length)
const currentlyOnSite = computed(() => attendanceRecords.value.filter((record) =>
  (record.morningInAt && !record.morningOutAt) || (record.afternoonInAt && !record.afternoonOutAt),
).length)
const completedToday = computed(() => attendanceRecords.value.filter((record) => record.attendanceStatus === 'Completed').length)
const lateToday = computed(() => attendanceRecords.value.filter((record) => record.arrivalStatus === 'Late').length)
const incompleteToday = computed(() => attendanceRecords.value.filter((record) => record.attendanceStatus === 'Incomplete').length)

function formatTime(value?: string) {
  if (!value) return 'Not recorded'
  return new Intl.DateTimeFormat('en-PH', {
    timeZone: attendanceTimezone.value,
    hour: 'numeric',
    minute: '2-digit',
    hour12: true,
  }).format(new Date(value))
}

function formatHours(value: number) {
  return `${Number(value || 0).toFixed(2)}h`
}

// GPS is captured afresh for every event and never reused between actions.
const showActionModal = ref(false)
const locationStatus = ref<'idle' | 'locating' | 'ready' | 'error'>('idle')
const locationError = ref('')
const userCoords = ref<{ lat: number; lng: number; accuracy: number } | null>(null)
const MAX_GPS_ACCURACY = 75

function requestLocation() {
  if (!navigator.geolocation) {
    locationStatus.value = 'error'
    locationError.value = 'This browser does not support location services.'
    return
  }
  locationStatus.value = 'locating'
  locationError.value = ''
  userCoords.value = null
  navigator.geolocation.getCurrentPosition(
    ({ coords }) => {
      userCoords.value = { lat: coords.latitude, lng: coords.longitude, accuracy: coords.accuracy }
      if (coords.accuracy > MAX_GPS_ACCURACY) {
        locationStatus.value = 'error'
        locationError.value = `GPS accuracy is insufficient (±${Math.round(coords.accuracy)}m). Move to an open area and try again.`
        return
      }
      locationStatus.value = 'ready'
    },
    (error) => {
      locationStatus.value = 'error'
      locationError.value = error.code === error.PERMISSION_DENIED
        ? 'Location permission was denied. Enable it to record attendance.'
        : 'Unable to determine your location. Check GPS and try again.'
    },
    { enableHighAccuracy: true, timeout: 15000, maximumAge: 0 },
  )
}

function openAttendanceAction() {
  if (!nextAction.value || !nextActionAvailable.value || isSubmitting.value) return
  actionError.value = ''
  showActionModal.value = true
  requestLocation()
}

function closeActionModal() {
  if (isSubmitting.value) return
  showActionModal.value = false
  locationStatus.value = 'idle'
  locationError.value = ''
  userCoords.value = null
}

async function confirmAttendanceAction() {
  if (!nextAction.value || !userCoords.value || locationStatus.value !== 'ready' || isSubmitting.value) return
  isSubmitting.value = true
  actionError.value = ''
  try {
    const raw = await submitAttendanceAction(nextAction.value, userCoords.value)
    const record = mapRecord(raw)
    attendanceRecords.value = [record]
    nextAction.value = raw.next_action
    nextActionAvailable.value = raw.next_action_available
    nextActionAvailableAt.value = raw.next_action_available_at
    nextActionMessage.value = raw.next_action_message
    scheduleAvailabilityRefresh()
    showActionModal.value = false
    locationStatus.value = 'idle'
    userCoords.value = null
  } catch (error) {
    const message = getUserFriendlyApiError(error)
    locationError.value = message
    actionError.value = message
  } finally {
    isSubmitting.value = false
  }
}

// Admin geofence settings
const attendanceLocation = ref<AttendanceSite | null>(null)
const settingsForm = reactive({ lat: 0, lng: 0, radius_meters: 150 })
const settingsMessage = ref('')
const settingsError = ref('')
const isSavingLocation = ref(false)
const mapContainer = ref<HTMLElement | null>(null)
let map: L.Map | null = null
let marker: L.Marker | null = null
let circle: L.Circle | null = null

function initializeMap() {
  if (!mapContainer.value || map) return
  const lat = settingsForm.lat || 13.1415
  const lng = settingsForm.lng || 123.4567
  map = L.map(mapContainer.value).setView([lat, lng], 15)
  L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', { maxZoom: 19, attribution: '© OpenStreetMap contributors' }).addTo(map)
  marker = L.marker([lat, lng], { draggable: true }).addTo(map)
  circle = L.circle([lat, lng], { radius: settingsForm.radius_meters, color: '#0284c7', fillColor: '#bae6fd', fillOpacity: 0.35 }).addTo(map)
  marker.on('dragend', () => {
    const point = marker?.getLatLng()
    if (point) {
      settingsForm.lat = Number(point.lat.toFixed(6))
      settingsForm.lng = Number(point.lng.toFixed(6))
    }
  })
}

watch(() => [settingsForm.lat, settingsForm.lng, settingsForm.radius_meters], ([lat, lng, radius]) => {
  if (!map || !marker || !circle || !Number.isFinite(Number(lat)) || !Number.isFinite(Number(lng))) return
  const point = L.latLng(Number(lat), Number(lng))
  marker.setLatLng(point)
  circle.setLatLng(point).setRadius(Number(radius) || 150)
  map.panTo(point)
})

async function loadGeofence() {
  attendanceLocation.value = await fetchAttendanceLocation()
  if (attendanceLocation.value) {
    settingsForm.lat = attendanceLocation.value.lat
    settingsForm.lng = attendanceLocation.value.lng
    settingsForm.radius_meters = attendanceLocation.value.radiusMeters
  }
  await nextTick()
  initializeMap()
}

function useAdminLocation() {
  settingsError.value = ''
  if (!navigator.geolocation) {
    settingsError.value = 'This browser does not support location services.'
    return
  }
  navigator.geolocation.getCurrentPosition(({ coords }) => {
    settingsForm.lat = Number(coords.latitude.toFixed(6))
    settingsForm.lng = Number(coords.longitude.toFixed(6))
    settingsMessage.value = 'Current coordinates captured. Save to apply the geofence.'
  }, (error) => { settingsError.value = error.message }, { enableHighAccuracy: true })
}

async function saveGeofence() {
  if (isSavingLocation.value) return
  isSavingLocation.value = true
  settingsMessage.value = ''
  settingsError.value = ''
  try {
    attendanceLocation.value = await setAttendanceLocation({ ...settingsForm })
    settingsMessage.value = 'Attendance geofence saved successfully.'
  } catch (error) {
    settingsError.value = getUserFriendlyApiError(error)
  } finally {
    isSavingLocation.value = false
  }
}

// Simple, audited Admin correction for missing/incorrect events.
const showCorrectionModal = ref(false)
const correctionRecord = ref<AttendanceRecord | null>(null)
const correctionForm = reactive({ morningIn: '', morningOut: '', afternoonIn: '', afternoonOut: '', reason: '' })
const correctionError = ref('')

function toLocalInput(value?: string) {
  if (!value) return ''
  const parts = new Intl.DateTimeFormat('sv-SE', {
    timeZone: attendanceTimezone.value, year: 'numeric', month: '2-digit', day: '2-digit', hour: '2-digit', minute: '2-digit', hour12: false,
  }).formatToParts(new Date(value))
  const part = (type: string) => parts.find((item) => item.type === type)?.value || ''
  return `${part('year')}-${part('month')}-${part('day')}T${part('hour')}:${part('minute')}`
}

function correctionIso(value: string) {
  return value ? new Date(`${value}:00+08:00`).toISOString() : undefined
}

function openCorrection(record: AttendanceRecord) {
  correctionRecord.value = record
  correctionForm.morningIn = toLocalInput(record.morningInAt)
  correctionForm.morningOut = toLocalInput(record.morningOutAt)
  correctionForm.afternoonIn = toLocalInput(record.afternoonInAt)
  correctionForm.afternoonOut = toLocalInput(record.afternoonOutAt)
  correctionForm.reason = ''
  correctionError.value = ''
  showCorrectionModal.value = true
}

async function saveCorrection() {
  if (!correctionRecord.value || correctionForm.reason.trim().length < 3 || isSubmitting.value) return
  isSubmitting.value = true
  correctionError.value = ''
  try {
    await correctAttendance(correctionRecord.value.id, {
      morning_in_at: correctionIso(correctionForm.morningIn),
      morning_out_at: correctionIso(correctionForm.morningOut),
      afternoon_in_at: correctionIso(correctionForm.afternoonIn),
      afternoon_out_at: correctionIso(correctionForm.afternoonOut),
      reason: correctionForm.reason.trim(),
    })
    await loadAttendance()
    showCorrectionModal.value = false
  } catch (error) {
    correctionError.value = getUserFriendlyApiError(error)
  } finally {
    isSubmitting.value = false
  }
}

onMounted(async () => {
  try {
    if (isAdmin.value) {
      await authStore.fetchStaffDirectory()
      await loadAttendance()
      await loadGeofence()
    } else {
      await loadAttendance()
    }
  } catch (error) {
    actionError.value = getUserFriendlyApiError(error)
  } finally {
    isLoading.value = false
  }
})

onBeforeUnmount(() => {
  if (availabilityTimer) window.clearTimeout(availabilityTimer)
  map?.remove()
  map = null
})
</script>

<template>
  <section class="relative space-y-6">
    <LocalLoader v-if="isLoading" />

    <header class="flex items-start gap-3">
      <div class="flex h-12 w-12 shrink-0 items-center justify-center rounded-xl bg-sky-50 ring-1 ring-sky-100">
        <Calendar class="dashboard-view-icon h-6 w-6 text-sky-600" />
      </div>
      <div>
        <h2 class="text-2xl font-semibold text-gray-900">Staff Attendance</h2>
        <p class="mt-1 text-sm text-gray-600">Four-event daily attendance · Philippine time</p>
      </div>
    </header>

    <div v-if="actionError" class="rounded-xl border border-red-200 bg-red-50 p-4 text-sm text-red-800">{{ actionError }}</div>

    <template v-if="!isAdmin">
      <div class="grid gap-4 lg:grid-cols-2">
        <article class="rounded-2xl border border-gray-200 bg-white p-5 sm:p-6">
          <div class="mb-5 flex items-center justify-between gap-3">
            <div>
              <p class="text-xs font-semibold uppercase tracking-wider text-sky-600">Morning Session</p>
              <h3 class="mt-1 text-lg font-semibold text-gray-900">Start of workday</h3>
            </div>
            <Clock3 class="h-5 w-5 text-sky-600" />
          </div>
          <div class="grid grid-cols-2 gap-4">
            <div class="rounded-xl bg-gray-50 p-4"><p class="text-xs text-gray-500">Time In</p><p class="mt-1 font-semibold text-gray-900">{{ formatTime(myAttendance?.morningInAt) }}</p></div>
            <div class="rounded-xl bg-gray-50 p-4"><p class="text-xs text-gray-500">Time Out</p><p class="mt-1 font-semibold text-gray-900">{{ formatTime(myAttendance?.morningOutAt) }}</p></div>
          </div>
          <div class="mt-4 flex items-center justify-between text-sm"><span class="text-gray-600">Arrival</span><span class="font-semibold" :class="myAttendance?.arrivalStatus === 'Late' ? 'text-amber-700' : 'text-emerald-700'">{{ myAttendance?.arrivalStatus || 'Pending' }}</span></div>
        </article>

        <article class="rounded-2xl border border-gray-200 bg-white p-5 sm:p-6">
          <div class="mb-5 flex items-center justify-between gap-3">
            <div><p class="text-xs font-semibold uppercase tracking-wider text-indigo-600">Afternoon Session</p><h3 class="mt-1 text-lg font-semibold text-gray-900">After lunch break</h3></div>
            <Clock3 class="h-5 w-5 text-indigo-600" />
          </div>
          <div class="grid grid-cols-2 gap-4">
            <div class="rounded-xl bg-gray-50 p-4"><p class="text-xs text-gray-500">Time In</p><p class="mt-1 font-semibold text-gray-900">{{ formatTime(myAttendance?.afternoonInAt) }}</p></div>
            <div class="rounded-xl bg-gray-50 p-4"><p class="text-xs text-gray-500">Time Out</p><p class="mt-1 font-semibold text-gray-900">{{ formatTime(myAttendance?.afternoonOutAt) }}</p></div>
          </div>
          <div class="mt-4 flex items-center justify-between text-sm"><span class="text-gray-600">Session hours</span><span class="font-semibold text-gray-900">{{ formatHours(myAttendance?.afternoonHours || 0) }}</span></div>
        </article>
      </div>

      <article class="rounded-2xl border border-gray-200 bg-white p-5 sm:p-6">
        <div class="grid gap-4 sm:grid-cols-2 lg:grid-cols-4">
          <div><p class="text-xs uppercase tracking-wide text-gray-500">Total Worked</p><p class="mt-1 text-2xl font-bold text-gray-900">{{ formatHours(myAttendance?.totalHoursWorked || 0) }}</p></div>
          <div><p class="text-xs uppercase tracking-wide text-gray-500">Regular</p><p class="mt-1 text-2xl font-bold text-gray-900">{{ formatHours(myAttendance?.regularHours || 0) }}</p></div>
          <div><p class="text-xs uppercase tracking-wide text-gray-500">Overtime</p><p class="mt-1 text-2xl font-bold text-gray-900">{{ formatHours(myAttendance?.overtimeHours || 0) }}</p></div>
          <div><p class="text-xs uppercase tracking-wide text-gray-500">Daily Status</p><p class="mt-1 text-lg font-bold" :class="myAttendance?.attendanceStatus === 'Completed' ? 'text-emerald-700' : 'text-amber-700'">{{ myAttendance?.attendanceStatus || 'Not Started' }}</p></div>
        </div>
      </article>

      <div class="rounded-2xl border border-sky-200 bg-sky-50 p-5">
        <div class="flex flex-col gap-4 sm:flex-row sm:items-center sm:justify-between">
          <div><p class="font-semibold text-sky-950">{{ nextActionLabel }}</p><p class="mt-1 text-sm text-sky-800">{{ nextActionMessage }}</p></div>
          <button v-if="nextAction && nextActionAvailable" type="button" class="rounded-xl bg-sky-600 px-5 py-3 font-semibold text-white hover:bg-sky-700 disabled:bg-gray-400" :disabled="isSubmitting" @click="openAttendanceAction">
            {{ nextActionLabel }}
          </button>
          <span v-else-if="!nextAction" class="inline-flex items-center gap-2 font-semibold text-emerald-700"><CheckCircle2 class="h-5 w-5" /> Completed</span>
        </div>
      </div>
    </template>

    <template v-else>
      <div class="grid gap-4 sm:grid-cols-2 xl:grid-cols-5">
        <div v-for="metric in [
          ['Attended Today', attendedToday], ['Currently On Site', currentlyOnSite], ['Completed', completedToday], ['Late Today', lateToday], ['Incomplete', incompleteToday],
        ]" :key="String(metric[0])" class="rounded-xl border border-gray-200 bg-white p-5">
          <p class="text-xs font-semibold uppercase tracking-wide text-gray-500">{{ metric[0] }}</p><p class="mt-2 text-2xl font-bold text-gray-900">{{ metric[1] }}</p>
        </div>
      </div>

      <article class="overflow-hidden rounded-2xl border border-gray-200 bg-white">
        <div class="border-b border-gray-200 px-5 py-4"><h3 class="font-semibold text-gray-900">Today's Attendance</h3><p class="mt-1 text-sm text-gray-500">Complete four-event status for every Staff member who attended today.</p></div>
        <div class="overflow-x-auto">
          <table class="w-full min-w-[700px] text-left text-sm">
            <thead class="border-b bg-gray-50 text-gray-500"><tr><th class="px-4 py-3">Staff</th><th class="px-4 py-3">Morning In</th><th class="px-4 py-3">Morning Out</th><th class="px-4 py-3">Afternoon In</th><th class="px-4 py-3">Afternoon Out</th><th class="px-4 py-3">Arrival</th><th class="px-4 py-3">Total</th><th class="px-4 py-3">Overtime</th><th class="px-4 py-3">Status</th><th class="px-4 py-3"><span class="sr-only">Actions</span></th></tr></thead>
            <tbody class="divide-y divide-gray-100">
              <tr v-if="attendanceRecords.length === 0"><td colspan="10" class="px-4 py-10 text-center text-gray-500">No attendance records for today.</td></tr>
              <tr v-for="record in attendanceRecords" :key="record.id">
                <td class="px-4 py-3 font-medium text-gray-900"><span class="block max-w-50 truncate" :title="record.staffName">{{ record.staffName }}</span><span v-if="record.manuallyModified" class="text-xs text-amber-700">Manually corrected</span></td>
                <td class="px-4 py-3">{{ formatTime(record.morningInAt) }}</td><td class="px-4 py-3">{{ formatTime(record.morningOutAt) }}</td><td class="px-4 py-3">{{ formatTime(record.afternoonInAt) }}</td><td class="px-4 py-3">{{ formatTime(record.afternoonOutAt) }}</td>
                <td class="px-4 py-3"><span :class="record.arrivalStatus === 'Late' ? 'text-amber-700' : 'text-emerald-700'" class="font-medium">{{ record.arrivalStatus || '—' }}</span></td>
                <td class="px-4 py-3 font-medium">{{ formatHours(record.totalHoursWorked) }}</td><td class="px-4 py-3">{{ formatHours(record.overtimeHours) }}</td>
                <td class="px-4 py-3"><span class="rounded-full px-2.5 py-1 text-xs font-semibold" :class="record.attendanceStatus === 'Completed' ? 'bg-emerald-50 text-emerald-700' : 'bg-amber-50 text-amber-700'">{{ record.attendanceStatus }}</span></td>
                <td class="px-4 py-3"><button type="button" class="rounded-lg p-2 text-sky-700 hover:bg-sky-50" aria-label="Correct attendance" @click="openCorrection(record)"><Pencil class="h-4 w-4" /></button></td>
              </tr>
            </tbody>
          </table>
        </div>
      </article>

      <article class="rounded-2xl border border-gray-200 bg-white p-5 sm:p-6">
        <div class="mb-5 flex items-center justify-between"><div><h3 class="font-semibold text-gray-900">Attendance Geofence</h3><p class="mt-1 text-sm text-gray-500">Required for every morning and afternoon attendance event.</p></div><span class="rounded-full px-3 py-1 text-xs font-semibold" :class="attendanceLocation ? 'bg-emerald-50 text-emerald-700' : 'bg-red-50 text-red-700'">{{ attendanceLocation ? 'Configured' : 'Required' }}</span></div>
        <form class="space-y-4" @submit.prevent="saveGeofence">
          <div class="grid gap-4 sm:grid-cols-3"><label class="text-sm font-medium text-gray-700">Latitude<input v-model.number="settingsForm.lat" required type="number" step="any" class="mt-1 w-full border border-gray-300 px-3 py-2" /></label><label class="text-sm font-medium text-gray-700">Longitude<input v-model.number="settingsForm.lng" required type="number" step="any" class="mt-1 w-full border border-gray-300 px-3 py-2" /></label><label class="text-sm font-medium text-gray-700">Radius (meters)<input v-model.number="settingsForm.radius_meters" required type="number" min="20" max="5000" class="mt-1 w-full border border-gray-300 px-3 py-2" /></label></div>
          <div class="overflow-hidden rounded-xl border border-gray-200"><div ref="mapContainer" class="h-64 w-full"></div></div>
          <p v-if="settingsMessage" class="rounded-lg bg-emerald-50 p-3 text-sm text-emerald-800">{{ settingsMessage }}</p><p v-if="settingsError" class="rounded-lg bg-red-50 p-3 text-sm text-red-800">{{ settingsError }}</p>
          <div class="flex flex-col gap-2 sm:flex-row sm:justify-between"><button type="button" class="inline-flex items-center justify-center gap-2 rounded-lg border border-gray-300 px-4 py-2 font-semibold text-gray-700 hover:bg-gray-50" @click="useAdminLocation"><MapPin class="h-4 w-4" /> Use My Location</button><button type="submit" :disabled="isSavingLocation" class="rounded-lg bg-sky-600 px-5 py-2 font-semibold text-white hover:bg-sky-700 disabled:bg-gray-400">{{ isSavingLocation ? 'Saving…' : 'Save Geofence' }}</button></div>
        </form>
      </article>
    </template>

    <ModalShell :show="showActionModal" :title="nextActionLabel" subtitle="GPS-verified attendance" tone="blue" size="sm" @close="closeActionModal">
      <div class="space-y-4"><div class="rounded-xl bg-sky-50 p-4"><p class="text-sm text-gray-600">Authoritative timezone</p><p class="font-semibold text-gray-900">Asia/Manila (Philippine time)</p></div><div class="rounded-xl border p-4" :class="locationStatus === 'ready' ? 'border-emerald-200 bg-emerald-50' : locationStatus === 'error' ? 'border-red-200 bg-red-50' : 'border-sky-200 bg-sky-50'"><div class="flex items-center justify-between"><p class="font-medium">Location verification</p><button v-if="locationStatus === 'error'" type="button" class="text-sm font-semibold text-sky-700" @click="requestLocation">Try again</button></div><p v-if="locationStatus === 'locating'" class="mt-2 text-sm text-sky-700">Getting a fresh GPS location…</p><p v-else-if="locationStatus === 'ready'" class="mt-2 text-sm text-emerald-700">GPS confirmed (±{{ Math.round(userCoords?.accuracy || 0) }}m)</p><p v-else-if="locationError" class="mt-2 text-sm text-red-700">{{ locationError }}</p></div></div>
      <template #footer><button type="button" class="rounded-xl border border-gray-300 px-4 py-3 font-semibold" :disabled="isSubmitting" @click="closeActionModal">Cancel</button><button type="button" class="rounded-xl bg-sky-600 px-4 py-3 font-semibold text-white disabled:bg-gray-400" :disabled="locationStatus !== 'ready' || isSubmitting" @click="confirmAttendanceAction">{{ isSubmitting ? 'Recording…' : `Confirm ${nextActionLabel}` }}</button></template>
    </ModalShell>

    <ModalShell :show="showCorrectionModal" title="Correct Attendance" subtitle="Admin-only audited correction" tone="amber" size="lg" @close="showCorrectionModal = false">
      <form id="attendance-correction-form" class="space-y-4" @submit.prevent="saveCorrection"><p class="rounded-xl bg-amber-50 p-3 text-sm text-amber-800">Changes are marked as manual and stored with your email, timestamp, and required reason.</p><div class="grid gap-4 sm:grid-cols-2"><label v-for="field in [{ key: 'morningIn', label: 'Morning In' }, { key: 'morningOut', label: 'Morning Out' }, { key: 'afternoonIn', label: 'Afternoon In' }, { key: 'afternoonOut', label: 'Afternoon Out' }]" :key="field.key" class="text-sm font-medium text-gray-700">{{ field.label }}<input v-model="correctionForm[field.key as keyof typeof correctionForm]" type="datetime-local" class="mt-1 w-full border border-gray-300 px-3 py-2" /></label></div><label class="block text-sm font-medium text-gray-700">Correction reason<textarea v-model="correctionForm.reason" required minlength="3" class="mt-1 w-full border border-gray-300 px-3 py-2" placeholder="Explain why this correction is required"></textarea></label><p v-if="correctionError" class="rounded-lg bg-red-50 p-3 text-sm text-red-800">{{ correctionError }}</p></form>
      <template #footer><button type="button" class="rounded-xl border border-gray-300 px-4 py-3 font-semibold" :disabled="isSubmitting" @click="showCorrectionModal = false">Cancel</button><button form="attendance-correction-form" type="submit" class="rounded-xl bg-amber-600 px-4 py-3 font-semibold text-white disabled:bg-gray-400" :disabled="isSubmitting || correctionForm.reason.trim().length < 3">{{ isSubmitting ? 'Saving…' : 'Save Correction' }}</button></template>
    </ModalShell>
  </section>
</template>
