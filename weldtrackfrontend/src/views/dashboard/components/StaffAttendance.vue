<script setup lang="ts">
import { ref, computed, onMounted, onUnmounted } from 'vue'
import { useAuthStore } from '../../../stores/auth'

interface Staff {
  id: string
  name: string
  position: string
  hoursWorkedToday: number
  checkedInTime?: string
  checkedOutTime?: string
  overtimeHours: number
}

interface AttendanceRecord {
  id: string
  staffId: string
  staffName: string
  date: string
  checkInAt: string
  checkOutAt?: string
  hoursWorked: number
  regularHours: number
  overtimeHours: number
}

const authStore = useAuthStore()
const isAdmin = computed(() => authStore.role === 'admin')

// Map email to staff ID (or use default for testing)
const currentUserId = computed(() => {
  const email = authStore.email?.toLowerCase() || ''

  if (email.includes('juan')) return '1'
  if (email.includes('maria')) return '2'
  if (email.includes('carlos')) return '3'
  if (email.includes('rosa')) return '4'

  // Keep staff flow working even for unmapped emails.
  return '1'
})

const staffList = ref<Staff[]>([
  { id: '1', name: 'Juan Cruz', position: 'Welder', hoursWorkedToday: 0, overtimeHours: 2.5 },
  { id: '2', name: 'Maria Santos', position: 'Fabricator', hoursWorkedToday: 0, overtimeHours: 0 },
  { id: '3', name: 'Carlos Reyes', position: 'Welder', hoursWorkedToday: 0, overtimeHours: 1 },
  { id: '4', name: 'Rosa Dela Cruz', position: 'Inspector', hoursWorkedToday: 0, overtimeHours: 0 },
])

const attendanceRecords = ref<AttendanceRecord[]>([])

const currentStaffId = ref<string>('')
const showCheckInModal = ref(false)
const checkInAction = ref<'checkin' | 'checkout'>('checkin')
const actionMessage = ref('')
const WORK_DAY_HOURS = 8
const nowTick = ref(Date.now())
let tickTimer: number | undefined

const newRecordForm = ref({
  staffId: '',
})

const todayAttendance = computed(() => {
  const today = new Date().toISOString().split('T')[0]
  return attendanceRecords.value.filter((record) => record.date === today)
})

const totalStaffHours = computed(() => {
  return todayAttendance.value.reduce((sum, record) => sum + record.hoursWorked, 0)
})

const totalOvertimeHours = computed(() => {
  return todayAttendance.value.reduce((sum, record) => sum + record.overtimeHours, 0)
})

const presentToday = computed(() => {
  return todayAttendance.value.length
})

const myTodayAttendance = computed(() => {
  return todayAttendance.value.find((record) => record.staffId === currentUserId.value)
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

const timeButtonLabel = computed(() => {
  const record = myTodayAttendance.value
  if (!record) return 'Check In'
  if (record.checkOutAt) return 'Timed Out For Today'
  if (canTimeOutNow.value) return 'Time Out'

  return `Time Out Available In ${formatDuration(remainingHoursBeforeTimeOut.value)}`
})

const isTimeButtonDisabled = computed(() => {
  const record = myTodayAttendance.value
  if (!record) return false
  if (record.checkOutAt) return true

  return !canTimeOutNow.value
})

onMounted(() => {
  tickTimer = window.setInterval(() => {
    nowTick.value = Date.now()
  }, 30000)
})

onUnmounted(() => {
  if (tickTimer) window.clearInterval(tickTimer)
})

function openCheckInModal(staffId: string) {
  actionMessage.value = ''
  currentStaffId.value = staffId
  newRecordForm.value.staffId = staffId
  
  const today = new Date().toISOString().split('T')[0]
  const existingRecord = attendanceRecords.value.find(
    (r) => r.staffId === staffId && r.date === today,
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
    checkInAction.value = 'checkin'
  }

  showCheckInModal.value = true
}

function closeCheckInModal() {
  showCheckInModal.value = false
  currentStaffId.value = ''
  newRecordForm.value.staffId = ''
  checkInAction.value = 'checkin'
}

function saveAttendance() {
  const staffId = newRecordForm.value.staffId
  if (!staffId) return

  const staff = staffList.value.find((s) => s.id === staffId) || staffList.value[0]
  if (!staff) return

  const now = new Date()
  const nowIso = now.toISOString()
  const today = now.toISOString().split('T')[0]

  if (checkInAction.value === 'checkin') {
    const newRecord: AttendanceRecord = {
      id: `${Date.now()}`,
      staffId: staffId,
      staffName: staff.name,
      date: today,
      checkInAt: nowIso,
      checkOutAt: undefined,
      hoursWorked: 0,
      regularHours: 0,
      overtimeHours: 0,
    }
    attendanceRecords.value.push(newRecord)
    staff.hoursWorkedToday = 0
  } else {
    const existingIndex = attendanceRecords.value.findIndex(
      (r) => r.staffId === staffId && r.date === today,
    )
    if (existingIndex >= 0) {
      const record = attendanceRecords.value[existingIndex]
      record.checkOutAt = nowIso

      const hoursWorked = getHoursBetween(record.checkInAt, record.checkOutAt)
      const regularHours = Math.min(hoursWorked, WORK_DAY_HOURS)
      const overtimeHours = Math.max(0, hoursWorked - WORK_DAY_HOURS)

      record.hoursWorked = round2(hoursWorked)
      record.regularHours = round2(regularHours)
      record.overtimeHours = round2(overtimeHours)

      staff.hoursWorkedToday = record.hoursWorked
      staff.overtimeHours = record.overtimeHours
    }
  }

  closeCheckInModal()
}

function deleteRecord(recordId: string) {
  const index = attendanceRecords.value.findIndex((r) => r.id === recordId)
  if (index >= 0) {
    attendanceRecords.value.splice(index, 1)
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
  <section class="space-y-6">
    <div>
      <h3 class="mb-1 text-2xl font-semibold text-gray-900">Staff Attendance</h3>
      <p class="text-sm text-gray-600">Track staff check-in/out and overtime</p>
    </div>

    <!-- Attendance Summary Cards -->
    <div class="grid grid-cols-1 gap-4 md:grid-cols-3">
      <div class="rounded-lg border border-gray-200 bg-white p-6">
        <div class="flex items-center gap-3">
          <div class="flex h-12 w-12 items-center justify-center rounded-lg bg-blue-100">
            <svg class="h-6 w-6 text-blue-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path
                stroke-linecap="round"
                stroke-linejoin="round"
                stroke-width="2"
                d="M17 20h5v-2a3 3 0 00-5.856-1.487M15 10a3 3 0 11-6 0 3 3 0 016 0zM6 20a7 7 0 1114 0"
              />
            </svg>
          </div>
          <div>
            <p class="text-2xl font-semibold text-gray-900">{{ presentToday }}</p>
            <p class="text-sm text-gray-600">Present Today</p>
          </div>
        </div>
      </div>

      <div class="rounded-lg border border-gray-200 bg-white p-6">
        <div class="flex items-center gap-3">
          <div class="flex h-12 w-12 items-center justify-center rounded-lg bg-green-100">
            <svg class="h-6 w-6 text-green-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 8v4l3 3m6-3a9 9 0 11-18 0 9 9 0 0118 0z" />
            </svg>
          </div>
          <div>
            <p class="text-2xl font-semibold text-gray-900">{{ totalStaffHours.toFixed(1) }}h</p>
            <p class="text-sm text-gray-600">Total Staff Hours</p>
          </div>
        </div>
      </div>

      <div class="rounded-lg border border-gray-200 bg-white p-6">
        <div class="flex items-center gap-3">
          <div class="flex h-12 w-12 items-center justify-center rounded-lg bg-orange-100">
            <svg class="h-6 w-6 text-orange-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path
                stroke-linecap="round"
                stroke-linejoin="round"
                stroke-width="2"
                d="M13 10V3L4 14h7v7l9-11h-7z"
              />
            </svg>
          </div>
          <div>
            <p class="text-2xl font-semibold text-gray-900">{{ totalOvertimeHours.toFixed(1) }}h</p>
            <p class="text-sm text-gray-600">Total Overtime</p>
          </div>
        </div>
      </div>
    </div>

    <!-- Personal Staff Stats (Staff Only) -->
    <div v-if="!isAdmin" class="grid grid-cols-1 gap-4 md:grid-cols-3">
      <div class="rounded-lg border border-blue-200 bg-blue-50 p-6">
        <div class="flex items-center gap-3">
          <div class="flex h-12 w-12 items-center justify-center rounded-lg bg-blue-100">
            <svg class="h-6 w-6 text-blue-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 8v4l3 3m6-3a9 9 0 11-18 0 9 9 0 0118 0z" />
            </svg>
          </div>
          <div>
            <p class="text-2xl font-semibold text-blue-900">{{ myHoursWorkedToday.toFixed(1) }}h</p>
            <p class="text-sm text-blue-700">My Total Hours Today</p>
          </div>
        </div>
      </div>

      <div class="rounded-lg border border-sky-200 bg-sky-50 p-6">
        <div class="flex items-center gap-3">
          <div class="flex h-12 w-12 items-center justify-center rounded-lg bg-sky-100">
            <svg class="h-6 w-6 text-sky-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 8v4l2.5 2.5M12 3a9 9 0 100 18 9 9 0 000-18z" />
            </svg>
          </div>
          <div>
            <p class="text-2xl font-semibold text-sky-900">{{ myRegularHoursToday.toFixed(1) }}h</p>
            <p class="text-sm text-sky-700">My Regular Hours Today</p>
          </div>
        </div>
      </div>

      <div class="rounded-lg border border-orange-200 bg-orange-50 p-6">
        <div class="flex items-center gap-3">
          <div class="flex h-12 w-12 items-center justify-center rounded-lg bg-orange-100">
            <svg class="h-6 w-6 text-orange-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M13 10V3L4 14h7v7l9-11h-7z" />
            </svg>
          </div>
          <div>
            <p class="text-2xl font-semibold text-orange-900">{{ myOvertimeHours.toFixed(1) }}h</p>
            <p class="text-sm text-orange-700">My Overtime (After 8h)</p>
          </div>
        </div>
      </div>
    </div>

    <!-- My Attendance Section (Staff) -->
    <div v-if="!isAdmin" class="rounded-lg border border-gray-200 bg-white p-6">
      <h4 class="mb-4 text-lg font-semibold text-gray-900">My Attendance</h4>
      <div class="space-y-4">
        <button
          type="button"
          class="w-full rounded-lg px-4 py-3 font-semibold text-white transition-colors"
          :class="isTimeButtonDisabled ? 'cursor-not-allowed bg-gray-400' : 'bg-blue-600 hover:bg-blue-700'"
          :disabled="isTimeButtonDisabled"
          @click="openCheckInModal(currentUserId)"
        >
          {{ timeButtonLabel }}
        </button>
        <p v-if="actionMessage" class="rounded-lg bg-yellow-50 p-3 text-sm text-yellow-800">
          {{ actionMessage }}
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

    <!-- Today's Attendance Records (Admin Only) -->
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
                  <p class="text-orange-600 font-semibold">{{ record.overtimeHours }}h</p>
                </div>
              </div>
            </div>
            <button
              type="button"
              class="ml-4 text-red-600 hover:text-red-800"
              @click="deleteRecord(record.id)"
            >
              <svg class="h-5 w-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12" />
              </svg>
            </button>
          </div>
        </div>
      </div>
    </div>

    <!-- Check-In Modal -->
    <div v-if="showCheckInModal" class="fixed inset-0 z-50 flex items-center justify-center bg-black/60">
      <div class="w-full max-w-md rounded-lg bg-white p-6">
        <h3 class="mb-4 text-lg font-semibold text-gray-900">
          {{ checkInAction === 'checkin' ? 'Check In' : 'Check Out' }}
        </h3>

        <div class="mb-6 space-y-4">
          <div class="rounded-lg bg-blue-50 p-4">
            <p class="text-sm text-gray-600">Staff Member</p>
            <p class="text-lg font-semibold text-gray-900">
              {{ staffList.find((s) => s.id === newRecordForm.staffId)?.name }}
            </p>
          </div>

          <div class="rounded-lg bg-green-50 p-4">
            <p class="text-sm text-gray-600">{{ checkInAction === 'checkin' ? 'Check In Time' : 'Check Out Time' }}</p>
            <p class="text-2xl font-semibold text-green-600">
              {{ formatTime(new Date().toISOString()) }}
            </p>
            <p class="mt-1 text-xs text-gray-500">System time (auto-captured)</p>
          </div>
        </div>

        <div class="flex gap-3">
          <button
            type="button"
            class="flex-1 rounded-lg border border-gray-300 px-4 py-2 font-semibold text-gray-700 transition-colors hover:bg-gray-50"
            @click="closeCheckInModal"
          >
            Cancel
          </button>
          <button
            type="button"
            :class="[
              'flex-1 rounded-lg px-4 py-2 font-semibold text-white transition-colors',
              checkInAction === 'checkin'
                ? 'bg-green-600 hover:bg-green-700'
                : 'bg-orange-600 hover:bg-orange-700'
            ]"
            @click="saveAttendance"
          >
            Confirm {{ checkInAction === 'checkin' ? 'Check In' : 'Check Out' }}
          </button>
        </div>
      </div>
    </div>
  </section>
</template>
