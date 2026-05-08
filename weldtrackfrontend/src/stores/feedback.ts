import { defineStore } from 'pinia'
import api from '../services/api'

export type Feedback = {
  id: number
  email: string
  projectType: string
  rating: number
  comment: string
  date: string
}

type BackendFeedback = {
  id: number
  email: string
  project_type: string
  rating: number
  comment: string
  date: string
}

function toFrontendFeedback(item: BackendFeedback): Feedback {
  return {
    id: item.id,
    email: item.email,
    projectType: item.project_type,
    rating: item.rating,
    comment: item.comment,
    date: item.date,
  }
}

function toBackendFeedbackPayload(item: Partial<Feedback>) {
  return {
    ...(item.email !== undefined ? { email: item.email } : {}),
    ...(item.projectType !== undefined ? { project_type: item.projectType } : {}),
    ...(item.rating !== undefined ? { rating: item.rating } : {}),
    ...(item.comment !== undefined ? { comment: item.comment } : {}),
  }
}

export const useFeedbackStore = defineStore('feedback', {
  state: () => ({
    feedbacks: [] as Feedback[],
  }),
  actions: {
    async fetchFeedbacks() {
      const response = await api.get('/feedbacks')
      this.feedbacks = Array.isArray(response.data)
        ? (response.data as BackendFeedback[]).map(toFrontendFeedback)
        : []
      return this.feedbacks
    },

    async addFeedback(feedback: Omit<Feedback, 'id' | 'date'>) {
      const response = await api.post('/feedbacks', toBackendFeedbackPayload(feedback))
      const created = toFrontendFeedback(response.data as BackendFeedback)
      this.feedbacks.push(created)
      return created
    },

    async updateFeedback(id: number, feedback: Partial<Omit<Feedback, 'id'>>) {
      const response = await api.put(`/feedbacks/${id}`, toBackendFeedbackPayload(feedback))
      const updated = toFrontendFeedback(response.data as BackendFeedback)
      const idx = this.feedbacks.findIndex((f) => f.id === id)
      if (idx !== -1) {
        this.feedbacks[idx] = updated
      }
      return updated
    },

    async deleteFeedback(id: number) {
      await api.delete(`/feedbacks/${id}`)
      this.feedbacks = this.feedbacks.filter((f) => f.id !== id)
      return true
    },
  },
})
