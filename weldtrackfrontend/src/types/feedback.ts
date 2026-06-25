export type Feedback = {
  id: number
  email: string
  projectType: string
  rating: number
  comment: string
  date: string
  profileImage?: string
}

export type BackendFeedback = {
  id: number
  email: string
  project_type: string
  rating: number
  comment: string
  date: string
  profile_image?: string
}
