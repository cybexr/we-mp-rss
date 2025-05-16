<template>
  <div class="article-list">
    <a-page-header
      title="文章列表"
      subtitle="管理您的公众号订阅内容"
      :show-back="false"
    >
      <template #extra>
        <a-space>
          <a-button type="primary" @click="showAddModal">
            <template #icon><icon-plus /></template>
            添加订阅
          </a-button>
          <a-button @click="refresh">
            <template #icon><icon-refresh /></template>
            刷新
          </a-button>
        </a-space>
      </template>
    </a-page-header>

    <a-card>
      <div class="search-bar">
        <a-input-search
          v-model="searchText"
          placeholder="搜索文章标题"
          @search="handleSearch"
          allow-clear
        />
        <a-select
          v-model="filterStatus"
          placeholder="筛选状态"
          style="width: 200px; margin-left: 12px"
          allow-clear
        >
          <a-option value="published">已发布</a-option>
          <a-option value="draft">草稿</a-option>
          <a-option value="deleted">已删除</a-option>
        </a-select>
      </div>

      <a-table
        :columns="columns"
        :data="articles"
        :loading="loading"
        :pagination="pagination"
        @page-change="handlePageChange"
        row-key="id"
      >
        <template #status="{ record }">
          <a-tag :color="statusColorMap[record.status]">
            {{ statusTextMap[record.status] }}
          </a-tag>
        </template>
        <template #actions="{ record }">
          <a-button type="text" @click="editArticle(record.id)">
            <template #icon><icon-edit /></template>
            编辑
          </a-button>
          <a-button type="text" status="danger" @click="deleteArticle(record.id)">
            <template #icon><icon-delete /></template>
            删除
          </a-button>
        </template>
      </a-table>
    </a-card>

    <AddSubscriptionModal 
      :visible="addModalVisible" 
      @update:visible="addModalVisible = $event"
      @success="handleAddSuccess"
    />
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { getArticles } from '@/api/article'
import AddSubscriptionModal from '@/components/AddSubscriptionModal.vue'

const articles = ref([])
const loading = ref(false)
const searchText = ref('')
const filterStatus = ref('')
const addModalVisible = ref(false)

const pagination = ref({
  current: 1,
  pageSize: 10,
  total: 0
})

const statusTextMap = {
  published: '已发布',
  draft: '草稿',
  deleted: '已删除'
}

const statusColorMap = {
  published: 'green',
  draft: 'orange',
  deleted: 'red'
}

const columns = [
  {
    title: 'ID',
    dataIndex: 'id',
    width: 80
  },
  {
    title: '标题',
    dataIndex: 'title',
    ellipsis: true
  },
  {
    title: '公众号',
    dataIndex: 'account_name'
  },
  {
    title: '发布时间',
    dataIndex: 'publish_time'
  },
  {
    title: '状态',
    slotName: 'status'
  },
  {
    title: '操作',
    slotName: 'actions',
    width: 200
  }
]

const fetchArticles = async () => {
  loading.value = true
  try {
    const res = await getArticles({
      page: pagination.value.current,
      pageSize: pagination.value.pageSize,
      search: searchText.value,
      status: filterStatus.value
    })
    articles.value = res.data
    pagination.value.total = res.total
  } finally {
    loading.value = false
  }
}

const handlePageChange = (page: number) => {
  pagination.value.current = page
  fetchArticles()
}

const handleSearch = () => {
  pagination.value.current = 1
  fetchArticles()
}

const refresh = () => {
  fetchArticles()
}

const showAddModal = () => {
  addModalVisible.value = true
}

const handleAddSuccess = () => {
  fetchArticles()
}

const editArticle = (id: number) => {
  // 编辑逻辑
}

const deleteArticle = (id: number) => {
  // 删除逻辑
}

onMounted(() => {
  fetchArticles()
})
</script>

<style scoped>
.article-list {
  padding: 20px;
}

.search-bar {
  display: flex;
  margin-bottom: 20px;
}
</style>