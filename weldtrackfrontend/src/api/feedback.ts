import api from './api'
import type { Feedback, BackendFeedback } from '../types/feedback'

export function toFrontendFeedback(item: BackendFeedback): Feedback {
  return {
    id: item.id,
    email: item.email,
    projectType: item.project_type,
    rating: item.rating,
    comment: item.comment,
    date: item.date,
  }
}

export function toBackendFeedbackPayload(item: Partial<Feedback>) {
  return {
    ...(item.email !== undefined ? { email: item.email } : {}),
    ...(item.projectType !== undefined ? { project_type: item.projectType } : {}),
    ...(item.rating !== undefined ? { rating: item.rating } : {}),
    ...(item.comment !== undefined ? { comment: item.comment } : {}),
  }
}

export async function fetchFeedbacks() {
  const response = await api.get('/feedbacks')
  return Array.isArray(response.data)
    ? (response.data as BackendFeedback[]).map(toFrontendFeedback)
    : []
}

export async function addFeedback(feedback: Omit<Feedback, 'id' | 'date'>) {
  const response = await api.post('/feedbacks', toBackendFeedbackPayload(feedback))
  return toFrontendFeedback(response.data as BackendFeedback)
}

export async function updateFeedback(id: number, feedback: Partial<Omit<Feedback, 'id'>>) {
  const response = await api.put(`/feedbacks/${id}`, toBackendFeedbackPayload(feedback))
  return toFrontendFeedback(response.data as BackendFeedback)
}

export async function deleteFeedback(id: number) {
  await api.delete(`/feedbacks/${id}`)
}
