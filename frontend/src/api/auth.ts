import client from './client'
import type { TokenResponse, User } from '@/types'

export async function apiLogin(username: string, password: string): Promise<TokenResponse> {
  const res = await client.post<TokenResponse>('/auth/login', { username, password })
  return res.data
}

export async function apiGetMe(): Promise<User> {
  const res = await client.get<User>('/auth/me')
  return res.data
}

export async function apiGetUsers(): Promise<User[]> {
  const res = await client.get<User[]>('/auth/users')
  return res.data
}

export async function apiCreateUser(data: { username: string; password: string; role: string }): Promise<User> {
  const res = await client.post<User>('/auth/users', data)
  return res.data
}

export async function apiUpdateUser(id: string, data: { password?: string; role?: string; is_active?: boolean }): Promise<User> {
  const res = await client.put<User>(`/auth/users/${id}`, data)
  return res.data
}

export async function apiDeleteUser(id: string): Promise<void> {
  await client.delete(`/auth/users/${id}`)
}
