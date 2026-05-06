<script setup lang="ts">
import { computed, reactive, ref } from 'vue'
import { useAuthStore } from '../../../stores/auth'
import { useFeedbackStore } from '../../../stores/feedback'

const props = defineProps<{ isAdmin?: boolean }>()

const authStore = useAuthStore()
const feedbackStore = useFeedbackStore()

const isStaff = computed(() => authStore.role === 'staff')
const canSubmitFeedback = computed(() => !props.isAdmin && !isStaff.value)

const isDialogOpen = ref(false)
const currentEmail = computed(() => authStore.email || '')

const formData = reactive({
  customerName: '',
  projectType: '',
  rating: 5,
  comment: '',
})

const projectTypes = [
  'Gate Welding',
  'Metal Railings',
  'Steel Frame Construction',
  'Staircase Fabrication',
  'Metal Doors & Windows',
  'Pipe & Duct Welding',
  'Metal Shelving',
  'Automotive Welding',
  'Fence Installation',
  'Tank & Vessel Fabrication',
  'Repair & Maintenance',
  'Other',
]

const feedbacksSorted = computed(() => {
  return [...feedbackStore.feedbacks].sort((a, b) => {
    return new Date(b.date).getTime() - new Date(a.date).getTime()
  })
})

const averageRating = computed(() => {
  if (feedbackStore.feedbacks.length === 0) return 0
  const sum = feedbackStore.feedbacks.reduce((acc, f) => acc + f.rating, 0)
  return Math.round((sum / feedbackStore.feedbacks.length) * 10) / 10
})

const ratingCounts = computed(() => {
  const counts = { 5: 0, 4: 0, 3: 0, 2: 0, 1: 0 }
  feedbackStore.feedbacks.forEach((f) => {
    counts[f.rating as keyof typeof counts]++
  })
  return counts
})

const starPercentage = (rating: number) => {
  const count = ratingCounts.value[rating as keyof typeof ratingCounts.value]
  const total = feedbackStore.feedbacks.length
  return total === 0 ? 0 : Math.round((count / total) * 100)
}

function resetForm() {
  formData.customerName = authStore.email || ''
  formData.projectType = ''
  formData.rating = 5
  formData.comment = ''
}

function openDialog() {
  resetForm()
  isDialogOpen.value = true
}

function closeDialog() {
  isDialogOpen.value = false
}

async function submitFeedback() {
  if (!formData.customerName || !formData.projectType || !formData.comment.trim()) {
    return
  }

  await feedbackStore.addFeedback({
    customerName: formData.customerName,
    email: currentEmail.value,
    projectType: formData.projectType,
    rating: formData.rating,
    comment: formData.comment.trim(),
    date: '', // Backend will set the date
  }).catch(() => {
    // Fallback to local add is handled in store
  })
  closeDialog()
  resetForm()
}

function getRatingBgColor(rating: number) {
  if (rating >= 4) return 'bg-green-50 border-green-200'
  if (rating === 3) return 'bg-yellow-50 border-yellow-200'
  return 'bg-red-50 border-red-200'
}
</script>

<template>
  <section class="space-y-8">
    <div class="mb-6 flex flex-col justify-between gap-4 lg:flex-row lg:items-center">
      <div>
        <h1 class="text-3xl font-bold text-gray-900">{{ props.isAdmin ? 'Customer Feedback Monitoring' : 'Service Feedback' }}</h1>
        <p class="mt-2 text-gray-600">{{ props.isAdmin ? 'Monitor and review customer feedback on our welding services' : 'See what our customers say about our welding services' }}</p>
      </div>
      <button
        v-if="canSubmitFeedback"
        type="button"
        class="inline-flex items-center justify-center rounded-lg bg-blue-600 px-4 py-3 font-semibold text-white transition-colors hover:bg-blue-700"
        @click="openDialog"
      >
        <svg class="mr-2 h-5 w-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 4v16m8-8H4" />
        </svg>
        Leave Feedback
      </button>
    </div>

    <!-- Rating Overview -->
    <div class="rounded-lg border border-gray-200 bg-white p-6">
      <div class="grid grid-cols-1 gap-6 md:grid-cols-2">
        <div>
          <div class="flex items-baseline gap-2">
            <span class="text-5xl font-bold text-gray-900">{{ averageRating }}</span>
            <span class="text-xl text-gray-600">/ 5</span>
          </div>
          <p class="mt-2 text-sm text-gray-600">Based on {{ feedbackStore.feedbacks.length }} reviews</p>
          <div class="mt-4 flex gap-1">
            <span v-for="i in 5" :key="i" :class="['h-2 w-2 rounded-full', i <= Math.round(averageRating) ? 'bg-yellow-400' : 'bg-gray-300']" />
          </div>
        </div>

        <div class="space-y-3">
          <div v-for="rating in [5, 4, 3, 2, 1]" :key="rating" class="flex items-center gap-3">
            <div class="flex gap-1">
              <span v-for="i in 5" :key="i" :class="['h-3 w-3 rounded-full', i <= rating ? 'bg-yellow-400' : 'bg-gray-300']" />
            </div>
            <div class="h-2 w-24 rounded-full border border-gray-200 bg-gray-100">
              <div class="h-full rounded-full bg-yellow-400" :style="{ width: starPercentage(rating) + '%' }" />
            </div>
            <span class="w-12 text-right text-sm text-gray-600">{{ starPercentage(rating) }}%</span>
          </div>
        </div>
      </div>
    </div>

    <!-- Feedbacks List -->
    <div class="space-y-4">
      <div v-if="feedbacksSorted.length === 0" class="rounded-lg border border-gray-200 bg-gray-50 p-8 text-center">
        <svg class="mx-auto h-12 w-12 text-gray-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M7 8h10M7 12h4m1 8l-4-4H5a2 2 0 01-2-2V6a2 2 0 012-2h14a2 2 0 012 2v8a2 2 0 01-2 2h-3l-4 4z" />
        </svg>
        <h3 class="mt-4 text-lg font-medium text-gray-900">No feedback yet</h3>
        <p class="mt-1 text-sm text-gray-600">Be the first to share your experience</p>
      </div>

      <div v-for="feedback in feedbacksSorted" :key="feedback.id" :class="['rounded-lg border p-6', getRatingBgColor(feedback.rating)]">
        <div class="flex items-start justify-between gap-4">
          <div class="flex-1">
            <div class="flex items-center gap-3">
              <div class="flex h-10 w-10 items-center justify-center rounded-full bg-blue-600 text-white font-bold">
                {{ feedback.customerName.slice(0, 1).toUpperCase() }}
              </div>
              <div>
                <h3 class="font-semibold text-gray-900">{{ feedback.customerName }}</h3>
                <p class="text-sm text-gray-600">{{ feedback.projectType }}</p>
              </div>
            </div>
          </div>
          <div class="flex flex-col items-end gap-2">
            <div class="flex gap-1">
              <span v-for="i in 5" :key="i" :class="['h-4 w-4 rounded-full', i <= feedback.rating ? 'bg-yellow-400' : 'bg-gray-300']" />
            </div>
            <p class="text-xs text-gray-600">{{ feedback.date }}</p>
          </div>
        </div>
        <p class="mt-4 text-gray-700">{{ feedback.comment }}</p>
      </div>
    </div>

    <!-- Feedback Modal -->
    <div v-if="isDialogOpen && canSubmitFeedback" class="fixed inset-0 z-50 flex items-center justify-center bg-black/50 p-4" @click.self="closeDialog">
      <div class="w-full max-w-2xl rounded-2xl bg-white p-6 shadow-2xl">
        <div class="mb-5">
          <h4 class="text-lg font-semibold text-gray-900">Share Your Feedback</h4>
        </div>

        <form class="space-y-4" @submit.prevent="submitFeedback">
          <div>
            <label class="block text-sm font-medium text-gray-700" for="name">Name</label>
            <input id="name" v-model="formData.customerName" type="text" required class="mt-1 w-full rounded-lg border border-gray-300 bg-gray-50 px-4 py-3" />
          </div>

          <div>
            <label class="block text-sm font-medium text-gray-700" for="projectType">Project Type</label>
            <select id="projectType" v-model="formData.projectType" required class="mt-1 w-full rounded-lg border border-gray-300 bg-gray-50 px-4 py-3">
              <option value="">Select project type</option>
              <option v-for="type in projectTypes" :key="type" :value="type">{{ type }}</option>
            </select>
          </div>

          <div>
            <label class="block text-sm font-medium text-gray-700 mb-2">Rating</label>
            <div class="flex gap-2">
              <button
                v-for="rating in [1, 2, 3, 4, 5]"
                :key="rating"
                type="button"
                class="flex h-12 w-12 items-center justify-center rounded-lg border-2 transition-all"
                :class="formData.rating === rating ? 'border-yellow-400 bg-yellow-50' : 'border-gray-300 bg-white hover:border-yellow-300'"
                @click="formData.rating = rating"
              >
                <span class="text-lg font-bold" :class="formData.rating === rating ? 'text-yellow-600' : 'text-gray-400'">{{ rating }}</span>
              </button>
            </div>
          </div>

          <div>
            <label class="block text-sm font-medium text-gray-700" for="comment">Your Feedback</label>
            <textarea id="comment" v-model="formData.comment" required rows="4" placeholder="Tell us about your experience with our service..." class="mt-1 w-full rounded-lg border border-gray-300 bg-gray-50 px-4 py-3" />
          </div>

          <div class="flex gap-3 pt-4">
            <button type="button" class="flex-1 rounded-lg border border-gray-300 px-4 py-3 font-semibold text-gray-700 hover:bg-gray-50" @click="closeDialog">Cancel</button>
            <button type="submit" class="flex-1 rounded-lg bg-blue-600 px-4 py-3 font-semibold text-white hover:bg-blue-700">Submit Feedback</button>
          </div>
        </form>
      </div>
    </div>
  </section>
</template>
