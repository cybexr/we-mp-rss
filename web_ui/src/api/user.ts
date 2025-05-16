import http from './http'

export interface UserInfo {
  username: string
  nickname: string
  email: string
  avatar: string
}

export interface ChangePasswordParams {
  old_password: string
  new_password: string
}

export const getUserInfo = () => {
  return http.get<UserInfo>('/user/info')
}

export const updateUserInfo = (data: Partial<UserInfo>) => {
  return http.put('/user/info', data)
}

export const changePassword = (data: ChangePasswordParams) => {
  return http.put('/user/password', data)
}

export const uploadAvatar = (file: FormData) => {
  return http.post<{ url: string }>('/user/avatar', file, {
    headers: {
      'Content-Type': 'multipart/form-data'
    }
  })
}