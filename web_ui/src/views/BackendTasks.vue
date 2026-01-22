<template>
  <div class="backend-tasks">
    <a-card title="后台任务管理" :bordered="false">
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

          <!-- Scheduler Status -->
          <a-card title="调度器状态" :bordered="true">
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
            <a-row :gutter="16">
              <a-col :span="12">
                <a-statistic
                  title="调度器状态"
                  :value="schedulerStatus.running ? '运行中' : '已停止'"
                  :value-style="{ color: schedulerStatus.running ? '#00b42a' : '#f53f3f' }"
                />
              </a-col>
              <a-col :span="12">
                <a-statistic
                  title="调度任务数量"
                  :value="schedulerStatus.job_count"
                  :value-style="{ color: '#165dff' }"
                />
              </a-col>
            </a-row>
          </a-card>

          <!-- Scheduler History -->
          <a-card title="调度历史" :bordered="true">
            <template #extra>
              <a-button type="outline" @click="showHistoryModal = true">
                查看调度历史
              </a-button>
            </template>
            <a-table
              :columns="schedulerColumns"
              :data="schedulerJobs"
              :pagination="false"
              :bordered="{ cell: true }"
              row-key="id"
            >
              <template #status="{ record }">
                <a-tag
                  :color="record.status === 'active' ? 'green' : 'red'"
                >
                  {{ record.status === 'active' ? '活动' : '暂停' }}
                </a-tag>
              </template>

              <template #next_run_time="{ record }">
                <span v-if="record.next_run_time" style="font-size: 12px;">
                  {{ formatTime(record.next_run_time) }}
                </span>
                <span v-else style="color: #c9cdd4;">-</span>
              </template>

              <template #last_run_time="{ record }">
                <span v-if="record.last_run_time" style="font-size: 12px;">
                  {{ formatTime(record.last_run_time) }}
                </span>
                <span v-else style="color: #c9cdd4;">-</span>
              </template>
            </a-table>
          </a-card>
        </a-space>
      </a-spin>
    </a-card>

    <!-- Scheduler History Modal -->
    <a-modal
      v-model:visible="showHistoryModal"
      title="调度任务历史"
      :footer="false"
      width="80%"
    >
      <a-table
        :columns="schedulerColumns"
        :data="schedulerJobs"
        :pagination="false"
        :bordered="{ cell: true }"
        row-key="id"
      >
        <template #status="{ record }">
          <a-tag
            :color="record.status === 'active' ? 'green' : 'red'"
          >
            {{ record.status === 'active' ? '活动' : '暂停' }}
          </a-tag>
        </template>

        <template #next_run_time="{ record }">
          <span v-if="record.next_run_time" style="font-size: 12px;">
            {{ formatTime(record.next_run_time) }}
          </span>
          <span v-else style="color: #c9cdd4;">-</span>
        </template>

        <template #last_run_time="{ record }">
          <span v-if="record.last_run_time" style="font-size: 12px;">
            {{ formatTime(record.last_run_time) }}
          </span>
          <span v-else style="color: #c9cdd4;">-</span>
        </template>
      </a-table>
    </a-modal>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted, onUnmounted } from 'vue'
import { Message } from '@arco-design/web-vue'
import type { QueueStatus } from '../types/queue'
import type { SchedulerJob, SchedulerStatus } from '../types/scheduler'
import {
  fetchQueueStatus,
  fetchJobs,
  pauseListQueue,
  resumeListQueue,
  pauseContentQueue,
  resumeContentQueue
} from '../api/queue'
import {
  fetchSchedulerJobs,
  fetchSchedulerStatus
} from '../api/scheduler'

// Reactive state
const queueStatuses = ref<QueueStatus[]>([])
const schedulerJobs = ref<SchedulerJob[]>([])
const schedulerStatus = ref<SchedulerStatus>({ running: false, job_count: 0 })
const loading = ref(false)
const autoRefresh = ref(true)
const pausingList = ref(false)
const resumingList = ref(false)
const pausingContent = ref(false)
const resumingContent = ref(false)
const showHistoryModal = ref(false)

let refreshInterval: ReturnType<typeof setInterval> | null = null

// Table columns
const schedulerColumns = [
  {
    title: '任务ID',
    dataIndex: 'id',
    width: 250
  },
  {
    title: '任务名称',
    dataIndex: 'name',
    width: 150
  },
  {
    title: '状态',
    dataIndex: 'status',
    slotName: 'status',
    width: 100
  },
  {
    title: 'Cron表达式',
    dataIndex: 'trigger',
    width: 200
  },
  {
    title: '下次运行时间',
    dataIndex: 'next_run_time',
    slotName: 'next_run_time',
    width: 180
  },
  {
    title: '上次运行时间',
    dataIndex: 'last_run_time',
    slotName: 'last_run_time',
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

// Load scheduler jobs
const loadSchedulerJobs = async () => {
  try {
    schedulerJobs.value = await fetchSchedulerJobs()
  } catch (error: any) {
    Message.error(error.message || '加载调度任务失败')
    throw error
  }
}

// Load scheduler status
const loadSchedulerStatusData = async () => {
  try {
    schedulerStatus.value = await fetchSchedulerStatus()
  } catch (error: any) {
    Message.error(error.message || '加载调度器状态失败')
    throw error
  }
}

// Load all data
const loadData = async () => {
  loading.value = true
  try {
    await Promise.all([
      loadQueueStatus(),
      loadSchedulerJobs(),
      loadSchedulerStatusData()
    ])
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
.backend-tasks {
  padding: 16px;
}
</style>
