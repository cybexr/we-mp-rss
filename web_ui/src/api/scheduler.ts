import http from './http'
import type { SchedulerJob, SchedulerStatus } from '../types/scheduler'

/**
 * Fetch all scheduled jobs from the scheduler
 * @returns Promise resolving to array of scheduler jobs
 */
export const fetchSchedulerJobs = async (): Promise<SchedulerJob[]> => {
  const response = await http.get<SchedulerJob[]>('/scheduler/jobs')
  return response.data || []
}

/**
 * Fetch the scheduler status
 * @returns Promise resolving to scheduler status
 */
export const fetchSchedulerStatus = async (): Promise<SchedulerStatus> => {
  const response = await http.get<SchedulerStatus>('/scheduler/status')
  return response.data
}
