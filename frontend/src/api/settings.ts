import client from './client'
import type { Stats } from '@/types'

export async function apiGetLocations(): Promise<string[]> {
  const res = await client.get<string[]>('/settings/locations')
  return res.data
}

export async function apiAddLocation(name: string): Promise<string[]> {
  const res = await client.post<string[]>('/settings/locations', { name })
  return res.data
}

export async function apiDeleteLocation(name: string): Promise<string[]> {
  const res = await client.delete<string[]>(`/settings/locations/${encodeURIComponent(name)}`)
  return res.data
}

export async function apiGetStats(): Promise<Stats> {
  const res = await client.get<Stats>('/settings/stats')
  return res.data
}

export async function apiSeedTestData(): Promise<void> {
  await client.post('/settings/seed-test-data')
}

export async function apiExportBackup(): Promise<void> {
  const res = await client.get('/backup/export', { responseType: 'blob' })
  const url = URL.createObjectURL(res.data)
  const a = document.createElement('a')
  a.href = url
  a.download = 'vesto-backup.json'
  a.click()
  URL.revokeObjectURL(url)
}

export async function apiImportBackup(file: File): Promise<void> {
  const formData = new FormData()
  formData.append('file', file)
  await client.post('/backup/import', formData, {
    headers: { 'Content-Type': 'multipart/form-data' },
  })
}
