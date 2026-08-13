import api from '../api/api'

export type ImageFolder = 'avatars' | 'services' | 'jobs'

export async function uploadImage(file: File, folder: ImageFolder) {
  const formData = new FormData()
  formData.append('file', file)
  const response = await api.post<{ url: string }>(`/uploads/image?folder=${folder}`, formData, {
    headers: { 'Content-Type': 'multipart/form-data' },
  })
  return response.data.url
}

export function resolveImageUrl(url?: string | null) {
  if (!url || url.startsWith('data:') || url.startsWith('blob:') || /^https?:\/\//.test(url)) return url || ''
  const apiBase = String(import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000').replace(/\/$/, '')
  const origin = apiBase.replace(/\/api$/, '')
  return `${origin}${url.startsWith('/') ? url : `/${url}`}`
}
