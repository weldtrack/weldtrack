import { defineStore } from 'pinia'
import api from '../services/api'

export type Feedback = {
  id: number
  customerName: string
  email: string
  projectType: string
  rating: number
  comment: string
  date: string
}

export const useFeedbackStore = defineStore('feedback', {
  state: () => ({
    feedbacks: [
      {
        id: 1,
        customerName: 'John Doe',
        email: 'john@example.com',
        projectType: 'Gate Welding',
        rating: 5,
        comment: 'Excellent work! The gate looks amazing and was completed on time. Highly recommend!',
        date: '2024-04-15',
      },
      {
        id: 2,
        customerName: 'Maria Garcia',
        email: 'maria@example.com',
        projectType: 'Metal Railings',
        rating: 4,
        comment: 'Great craftsmanship. The railings are sturdy and well-designed. Very satisfied with the results.',
        date: '2024-04-10',
      },
      {
        id: 3,
        customerName: 'Robert Smith',
        email: 'robert@example.com',
        projectType: 'Steel Frame Construction',
        rating: 5,
        comment: 'Professional team, excellent attention to detail. Our steel frame project exceeded expectations!',
        date: '2024-04-05',
      },
      {
        id: 4,
        customerName: 'Anna Martinez',
        email: 'anna@example.com',
        projectType: 'Metal Shelving',
        rating: 4,
        comment: 'Good quality work. Communication was clear throughout the project. Would work with them again.',
        date: '2024-03-28',
      },
      {
        id: 5,
        customerName: 'David Lee',
        email: 'david@example.com',
        projectType: 'Repair & Maintenance',
        rating: 5,
        comment: 'Quick turnaround and excellent service. Fixed our equipment perfectly!',
        date: '2024-03-20',
      },
    ] as Feedback[],
  }),
  actions: {
    async fetchFeedbacks() {
      try {
        const response = await api.get('/feedbacks')
        this.feedbacks = response.data
        return response.data
      } catch (error) {
        console.error('Failed to fetch feedbacks:', error)
        // Fall back to existing local data on API error
        return this.feedbacks
      }
    },

    async addFeedback(feedback: Omit<Feedback, 'id'>) {
      try {
        const response = await api.post('/feedbacks', feedback)
        this.feedbacks.push(response.data)
        return response.data
      } catch (error) {
        console.error('Failed to add feedback:', error)
        // Fallback: add locally with generated ID
        const newFeedback = {
          ...feedback,
          id: Date.now(),
        }
        this.feedbacks.push(newFeedback)
        return newFeedback
      }
    },

    async updateFeedback(id: number, feedback: Partial<Omit<Feedback, 'id'>>) {
      try {
        const response = await api.put(`/feedbacks/${id}`, feedback)
        const idx = this.feedbacks.findIndex((f) => f.id === id)
        if (idx !== -1) {
          this.feedbacks[idx] = response.data
        }
        return response.data
      } catch (error) {
        console.error('Failed to update feedback:', error)
        // Fallback: update locally
        const idx = this.feedbacks.findIndex((f) => f.id === id)
        if (idx !== -1) {
          this.feedbacks[idx] = { ...this.feedbacks[idx], ...feedback }
        }
        return this.feedbacks[idx]
      }
    },

    async deleteFeedback(id: number) {
      try {
        await api.delete(`/feedbacks/${id}`)
        this.feedbacks = this.feedbacks.filter((f) => f.id !== id)
        return true
      } catch (error) {
        console.error('Failed to delete feedback:', error)
        // Fallback: delete locally
        this.feedbacks = this.feedbacks.filter((f) => f.id !== id)
        return true
      }
    },
  },
})
