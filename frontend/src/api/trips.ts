import client from './client'
import type { TripPlan, TripPlanCreate } from '@/types'

export async function apiGetTrips(): Promise<TripPlan[]> {
  const res = await client.get<TripPlan[]>('/trips')
  return res.data
}

export async function apiGetTrip(id: string): Promise<TripPlan> {
  const res = await client.get<TripPlan>(`/trips/${id}`)
  return res.data
}

export async function apiCreateTrip(data: TripPlanCreate): Promise<TripPlan> {
  const res = await client.post<TripPlan>('/trips', data)
  return res.data
}

export async function apiUpdateTrip(id: string, data: TripPlanCreate): Promise<TripPlan> {
  const res = await client.put<TripPlan>(`/trips/${id}`, data)
  return res.data
}

export async function apiUpdateTripItems(id: string, itemIds: string[], lockedIds: string[] = []): Promise<TripPlan> {
  const res = await client.put<TripPlan>(`/trips/${id}/items`, { item_ids: itemIds, locked_item_ids: lockedIds })
  return res.data
}

export async function apiDeleteTrip(id: string): Promise<void> {
  await client.delete(`/trips/${id}`)
}
