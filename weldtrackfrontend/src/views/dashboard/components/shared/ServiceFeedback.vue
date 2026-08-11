<script setup lang="ts">
import InfoTooltip from '../../../../components/ui/InfoTooltip.vue'
import LocalLoader from '../../../../components/ui/LocalLoader.vue'
import { computed, onMounted, reactive, ref } from 'vue'
import { Star, ThumbsUp, MessageSquare, Send } from 'lucide-vue-next'
import { useAuthStore } from '../../../../stores/auth'
import { useFeedbackStore } from '../../../../stores/feedback'
import { useModalStore } from '../../../../stores/modal'
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
const editingFeedbackId = ref<string | null>(null)
const isSubmitting = ref(false)
const newCommentText = ref<Record<string, string>>({})
const showComments = ref<Record<string, boolean>>({})
const activeRatingFilter = ref<number | null>(null)

const formData = reactive({
  projectType: '',
  rating: 5,
  comment: '',
})

const services = ref<Array<{ id: string; name: string }>>([])
const loadingServices = ref(false)

const failedProfileImages = ref<Record<string, boolean>>({})

const getImageUrl = (url?: string) => {
  if (!url) return ''
  if (/^(data:|blob:|https?:\/\/)/i.test(url)) return url

  const apiBase = String(import.meta.env.VITE_API_BASE_URL || '').replace(/\/$/, '')
  const cleanUrl = url.startsWith('/api/') && apiBase.endsWith('/api')
    ? url.slice(4)
    : url
  return `${apiBase}${cleanUrl.startsWith('/') ? '' : '/'}${cleanUrl}`
}

function markProfileImageFailed(key: string) {
  failedProfileImages.value[key] = true
}

const getSortedComments = (comments: FeedbackComment[]) => {
  return [...comments].sort((a, b) => new Date(b.date).getTime() - new Date(a.date).getTime())
}

const isLiked = (feedback: Feedback) => {
  return feedback.likes.some(l => l.userEmail.toLowerCase() === currentEmail.value.toLowerCase())
}

const toggleComments = (feedbackId: string) => {
  showComments.value[feedbackId] = !showComments.value[feedbackId]
}

async function handleAddComment(feedbackId: string) {
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
  await feedbackStore.fetchFeedbacks()
})

function resetForm() {
  formData.projectType = ''
  formData.rating = 5
  formData.comment = ''
}

async function ensureServicesLoaded() {
  if (services.value.length === 0 && !loadingServices.value) await fetchServices()
}

function openDialog() {
  editingFeedbackId.value = null
  resetForm()
  isDialogOpen.value = true
  void ensureServicesLoaded()
}

function closeDialog() {
  isDialogOpen.value = false
  editingFeedbackId.value = null
}

function openEditDialog(feedback: { id: string; email: string; projectType: string; rating: number; comment: string }) {
  if (feedback.email.toLowerCase() !== currentEmail.value.toLowerCase()) return
  editingFeedbackId.value = feedback.id
  formData.projectType = feedback.projectType
  formData.rating = feedback.rating
  formData.comment = feedback.comment
  isDialogOpen.value = true
  void ensureServicesLoaded()
}

async function deleteFeedback(feedbackId: string, feedbackEmail: string) {
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
      comments: [],
      likes: []
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
  <section class="space-y-6 relative">
    <LocalLoader v-if="loadingServices" />
    <template v-if="!isDialogOpen || !canSubmitFeedback">
      <!-- Header -->
      <div class="flex flex-col gap-4 sm:flex-row sm:items-center sm:justify-between">
        <div class="flex items-start gap-3">
          <div class="flex h-12 w-12 items-center justify-center">
            <Star class="dashboard-view-icon h-6 w-6 text-sky-600 dark:text-sky-400" />
          </div>
          <div>
            <h3 class="text-2xl font-semibold text-slate-900 dark:text-slate-100">
              {{ props.isAdmin ? 'Customer Feedback Monitoring' : 'Service Feedback' }}
            </h3>
            <p class="text-sm text-slate-600 dark:text-slate-400">
              {{ props.isAdmin ? 'Monitor and review customer feedback on our welding services' : 'See what our customers say about our welding services' }}
            </p>
          </div>
        </div>
        <button
          v-if="canSubmitFeedback"
          type="button"
          class="inline-flex items-center justify-center gap-2 rounded-xl bg-sky-600 px-4 py-2.5 text-sm font-semibold text-white shadow-xs transition-colors hover:bg-sky-700 dark:bg-sky-600 dark:hover:bg-sky-500 shrink-0"
          @click="openDialog"
        >
          <svg class="h-4 w-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 4v16m8-8H4" />
          </svg>
          <span>Leave Feedback</span>
        </button>
      </div>

      <!-- Rating Summary Card -->
      <div class="rounded-2xl border border-slate-200 bg-white p-6 shadow-xs dark:border-slate-800 dark:bg-slate-900">
        <div class="grid grid-cols-1 gap-6 md:grid-cols-2 items-center">
          <div>
            <div class="flex items-baseline gap-2">
              <span class="text-5xl font-extrabold text-slate-900 dark:text-slate-100">{{ averageRating }}</span>
              <span class="text-xl font-medium text-slate-400 dark:text-slate-500">/ 5</span>
            </div>
            <p class="mt-1.5 text-sm text-slate-500 dark:text-slate-400 font-medium">Based on {{ feedbackStore.feedbacks.length }} reviews</p>
            
            <!-- Overall Stars -->
            <div class="mt-3 flex gap-1">
              <svg
                v-for="i in 5"
                :key="i"
                viewBox="0 0 24 24"
                :class="['h-5 w-5', i <= Math.round(averageRating) ? 'text-amber-400' : 'text-slate-200 dark:text-slate-700']"
                fill="currentColor"
                aria-hidden="true"
              >
                <path d="M12 17.27L18.18 21l-1.64-7.03L22 9.24l-7.19-.61L12 2 9.19 8.63 2 9.24l5.46 4.73L5.82 21z" />
              </svg>
            </div>

            <!-- Rating Filter Buttons -->
            <div class="mt-5 flex flex-wrap gap-2">
              <button
                v-for="rating in [null, 5, 4, 3, 2, 1]"
                :key="rating ?? 'all'"
                @click="activeRatingFilter = rating"
                :class="['px-3 py-1.5 rounded-full text-xs font-semibold transition-all', activeRatingFilter === rating ? 'bg-sky-600 text-white shadow-xs' : 'bg-slate-100 text-slate-600 dark:bg-slate-800 dark:text-slate-300 hover:bg-slate-200 dark:hover:bg-slate-700']"
              >
                {{ rating === null ? 'All Reviews' : `${rating} Stars` }}
              </button>
            </div>
          </div>

          <!-- Breakdown Progress Bars -->
          <div class="space-y-2.5 pt-2 border-t border-slate-100 md:border-t-0 md:border-l md:pl-6 md:pt-0 dark:border-slate-800">
            <div v-for="rating in [5, 4, 3, 2, 1]" :key="rating" class="flex items-center gap-3">
              <div class="flex gap-0.5" :aria-label="`${rating} star ratings`">
                <svg
                  v-for="i in 5"
                  :key="i"
                  viewBox="0 0 24 24"
                  :class="['h-3.5 w-3.5', i <= rating ? 'text-amber-400' : 'text-slate-200 dark:text-slate-700']"
                  fill="currentColor"
                  aria-hidden="true"
                >
                  <path d="M12 17.27L18.18 21l-1.64-7.03L22 9.24l-7.19-.61L12 2 9.19 8.63 2 9.24l5.46 4.73L5.82 21z" />
                </svg>
              </div>
              <div class="h-2.5 flex-1 rounded-full bg-slate-100 dark:bg-slate-800 overflow-hidden">
                <div class="h-full rounded-full bg-amber-400 transition-all duration-300" :style="{ width: starPercentage(rating) + '%' }" />
              </div>
              <span class="w-10 text-right text-xs font-semibold text-slate-500 dark:text-slate-400">{{ starPercentage(rating) }}%</span>
            </div>
          </div>
        </div>
      </div>

      <!-- Feedbacks List -->
      <div class="space-y-4">
        <div v-if="feedbacksSorted.length === 0" class="rounded-2xl border border-slate-200 bg-slate-50 p-8 text-center dark:border-slate-800 dark:bg-slate-900">
          <Star class="mx-auto h-10 w-10 text-slate-400" />
          <h3 class="mt-3 text-lg font-bold text-slate-900 dark:text-slate-100">No feedback submitted yet</h3>
          <p class="mt-1 text-sm text-slate-500 dark:text-slate-400">Be the first to share your experience with our services.</p>
        </div>

        <div v-for="feedback in feedbacksSorted" :key="feedback.id" class="rounded-2xl border border-slate-200 bg-white p-5 sm:p-6 shadow-xs transition-all hover:border-slate-300 dark:border-slate-800 dark:bg-slate-900">
          <div class="flex flex-col gap-3 sm:flex-row sm:items-start sm:justify-between">
            <div class="flex items-start gap-3 min-w-0 flex-1">
              <div class="flex h-10 w-10 shrink-0 items-center justify-center rounded-full bg-slate-100 border border-slate-200 overflow-hidden dark:bg-slate-800 dark:border-slate-700">
                <img v-if="feedback.profileImage && !failedProfileImages[`feedback-${feedback.id}`]" :src="getImageUrl(feedback.profileImage)" :alt="`${feedback.email} profile`" class="h-full w-full object-cover" @error="markProfileImageFailed(`feedback-${feedback.id}`)">
                <span v-else class="text-sm font-bold text-slate-700 dark:text-slate-300">{{ feedback.email.slice(0, 1).toUpperCase() }}</span>
              </div>
              <div class="min-w-0 flex-1">
                <h4 class="font-bold text-slate-900 dark:text-slate-100 text-sm sm:text-base truncate">{{ feedback.email }}</h4>
                <p class="text-xs font-medium text-slate-500 dark:text-slate-400 truncate">{{ feedback.projectType }}</p>
              </div>
            </div>
            <div class="flex flex-col items-start sm:items-end gap-1.5 shrink-0">
              <div class="flex gap-0.5" :aria-label="`${feedback.rating} out of 5 stars`">
                <svg
                  v-for="i in 5"
                  :key="i"
                  viewBox="0 0 24 24"
                  :class="['h-4 w-4', i <= feedback.rating ? 'text-amber-400' : 'text-slate-200 dark:text-slate-700']"
                  fill="currentColor"
                  aria-hidden="true"
                >
                  <path d="M12 17.27L18.18 21l-1.64-7.03L22 9.24l-7.19-.61L12 2 9.19 8.63 2 9.24l5.46 4.73L5.82 21z" />
                </svg>
              </div>
              <p class="text-xs text-slate-400">{{ formatFeedbackDate(feedback.date) }}</p>
              <div v-if="canManageFeedback(feedback.email)" class="mt-1 flex gap-2">
                <button type="button" class="rounded-lg border border-slate-200 bg-white px-2.5 py-1 text-xs font-semibold text-slate-700 hover:bg-slate-50 dark:border-slate-700 dark:bg-slate-800 dark:text-slate-300 dark:hover:bg-slate-700 transition" @click="openEditDialog(feedback)">Edit</button>
                <button type="button" class="rounded-lg border border-rose-200 bg-rose-50/50 px-2.5 py-1 text-xs font-semibold text-rose-600 hover:bg-rose-100 dark:border-rose-900/50 dark:bg-rose-950/40 dark:text-rose-400 dark:hover:bg-rose-900/60 transition" @click="deleteFeedback(feedback.id, feedback.email)">Delete</button>
              </div>
            </div>
          </div>
          <p class="mt-4 text-sm sm:text-base text-slate-800 dark:text-slate-200 leading-relaxed break-words">{{ feedback.comment }}</p>

          <div class="mt-4 flex items-center gap-4 border-t border-slate-100 pt-3 dark:border-slate-800">
            <button @click="feedbackStore.toggleLike(feedback.id)" :class="['flex items-center gap-1.5 text-xs font-semibold transition', isLiked(feedback) ? 'text-sky-600 dark:text-sky-400' : 'text-slate-500 hover:text-slate-800 dark:text-slate-400 dark:hover:text-slate-200']">
              <ThumbsUp class="h-4 w-4" />
              <span>{{ feedback.likes.length }}</span>
            </button>
            <button @click="toggleComments(feedback.id)" class="flex items-center gap-1.5 text-xs font-semibold text-slate-500 hover:text-slate-800 dark:text-slate-400 dark:hover:text-slate-200 transition">
              <MessageSquare class="h-4 w-4" />
              <span>{{ feedback.comments.length }}</span>
            </button>
          </div>

          <div v-if="showComments[feedback.id]" class="mt-4 space-y-3 pt-2">
            <div class="max-h-[220px] overflow-y-auto space-y-2 pr-1">
              <div v-for="comment in getSortedComments(feedback.comments)" :key="comment.id" class="text-xs sm:text-sm bg-slate-50 p-3.5 rounded-xl border border-slate-100 flex gap-3 dark:bg-slate-800/60 dark:border-slate-800">
                <div class="flex h-7 w-7 shrink-0 items-center justify-center overflow-hidden rounded-full border border-slate-200 bg-slate-200 text-xs font-bold text-slate-700 dark:border-slate-600 dark:bg-slate-700 dark:text-slate-300">
                  <img
                    v-if="comment.profileImage && !failedProfileImages[`comment-${comment.id}`]"
                    :src="getImageUrl(comment.profileImage)"
                    :alt="`${comment.userEmail} profile`"
                    class="h-full w-full object-cover"
                    @error="markProfileImageFailed(`comment-${comment.id}`)"
                  >
                  <span v-else>{{ comment.userEmail.slice(0, 1).toUpperCase() }}</span>
                </div>
                <div class="flex-1 min-w-0">
                  <div class="flex items-center justify-between">
                    <span class="font-bold text-slate-900 dark:text-slate-100 truncate">{{ comment.userEmail }}</span>
                    <span class="text-[11px] text-slate-400 shrink-0">{{ formatFeedbackDate(comment.date) }}</span>
                  </div>
                  <p class="text-slate-700 dark:text-slate-300 mt-1 break-words">{{ comment.comment }}</p>
                </div>
              </div>
            </div>
            <div class="flex gap-2">
              <input v-model="newCommentText[feedback.id]" placeholder="Write a comment..." class="flex-1 rounded-xl border border-slate-200 bg-white px-3.5 py-2 text-xs sm:text-sm text-slate-900 outline-none focus:border-sky-500 dark:border-slate-700 dark:bg-slate-800 dark:text-slate-100">
              <button @click="handleAddComment(feedback.id)" class="rounded-xl bg-sky-600 px-3.5 py-2 text-white hover:bg-sky-700 transition">
                <Send class="h-4 w-4" />
              </button>
            </div>
          </div>
        </div>
      </div>
    </template>

    <!-- Inline Feedback Form -->
    <template v-else-if="isDialogOpen && canSubmitFeedback">
      <div class="rounded-2xl border border-slate-200 bg-white shadow-xs max-w-2xl mx-auto dark:border-slate-800 dark:bg-slate-900">
        <div class="border-b border-slate-100 px-6 py-5 flex items-center justify-between dark:border-slate-800">
          <div>
            <h3 class="text-xl font-bold text-slate-900 dark:text-slate-100">{{ editingFeedbackId ? 'Edit Feedback' : 'Share Your Feedback' }}</h3>
            <p class="text-xs text-slate-500 dark:text-slate-400 mt-0.5">Please share your experience with our welding services.</p>
          </div>
          <button 
            @click="closeDialog" 
            class="text-sm font-semibold text-slate-500 hover:text-slate-800 dark:text-slate-400 dark:hover:text-slate-200 transition-colors"
          >
            Cancel
          </button>
        </div>

        <div class="p-6">
          <form class="space-y-5" @submit.prevent="submitFeedback">
            <div>
              <label class="flex items-center text-sm font-semibold text-slate-700 dark:text-slate-300 mb-1.5" for="email">Your Email<InfoTooltip text="Please provide the email." /></label>
              <input
                id="email"
                :value="currentEmail"
                type="email"
                readonly
                class="w-full rounded-xl border border-slate-200 bg-slate-50 px-4 py-3 text-slate-600 shadow-xs cursor-not-allowed outline-none dark:border-slate-800 dark:bg-slate-950 dark:text-slate-400"
              />
            </div>

            <div>
              <label class="flex items-center text-sm font-semibold text-slate-700 dark:text-slate-300 mb-1.5" for="projectType">Project Type <span class="text-rose-500">*</span><InfoTooltip text="Please select the project type." /></label>
              <select
                id="projectType"
                v-model="formData.projectType"
                required
                :disabled="loadingServices || services.length === 0"
                class="w-full rounded-xl border border-slate-200 bg-white px-4 py-3 shadow-xs outline-none transition focus:border-sky-500 focus:ring-2 focus:ring-sky-200 disabled:opacity-50 disabled:cursor-not-allowed font-medium text-slate-800 dark:border-slate-800 dark:bg-slate-950 dark:text-slate-100"
              >
                <option value="">{{ loadingServices ? 'Loading services...' : services.length === 0 ? 'No services available' : 'Select project type' }}</option>
                <option v-for="service in services" :key="service.id" :value="service.name">{{ service.name }}</option>
              </select>
            </div>

            <div>
              <label class="flex items-center text-sm font-semibold text-slate-700 dark:text-slate-300 mb-1.5">Rating <span class="text-rose-500">*</span><InfoTooltip text="Please provide the rating." /></label>
              <div class="flex items-center gap-2">
                <button
                  v-for="rating in [1, 2, 3, 4, 5]"
                  :key="rating"
                  type="button"
                  class="rounded-xl p-2 transition-transform hover:scale-110 hover:bg-slate-50 dark:hover:bg-slate-800"
                  :aria-label="`Rate ${rating} star${rating > 1 ? 's' : ''}`"
                  @click="formData.rating = rating"
                >
                  <svg
                    viewBox="0 0 24 24"
                    :class="['h-9 w-9', rating <= formData.rating ? 'text-amber-400' : 'text-slate-200 dark:text-slate-700']"
                    fill="currentColor"
                    aria-hidden="true"
                  >
                    <path d="M12 17.27L18.18 21l-1.64-7.03L22 9.24l-7.19-.61L12 2 9.19 8.63 2 9.24l5.46 4.73L5.82 21z" />
                  </svg>
                </button>
              </div>
              <p class="mt-1.5 text-xs font-semibold text-slate-500 dark:text-slate-400">Selected: {{ formData.rating }} out of 5 stars</p>
            </div>

            <div>
              <label class="flex items-center text-sm font-semibold text-slate-700 dark:text-slate-300 mb-1.5" for="comment">Your Feedback <span class="text-rose-500">*</span><InfoTooltip text="Please provide your feedback." /></label>
              <textarea
                id="comment"
                v-model="formData.comment"
                required
                rows="4"
                placeholder="Tell us about your experience with our service..."
                class="w-full rounded-xl border border-slate-200 bg-white px-4 py-3 shadow-xs outline-none transition focus:border-sky-500 focus:ring-2 focus:ring-sky-200 dark:border-slate-800 dark:bg-slate-950 dark:text-slate-100"
              />
            </div>

            <div class="flex gap-3 pt-4 border-t border-slate-100 dark:border-slate-800 justify-end">
              <button type="button" class="rounded-xl border border-slate-200 bg-white px-5 py-2.5 text-sm font-semibold text-slate-700 shadow-xs hover:bg-slate-50 disabled:opacity-50 transition-colors dark:border-slate-700 dark:bg-slate-800 dark:text-slate-300 dark:hover:bg-slate-700" :disabled="isSubmitting" @click="closeDialog">Cancel</button>
              <button type="submit" class="rounded-xl bg-sky-600 px-6 py-2.5 text-sm font-semibold text-white shadow-xs hover:bg-sky-700 disabled:opacity-50 inline-flex items-center justify-center gap-2 transition-all dark:bg-sky-600 dark:hover:bg-sky-500" :disabled="isSubmitting">
                <svg v-if="isSubmitting" class="h-4 w-4 animate-spin" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"></circle>
                  <path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
                </svg>
                <span>{{ isSubmitting ? (editingFeedbackId ? 'Updating...' : 'Submitting...') : (editingFeedbackId ? 'Update Feedback' : 'Submit Feedback') }}</span>
              </button>
            </div>
          </form>
        </div>
      </div>
    </template>
  </section>
</template>
