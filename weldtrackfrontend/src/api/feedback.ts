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
    profileImage: item.profile_image,
    comments: item.comments.map(c => ({
      id: c.id,
      feedbackId: c.feedback_id,
      userEmail: c.user_email,
      comment: c.comment,
      date: c.date,
      profileImage: c.profile_image,
    })),
    likes: item.likes.map(l => ({
      id: l.id,
      feedbackId: l.feedback_id,
      userEmail: l.user_email,
    })),
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

export async function updateFeedback(id: string, feedback: Partial<Omit<Feedback, 'id'>>) {
  const response = await api.put(`/feedbacks/${id}`, toBackendFeedbackPayload(feedback))
  return toFrontendFeedback(response.data as BackendFeedback)
}

export async function deleteFeedback(id: string) {
  await api.delete(`/feedbacks/${id}`)
}

export async function toggleLike(feedbackId: string) {
  await api.post(`/feedbacks/${feedbackId}/likes`)
}

export async function addComment(feedbackId: string, comment: string) {
  const response = await api.post(`/feedbacks/${feedbackId}/comments`, { comment })
  return {
    id: response.data.id,
    feedbackId: response.data.feedback_id,
    userEmail: response.data.user_email,
    comment: response.data.comment,
    date: response.data.date,
    profileImage: response.data.profile_image,
  }
}
