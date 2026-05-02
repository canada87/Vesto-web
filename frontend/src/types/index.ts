export interface User {
  id: string
  username: string
  role: 'admin' | 'user'
  is_active: boolean
  totp_enabled: boolean
  created_at: string
}

export interface LoginResponse {
  access_token?: string
  token_type: string
  requires_2fa: boolean
  partial_token?: string
}

export interface TwoFAVerifyResponse {
  access_token: string
  token_type: string
  trusted_device_token?: string
}

export interface TwoFASetupResponse {
  qr_code: string
  secret: string
}

export interface ClothingItem {
  id: string
  user_id: string
  name: string
  category: ClothingCategory
  age_years: number
  weight: ClothingWeight
  condition: ClothingCondition
  like_score: number
  usage_type: UsageType
  seasons: Season[]
  status: ItemStatus
  location: string
  color?: string
  notes?: string
  local_photo_path?: string
  photo_url?: string
  created_at: string
  updated_at: string
}

export interface ClothingItemCreate {
  name: string
  category: string
  age_years?: number
  weight?: string
  condition?: string
  like_score?: number
  usage_type?: string
  seasons?: string[]
  status?: string
  location?: string
  color?: string
  notes?: string
}

export interface ClothingItemListResponse {
  items: ClothingItem[]
  total: number
}

export interface OutfitLog {
  id: string
  user_id: string
  date: string
  item_ids: string[]
  occasion: string
  weather?: string
  notes?: string
  created_at: string
}

export interface OutfitLogCreate {
  date: string
  item_ids: string[]
  occasion: string
  weather?: string
  notes?: string
}

export interface TripPlan {
  id: string
  user_id: string
  name: string
  destination?: string
  start_date?: string
  end_date?: string
  trip_type: string
  duration_only: boolean
  custom_duration_days?: number
  item_ids: string[]
  locked_item_ids: string[]
  created_at: string
}

export interface TripPlanCreate {
  name: string
  destination?: string
  start_date?: string
  end_date?: string
  trip_type?: string
  duration_only?: boolean
  custom_duration_days?: number
}

export interface OutfitSuggestionRequest {
  occasion: string
  weather?: string
  season?: string
  location?: string
  novelty?: boolean
}

export interface OutfitSuggestionResponse {
  top?: ClothingItem
  bottom?: ClothingItem
  shoes?: ClothingItem
  outerwear?: ClothingItem
  accessories: ClothingItem[]
  missing_categories: string[]
}

export interface PackingSuggestionRequest {
  trip_type: string
  season: string
  duration_days: number
}

export interface PackingSuggestionResponse {
  items: ClothingItem[]
  missing_categories: string[]
}

export interface Stats {
  total_items: number
  total_logs: number
  total_trips: number
}

export type ClothingCategory = 'top' | 'bottom' | 'shoes' | 'outerwear' | 'accessory' | 'underwear' | 'sportswear'
export type ClothingWeight = 'light' | 'medium' | 'heavy'
export type ClothingCondition = 'new' | 'good' | 'worn' | 'old'
export type UsageType = 'work' | 'personal' | 'both'
export type Season = 'spring' | 'summer' | 'autumn' | 'winter'
export type ItemStatus = 'inWardrobe' | 'inLaundry' | 'inUse'
export type Weather = 'sunny' | 'cloudy' | 'rainy' | 'cold' | 'hot'
