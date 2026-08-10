import { defineStore } from 'pinia'
import axios from 'axios'
import type { Feedback } from '../types/feedback'
import * as feedbackService from '../api/feedback'

export const useFeedbackStore = defineStore('feedback', {
  state: () => ({
    feedbacks: [] as Feedback[],
  }),
  actions: {
    async fetchFeedbacks() {
      try {
        this.feedbacks = await feedbackService.fetchFeedbacks()
        return this.feedbacks
      } catch (error) {
        if (axios.isAxiosError(error) && error.response?.status === 404) {
          this.feedbacks = []
          return this.feedbacks
        }
        throw error
      }
    },

    async addFeedback(feedback: Omit<Feedback, 'id' | 'date'>) {
      const created = await feedbackService.addFeedback(feedback)
      this.feedbacks.push(created)
      return created
    },

    async updateFeedback(id: string, feedback: Partial<Omit<Feedback, 'id'>>) {
      const updated = await feedbackService.updateFeedback(id, feedback)
      const idx = this.feedbacks.findIndex((f) => f.id === id)
      if (idx !== -1) {
        this.feedbacks[idx] = updated
      }
      return updated
    },

    async toggleLike(feedbackId: string) {
      await feedbackService.toggleLike(feedbackId)
      await this.fetchFeedbacks() // Refresh feedback to update likes count/state
    },

    async addComment(feedbackId: string, comment: string) {
      await feedbackService.addComment(feedbackId, comment)
      await this.fetchFeedbacks() // Refresh feedback to update comments
    },

    async deleteFeedback(id: string) {
      await feedbackService.deleteFeedback(id)
      this.feedbacks = this.feedbacks.filter((f) => f.id !== id)
    },
  },
})
