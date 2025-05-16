import http from './http'

export interface Subscription {
  id: number
  name: string
  accountId: string
  rssUrl: string
  category: string
  description: string
  status: string
}

export interface AddSubscriptionParams {
  name: string
  accountId: string
  rssUrl: string
  category: string
  description?: string
}

export const getSubscriptions = () => {
  return http.get<Subscription[]>('/wx/mps')
}

export const addSubscription = (data: AddSubscriptionParams) => {
  return http.post('/wx/mps', data)
}

export const deleteSubscription = (id: number) => {
  return http.delete(`/wx/mps/${id}`)
}

export const updateSubscription = (id: number, data: Partial<Subscription>) => {
  return http.put(`/wx/mps/${id}`, data)
}