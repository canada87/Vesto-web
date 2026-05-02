import client from './client'
import type { ClothingItem, ClothingItemListResponse } from '@/types'

export interface ItemFilters {
  category?: string
  status?: string
  season?: string
  location?: string
  usage_type?: string
}

export async function apiGetItems(filters: ItemFilters = {}): Promise<ClothingItemListResponse> {
  const res = await client.get<ClothingItemListResponse>('/items', { params: filters })
  return res.data
}

export async function apiGetItem(id: string): Promise<ClothingItem> {
  const res = await client.get<ClothingItem>(`/items/${id}`)
  return res.data
}

export async function apiCreateItem(formData: FormData): Promise<ClothingItem> {
  const res = await client.post<ClothingItem>('/items', formData, {
    headers: { 'Content-Type': 'multipart/form-data' },
  })
  return res.data
}

export async function apiUpdateItem(id: string, data: object): Promise<ClothingItem> {
  const res = await client.put<ClothingItem>(`/items/${id}`, data)
  return res.data
}

export async function apiDeleteItem(id: string): Promise<void> {
  await client.delete(`/items/${id}`)
}

export async function apiUploadPhoto(id: string, file: File): Promise<ClothingItem> {
  const formData = new FormData()
  formData.append('photo', file)
  const res = await client.post<ClothingItem>(`/items/${id}/photo`, formData, {
    headers: { 'Content-Type': 'multipart/form-data' },
  })
  return res.data
}

export async function apiDeletePhoto(id: string): Promise<ClothingItem> {
  const res = await client.delete<ClothingItem>(`/items/${id}/photo`)
  return res.data
}
