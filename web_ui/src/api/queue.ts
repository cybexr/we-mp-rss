import http from './http'
import type { QueueStatus, JobStatus, QueueStatusResponse, JobListResponse } from '../types/queue'

/**
 * Fetch status of all queues
 * @returns Promise resolving to array of queue statuses
 */
export const fetchQueueStatus = async (): Promise<QueueStatus[]> => {
  const response = await http.get<QueueStatus[]>('/queues/status')
  return response || []
}

/**
 * Fetch job list from queues
 * @param queueName Optional queue name filter
 * @returns Promise resolving to array of job statuses
 */
export const fetchJobs = async (queueName?: string): Promise<JobStatus[]> => {
  const params = queueName ? { queue_name: queueName } : {}
  const response = await http.get<JobStatus[]>('/queues/jobs', { params })
  return response || []
}

/**
 * Pause the list queue
 * @returns Promise resolving when operation completes
 */
export const pauseListQueue = async (): Promise<void> => {
  await http.post('/queues/list/pause')
}

/**
 * Resume the list queue
 * @returns Promise resolving when operation completes
 */
export const resumeListQueue = async (): Promise<void> => {
  await http.post('/queues/list/resume')
}

/**
 * Pause the content queue
 * @returns Promise resolving when operation completes
 */
export const pauseContentQueue = async (): Promise<void> => {
  await http.post('/queues/content/pause')
}

/**
 * Resume the content queue
 * @returns Promise resolving when operation completes
 */
export const resumeContentQueue = async (): Promise<void> => {
  await http.post('/queues/content/resume')
}
