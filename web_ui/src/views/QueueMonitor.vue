<template>
  <div class="queue-monitor">
    <a-card title="队列监控" :bordered="false">
      <a-spin :loading="loading" style="width: 100%;">
        <a-space direction="vertical" :size="16" style="width: 100%;">
          <!-- Queue Status Cards -->
          <a-row :gutter="16">
            <!-- List Queue Card -->
            <a-col :span="12">
              <a-card title="文章列表采集队列" :bordered="true">
                <template #extra>
                  <a-badge
                    :status="getListQueue()?.is_paused ? 'danger' : 'processing'"
                    :text="getListQueue()?.is_paused ? '已暂停' : '运行中'"
                  />
                </template>
                <a-space direction="vertical" :size="12" style="width: 100%;">
                  <a-statistic
                    title="队列大小"
                    :value="getListQueue()?.queue_size || 0"
                    :value-style="{ color: '#165dff' }"
                  />
                  <a-statistic
                    title="已处理任务"
                    :value="getListQueue()?.job_count || 0"
                  />
                  <a-space>
                    <a-button
                      v-if="!getListQueue()?.is_paused"
                      type="primary"
                      status="warning"
                      @click="handlePauseListQueue"
                      :loading="pausingList"
                    >
                      暂停队列
                    </a-button>
                    <a-button
                      v-else
                      type="primary"
                      @click="handleResumeListQueue"
                      :loading="resumingList"
                    >
                      恢复队列
                    </a-button>
                  </a-space>
                </a-space>
              </a-card>
            </a-col>

            <!-- Content Queue Card -->
            <a-col :span="12">
              <a-card title="文章内容采集队列" :bordered="true">
                <template #extra>
                  <a-badge
                    :status="getContentQueue()?.is_paused ? 'danger' : 'processing'"
                    :text="getContentQueue()?.is_paused ? '已暂停' : '运行中'"
                  />
                </template>
                <a-space direction="vertical" :size="12" style="width: 100%;">
                  <a-statistic
                    title="队列大小"
                    :value="getContentQueue()?.queue_size || 0"
                    :value-style="{ color: '#165dff' }"
                  />
                  <a-statistic
                    title="已处理任务"
                    :value="getContentQueue()?.job_count || 0"
                  />
                  <a-space>
                    <a-button
                      v-if="!getContentQueue()?.is_paused"
                      type="primary"
                      status="warning"
                      @click="handlePauseContentQueue"
                      :loading="pausingContent"
                    >
                      暂停队列
                    </a-button>
                    <a-button
                      v-else
                      type="primary"
                      @click="handleResumeContentQueue"
                      :loading="resumingContent"
                    >
                      恢复队列
                    </a-button>
                  </a-space>
                </a-space>
              </a-card>
            </a-col>
          </a-row>

          <!-- Job List Table -->
          <a-card title="任务列表" :bordered="true">
            <template #extra>
              <a-space>
                <a-switch v-model="autoRefresh" @change="handleAutoRefreshChange">
                  <template #checked>自动刷新</template>
                  <template #unchecked>手动刷新</template>
                </a-switch>
                <a-button @click="loadData" :loading="loading">
                  刷新
                </a-button>
              </a-space>
            </template>
            <a-table
              :columns="columns"
              :data="jobs"
              :pagination="false"
              :bordered="{ cell: true }"
              row-key="job_id"
            >
              <template #status="{ record }">
                <a-tag
                  :color="getStatusColor(record.status)"
                >
                  {{ record.status }}
                </a-tag>
              </template>

              <template #queue_name="{ record }">
                <a-tag color="blue">
                  {{ record.queue_name }}
                </a-tag>
              </template>

              <template #created_at="{ record }">
                <span style="font-size: 12px;">
                  {{ formatTime(record.created_at) }}
                </span>
              </template>

              <template #completed_at="{ record }">
                <span v-if="record.completed_at" style="font-size: 12px;">
                  {{ formatTime(record.completed_at) }}
                </span>
                <span v-else style="color: #c9cdd4;">-</span>
              </template>
            </a-table>
          </a-card>
        </a-space>
      </a-spin>
    </a-card>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted, onUnmounted } from 'vue'
import { Message } from '@arco-design/web-vue'
import type { QueueStatus, JobStatus } from '../types/queue'
import {
  fetchQueueStatus,
  fetchJobs,
  pauseListQueue,
  resumeListQueue,
  pauseContentQueue,
  resumeContentQueue
} from '../api/queue'

// Reactive state
const queueStatuses = ref<QueueStatus[]>([])
const jobs = ref<JobStatus[]>([])
const loading = ref(false)
const autoRefresh = ref(true)
const pausingList = ref(false)
const resumingList = ref(false)
const pausingContent = ref(false)
const resumingContent = ref(false)

let refreshInterval: ReturnType<typeof setInterval> | null = null

// Table columns
const columns = [
  {
    title: '任务ID',
    dataIndex: 'job_id',
    width: 250
  },
  {
    title: '队列',
    dataIndex: 'queue_name',
    slotName: 'queue_name',
    width: 150
  },
  {
    title: '状态',
    dataIndex: 'status',
    slotName: 'status',
    width: 120
  },
  {
    title: '创建时间',
    dataIndex: 'created_at',
    slotName: 'created_at',
    width: 180
  },
  {
    title: '完成时间',
    dataIndex: 'completed_at',
    slotName: 'completed_at',
    width: 180
  }
]

// Load queue status
const loadQueueStatus = async () => {
  try {
    queueStatuses.value = await fetchQueueStatus()
  } catch (error: any) {
    Message.error(error.message || '加载队列状态失败')
    throw error
  }
}

// Load jobs
const loadJobs = async () => {
  try {
    jobs.value = await fetchJobs()
  } catch (error: any) {
    Message.error(error.message || '加载任务列表失败')
    throw error
  }
}

// Load all data
const loadData = async () => {
  loading.value = true
  try {
    await Promise.all([loadQueueStatus(), loadJobs()])
  } catch (error) {
    // Error already handled in individual functions
  } finally {
    loading.value = false
  }
}

// Get list queue from statuses
const getListQueue = (): QueueStatus | undefined => {
  return queueStatuses.value.find(q => q.name === 'list_queue')
}

// Get content queue from statuses
const getContentQueue = (): QueueStatus | undefined => {
  return queueStatuses.value.find(q => q.name === 'content_queue')
}

// Handle pause list queue
const handlePauseListQueue = async () => {
  pausingList.value = true
  try {
    await pauseListQueue()
    Message.success('文章列表采集队列已暂停')
    await loadQueueStatus()
  } catch (error: any) {
    Message.error(error.message || '暂停队列失败')
  } finally {
    pausingList.value = false
  }
}

// Handle resume list queue
const handleResumeListQueue = async () => {
  resumingList.value = true
  try {
    await resumeListQueue()
    Message.success('文章列表采集队列已恢复')
    await loadQueueStatus()
  } catch (error: any) {
    Message.error(error.message || '恢复队列失败')
  } finally {
    resumingList.value = false
  }
}

// Handle pause content queue
const handlePauseContentQueue = async () => {
  pausingContent.value = true
  try {
    await pauseContentQueue()
    Message.success('文章内容采集队列已暂停')
    await loadQueueStatus()
  } catch (error: any) {
    Message.error(error.message || '暂停队列失败')
  } finally {
    pausingContent.value = false
  }
}

// Handle resume content queue
const handleResumeContentQueue = async () => {
  resumingContent.value = true
  try {
    await resumeContentQueue()
    Message.success('文章内容采集队列已恢复')
    await loadQueueStatus()
  } catch (error: any) {
    Message.error(error.message || '恢复队列失败')
  } finally {
    resumingContent.value = false
  }
}

// Handle auto-refresh toggle
const handleAutoRefreshChange = (value: boolean) => {
  if (value) {
    startAutoRefresh()
  } else {
    stopAutoRefresh()
  }
}

// Start auto-refresh
const startAutoRefresh = () => {
  if (refreshInterval) return
  refreshInterval = setInterval(() => {
    loadData()
  }, 5000) // Refresh every 5 seconds
}

// Stop auto-refresh
const stopAutoRefresh = () => {
  if (refreshInterval) {
    clearInterval(refreshInterval)
    refreshInterval = null
  }
}

// Get status color for badge
const getStatusColor = (status: string): string => {
  switch (status) {
    case 'QUEUED':
      return 'blue'
    case 'RUNNING':
      return 'orange'
    case 'COMPLETED':
      return 'green'
    case 'FAILED':
      return 'red'
    default:
      return 'gray'
  }
}

// Format timestamp
const formatTime = (timestamp: string): string => {
  if (!timestamp) return '-'
  const date = new Date(timestamp)
  return date.toLocaleString('zh-CN', {
    year: 'numeric',
    month: '2-digit',
    day: '2-digit',
    hour: '2-digit',
    minute: '2-digit',
    second: '2-digit'
  })
}

// Lifecycle hooks
onMounted(() => {
  loadData()
  if (autoRefresh.value) {
    startAutoRefresh()
  }
})

onUnmounted(() => {
  stopAutoRefresh()
})
</script>

<style scoped>
.queue-monitor {
  padding: 16px;
}
</style>
