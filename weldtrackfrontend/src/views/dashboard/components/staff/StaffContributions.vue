<script setup lang="ts">
import { computed, onMounted, ref } from 'vue'
import LocalLoader from '../../../../components/ui/LocalLoader.vue'
import { CheckCircle } from 'lucide-vue-next'
import { useAuthStore } from '../../../../stores/auth'
import { useStaffContributionsStore } from '../../../../stores/staffContributions'

const authStore = useAuthStore()
const staffContributionsStore = useStaffContributionsStore()
const isAdmin = computed(() => authStore.role.trim().toLowerCase() === 'admin')
const currentUserId = ref('')

function getStaffLabel(staffId: string) {
  return authStore.getStaffLabel(staffId)
}

function getContributorDetails(snapshot: { contributorIds?: string[]; contributorEmails?: string[] }) {
  const emails = snapshot.contributorEmails?.filter(Boolean) || []
  const ids = snapshot.contributorIds || []
  
  // Combine into a list of unique emails/identifiers
  const contributors = [...new Set([...emails, ...ids.map((id) => getStaffLabel(id)).filter(Boolean)])]
  
  return contributors
}

const completedContributions = computed(() => {
  const relevantSnapshots = staffContributionsStore.snapshots.filter((snapshot) => {
    if (isAdmin.value) return true

    const matchesId = Array.isArray(snapshot.contributorIds) && snapshot.contributorIds.includes(currentUserId.value)
    const matchesEmail = Array.isArray(snapshot.contributorEmails) && snapshot.contributorEmails.includes(currentUserId.value)

    return matchesId || matchesEmail
  })

  const byProject: Record<
    string,
    { projectName: string; doneCount: number; lastDoneAt: string; contributors: string[] }
  > = {}

  relevantSnapshots.forEach((snapshot) => {
    const existing = byProject[snapshot.projectName]
    const contributorNames = getContributorDetails(snapshot)

    if (!existing) {
      byProject[snapshot.projectName] = {
        projectName: snapshot.projectName,
        doneCount: 1,
        lastDoneAt: snapshot.completedAt,
        contributors: [...contributorNames],
      }
    } else {
      existing.doneCount += 1
      if (new Date(snapshot.completedAt) > new Date(existing.lastDoneAt)) existing.lastDoneAt = snapshot.completedAt
      contributorNames.forEach((name) => {
        if (!existing.contributors.includes(name)) existing.contributors.push(name)
      })
    }
  })

  return Object.values(byProject).sort((a, b) => {
    return new Date(b.lastDoneAt).getTime() - new Date(a.lastDoneAt).getTime()
  })
})

function isCurrentUserContributor(email: string) {
  if (isAdmin.value) return false
  return email.toLowerCase() === authStore.email.toLowerCase()
}

const isLoading = ref(true)

onMounted(async () => {
  isLoading.value = true
  try {
    await Promise.all([
      staffContributionsStore.fetchSnapshots(),
      authStore.fetchStaffDirectory(),
    ])
    currentUserId.value = authStore.email
  } finally {
    isLoading.value = false
  }
})
</script>

<template>
  <section class="space-y-4 relative">
    <LocalLoader v-if="isLoading" />
    <div class="flex items-start gap-3">
      <div
        class="flex h-12 w-12 items-center justify-center rounded-lg bg-linear-to-br from-sky-50 to-sky-100 ring-1 ring-sky-100">
        <CheckCircle class="dashboard-view-icon h-6 w-6 text-sky-600 dark:text-sky-400" />
      </div>
      <div>
        <h3 class="mb-1 text-2xl font-semibold text-gray-900">Staff Contributions</h3>
        <p class="text-sm text-gray-600">See recently completed tasks and their contributors.</p>
      </div>
    </div>

    <div v-if="completedContributions.length === 0" class="rounded-lg bg-gray-50 p-4 text-sm text-gray-500">
      No completed tasks yet.
    </div>

    <div v-else class="grid grid-cols-1 gap-4 md:grid-cols-2">
      <div v-for="proj in completedContributions" :key="proj.projectName"
        class="rounded-xl border border-gray-100 bg-white p-5 shadow-sm transition-shadow hover:shadow-md">
        <div class="flex items-start justify-between">
          <div class="min-w-0">
            <h4 class="truncate font-semibold text-gray-900">{{ proj.projectName }}</h4>
            <p class="text-sm text-gray-600">Completed: {{ proj.doneCount }} tasks</p>
          </div>
          <span class="text-xs text-gray-500 whitespace-nowrap">
            Last: {{ new Date(proj.lastDoneAt).toLocaleDateString('en-PH', { month: 'short', day: 'numeric' }) }}
          </span>
        </div>
        
        <div class="mt-4">
          <p class="text-xs font-bold uppercase tracking-wider text-gray-500 mb-2">Contributors</p>
          <div class="flex flex-wrap gap-2">
            <div v-for="email in proj.contributors" :key="email"
              :class="['flex items-center gap-2 rounded-full border px-2 py-1 text-xs', isCurrentUserContributor(email) ? 'border-blue-200 bg-blue-50' : 'border-gray-100 bg-gray-50']">
              <span class="flex h-5 w-5 items-center justify-center rounded-full bg-gray-200 text-[10px] font-semibold text-gray-600">
                {{ email.slice(0, 1).toUpperCase() }}
              </span>
              <span :class="isCurrentUserContributor(email) ? 'font-semibold text-blue-700' : 'text-gray-700'">
                {{ email }}
              </span>
            </div>
          </div>
        </div>
      </div>
    </div>
  </section>
</template>
