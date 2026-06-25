<script setup lang="ts">
import { computed, onMounted, reactive, ref } from 'vue'
import { Star, ThumbsUp, MessageSquare, Send } from 'lucide-vue-next'
import { useAuthStore } from '../../../../stores/auth'
import { useFeedbackStore } from '../../../../stores/feedback'
import { useModalStore } from '../../../../stores/modal'
import ModalShell from '../../../../components/ui/ModalShell.vue'
import api from '../../../../api/api'
import { type Feedback, type FeedbackComment } from '../../../../types/feedback'

const props = defineProps<{ isAdmin?: boolean }>()

const authStore = useAuthStore()
const feedbackStore = useFeedbackStore()
const modalStore = useModalStore()

const isStaff = computed(() => authStore.role === 'staff')
const canSubmitFeedback = computed(() => !props.isAdmin && !isStaff.value)

const isDialogOpen = ref(false)
const currentEmail = computed(() => authStore.email || '')
const editingFeedbackId = ref<number | null>(null)
const isSubmitting = ref(false)
const newCommentText = ref<Record<number, string>>({})
const showComments = ref<Record<number, boolean>>({})
const activeRatingFilter = ref<number | null>(null)

const formData = reactive({
  projectType: '',
  rating: 5,
  comment: '',
})

const services = ref<Array<{ id: number; name: string }>>([])
const loadingServices = ref(false)

const getImageUrl = (url?: string) => {
    if (!url) return '';
    const cleanUrl = url.replace('/api', '');
    return `${import.meta.env.VITE_API_BASE_URL}${cleanUrl}`;
};

const getSortedComments = (comments: FeedbackComment[]) => {
  return [...comments].sort((a, b) => new Date(b.date).getTime() - new Date(a.date).getTime())
}

const isLiked = (feedback: Feedback) => {
  return feedback.likes.some(l => l.userEmail.toLowerCase() === currentEmail.value.toLowerCase())
}

const toggleComments = (feedbackId: number) => {
  showComments.value[feedbackId] = !showComments.value[feedbackId]
}

async function handleAddComment(feedbackId: number) {
  const comment = newCommentText.value[feedbackId]
  if (!comment || !comment.trim()) return
  await feedbackStore.addComment(feedbackId, comment)
  newCommentText.value[feedbackId] = ''
}

async function fetchServices() {
  loadingServices.value = true
  try {
    const response = await api.get('/services')
    services.value = (response.data || []).map((s: any) => ({
      id: s.id,
      name: s.name,
    }))
  } catch (error) {
    console.error('Failed to load services:', error)
    services.value = []
  } finally {
    loadingServices.value = false
  }
}

const feedbacksSorted = computed(() => {
  let filtered = [...feedbackStore.feedbacks]
  
  if (activeRatingFilter.value !== null) {
    filtered = filtered.filter(f => f.rating === activeRatingFilter.value)
  }

  return filtered.sort((a, b) => {
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

onMounted(async () => {
  await Promise.all([
    feedbackStore.fetchFeedbacks(),
    fetchServices(),
  ])
})

function resetForm() {
  formData.projectType = ''
  formData.rating = 5
  formData.comment = ''
}

function openDialog() {
  editingFeedbackId.value = null
  resetForm()
  isDialogOpen.value = true
}

function closeDialog() {
  isDialogOpen.value = false
  editingFeedbackId.value = null
}

function openEditDialog(feedback: { id: number; email: string; projectType: string; rating: number; comment: string }) {
  if (feedback.email.toLowerCase() !== currentEmail.value.toLowerCase()) return
  editingFeedbackId.value = feedback.id
  formData.projectType = feedback.projectType
  formData.rating = feedback.rating
  formData.comment = feedback.comment
  isDialogOpen.value = true
}

async function deleteFeedback(feedbackId: number, feedbackEmail: string) {
  if (feedbackEmail.toLowerCase() !== currentEmail.value.toLowerCase()) return
  modalStore.open({
    title: 'Delete feedback?',
    message: 'This action will permanently remove the feedback entry.',
    variant: 'error',
    confirmLabel: 'Delete',
    cancelLabel: 'Cancel',
    onConfirm: () => feedbackStore.deleteFeedback(feedbackId),
  })
}

async function submitFeedback() {
  if (!currentEmail.value || !formData.projectType || !formData.comment.trim()) {
    return
  }

  isSubmitting.value = true
  try {
    const payload = {
      email: currentEmail.value,
      projectType: formData.projectType,
      rating: formData.rating,
      comment: formData.comment.trim(),
    }

    if (editingFeedbackId.value) {
      await feedbackStore.updateFeedback(editingFeedbackId.value, payload)
    } else {
      await feedbackStore.addFeedback(payload)
    }

    closeDialog()
    resetForm()
  } finally {
    isSubmitting.value = false
  }
}

function getRatingBgColor(rating: number) {
  if (rating >= 4) return 'bg-green-50 border-green-200'
  if (rating === 3) return 'bg-yellow-50 border-yellow-200'
  return 'bg-red-50 border-red-200'
}

function formatFeedbackDate(value: string) {
  const date = new Date(value)
  if (Number.isNaN(date.getTime())) {
    return value
  }

  return date.toLocaleString('en-PH', {
    year: 'numeric',
    month: 'short',
    day: '2-digit',
    hour: '2-digit',
    minute: '2-digit',
  })
}

function canManageFeedback(feedbackEmail: string) {
  if (!canSubmitFeedback.value) return false
  return feedbackEmail.toLowerCase() === currentEmail.value.toLowerCase()
}
</script>

<template>
  <section class="space-y-8">
    <div class="mb-6 flex flex-col gap-4 lg:flex-row lg:items-center lg:justify-between">
      <div class="flex items-start gap-3">
        <div class="flex h-12 w-12 items-center justify-center rounded-lg bg-linear-to-br from-sky-50 to-white ring-1 ring-sky-100">
          <Star class="h-6 w-6 text-sky-600" />
        </div>
        <div>
          <h1 class="text-3xl font-bold text-gray-900">
            {{ props.isAdmin ? 'Customer Feedback Monitoring' : 'Service Feedback' }}
          </h1>
          <p class="mt-2 text-gray-600">
            {{ props.isAdmin ? 'Monitor and review customer feedback on our welding services' : 'See what our customers say about our welding services' }}
          </p>
        </div>
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

    <div class="rounded-lg border border-gray-200 bg-white p-6">
      <div class="grid grid-cols-1 gap-6 md:grid-cols-2">
        <div>
          <div class="flex items-baseline gap-2">
            <span class="text-5xl font-bold text-gray-900">{{ averageRating }}</span>
            <span class="text-xl text-gray-600">/ 5</span>
          </div>
          <p class="mt-2 text-sm text-gray-600">Based on {{ feedbackStore.feedbacks.length }} reviews</p>
          
          <!-- Rating Filter Buttons -->
          <div class="mt-4 flex flex-wrap gap-2">
            <button
              v-for="rating in [null, 5, 4, 3, 2, 1]"
              :key="rating ?? 'all'"
              @click="activeRatingFilter = rating"
              :class="['px-3 py-1 rounded-full text-xs font-semibold transition', activeRatingFilter === rating ? 'bg-sky-600 text-white' : 'bg-slate-100 text-slate-600 hover:bg-slate-200']"
            >
              {{ rating === null ? 'All' : `${rating} Stars` }}
            </button>
          </div>
          
          <p v-if="feedbackStore.feedbacks.length === 0" class="mt-3 text-xs font-medium text-gray-500">No ratings yet</p>
          <div v-else class="mt-4 flex gap-1">
            <svg
              v-for="i in 5"
              :key="i"
              viewBox="0 0 24 24"
              :class="['h-5 w-5', i <= Math.round(averageRating) ? 'text-yellow-400' : 'text-gray-300']"
              fill="currentColor"
              aria-hidden="true"
            >
              <path d="M12 17.27L18.18 21l-1.64-7.03L22 9.24l-7.19-.61L12 2 9.19 8.63 2 9.24l5.46 4.73L5.82 21z" />
            </svg>
          </div>
        </div>

        <div class="space-y-3">
          <div v-for="rating in [5, 4, 3, 2, 1]" :key="rating" class="flex items-center gap-3">
            <div class="flex gap-1" :aria-label="`${rating} star ratings`">
              <svg
                v-for="i in 5"
                :key="i"
                viewBox="0 0 24 24"
                :class="['h-4 w-4', i <= rating && starPercentage(rating) > 0 ? 'text-yellow-400' : 'text-gray-300']"
                fill="currentColor"
                aria-hidden="true"
              >
                <path d="M12 17.27L18.18 21l-1.64-7.03L22 9.24l-7.19-.61L12 2 9.19 8.63 2 9.24l5.46 4.73L5.82 21z" />
              </svg>
            </div>
            <div class="h-2 w-24 rounded-full border border-gray-200 bg-gray-100">
              <div class="h-full rounded-full bg-yellow-400" :style="{ width: starPercentage(rating) + '%' }" />
            </div>
            <span class="w-12 text-right text-sm text-gray-600">{{ starPercentage(rating) }}%</span>
          </div>
        </div>
      </div>
    </div>

    <div class="space-y-4">
      <div v-if="feedbacksSorted.length === 0" class="rounded-lg border border-gray-200 bg-gray-50 p-8 text-center">
        <svg class="mx-auto h-12 w-12 text-gray-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M7 8h10M7 12h4m1 8l-4-4H5a2 2 0 01-2-2V6a2 2 0 012-2h14a2 2 0 012 2v8a2 2 0 01-2 2h-3l-4 4z" />
        </svg>
        <h3 class="mt-4 text-lg font-medium text-gray-900">No feedback yet</h3>
        <p class="mt-1 text-sm text-gray-600">Be the first to share your experience</p>
      </div>

      <div v-for="feedback in feedbacksSorted" :key="feedback.id" :class="['rounded-lg border p-4 sm:p-6', getRatingBgColor(feedback.rating)]">
        <div class="flex flex-col gap-3 sm:flex-row sm:items-start sm:justify-between">
          <div class="flex items-start gap-2 sm:gap-3 min-w-0 flex-1">
            <div class="flex h-8 w-8 sm:h-10 sm:w-10 shrink-0 items-center justify-center rounded-full bg-slate-200 overflow-hidden border border-slate-300">
              <img v-if="feedback.profileImage" :src="getImageUrl(feedback.profileImage)" alt="Profile" class="h-full w-full object-cover">
              <span v-else class="text-xs font-semibold text-slate-600">{{ feedback.email.slice(0, 1).toUpperCase() }}</span>
            </div>
            <div class="min-w-0 flex-1">
              <h3 class="font-semibold text-gray-900 text-sm sm:text-base overflow-auto">{{ feedback.email }}</h3>
              <p class="text-xs sm:text-sm text-gray-600 overflow-auto">{{ feedback.projectType }}</p>
            </div>
          </div>
          <div class="flex flex-col items-start sm:items-end gap-2 shrink-0">
            <div class="flex gap-0.5 sm:gap-1" :aria-label="`${feedback.rating} out of 5 stars`">
              <svg
                v-for="i in 5"
                :key="i"
                viewBox="0 0 24 24"
                :class="['h-3 w-3 sm:h-4 sm:w-4', i <= feedback.rating ? 'text-yellow-400' : 'text-gray-300']"
                fill="currentColor"
                aria-hidden="true"
              >
                <path d="M12 17.27L18.18 21l-1.64-7.03L22 9.24l-7.19-.61L12 2 9.19 8.63 2 9.24l5.46 4.73L5.82 21z" />
              </svg>
            </div>
            <p class="text-xs text-gray-600">{{ formatFeedbackDate(feedback.date) }}</p>
            <div v-if="canManageFeedback(feedback.email)" class="mt-1 flex gap-1 sm:gap-2">
              <button type="button" class="rounded-lg border border-blue-300 px-2 py-0.5 sm:py-1 text-xs font-semibold text-blue-700 hover:bg-blue-50 whitespace-nowrap" @click="openEditDialog(feedback)">Edit</button>
              <button type="button" class="rounded-lg border border-red-300 px-2 py-0.5 sm:py-1 text-xs font-semibold text-red-700 hover:bg-red-50 whitespace-nowrap" @click="deleteFeedback(feedback.id, feedback.email)">Delete</button>
            </div>
          </div>
        </div>
        <p class="mt-3 sm:mt-4 text-sm sm:text-base text-gray-700 overflow-auto">{{ feedback.comment }}</p>

        <div class="mt-4 flex items-center gap-4">
          <button @click="feedbackStore.toggleLike(feedback.id)" :class="['flex items-center gap-1 text-xs font-semibold', isLiked(feedback) ? 'text-blue-600' : 'text-slate-500']">
            <ThumbsUp class="h-4 w-4" />
            {{ feedback.likes.length }}
          </button>
          <button @click="toggleComments(feedback.id)" class="flex items-center gap-1 text-xs text-slate-500 font-semibold">
            <MessageSquare class="h-4 w-4" />
            {{ feedback.comments.length }}
          </button>
        </div>

        <div v-if="showComments[feedback.id]" class="mt-4 space-y-2">
          <div class="max-h-[200px] overflow-y-auto space-y-2">
            <div v-for="comment in getSortedComments(feedback.comments)" :key="comment.id" class="text-sm bg-slate-50 p-3 rounded-lg border border-slate-100 flex gap-3">
              <div class="h-8 w-8 shrink-0 rounded-full bg-slate-200 overflow-hidden border border-slate-300">
                <img v-if="comment.profileImage" :src="getImageUrl(comment.profileImage)" alt="Profile" class="h-full w-full object-cover">
                <span v-else class="text-xs font-semibold text-slate-600 w-full h-full flex items-center justify-center">{{ comment.userEmail.slice(0, 1).toUpperCase() }}</span>
              </div>
              <div class="flex-1">
                <div class="flex items-center justify-between">
                    <span class="font-semibold text-slate-800">{{ comment.userEmail }}</span>
                    <span class="text-xs text-slate-500">{{ formatFeedbackDate(comment.date) }}</span>
                </div>
                <p class="text-slate-700 mt-1">{{ comment.comment }}</p>
              </div>
            </div>
          </div>
          <div class="flex gap-2">
            <input v-model="newCommentText[feedback.id]" placeholder="Add a comment..." class="flex-1 rounded-lg border border-slate-200 px-3 py-1 text-sm">
            <button @click="handleAddComment(feedback.id)" class="text-blue-600 hover:text-blue-700">
              <Send class="h-4 w-4" />
            </button>
          </div>
        </div>
      </div>
    </div>

    <ModalShell
      :show="isDialogOpen && canSubmitFeedback"
      :title="editingFeedbackId ? 'Edit Feedback' : 'Share Your Feedback'"
      subtitle="Customer review"
      tone="blue"
      size="lg"
      @close="closeDialog"
    >
      <form class="space-y-4" @submit.prevent="submitFeedback">
        <div>
          <label class="block text-sm font-medium text-gray-700" for="email">Email</label>
          <input
            id="email"
            :value="currentEmail"
            type="email"
            readonly
            class="mt-1 w-full rounded-xl border border-slate-200 bg-slate-50 px-4 py-3 text-slate-600 shadow-sm"
          />
        </div>

        <div>
          <label class="block text-sm font-medium text-gray-700" for="projectType">Project Type</label>
          <select
            id="projectType"
            v-model="formData.projectType"
            required
            :disabled="loadingServices || services.length === 0"
            class="mt-1 w-full rounded-xl border border-slate-200 bg-slate-50 px-4 py-3 shadow-sm outline-none transition focus:border-blue-500 focus:ring-2 focus:ring-blue-200 disabled:opacity-50 disabled:cursor-not-allowed"
          >
            <option value="">{{ loadingServices ? 'Loading services...' : services.length === 0 ? 'No services available' : 'Select project type' }}</option>
            <option v-for="service in services" :key="service.id" :value="service.name">{{ service.name }}</option>
          </select>
        </div>

        <div>
          <label class="mb-2 block text-sm font-medium text-gray-700">Rating</label>
          <div class="flex items-center gap-2">
            <button
              v-for="rating in [1, 2, 3, 4, 5]"
              :key="rating"
              type="button"
              class="rounded p-1 transition-transform hover:scale-110"
              :aria-label="`Rate ${rating} star${rating > 1 ? 's' : ''}`"
              @click="formData.rating = rating"
            >
              <svg
                viewBox="0 0 24 24"
                :class="['h-8 w-8', rating <= formData.rating ? 'text-yellow-400' : 'text-slate-300']"
                fill="currentColor"
                aria-hidden="true"
              >
                <path d="M12 17.27L18.18 21l-1.64-7.03L22 9.24l-7.19-.61L12 2 9.19 8.63 2 9.24l5.46 4.73L5.82 21z" />
              </svg>
            </button>
          </div>
          <p class="mt-1 text-xs font-medium text-slate-500">Selected: {{ formData.rating }}/5</p>
        </div>

        <div>
          <label class="block text-sm font-medium text-gray-700" for="comment">Your Feedback</label>
          <textarea
            id="comment"
            v-model="formData.comment"
            required
            rows="4"
            placeholder="Tell us about your experience with our service..."
            class="mt-1 w-full rounded-xl border border-slate-200 bg-slate-50 px-4 py-3 shadow-sm outline-none transition focus:border-blue-500 focus:ring-2 focus:ring-blue-200"
          />
        </div>

        <div class="flex gap-3 pt-4">
          <button type="button" class="flex-1 rounded-xl border border-slate-200 bg-white px-4 py-3 font-semibold text-slate-700 shadow-sm hover:bg-slate-50 disabled:opacity-50 disabled:cursor-not-allowed" :disabled="isSubmitting" @click="closeDialog">Cancel</button>
          <button type="submit" class="flex-1 rounded-xl bg-linear-to-r from-blue-600 to-sky-600 px-4 py-3 font-semibold text-white shadow-lg shadow-blue-600/20 hover:from-blue-700 hover:to-sky-700 disabled:opacity-50 disabled:cursor-not-allowed inline-flex items-center justify-center gap-2" :disabled="isSubmitting">
            <svg v-if="isSubmitting" class="h-4 w-4 animate-spin" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"></circle>
              <path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
            </svg>
            <span>{{ isSubmitting ? (editingFeedbackId ? 'Updating...' : 'Submitting...') : (editingFeedbackId ? 'Update Feedback' : 'Submit Feedback') }}</span>
          </button>
        </div>
      </form>
    </ModalShell>
  </section>
</template>
