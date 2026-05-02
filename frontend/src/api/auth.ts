import client from './client'
import type { LoginResponse, TwoFAVerifyResponse, TwoFASetupResponse, User } from '@/types'

export async function apiLogin(
  username: string,
  password: string,
  trustedDeviceToken?: string | null,
): Promise<LoginResponse> {
  const res = await client.post<LoginResponse>('/auth/login', {
    username,
    password,
    trusted_device_token: trustedDeviceToken ?? undefined,
  })
  return res.data
}

export async function apiVerify2FA(
  partialToken: string,
  otpCode: string,
  rememberDevice: boolean,
): Promise<TwoFAVerifyResponse> {
  const res = await client.post<TwoFAVerifyResponse>('/auth/2fa/verify', {
    partial_token: partialToken,
    otp_code: otpCode,
    remember_device: rememberDevice,
  })
  return res.data
}

export async function apiSetup2FA(): Promise<TwoFASetupResponse> {
  const res = await client.post<TwoFASetupResponse>('/auth/2fa/setup')
  return res.data
}

export async function apiEnable2FA(otpCode: string): Promise<{ trusted_device_token: string }> {
  const res = await client.post('/auth/2fa/enable', { otp_code: otpCode })
  return res.data
}

export async function apiDisable2FA(otpCode: string): Promise<void> {
  await client.post('/auth/2fa/disable', { otp_code: otpCode })
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
