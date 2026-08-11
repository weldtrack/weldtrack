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
  <section class="space-y-6 relative">
    <LocalLoader v-if="isLoading" />

    <!-- Header -->
    <div class="flex items-start gap-3">
      <div class="flex h-12 w-12 items-center justify-center">
        <CheckCircle class="dashboard-view-icon h-6 w-6 text-sky-600 dark:text-sky-400" />
      </div>
      <div>
        <h3 class="text-2xl font-semibold text-slate-900">Staff Contributions</h3>
        <p class="text-sm text-slate-600">Overview of completed project tasks and team contributors</p>
      </div>
    </div>

    <!-- Empty State -->
    <div v-if="completedContributions.length === 0" class="rounded-xl border border-slate-200 bg-white p-8 text-center text-sm text-slate-500">
      No completed task contributions recorded yet.
    </div>

    <!-- Contributions Grid -->
    <div v-else class="grid grid-cols-1 gap-5 md:grid-cols-2">
      <div
        v-for="proj in completedContributions"
        :key="proj.projectName"
        class="group relative flex flex-col justify-between rounded-2xl border border-slate-200 bg-white p-6 shadow-xs transition-all duration-200 hover:border-slate-300 hover:shadow-md"
      >
        <div>
          <!-- Header info -->
          <div class="flex items-start justify-between gap-3">
            <div class="min-w-0 flex-1">
              <h4 class="truncate text-lg font-bold text-slate-900" :title="proj.projectName">{{ proj.projectName }}</h4>
              <p class="mt-1 text-xs font-semibold text-sky-700">
                {{ proj.doneCount }} {{ proj.doneCount === 1 ? 'task' : 'tasks' }} completed
              </p>
            </div>
            <span class="inline-flex shrink-0 items-center rounded-full bg-slate-100 px-3 py-1 text-[11px] font-medium text-slate-600">
              {{ new Date(proj.lastDoneAt).toLocaleDateString('en-PH', { month: 'short', day: 'numeric', year: 'numeric' }) }}
            </span>
          </div>

          <!-- Contributors section -->
          <div class="mt-6 pt-4 border-t border-slate-100">
            <p class="text-[10px] font-bold uppercase tracking-wider text-slate-400 mb-3">Contributors</p>
            <div class="flex flex-wrap gap-2">
              <div
                v-for="email in proj.contributors"
                :key="email"
                :class="[
                  'flex items-center gap-2 rounded-xl border px-3 py-1.5 text-xs transition-colors',
                  isCurrentUserContributor(email)
                    ? 'border-sky-200 bg-sky-50 text-sky-900 font-semibold'
                    : 'border-slate-200 bg-slate-50 text-slate-700'
                ]"
              >
                <span :class="['flex h-5 w-5 items-center justify-center rounded-full text-[10px] font-bold', isCurrentUserContributor(email) ? 'bg-sky-600 text-white' : 'bg-slate-200 text-slate-600']">
                  {{ email.slice(0, 1).toUpperCase() }}
                </span>
                <span class="truncate max-w-44">{{ email }}</span>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  </section>
</template>
