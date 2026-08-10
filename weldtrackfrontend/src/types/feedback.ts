export type FeedbackComment = {
  id: string
  feedbackId: string
  userEmail: string
  comment: string
  date: string
  profileImage?: string
}

export type FeedbackLike = {
  id: string
  feedbackId: string
  userEmail: string
}

export type Feedback = {
  id: string
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
  id: string
  email: string
  project_type: string
  rating: number
  comment: string
  date: string
  profile_image?: string
  comments: { id: string; feedback_id: string; user_email: string; comment: string; date: string; profile_image?: string }[]
  likes: { id: string; feedback_id: string; user_email: string }[]
}
