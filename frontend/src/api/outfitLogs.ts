import client from './client'
import type { OutfitLog, OutfitLogCreate } from '@/types'

export async function apiGetLogs(days = 90): Promise<OutfitLog[]> {
  const res = await client.get<OutfitLog[]>('/outfit-logs', { params: { days } })
  return res.data
}

export async function apiCreateLog(data: OutfitLogCreate): Promise<OutfitLog> {
  const res = await client.post<OutfitLog>('/outfit-logs', data)
  return res.data
}

export async function apiDeleteLog(id: string): Promise<void> {
  await client.delete(`/outfit-logs/${id}`)
}
