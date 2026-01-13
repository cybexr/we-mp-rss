/**
 * Queue Status Interface
 * Represents the status of a task queue
 */
export interface QueueStatus {
  /** Queue name (e.g., 'list_queue', 'content_queue') */
  name: string
  /** Whether the queue is currently paused */
  is_paused: boolean
  /** Number of tasks currently in the queue */
  queue_size: number
  /** Total number of jobs processed */
  job_count: number
}

/**
 * Job Status Interface
 * Represents the status of an individual job in the queue
 */
export interface JobStatus {
  /** Unique job identifier */
  job_id: string
  /** Current job status (QUEUED, RUNNING, COMPLETED, FAILED) */
  status: string
  /** Name of the queue this job belongs to */
  queue_name: string
  /** Timestamp when the job was created */
  created_at: string
  /** Timestamp when the job was completed (null if not completed) */
  completed_at: string | null
}

/**
 * Queue Status Response
 * API response containing array of queue statuses
 */
export interface QueueStatusResponse {
  queues: QueueStatus[]
}

/**
 * Job List Response
 * API response containing array of job statuses
 */
export interface JobListResponse {
  jobs: JobStatus[]
}
