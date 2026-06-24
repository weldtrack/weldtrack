<script setup lang="ts">
import { computed} from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { useAuthStore } from '../../../../stores/auth'

const route = useRoute()
const router = useRouter()

const authStore = useAuthStore()
const isAdmin = computed(() => authStore.role.trim().toLowerCase() === 'admin')

const currentSection = computed<string>(() => {
  const name = route.name as string
  if (name.includes('attendance')) return 'attendance'
  if (name.includes('tasks')) return 'tasks'
  if (name.includes('contributions')) return 'contributions'
  if (name.includes('create')) return 'create'
  return 'attendance'
})
</script>

<template>
  <section class="space-y-4">
    <!-- Admin-only tabs -->
    <div v-if="isAdmin" class="flex gap-2 border-b border-gray-200 overflow-x-auto">
      <button type="button" @click="router.push({ name: isAdmin ? 'admin-staff-attendance' : 'staff-attendance' })"
        :class="currentSection === 'attendance' ? 'border-b-2 border-blue-600 text-blue-600' : 'text-gray-600 hover:text-gray-900'"
        class="px-4 py-2 font-semibold transition-colors whitespace-nowrap">
        Attendance
      </button>
      <button type="button" @click="router.push({ name: isAdmin ? 'admin-staff-tasks' : 'staff-tasks' })"
        :class="currentSection === 'tasks' ? 'border-b-2 border-blue-600 text-blue-600' : 'text-gray-600 hover:text-gray-900'"
        class="px-4 py-2 font-semibold transition-colors whitespace-nowrap">
        Tasks
      </button>
      <button type="button" @click="router.push({ name: isAdmin ? 'admin-staff-contributions' : 'staff-contributions' })"
        :class="currentSection === 'contributions' ? 'border-b-2 border-blue-600 text-blue-600' : 'text-gray-600 hover:text-gray-900'"
        class="px-4 py-2 font-semibold transition-colors whitespace-nowrap">
        Contributions
      </button>
      <button type="button" @click="router.push({ name: isAdmin ? 'admin-staff-create' : 'staff-create' })"
        :class="currentSection === 'create' ? 'border-b-2 border-blue-600 text-blue-600' : 'text-gray-600 hover:text-gray-900'"
        class="px-4 py-2 font-semibold transition-colors whitespace-nowrap">
        Create Staff
      </button>
    </div>

    <RouterView />
  </section>
</template>
