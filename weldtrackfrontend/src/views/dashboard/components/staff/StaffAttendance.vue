<script setup lang="ts">
import { ref, computed, onMounted, onUnmounted, watch, nextTick } from 'vue'
import LocalLoader from '../../../../components/ui/LocalLoader.vue'
import { Calendar } from 'lucide-vue-next'
import axios from 'axios'
import L from 'leaflet'
import 'leaflet/dist/leaflet.css'
import { useAuthStore } from '../../../../stores/auth'
import api from '../../../../api/api'
import {
  fetchAttendanceRecords,
  toAttendanceRecord,
  checkIn,
  checkOut,
} from '../../../../api/attendance'
import {
  fetchAttendanceLocation,
  setAttendanceLocation,
} from '../../../../api/settings'
import { getUserFriendlyApiError } from '../../../../services/errorMessage'
import ModalShell from '../../../../components/ui/ModalShell.vue'
import type { AttendanceRecord, AttendanceSite } from '../../../../types/attendance'

const authStore = useAuthStore()
const isAdmin = computed(() => authStore.role === 'admin')
const currentUserEmail = ref('')

const attendanceRecords = ref<AttendanceRecord[]>([])

const currentStaffEmail = ref<string>('')
const showCheckInModal = ref(false)
const checkInAction = ref<'checkin' | 'checkout'>('checkin')
const actionMessage = ref('')
const WORK_DAY_HOURS = 8
const nowTick = ref(Date.now())
let tickTimer: number | undefined

// A GPS reading with a large accuracy radius is too unreliable to trust for
// a site check-in (and is also what a spoofed/mocked location often looks
// like), so readings worse than this are rejected and the user is asked to
// retry rather than silently accepted.
const MAX_LOCATION_ACCURACY_METERS = 75

type LocationStatus = 'idle' | 'locating' | 'ready' | 'error' | 'unsupported'

const locationStatus = ref<LocationStatus>('idle')
const locationError = ref('')
const userCoords = ref<{ lat: number; lng: number; accuracy: number } | null>(null)

// Geofence settings (admin only)
const attendanceLocation = ref<AttendanceSite | null>(null)
const settingsForm = ref({
  lat: 0,
  lng: 0,
  radius_meters: 150,
})
const settingsSuccess = ref('')
const settingsError = ref('')
const isFetchingLocation = ref(false)
const isSavingLocation = ref(false)

// Map variables
const mapContainer = ref<HTMLElement | null>(null)
let leafletMap: L.Map | null = null
let mapMarker: L.Marker | null = null
let mapCircle: L.Circle | null = null

function initMap() {
  if (!mapContainer.value) return

  const defaultLat = settingsForm.value.lat || 13.1415
  const defaultLng = settingsForm.value.lng || 123.4567

  // Create map instance
  leafletMap = L.map(mapContainer.value).setView([defaultLat, defaultLng], 15)

  // Use OpenStreetMap style tiles
  L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
    maxZoom: 19,
    attribution: '© OpenStreetMap contributors',
  }).addTo(leafletMap)

  // Add marker
  mapMarker = L.marker([defaultLat, defaultLng], { draggable: true }).addTo(leafletMap)

  // Sync drag events back to settings inputs
  mapMarker.on('dragend', () => {
    if (mapMarker) {
      const position = mapMarker.getLatLng()
      settingsForm.value.lat = Number(position.lat.toFixed(6))
      settingsForm.value.lng = Number(position.lng.toFixed(6))
    }
  })

  // Add Geofence circle
  mapCircle = L.circle([defaultLat, defaultLng], {
    color: '#0284c7',
    fillColor: '#bae6fd',
    fillOpacity: 0.4,
    radius: settingsForm.value.radius_meters,
  }).addTo(leafletMap)
}

// Watch inputs and update map dynamically
watch(
  () => [settingsForm.value.lat, settingsForm.value.lng, settingsForm.value.radius_meters],
  ([newLat, newLng, newRadius]) => {
    const latNum = Number(newLat)
    const lngNum = Number(newLng)
    const radNum = Number(newRadius)

    if (isNaN(latNum) || isNaN(lngNum) || !leafletMap) return

    const newLatLng = new L.LatLng(latNum, lngNum)

    if (mapMarker) {
      mapMarker.setLatLng(newLatLng)
    }
    if (mapCircle) {
      mapCircle.setLatLng(newLatLng)
      if (!isNaN(radNum)) {
        mapCircle.setRadius(radNum)
      }
    }
    leafletMap.panTo(newLatLng)
  },
  { deep: true }
)

async function loadAttendanceLocation() {
  if (!isAdmin.value) return
  isFetchingLocation.value = true
  try {
    const loc = await fetchAttendanceLocation()
    if (loc) {
      attendanceLocation.value = loc
      settingsForm.value.lat = loc.lat
      settingsForm.value.lng = loc.lng
      settingsForm.value.radius_meters = loc.radiusMeters
    }
  } catch (error) {
    console.error('Failed to load geofence settings:', error)
  } finally {
    isFetchingLocation.value = false
  }
}

async function saveGeofenceLocation() {
  settingsSuccess.value = ''
  settingsError.value = ''
  isSavingLocation.value = true
  try {
    const saved = await setAttendanceLocation({
      lat: Number(settingsForm.value.lat),
      lng: Number(settingsForm.value.lng),
      radius_meters: Number(settingsForm.value.radius_meters),
    })
    attendanceLocation.value = saved
    settingsSuccess.value = 'Geofence location updated successfully.'
  } catch (error) {
    settingsError.value = getUserFriendlyApiError(error)
  } finally {
    isSavingLocation.value = false
  }
}

function captureCurrentAdminLocation() {
  if (!('geolocation' in navigator)) {
    settingsError.value = 'Geolocation is not supported by your browser.'
    return
  }
  settingsSuccess.value = ''
  settingsError.value = ''
  navigator.geolocation.getCurrentPosition(
    (position) => {
      settingsForm.value.lat = position.coords.latitude
      settingsForm.value.lng = position.coords.longitude
      settingsSuccess.value = `Captured current coordinates: ${position.coords.latitude.toFixed(6)}, ${position.coords.longitude.toFixed(6)}`
    },
    (error) => {
      settingsError.value = 'Failed to get current location: ' + error.message
    },
    { enableHighAccuracy: true }
  )
}

const newRecordForm = ref({
  email: '',
})

const currentStaffLabel = computed(() =>
  newRecordForm.value.email
    ? authStore.getStaffLabel(newRecordForm.value.email, newRecordForm.value.email)
    : '-',
)

async function fetchCurrentUser() {
  try {
    const { data } = await api.get('/auth/me')
    currentUserEmail.value = data?.email ?? ''
  } catch (error) {
    actionMessage.value = getUserFriendlyApiError(error)
    currentUserEmail.value = ''
  }
}

async function fetchAttendance() {
  try {
    const raw = await fetchAttendanceRecords()
    attendanceRecords.value = raw.map((r) =>
      toAttendanceRecord(r, (email, fallback) =>
        authStore.getStaffLabel(email, fallback),
      ),
    )
  } catch (error) {
    if (axios.isAxiosError(error) && error.response?.status === 404) {
      attendanceRecords.value = []
      actionMessage.value = ''
      return
    }

    actionMessage.value = getUserFriendlyApiError(error)
    attendanceRecords.value = []
  }
}

const todayAttendance = computed(() => {
  const today = new Date().toISOString().split('T')[0]
  return attendanceRecords.value.filter((record) => record.date === today)
})

const totalStaffHours = computed(() => {
  return todayAttendance.value.reduce((sum, record) => {
    if (record.checkOutAt) return sum + Number(record.hoursWorked ?? 0)

    if (record.checkInAt) {
      const hours = getHoursBetween(record.checkInAt, new Date(nowTick.value).toISOString())
      return sum + round2(hours)
    }

    return sum
  }, 0)
})

const totalOvertimeHours = computed(() => {
  return todayAttendance.value.reduce((sum, record) => {
    if (record.checkOutAt) return sum + Number(record.overtimeHours ?? 0)

    if (record.checkInAt) {
      const hours = getHoursBetween(record.checkInAt, new Date(nowTick.value).toISOString())
      const overtime = Math.max(0, round2(hours) - WORK_DAY_HOURS)
      return sum + overtime
    }

    return sum
  }, 0)
})

const presentToday = computed(() => {
  return todayAttendance.value.length
})

const myTodayAttendance = computed(() => {
  return todayAttendance.value.find((record) => record.email === currentUserEmail.value)
})

const myHoursWorkedToday = computed(() => {
  const record = myTodayAttendance.value
  if (!record) return 0

  if (!record.checkOutAt) {
    const hours = getHoursBetween(record.checkInAt, new Date(nowTick.value).toISOString())
    return round2(hours)
  }

  return record.hoursWorked
})

const myOvertimeHours = computed(() => {
  const currentHours = myHoursWorkedToday.value
  return round2(Math.max(0, currentHours - WORK_DAY_HOURS))
})

const myRegularHoursToday = computed(() => {
  return round2(Math.min(myHoursWorkedToday.value, WORK_DAY_HOURS))
})

const canTimeOutNow = computed(() => {
  const record = myTodayAttendance.value
  if (!record || record.checkOutAt) return false

  const hours = getHoursBetween(record.checkInAt, new Date(nowTick.value).toISOString())
  return hours >= WORK_DAY_HOURS
})

const remainingHoursBeforeTimeOut = computed(() => {
  const record = myTodayAttendance.value
  if (!record || record.checkOutAt) return 0

  const hours = getHoursBetween(record.checkInAt, new Date(nowTick.value).toISOString())
  return Math.max(0, WORK_DAY_HOURS - hours)
})

const checkInStatus = computed(() => {
  const date = new Date(nowTick.value)
  const hours = date.getHours()
  const minutes = date.getMinutes()
  const timeInMinutes = hours * 60 + minutes

  if (timeInMinutes < 420) {
    return { allowed: false, status: 'early', message: 'Too early to check in. Check-in starts at 7:00 AM.' }
  } else if (timeInMinutes >= 540) {
    return { allowed: false, status: 'too_late', message: 'Check-in is no longer allowed after 9:00 AM.' }
  } else if (timeInMinutes >= 480) {
    return { allowed: true, status: 'late', message: "You're late." }
  }
  return { allowed: true, status: 'normal', message: '' }
})

const timeButtonLabel = computed(() => {
  const record = myTodayAttendance.value
  if (!record) {
    if (checkInStatus.value.status === 'early') {
      return 'Too Early to Check In'
    }
    if (checkInStatus.value.status === 'too_late') {
      return 'Check-in Closed'
    }
    return 'Check In'
  }
  if (record.checkOutAt) return 'Timed Out For Today'
  if (canTimeOutNow.value) return 'Time Out'

  return `Time Out Available In ${formatDuration(remainingHoursBeforeTimeOut.value)}`
})

const isTimeButtonDisabled = computed(() => {
  const record = myTodayAttendance.value
  if (!record) {
    return !checkInStatus.value.allowed
  }
  if (record.checkOutAt) return true

  return !canTimeOutNow.value
})

const canConfirmAttendance = computed(() => {
  if (locationStatus.value !== 'ready' || !userCoords.value) return false
  return userCoords.value.accuracy <= MAX_LOCATION_ACCURACY_METERS
})

const isLoading = ref(true)

onMounted(async () => {
  isLoading.value = true
  try {
    await fetchCurrentUser()
    try {
      if (authStore.role === 'admin') {
        await authStore.fetchStaffDirectory()
        await loadAttendanceLocation()
        nextTick(() => {
          initMap()
        })
      }
    } catch (err) {
    }

    await fetchAttendance()

    tickTimer = window.setInterval(() => {
      nowTick.value = Date.now()
    }, 30000)
  } finally {
    isLoading.value = false
  }
})

onUnmounted(() => {
  if (tickTimer) window.clearInterval(tickTimer)
})

function requestLocation() {
  if (!('geolocation' in navigator)) {
    locationStatus.value = 'unsupported'
    locationError.value = 'This device/browser does not support location. Ask an admin to record this manually.'
    return
  }

  locationStatus.value = 'locating'
  locationError.value = ''
  userCoords.value = null

  navigator.geolocation.getCurrentPosition(
    (position) => {
      const { latitude, longitude, accuracy } = position.coords
      userCoords.value = { lat: latitude, lng: longitude, accuracy }

      if (accuracy > MAX_LOCATION_ACCURACY_METERS) {
        locationStatus.value = 'error'
        locationError.value = `Location signal is too weak (±${Math.round(accuracy)}m). Move to an open area and try again.`
        return
      }

      locationStatus.value = 'ready'
    },
    (error) => {
      locationStatus.value = 'error'
      if (error.code === error.PERMISSION_DENIED) {
        locationError.value = 'Location access was denied. Enable location permission for this site to check in.'
      } else if (error.code === error.TIMEOUT) {
        locationError.value = 'Getting your location timed out. Check your GPS/network and try again.'
      } else {
        locationError.value = 'Could not determine your location. Try again from an open area.'
      }
    },
    { enableHighAccuracy: true, timeout: 15000, maximumAge: 0 },
  )
}

function openCheckInModal(email: string) {
  actionMessage.value = ''
  currentStaffEmail.value = email
  newRecordForm.value.email = email
  
  const today = new Date().toISOString().split('T')[0]
  const existingRecord = attendanceRecords.value.find(
    (r) => r.email === email && r.date === today,
  )

  if (existingRecord?.checkOutAt) {
    actionMessage.value = 'You already timed out for today.'
    return
  }

  if (existingRecord && !existingRecord.checkOutAt) {
    const workedHours = getHoursBetween(existingRecord.checkInAt, new Date().toISOString())
    if (workedHours < WORK_DAY_HOURS) {
      const remaining = WORK_DAY_HOURS - workedHours
      actionMessage.value = `Time out is available after 8 hours. Remaining: ${formatDuration(remaining)}.`
      return
    }

    checkInAction.value = 'checkout'
  } else {
    if (!checkInStatus.value.allowed) {
      actionMessage.value = checkInStatus.value.message
      return
    }
    checkInAction.value = 'checkin'
  }

  showCheckInModal.value = true
  requestLocation()
}

function closeCheckInModal() {
  showCheckInModal.value = false
  currentStaffEmail.value = ''
  newRecordForm.value.email = ''
  checkInAction.value = 'checkin'
  locationStatus.value = 'idle'
  locationError.value = ''
  userCoords.value = null
}

async function saveAttendance() {
  if (!newRecordForm.value.email) return

  if (!canConfirmAttendance.value || !userCoords.value) {
    locationError.value = locationError.value || 'We need your location to record attendance. Please allow location access and try again.'
    return
  }

  const payload = {
    lat: userCoords.value.lat,
    lng: userCoords.value.lng,
    accuracy: userCoords.value.accuracy,
  }

  try {
    if (checkInAction.value === 'checkin') {
      await checkIn(payload)
    } else {
      await checkOut(payload)
    }

    await fetchAttendance()
    closeCheckInModal()
  } catch (error) {
    actionMessage.value = getUserFriendlyApiError(error)
  }
}

function round2(value: number) {
  return Math.round(value * 100) / 100
}

function getHoursBetween(startIso: string, endIso: string) {
  const diffMs = new Date(endIso).getTime() - new Date(startIso).getTime()
  return Math.max(0, diffMs / (1000 * 60 * 60))
}

function formatTime(iso?: string) {
  if (!iso) return '-'
  return new Date(iso).toLocaleTimeString('en-US', {
    hour: '2-digit',
    minute: '2-digit',
    hour12: true,
  })
}

function formatDuration(hours: number) {
  const totalMinutes = Math.ceil(hours * 60)
  const h = Math.floor(totalMinutes / 60)
  const m = totalMinutes % 60
  return `${h}h ${m}m`
}

</script>

<template>
  <section class="space-y-6 relative">
    <LocalLoader v-if="isLoading" />
    <div class="mb-6 flex items-start gap-3">
      <div class="flex h-12 w-12 items-center justify-center rounded-lg bg-linear-to-br from-sky-50 to-white ring-1 ring-sky-100">
        <Calendar class="dashboard-view-icon h-6 w-6 text-sky-600 dark:text-sky-400" />
      </div>
      <div>
        <h3 class="mb-1 text-2xl font-semibold text-gray-900">Staff Attendance</h3>
        <p class="text-sm text-gray-600">Track staff check-in/out and overtime</p>
      </div>
    </div>

    <div v-if="isAdmin" class="grid grid-cols-1 gap-4 sm:grid-cols-3">
      <div class="rounded-lg bg-sky-50 p-6">
        <p class="text-xs uppercase tracking-wide text-sky-600 font-semibold">Present Today</p>
        <p class="mt-2 text-2xl font-bold text-gray-900">{{ presentToday }}</p>
      </div>

      <div class="rounded-lg bg-sky-50 p-6">
        <p class="text-xs uppercase tracking-wide text-sky-600 font-semibold">Total Staff Hours</p>
        <p class="mt-2 text-2xl font-bold text-gray-900">{{ totalStaffHours.toFixed(1) }}h</p>
      </div>

      <div class="rounded-lg bg-sky-50 p-6">
        <p class="text-xs uppercase tracking-wide text-sky-600 font-semibold">Total Overtime</p>
        <p class="mt-2 text-2xl font-bold text-gray-900">{{ totalOvertimeHours.toFixed(1) }}h</p>
      </div>
    </div>

    <div v-if="!isAdmin" class="grid grid-cols-1 gap-4 md:grid-cols-3">
      <div class="rounded-lg border border-sky-200 bg-sky-50 p-6">
        <div class="flex items-center gap-3">
          <div class="flex h-12 w-12 items-center justify-center rounded-lg bg-sky-100">
            <svg class="h-6 w-6 text-sky-600 dark:text-sky-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 8v4l3 3m6-3a9 9 0 11-18 0 9 9 0 0118 0z" />
            </svg>
          </div>
          <div>
            <p class="text-2xl font-semibold text-sky-900">{{ myHoursWorkedToday.toFixed(1) }}h</p>
            <p class="text-sm text-sky-700">My Total Hours Today</p>
          </div>
        </div>
      </div>

      <div class="rounded-lg border border-sky-200 bg-sky-50 p-6">
        <div class="flex items-center gap-3">
          <div class="flex h-12 w-12 items-center justify-center rounded-lg bg-sky-100">
            <svg class="h-6 w-6 text-sky-600 dark:text-sky-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 8v4l2.5 2.5M12 3a9 9 0 100 18 9 9 0 000-18z" />
            </svg>
          </div>
          <div>
            <p class="text-2xl font-semibold text-sky-900">{{ myRegularHoursToday.toFixed(1) }}h</p>
            <p class="text-sm text-sky-700">My Regular Hours Today</p>
          </div>
        </div>
      </div>

      <div class="rounded-lg border border-sky-200 bg-sky-50 p-6">
        <div class="flex items-center gap-3">
          <div class="flex h-12 w-12 items-center justify-center rounded-lg bg-sky-100">
            <svg class="h-6 w-6 text-sky-600 dark:text-sky-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M13 10V3L4 14h7v7l9-11h-7z" />
            </svg>
          </div>
          <div>
            <p class="text-2xl font-semibold text-sky-900">{{ myOvertimeHours.toFixed(1) }}h</p>
            <p class="text-sm text-sky-700">My Overtime (After 8h)</p>
          </div>
        </div>
      </div>
    </div>

    <div v-if="!isAdmin" class="rounded-lg border border-gray-200 bg-white p-6">
      <h4 class="mb-4 text-lg font-semibold text-gray-900">My Attendance</h4>
      <div class="space-y-4">
        <button
          type="button"
          class="w-full rounded-lg px-4 py-3 font-semibold text-white transition-colors"
          :class="isTimeButtonDisabled ? 'cursor-not-allowed bg-gray-400' : 'bg-sky-600 hover:bg-sky-700'"
          :disabled="isTimeButtonDisabled"
          @click="openCheckInModal(currentUserEmail)"
        >
          {{ timeButtonLabel }}
        </button>
        <p v-if="actionMessage" class="rounded-lg bg-yellow-50 p-3 text-sm text-yellow-800">
          {{ actionMessage }}
        </p>
        <p v-if="!myTodayAttendance && checkInStatus.message" class="rounded-lg p-3 text-sm border"
          :class="checkInStatus.status === 'late' ? 'bg-amber-50 text-amber-800 border-amber-200' : 'bg-red-50 text-red-800 border-red-200'">
          {{ checkInStatus.message }}
        </p>
        <div v-if="myTodayAttendance" class="rounded-lg bg-gray-50 p-4">
          <div class="grid grid-cols-2 gap-4">
            <div>
              <p class="text-sm text-gray-600">Check In</p>
              <p class="text-lg font-semibold text-gray-900">{{ formatTime(myTodayAttendance.checkInAt) }}</p>
            </div>
            <div>
              <p class="text-sm text-gray-600">Check Out</p>
              <p class="text-lg font-semibold text-gray-900">{{ formatTime(myTodayAttendance.checkOutAt) }}</p>
            </div>
          </div>
        </div>
        <div v-else class="rounded-lg bg-yellow-50 p-4 text-center">
          <p class="text-sm text-yellow-800">No attendance record yet. Please check in to start tracking.</p>
        </div>
      </div>
    </div>

    <div v-if="isAdmin" class="rounded-lg border border-gray-200 bg-white p-6">
      <h4 class="mb-4 text-lg font-semibold text-gray-900">Today's Records</h4>
      <div v-if="todayAttendance.length === 0" class="py-8 text-center text-gray-500">
        No attendance records yet
      </div>
      <div v-else class="space-y-3">
        <div v-for="record in todayAttendance" :key="record.id" class="rounded-lg bg-gray-50 p-4">
          <div class="flex items-start justify-between">
            <div class="flex-1">
              <p class="font-semibold text-gray-900">{{ record.staffName }}</p>
              <div class="mt-2 grid grid-cols-2 gap-2 text-sm">
                <div>
                  <span class="text-gray-600">Check In:</span>
                  <p class="text-gray-900">{{ formatTime(record.checkInAt) }}</p>
                </div>
                <div>
                  <span class="text-gray-600">Check Out:</span>
                  <p class="text-gray-900">{{ formatTime(record.checkOutAt) }}</p>
                </div>
                <div>
                  <span class="text-gray-600">Hours Worked:</span>
                  <p class="text-gray-900">{{ record.hoursWorked }}h</p>
                </div>
                <div>
                  <span class="text-gray-600">Overtime:</span>
                  <p class="text-sky-600 font-semibold">{{ record.overtimeHours }}h</p>
                </div>
              </div>
            </div>
            <div class="ml-4"></div>
          </div>
        </div>
      </div>
    </div>
    <div v-if="isAdmin" class="rounded-lg border border-gray-200 bg-white p-6">
      <div class="mb-4 flex items-center justify-between">
        <h4 class="text-lg font-semibold text-gray-900 font-display">Geofence Site Settings</h4>
        <span class="rounded-full px-2.5 py-0.5 text-xs font-semibold"
          :class="attendanceLocation ? 'bg-emerald-50 text-emerald-700' : 'bg-amber-50 text-amber-700'">
          {{ attendanceLocation ? 'Configured' : 'Not Set' }}
        </span>
      </div>

      <p class="mb-6 text-sm text-gray-600">
        Configure the coordinates and radius of the work site. Staff check-in and check-out will be restricted to this area.
      </p>

      <form @submit.prevent="saveGeofenceLocation" class="space-y-4">
        <div class="grid grid-cols-1 gap-4 sm:grid-cols-3">
          <div>
            <label class="block text-xs font-semibold text-gray-700 uppercase tracking-wider mb-1">Latitude</label>
            <input
              type="number"
              step="any"
              required
              v-model="settingsForm.lat"
              placeholder="e.g. 13.1415"
              class="w-full rounded-lg border border-slate-200 bg-white px-3 py-2 text-sm focus:border-sky-500 focus:outline-hidden focus:ring-1 focus:ring-sky-500"
            />
          </div>

          <div>
            <label class="block text-xs font-semibold text-gray-700 uppercase tracking-wider mb-1">Longitude</label>
            <input
              type="number"
              step="any"
              required
              v-model="settingsForm.lng"
              placeholder="e.g. 123.4567"
              class="w-full rounded-lg border border-slate-200 bg-white px-3 py-2 text-sm focus:border-sky-500 focus:outline-hidden focus:ring-1 focus:ring-sky-500"
            />
          </div>

          <div>
            <label class="block text-xs font-semibold text-gray-700 uppercase tracking-wider mb-1">Geofence Radius (meters)</label>
            <input
              type="number"
              required
              min="20"
              max="5000"
              v-model="settingsForm.radius_meters"
              placeholder="e.g. 150"
              class="w-full rounded-lg border border-slate-200 bg-white px-3 py-2 text-sm focus:border-sky-500 focus:outline-hidden focus:ring-1 focus:ring-sky-500"
            />
          </div>
        </div>

        <!-- Minimap Container -->
        <div class="overflow-hidden rounded-lg border border-slate-200 bg-slate-50">
          <div ref="mapContainer" class="h-64 w-full z-0" style="min-height: 256px;"></div>
        </div>

        <div v-if="settingsSuccess" class="rounded-lg bg-emerald-50 p-3 text-sm text-emerald-800">
          {{ settingsSuccess }}
        </div>
        <div v-if="settingsError" class="rounded-lg bg-red-50 p-3 text-sm text-red-800">
          {{ settingsError }}
        </div>

        <div class="flex flex-col gap-2 sm:flex-row sm:justify-between pt-2">
          <button
            type="button"
            @click="captureCurrentAdminLocation"
            class="inline-flex items-center justify-center gap-2 rounded-lg border border-slate-200 bg-white px-4 py-2 text-sm font-semibold text-slate-700 hover:bg-slate-50"
          >
            <svg class="h-4 w-4 text-gray-500" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M17.657 16.657L13.414 20.9a1.998 1.998 0 01-2.827 0l-4.244-4.243a8 8 0 1111.314 0z" />
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15 11a3 3 0 11-6 0 3 3 0 016 0z" />
            </svg>
            Use My Current Location
          </button>

          <button
            type="submit"
            :disabled="isSavingLocation"
            class="inline-flex items-center justify-center rounded-lg bg-sky-600 px-4 py-2 text-sm font-semibold text-white shadow-xs hover:bg-sky-700 disabled:bg-gray-400"
          >
            {{ isSavingLocation ? 'Saving...' : 'Save Geofence Settings' }}
          </button>
        </div>
      </form>
    </div>

    <ModalShell
      :show="showCheckInModal"
      :title="checkInAction === 'checkin' ? 'Check In' : 'Check Out'"
      subtitle="Attendance capture"
      tone="blue"
      size="sm"
      @close="closeCheckInModal"
    >
      <div class="mb-6 space-y-4">
        <div class="rounded-2xl bg-sky-50 p-4">
          <p class="text-sm text-gray-600">Staff Member</p>
          <p class="text-lg font-semibold text-gray-900">{{ currentStaffLabel }}</p>
        </div>

        <div class="rounded-2xl bg-sky-50 p-4">
          <p class="text-sm text-gray-600">{{ checkInAction === 'checkin' ? 'Check In Time' : 'Check Out Time' }}</p>
          <p class="text-2xl font-semibold text-sky-600">{{ formatTime(new Date().toISOString()) }}</p>
          <p class="mt-1 text-xs text-gray-500">System time (auto-captured)</p>
        </div>

        <div v-if="checkInAction === 'checkin' && checkInStatus.status === 'late'" class="rounded-2xl bg-amber-50 p-4 border border-amber-200">
          <p class="text-sm font-medium text-amber-800 flex items-center gap-2">
            <span>⚠️</span> You're late.
          </p>
        </div>

        <div class="rounded-2xl border p-4"
          :class="locationStatus === 'ready' ? 'border-emerald-200 bg-emerald-50' : locationStatus === 'error' || locationStatus === 'unsupported' ? 'border-amber-200 bg-amber-50' : 'border-sky-200 bg-sky-50'">
          <div class="flex items-center justify-between">
            <p class="text-sm text-gray-600">Location</p>
            <button v-if="locationStatus === 'error'" type="button"
              class="text-xs font-semibold text-sky-700 hover:text-sky-900" @click="requestLocation">
              Try again
            </button>
          </div>

          <p v-if="locationStatus === 'locating'" class="mt-1 flex items-center gap-2 text-sm font-medium text-sky-700">
            <span class="h-2 w-2 animate-pulse rounded-full bg-sky-500"></span>
            Getting your location…
          </p>
          <p v-else-if="locationStatus === 'ready'" class="mt-1 text-sm font-medium text-emerald-700">
            Location confirmed (±{{ Math.round(userCoords?.accuracy ?? 0) }}m accuracy)
          </p>
          <p v-else-if="locationStatus === 'error' || locationStatus === 'unsupported'" class="mt-1 text-sm font-medium text-amber-800">
            {{ locationError }}
          </p>
        </div>
      </div>

      <template #footer>
        <button type="button" class="rounded-xl border border-slate-200 bg-white px-4 py-3 font-semibold text-slate-700 shadow-sm hover:bg-slate-50" @click="closeCheckInModal">Cancel</button>
        <button type="button"
          class="rounded-xl px-4 py-3 font-semibold text-white shadow-lg transition-colors"
          :class="canConfirmAttendance ? 'bg-linear-to-r from-sky-600 to-sky-700 shadow-sky-600/20 hover:from-sky-700 hover:to-sky-800' : 'cursor-not-allowed bg-gray-400 shadow-none'"
          :disabled="!canConfirmAttendance"
          @click="saveAttendance">
          Confirm {{ checkInAction === 'checkin' ? 'Check In' : 'Check Out' }}
        </button>
      </template>
    </ModalShell>
  </section>
</template>
