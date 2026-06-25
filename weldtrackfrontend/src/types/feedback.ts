export type FeedbackComment = {
  id: number
  feedbackId: number
  userEmail: string
  comment: string
  date: string
  profileImage?: string
}

export type FeedbackLike = {
  id: number
  feedbackId: number
  userEmail: string
}

export type Feedback = {
  id: number
  email: string
  projectType: string
  rating: number
  comment: string
  date: string
  profileImage?: string
  comments: FeedbackComment[]
  likes: FeedbackLike[]
}

export type BackendFeedback = {
  id: number
  email: string
  project_type: string
  rating: number
  comment: string
  date: string
  profile_image?: string
  comments: { id: number; feedback_id: number; user_email: string; comment: string; date: string }[]
  likes: { id: number; feedback_id: number; user_email: string }[]
}
