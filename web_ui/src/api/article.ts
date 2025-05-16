import http from './http'

export interface Article {
  id: number
  title: string
  content: string
  account_name: string
  publish_time: string
  status: string
  link: string
}

export interface ArticleListParams {
  page?: number
  pageSize?: number
  search?: string
  status?: string
  account_id?: number
}

export interface ArticleListResult {
  total: number
  data: Article[]
}

export const getArticles = (params: ArticleListParams) => {
  return http.get<ArticleListResult>('/mps', { params })
}

export const getArticleDetail = (id: number) => {
  return http.get<Article>(`/feeds/${id}`)
}

export const deleteArticle = (id: number) => {
  return http.delete(`/feeds/${id}`)
}