import client from './client'
import type { OutfitSuggestionRequest, OutfitSuggestionResponse, PackingSuggestionRequest, PackingSuggestionResponse } from '@/types'

export async function apiSuggestOutfit(data: OutfitSuggestionRequest): Promise<OutfitSuggestionResponse> {
  const res = await client.post<OutfitSuggestionResponse>('/suggestions/outfit', data)
  return res.data
}

export async function apiSuggestPacking(data: PackingSuggestionRequest): Promise<PackingSuggestionResponse> {
  const res = await client.post<PackingSuggestionResponse>('/suggestions/packing', data)
  return res.data
}
