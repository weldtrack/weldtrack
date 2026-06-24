<script setup lang="ts">
import { computed, onMounted, ref } from 'vue'
import { User } from 'lucide-vue-next'
import { useAuthStore } from '../../../../stores/auth'
import { useStaffContributionsStore } from '../../../../stores/staffContributions'

const authStore = useAuthStore()
const staffContributionsStore = useStaffContributionsStore()
const isAdmin = computed(() => authStore.role.trim().toLowerCase() === 'admin')
const currentUserId = ref('')

function getStaffLabel(staffId: string) {
  return authStore.getStaffLabel(staffId)
}

function getContributorLabels(snapshot: { contributorIds?: string[]; contributorEmails?: string[] }) {
  if (snapshot.contributorEmails?.length) return snapshot.contributorEmails.filter(Boolean)
  if (!snapshot.contributorIds?.length) return []
  return snapshot.contributorIds
    .map((id) => getStaffLabel(id))
    .filter(Boolean)
}

const completedContributions = computed(() => {
  const relevantSnapshots = staffContributionsStore.snapshots.filter((snapshot) => {
    if (isAdmin.value) return true
    if (Array.isArray(snapshot.contributorIds)) return snapshot.contributorIds.includes(currentUserId.value)
    return false
  })

  const byProject: Record<
    string,
    { projectName: string; doneCount: number; lastDoneAt: string; contributors: string[] }
  > = {}

  relevantSnapshots.forEach((snapshot) => {
    const existing = byProject[snapshot.projectName]
    const contributorNames = getContributorLabels(snapshot)

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

function isCurrentUserContributor(name: string) {
  if (isAdmin.value) return false
  const currentName = currentUserId.value ? getStaffLabel(currentUserId.value) : ''
  return Boolean(currentName && name === currentName)
}

onMounted(async () => {
  await Promise.all([
    staffContributionsStore.fetchSnapshots(),
    authStore.fetchStaffDirectory(),
    // Assuming authStore or api can provide current user ID. 
    // In original code, it was fetching /auth/me, I'll simplify.
  ])
})
</script>

<template>
  <section class="space-y-4">
    <div class="flex items-start gap-3">
      <div
        class="flex h-12 w-12 items-center justify-center rounded-lg bg-linear-to-br from-sky-50 to-sky ring-1 ring-sky-100">
        <User class="h-6 w-6 text-sky-600" />
      </div>
      <div>
        <h3 class="mb-1 text-2xl font-semibold text-gray-900">Staff Contributions</h3>
        <p class="text-sm text-gray-600">See recently completed tasks and their contributors.</p>
      </div>
    </div>

    <div v-if="completedContributions.length === 0" class="rounded-lg bg-gray-50 p-4 text-sm text-gray-500">
      No completed tasks yet.
    </div>

    <div v-else class="space-y-3">
      <div v-for="proj in completedContributions" :key="proj.projectName"
        class="rounded-lg border border-gray-200 bg-white p-4">
        <div class="flex items-center justify-between">
          <div>
            <p class="font-semibold text-gray-900">{{ proj.projectName }}</p>
            <p class="text-sm text-gray-600">Completed tasks: {{ proj.doneCount }}</p>
            <div class="mt-1 flex flex-wrap gap-2">
              <span v-for="name in proj.contributors" :key="`${proj.projectName}-${name}`"
                class="rounded-full px-2 py-0.5 text-xs"
                :class="isCurrentUserContributor(name) ? 'bg-blue-100 font-semibold text-blue-700' : 'bg-gray-100 text-gray-600'">
                {{ name }}
                <span v-if="isCurrentUserContributor(name)">(You)</span>
              </span>
            </div>
          </div>
          <p class="text-sm text-gray-500">Last: {{ new Date(proj.lastDoneAt).toLocaleDateString('en-PH') }}</p>
        </div>
      </div>
    </div>
  </section>
</template>
