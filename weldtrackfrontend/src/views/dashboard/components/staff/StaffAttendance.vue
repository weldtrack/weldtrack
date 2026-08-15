<script setup lang="ts">
import InfoTooltip from '../../../../components/ui/InfoTooltip.vue'
import { computed, nextTick, onBeforeUnmount, onMounted, reactive, ref, watch } from 'vue'
import L from 'leaflet'
import 'leaflet/dist/leaflet.css'
import markerIcon2x from 'leaflet/dist/images/marker-icon-2x.png'
import markerIcon from 'leaflet/dist/images/marker-icon.png'
import markerShadow from 'leaflet/dist/images/marker-shadow.png'

delete (L.Icon.Default.prototype as any)._getIconUrl
L.Icon.Default.mergeOptions({
  iconRetinaUrl: markerIcon2x,
  iconUrl: markerIcon,
  shadowUrl: markerShadow,
})
import { Calendar, CheckCircle2, Clock3, MapPin, Navigation, Pencil, ShieldCheck } from 'lucide-vue-next'
import LocalLoader from '../../../../components/ui/LocalLoader.vue'
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
const MAX_GPS_ACCURACY = 30
let staffLocationWatchId: number | null = null
let staffLocationTimeout: number | undefined

function stopStaffLocationWatch() {
  if (staffLocationWatchId !== null) navigator.geolocation.clearWatch(staffLocationWatchId)
  staffLocationWatchId = null
  if (staffLocationTimeout) window.clearTimeout(staffLocationTimeout)
  staffLocationTimeout = undefined
}

function requestLocation() {
  if (!navigator.geolocation) {
    locationStatus.value = 'error'
    locationError.value = 'This browser does not support location services.'
    return
  }
  locationStatus.value = 'locating'
  locationError.value = ''
  userCoords.value = null
  stopStaffLocationWatch()
  let bestPosition: GeolocationPosition | null = null

  const finish = () => {
    stopStaffLocationWatch()
    if (!bestPosition || bestPosition.coords.accuracy > MAX_GPS_ACCURACY) {
      const accuracy = bestPosition ? ` Best reading: ±${Math.round(bestPosition.coords.accuracy)}m.` : ''
      locationStatus.value = 'error'
      locationError.value = `A precise GPS position is required (±${MAX_GPS_ACCURACY}m or better).${accuracy} Move outdoors, enable precise location, and try again.`
      userCoords.value = null
      return
    }

    const { latitude, longitude, accuracy } = bestPosition.coords
    userCoords.value = { lat: latitude, lng: longitude, accuracy }
    locationStatus.value = 'ready'
  }

  staffLocationWatchId = navigator.geolocation.watchPosition(
    (position) => {
      if (!bestPosition || position.coords.accuracy < bestPosition.coords.accuracy) bestPosition = position
      if (position.coords.accuracy <= MAX_GPS_ACCURACY) finish()
    },
    (error) => {
      stopStaffLocationWatch()
      locationStatus.value = 'error'
      userCoords.value = null
      locationError.value = error.code === error.PERMISSION_DENIED
        ? 'Precise location permission was denied. Enable it to record attendance.'
        : 'Unable to determine a precise location. Enable GPS and try again.'
    },
    { enableHighAccuracy: true, timeout: 15000, maximumAge: 0 },
  )
  staffLocationTimeout = window.setTimeout(finish, 12000)
}

function openAttendanceAction() {
  if (!nextAction.value || !nextActionAvailable.value || isSubmitting.value) return
  actionError.value = ''
  showActionModal.value = true
  requestLocation()
}

function closeActionModal() {
  if (isSubmitting.value) return
  stopStaffLocationWatch()
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
    stopStaffLocationWatch()
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

// Admin attendance work-area settings
const attendanceLocation = ref<AttendanceSite | null>(null)
const settingsForm = reactive({ lat: 0, lng: 0, radius_meters: 150 })
const settingsMessage = ref('')
const settingsError = ref('')
const isSavingLocation = ref(false)
const isLocatingAdmin = ref(false)
const mapContainer = ref<HTMLElement | null>(null)
let map: L.Map | null = null
let marker: L.Marker | null = null
let circle: L.Circle | null = null
let adminLocationWatchId: number | null = null
let adminLocationTimeout: number | undefined

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

async function loadAttendanceWorkArea() {
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
  settingsMessage.value = ''
  if (!navigator.geolocation) {
    settingsError.value = 'This browser does not support location services.'
    return
  }

  if (adminLocationWatchId !== null) navigator.geolocation.clearWatch(adminLocationWatchId)
  if (adminLocationTimeout) window.clearTimeout(adminLocationTimeout)
  isLocatingAdmin.value = true

  let bestPosition: GeolocationPosition | null = null

  const finish = () => {
    if (adminLocationWatchId !== null) navigator.geolocation.clearWatch(adminLocationWatchId)
    adminLocationWatchId = null
    if (adminLocationTimeout) window.clearTimeout(adminLocationTimeout)
    adminLocationTimeout = undefined
    isLocatingAdmin.value = false

    if (!bestPosition || bestPosition.coords.accuracy > MAX_GPS_ACCURACY) {
      const accuracy = bestPosition ? ` (best reading ±${Math.round(bestPosition.coords.accuracy)}m)` : ''
      settingsError.value = `Unable to get an accurate GPS position${accuracy}. Use a GPS-enabled phone, enable precise location, move outdoors, and try again.`
      return
    }

    const { latitude, longitude, accuracy } = bestPosition.coords
    settingsForm.lat = Number(latitude.toFixed(6))
    settingsForm.lng = Number(longitude.toFixed(6))
    settingsMessage.value = `Location captured with ±${Math.round(accuracy)}m accuracy. Check the marker and work-area boundary, then save.`
    map?.setView([latitude, longitude], 18)
  }

  adminLocationWatchId = navigator.geolocation.watchPosition(
    (position) => {
      if (!bestPosition || position.coords.accuracy < bestPosition.coords.accuracy) bestPosition = position
      if (position.coords.accuracy <= 25) finish()
    },
    (error) => {
      if (adminLocationWatchId !== null) navigator.geolocation.clearWatch(adminLocationWatchId)
      adminLocationWatchId = null
      if (adminLocationTimeout) window.clearTimeout(adminLocationTimeout)
      adminLocationTimeout = undefined
      isLocatingAdmin.value = false
      settingsError.value = error.code === error.PERMISSION_DENIED
        ? 'Precise location permission was denied. Allow it in your browser settings and try again.'
        : 'Unable to determine your location. Enable GPS and precise location, then try again.'
    },
    { enableHighAccuracy: true, timeout: 15000, maximumAge: 0 },
  )

  adminLocationTimeout = window.setTimeout(finish, 12000)
}

async function saveAttendanceWorkArea() {
  if (isSavingLocation.value) return
  isSavingLocation.value = true
  settingsMessage.value = ''
  settingsError.value = ''
  try {
    attendanceLocation.value = await setAttendanceLocation({ ...settingsForm })
    settingsMessage.value = 'Attendance work area saved successfully.'
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
      await loadAttendanceWorkArea()
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
  stopStaffLocationWatch()
  if (adminLocationWatchId !== null) navigator.geolocation.clearWatch(adminLocationWatchId)
  if (adminLocationTimeout) window.clearTimeout(adminLocationTimeout)
  map?.remove()
  map = null
})
</script>

<template>
  <section class="relative space-y-6">
    <LocalLoader v-if="isLoading" />

    <header class="flex items-start gap-3">
      <div class="flex h-12 w-12 shrink-0 items-center justify-center rounded-xl ">
        <Calendar class="dashboard-view-icon h-6 w-6 text-sky-600" />
      </div>
      <div>
        <h2 class="text-2xl font-semibold text-gray-900">Staff Attendance</h2>
        <p class="mt-1 text-sm text-gray-600">Four-event daily attendance · Philippine time</p>
      </div>
    </header>

    <div v-if="actionError" class="rounded-xl border border-red-200 bg-red-50 p-4 text-sm text-red-800">{{ actionError }}</div>

    <template v-if="!showActionModal && !showCorrectionModal">
      <template v-if="!isAdmin">
        <div class="rounded-2xl border border-sky-200 bg-sky-50 p-4 text-sm text-sky-900">
          <p class="font-semibold">Attendance windows · Philippine time</p>
          <p class="mt-1 text-sky-800">Morning Time In: 6:00–8:00 AM · Afternoon Time In: 12:00–2:00 PM · Work beyond 8 total hours is recorded as overtime.</p>
        </div>

        <div class="grid gap-4 lg:grid-cols-2">
          <article class="rounded-2xl border border-gray-200 bg-white p-5 sm:p-6">
            <div class="mb-5 flex items-center justify-between gap-3">
              <div>
                <p class="text-xs font-semibold uppercase tracking-wider text-sky-600">Morning Session · 6:00–8:00 AM Time In</p>
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
              <div><p class="text-xs font-semibold uppercase tracking-wider text-indigo-600">Afternoon Session · 12:00–2:00 PM Time In</p><h3 class="mt-1 text-lg font-semibold text-gray-900">After lunch break</h3></div>
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
            <button
              v-if="nextAction"
              type="button"
              class="rounded-xl px-5 py-3 font-semibold transition-colors"
              :class="nextActionAvailable
                ? 'bg-sky-600 text-white hover:bg-sky-700'
                : 'cursor-not-allowed border border-slate-200 bg-slate-100 text-slate-400'"
              :disabled="!nextActionAvailable || isSubmitting"
              :aria-disabled="!nextActionAvailable || isSubmitting"
              :title="nextActionAvailable ? nextActionLabel : nextActionMessage"
              @click="openAttendanceAction"
            >
              {{ nextActionAvailable ? nextActionLabel : `${nextActionLabel} · Unavailable Now` }}
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

        <article class="overflow-hidden rounded-2xl border border-slate-200 bg-white shadow-sm">
          <div class="border-b border-slate-200 bg-linear-to-r from-sky-50 via-white to-white px-5 py-5 sm:px-6">
            <div class="flex flex-col gap-4 sm:flex-row sm:items-start sm:justify-between">
              <div class="flex gap-3.5">
                <div class="flex h-11 w-11 shrink-0 items-center justify-center rounded-xl bg-sky-600 text-white shadow-sm shadow-sky-200">
                  <MapPin class="h-5 w-5" />
                </div>
                <div>
                  <h3 class="text-lg font-bold text-slate-900">Attendance Work Area</h3>
                  <p class="mt-1 max-w-2xl text-sm leading-6 text-slate-600">Choose the approved workplace where staff can time in and out. Attendance is accepted only while they are inside the distance shown on the map.</p>
                </div>
              </div>
              <span class="inline-flex w-fit items-center gap-1.5 rounded-full px-3 py-1.5 text-xs font-bold" :class="attendanceLocation ? 'bg-emerald-100 text-emerald-800' : 'bg-amber-100 text-amber-800'">
                <CheckCircle2 v-if="attendanceLocation" class="h-3.5 w-3.5" />
                <ShieldCheck v-else class="h-3.5 w-3.5" />
                {{ attendanceLocation ? 'Work area active' : 'Setup required' }}
              </span>
            </div>
          </div>

          <form class="grid gap-0 lg:grid-cols-[minmax(0,1.45fr)_minmax(20rem,0.75fr)]" @submit.prevent="saveAttendanceWorkArea">
            <div class="border-b border-slate-200 p-5 lg:border-b-0 lg:border-r sm:p-6">
              <div class="mb-3 flex items-center justify-between gap-3">
                <div>
                  <p class="font-semibold text-slate-900">Work area map</p>
                  <p class="mt-0.5 text-xs text-slate-500">Drag the marker to adjust the workplace center.</p>
                </div>
                <span class="rounded-lg bg-sky-50 px-2.5 py-1 text-xs font-semibold text-sky-700">{{ settingsForm.radius_meters }} m allowed distance</span>
              </div>
              <div class="overflow-hidden rounded-xl border border-slate-200 bg-slate-100 shadow-inner">
                <div ref="mapContainer" class="h-80 w-full sm:h-96"></div>
              </div>
              <div class="mt-3 flex items-start gap-2 rounded-xl bg-slate-50 px-3.5 py-3 text-xs leading-5 text-slate-600">
                <ShieldCheck class="mt-0.5 h-4 w-4 shrink-0 text-sky-600" />
                The blue circle is the approved attendance area. Staff outside it will be asked to move closer before recording attendance.
              </div>
            </div>

            <div class="flex flex-col p-5 sm:p-6">
              <div>
                <p class="font-semibold text-slate-900">Workplace details</p>
                <p class="mt-1 text-sm text-slate-500">Capture your current position or enter the exact coordinates.</p>
              </div>

              <button type="button" :disabled="isLocatingAdmin" class="mt-5 inline-flex w-full items-center justify-center gap-2 rounded-xl border border-sky-200 bg-sky-50 px-4 py-3 text-sm font-bold text-sky-700 transition hover:bg-sky-100 disabled:cursor-wait disabled:opacity-60" @click="useAdminLocation">
                <Navigation class="h-4 w-4" :class="isLocatingAdmin ? 'animate-pulse' : ''" />
                {{ isLocatingAdmin ? 'Finding your precise location…' : 'Set to My Current Location' }}
              </button>

              <div class="my-5 flex items-center gap-3 text-xs font-semibold uppercase tracking-wider text-slate-400">
                <span class="h-px flex-1 bg-slate-200"></span>Precise settings<span class="h-px flex-1 bg-slate-200"></span>
              </div>

              <div class="space-y-4">
                <div class="grid gap-4 sm:grid-cols-2 lg:grid-cols-1 xl:grid-cols-2">
                  <div>
                    <label for="attendance-work-area-lat" class="mb-1.5 flex items-center text-sm font-semibold text-slate-700">Latitude<InfoTooltip text="The north-south coordinate of the workplace center." /></label>
                    <input id="attendance-work-area-lat" v-model.number="settingsForm.lat" required type="number" step="any" class="w-full rounded-xl border border-slate-300 bg-white px-3.5 py-2.5 text-sm outline-none transition focus:border-sky-500 focus:ring-2 focus:ring-sky-200" />
                  </div>
                  <div>
                    <label for="attendance-work-area-lng" class="mb-1.5 flex items-center text-sm font-semibold text-slate-700">Longitude<InfoTooltip text="The east-west coordinate of the workplace center." /></label>
                    <input id="attendance-work-area-lng" v-model.number="settingsForm.lng" required type="number" step="any" class="w-full rounded-xl border border-slate-300 bg-white px-3.5 py-2.5 text-sm outline-none transition focus:border-sky-500 focus:ring-2 focus:ring-sky-200" />
                  </div>
                </div>
                <div>
                  <label for="attendance-work-area-distance" class="mb-1.5 flex items-center text-sm font-semibold text-slate-700">Allowed distance from workplace<InfoTooltip text="Staff must be within this distance of the marker to record attendance." /></label>
                  <div class="relative">
                    <input id="attendance-work-area-distance" v-model.number="settingsForm.radius_meters" required type="number" min="20" max="5000" class="w-full rounded-xl border border-slate-300 bg-white px-3.5 py-2.5 pr-16 text-sm outline-none transition focus:border-sky-500 focus:ring-2 focus:ring-sky-200" />
                    <span class="pointer-events-none absolute right-3.5 top-1/2 -translate-y-1/2 text-sm font-medium text-slate-400">meters</span>
                  </div>
                  <p class="mt-1.5 text-xs text-slate-500">Recommended: 50–150 meters for a typical workplace.</p>
                </div>
              </div>

              <div class="mt-5 space-y-3">
                <p v-if="settingsMessage" class="rounded-xl border border-emerald-200 bg-emerald-50 p-3 text-sm font-medium text-emerald-800">{{ settingsMessage }}</p>
                <p v-if="settingsError" class="rounded-xl border border-red-200 bg-red-50 p-3 text-sm font-medium text-red-800">{{ settingsError }}</p>
              </div>

              <button type="submit" :disabled="isSavingLocation || isLocatingAdmin" class="mt-auto w-full rounded-xl bg-sky-600 px-5 py-3 text-sm font-bold text-white shadow-sm shadow-sky-200 transition hover:bg-sky-700 disabled:cursor-not-allowed disabled:bg-slate-300 disabled:shadow-none">
                {{ isSavingLocation ? 'Saving work area…' : 'Save Attendance Work Area' }}
              </button>
            </div>
          </form>
        </article>
      </template>
    </template>

    <!-- Action View (GPS verified attendance) -->
    <template v-else-if="showActionModal">
      <div class="rounded-xl border border-slate-200 bg-white shadow-sm dark:border-slate-800 dark:bg-slate-900 max-w-xl mx-auto">
        <div class="border-b border-slate-100 px-6 py-5 flex items-center justify-between bg-transparent">
          <div>
            <h3 class="text-xl font-bold text-slate-900">{{ nextActionLabel }}</h3>
            <p class="text-sm text-slate-500 mt-1">GPS-verified attendance</p>
          </div>
          <button 
            @click="closeActionModal" 
            class="text-sm font-semibold text-slate-600 hover:text-slate-900 transition-colors"
          >
            Cancel
          </button>
        </div>
        <div class="p-6 space-y-6">
          <div class="rounded-xl border border-sky-100 bg-sky-50 px-5 py-4">
            <p class="text-sm text-gray-600 font-medium">Authoritative timezone</p>
            <p class="font-bold text-sky-900 mt-1">Asia/Manila (Philippine time)</p>
          </div>
          
          <div class="rounded-xl border p-5" :class="locationStatus === 'ready' ? 'border-emerald-200 bg-emerald-50' : locationStatus === 'error' ? 'border-red-200 bg-red-50' : 'border-sky-200 bg-sky-50'">
            <div class="flex items-center justify-between">
              <p class="font-bold text-slate-900">Location verification</p>
              <button v-if="locationStatus === 'error'" type="button" class="text-sm font-semibold text-sky-700 hover:text-sky-800" @click="requestLocation">Try again</button>
            </div>
            <p v-if="locationStatus === 'locating'" class="mt-2 text-sm font-medium text-sky-700">Getting a fresh GPS location…</p>
            <p v-else-if="locationStatus === 'ready'" class="mt-2 text-sm font-medium text-emerald-700">GPS confirmed (±{{ Math.round(userCoords?.accuracy || 0) }}m)</p>
            <p v-else-if="locationError" class="mt-2 text-sm font-medium text-red-700">{{ locationError }}</p>
          </div>

          <div class="pt-4 border-t border-slate-100 flex justify-end gap-3">
            <button type="button" class="rounded-xl border border-slate-200 bg-white px-6 py-2.5 font-semibold text-slate-700 shadow-sm hover:bg-slate-50 transition-colors" :disabled="isSubmitting" @click="closeActionModal">Cancel</button>
            <button type="button" class="rounded-xl bg-linear-to-r from-sky-600 to-blue-600 px-8 py-2.5 font-semibold text-white shadow-md shadow-sky-600/20 hover:from-sky-700 hover:to-blue-700 disabled:opacity-50 disabled:cursor-not-allowed transition-all" :disabled="locationStatus !== 'ready' || isSubmitting" @click="confirmAttendanceAction">
              {{ isSubmitting ? 'Recording…' : `Confirm ${nextActionLabel}` }}
            </button>
          </div>
        </div>
      </div>
    </template>

    <!-- Admin Correction View -->
    <template v-else-if="showCorrectionModal">
      <div class="rounded-xl border border-slate-200 bg-white shadow-sm dark:border-slate-800 dark:bg-slate-900 max-w-2xl mx-auto">
        <div class="border-b border-slate-100 px-6 py-5 flex items-center justify-between bg-transparent">
          <div>
            <h3 class="text-xl font-bold text-slate-900">Correct Attendance</h3>
            <p class="text-sm text-slate-500 mt-1">Admin-only audited correction</p>
          </div>
          <button 
            @click="showCorrectionModal = false" 
            class="text-sm font-semibold text-slate-600 hover:text-slate-900 transition-colors"
          >
            Cancel
          </button>
        </div>
        
        <div class="p-6">
          <form id="attendance-correction-form" class="space-y-6" @submit.prevent="saveCorrection">
            <p class="rounded-xl border border-amber-200 bg-amber-50 px-5 py-4 text-sm font-medium text-amber-800">
              Changes are marked as manual and stored with your email, timestamp, and required reason.
            </p>
            
            <div class="grid gap-6 sm:grid-cols-2">
              <div v-for="field in [{ key: 'morningIn', label: 'Morning In' }, { key: 'morningOut', label: 'Morning Out' }, { key: 'afternoonIn', label: 'Afternoon In' }, { key: 'afternoonOut', label: 'Afternoon Out' }]" :key="field.key">
                <label class="flex items-center text-sm font-semibold text-gray-700 mb-1.5">{{ field.label }}<InfoTooltip text="Please provide the fieldlabel." /></label>
                <input v-model="correctionForm[field.key as keyof typeof correctionForm]" type="datetime-local" class="w-full rounded-xl border border-slate-200 bg-white px-4 py-3 shadow-sm outline-none focus:border-amber-500 focus:ring-2 focus:ring-amber-200 transition" />
              </div>
            </div>
            
            <div>
              <label class="flex items-center text-sm font-semibold text-gray-700 mb-1.5">Correction reason <span class="text-red-500">*</span><InfoTooltip text="Please provide the correction reason." /></label>
              <textarea v-model="correctionForm.reason" required minlength="3" rows="4" class="w-full rounded-xl border border-slate-200 bg-white px-4 py-3 shadow-sm outline-none focus:border-amber-500 focus:ring-2 focus:ring-amber-200 transition" placeholder="Explain why this correction is required"></textarea>
            </div>
            
            <p v-if="correctionError" class="rounded-xl bg-red-50 p-4 text-sm font-medium text-red-800 border border-red-200">{{ correctionError }}</p>
            
            <div class="pt-4 border-t border-slate-100 flex justify-end gap-3">
              <button type="button" class="rounded-xl border border-slate-200 bg-white px-6 py-2.5 font-semibold text-slate-700 shadow-sm hover:bg-slate-50 transition-colors" :disabled="isSubmitting" @click="showCorrectionModal = false">Cancel</button>
              <button type="submit" class="rounded-xl bg-linear-to-r from-amber-600 to-orange-600 px-8 py-2.5 font-semibold text-white shadow-md shadow-amber-600/20 disabled:opacity-50 disabled:cursor-not-allowed hover:from-amber-700 hover:to-orange-700 transition-all" :disabled="isSubmitting || correctionForm.reason.trim().length < 3">
                {{ isSubmitting ? 'Saving…' : 'Save Correction' }}
              </button>
            </div>
          </form>
        </div>
      </div>
    </template>
  </section>
</template>
