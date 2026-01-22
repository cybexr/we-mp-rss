/**
 * Scheduler Job Interface
 * Represents a single scheduled job in the APScheduler
 */
export interface SchedulerJob {
  /** Unique job identifier */
  id: string
  /** Job name (typically the function name) */
  name: string
  /** Trigger expression (cron format) */
  trigger: string
  /** Next scheduled run time (ISO 8601) */
  next_run_time: string
  /** Last execution time (ISO 8601) */
  last_run_time: string
  /** Job status (active/paused) */
  status: string
}

/**
 * Scheduler Status Interface
 * Represents the overall status of the scheduler
 */
export interface SchedulerStatus {
  /** Whether the scheduler is running */
  running: boolean
  /** Total number of scheduled jobs */
  job_count: number
}

/**
 * Scheduler Status Response
 * API response containing scheduler status
 */
export interface SchedulerStatusResponse {
  running: boolean
  job_count: number
}
