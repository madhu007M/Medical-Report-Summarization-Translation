import axios from 'axios'

const BASE = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000'

const api = axios.create({ baseURL: BASE, timeout: 90000 })

export function getApiBaseUrl() {
  return BASE
}

export function apiAbsoluteUrl(path: string) {
  const normalized = path.startsWith('/') ? path : `/${path}`
  return `${BASE}${normalized}`
}

export async function extractText(file: File) {
  const form = new FormData()
  form.append('file', file)
  const { data } = await api.post('/extract-text', form)
  return data
}

export async function processReport(
  file: File,
  opts: { language?: string; phone?: string; location?: string; symptoms?: string }
) {
  const form = new FormData()
  form.append('file', file)
  if (opts.language)  form.append('language', opts.language)
  if (opts.phone)     form.append('phone', opts.phone)
  if (opts.location)  form.append('location', opts.location)
  if (opts.symptoms)  form.append('symptoms', opts.symptoms)
  const { data } = await api.post('/process-report', form)
  return data
}

export async function chat(sessionId: string, message: string, symptoms: string[]) {
  const { data } = await api.post('/chatbot', { session_id: sessionId, message, symptoms })
  return data
}

export async function getOutbreaks(region = '') {
  const { data } = await api.get('/outbreaks', { params: { region } })
  return data
}

export async function getDoctorAlerts(region = '') {
  const { data } = await api.get('/doctor/alerts', { params: { region } })
  return data
}

export async function postDoctorAlert(payload: {
  doctor_name: string; region: string; title: string; message: string
}) {
  const { data } = await api.post('/doctor/alerts', payload)
  return data
}

export async function translateText(text: string, targetLanguage: string) {
  const { data } = await api.post('/translate', { text, target_language: targetLanguage })
  return data
}

export async function getSupportedLanguages() {
  const { data } = await api.get('/languages')
  return data
}

export async function exportPDF(reportId: string) {
  const response = await api.get(`/export/pdf/${reportId}`, { responseType: 'blob' })
  return response.data
}

export default api
