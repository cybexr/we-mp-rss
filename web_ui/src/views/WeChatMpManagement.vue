<template>
  <div class="wechat-mp-management">
    <a-card title="公众号管理" :bordered="false">
      <a-space direction="vertical" :size="16" style="width: 100%;">
        <a-space>
          <a-button type="primary" @click="showAddModal">添加公众号</a-button>
          <a-button @click="showBatchCategoryModal" :disabled="!selectedRowKeys.length">批量分类更新</a-button>
        </a-space>

        <a-space :size="12">
          <a-input-search
            v-model="searchText"
            placeholder="搜索公众号名称"
            @search="handleSearch"
            @keyup.enter="handleSearch"
            allow-clear
            style="width: 300px;"
          />
          <a-select
            v-model="selectedCategory"
            placeholder="选择分类"
            allow-clear
            @change="handleCategoryChange"
            style="width: 200px;"
          >
            <a-option value="">全部分类</a-option>
            <a-option value="__BLANK__">(空白尚未维护)</a-option>
            <a-option v-for="category in categories" :key="category" :value="category">
              {{ category }}
            </a-option>
          </a-select>
          <a-button @click="handleReset">重置</a-button>
        </a-space>

        <a-table
          v-if="!isMobile"
          :columns="columns"
          :data="mpList"
          :pagination="pagination"
          :loading="loading"
          :row-selection="{
            type: 'checkbox',
            showCheckedAll: true
          }"
          row-key="id"
          v-model:selectedKeys="selectedRowKeys"
          @page-change="handlePageChange"
        >
          <template #mp_name="{ record }">
            <a-space>
              <a-image
                v-if="record.mp_cover"
                :src="getAvatarUrl(record.mp_cover)"
                width="32"
                height="32"
                fit="cover"
                style="border-radius: 4px;"
              />
              <a-avatar
                v-else
                style="background-color: #165dff; min-width: 32px;"
              >
                {{ record.mp_name?.charAt(0) || '?' }}
              </a-avatar>
              <span>{{ record.mp_name }}</span>
            </a-space>
          </template>

          <template #status="{ record }">
            <a-tag :color="record.status ? 'green' : 'red'">
              {{ record.status ? '已启用' : '已禁用' }}
            </a-tag>
          </template>

          <template #category="{ record }">
            <a-tag v-if="record.category" color="blue">{{ record.category }}</a-tag>
            <span v-else style="color: #c9cdd4;">-</span>
          </template>

          <template #mp_intro="{ record }">
            <div class="mp-intro-cell">
              {{ record.mp_intro || '-' }}
            </div>
          </template>

          <template #last_publish_time="{ record }">
            <span v-if="record.last_publish_time" style="font-size: 12px;">
              {{ formatPublishTime(record.last_publish_time) }}
            </span>
            <span v-else style="color: #c9cdd4;">-</span>
          </template>

          <template #article_count="{ record }">
            <a-tag color="arcoblue" size="small">
              {{ record.article_count || 0 }} 篇
            </a-tag>
          </template>

          <template #action="{ record }">
            <a-space>
              <a-button size="mini" @click="showArticles(record)">文章列表</a-button>
              <a-button size="mini" @click="editMp(record)">编辑</a-button>
              <a-button size="mini" @click="showRefreshModal(record)">刷新</a-button>
              <a-button
                size="mini"
                status="danger"
                @click="deleteMp(record.id)"
              >
                删除
              </a-button>
            </a-space>
          </template>
        </a-table>

        <a-list
          v-else
          :loading="loading"
          :loading-more="loadingMore"
          :data="mpList"
          :pagination="pagination"
        >
          <template #item="{ item }">
            <a-list-item class="mobile-list-item">
              <a-list-item-meta
                :title="item.mp_name"
                :description="getMobileDescription(item)"
              >
                <template #avatar>
                  <a-image
                    v-if="item.mp_cover"
                    :src="getAvatarUrl(item.mp_cover)"
                    width="60"
                    height="60"
                    fit="cover"
                  />
                  <a-avatar v-else style="background-color: #165dff">{{ item.mp_name.charAt(0) }}</a-avatar>
                </template>
              </a-list-item-meta>
              <template #actions>
                <a-space direction="vertical" :size="4">
                  <a-space :size="4">
                    <a-tag v-if="item.category" color="blue" size="small">{{ item.category }}</a-tag>
                    <a-tag color="arcoblue" size="small">
                      {{ item.article_count || 0 }} 篇
                    </a-tag>
                  </a-space>
                  <a-tag v-if="item.last_publish_time" size="small" style="font-size: 11px;">
                    {{ formatPublishTime(item.last_publish_time) }}
                  </a-tag>
                  <a-tag :color="item.status ? 'green' : 'red'" size="small">
                    {{ item.status ? '已启用' : '已禁用' }}
                  </a-tag>
                  <a-space :size="4">
                    <a-button size="mini" @click="showArticles(item)">文章列表</a-button>
                    <a-button size="mini" @click="showRefreshModal(item)">刷新</a-button>
                    <a-button size="mini" @click="editMp(item)">编辑</a-button>
                    <a-button
                      size="mini"
                      status="danger"
                      @click="deleteMp(item.id)"
                    >
                      删除
                    </a-button>
                  </a-space>
                </a-space>
              </template>
            </a-list-item>
          </template>
          <template #footer>
            <div v-if="pagination.current * pagination.pageSize < pagination.total" class="load-more">
              <a-button
                type="primary"
                :loading="loadingMore"
                @click="() => {
                  pagination.current++
                  loadData(searchText.value, selectedCategory.value, true)
                }"
              >
                加载更多
              </a-button>
              <div class="total-count">
                共 {{ pagination.total }} 条
              </div>
            </div>
          </template>
        </a-list>
      </a-space>
    </a-card>

    <a-modal 
      v-model:visible="visible" 
      :title="modalTitle"
      @ok="handleOk"
      @cancel="handleCancel"
    >
      <a-form :model="form">
        <a-form-item label="公众号ID" field="mp_id">
          <a-input v-model="form.mp_id" :disabled="modalTitle === '编辑公众号'" />
        </a-form-item>
        <a-form-item label="公众号名称" field="mp_name">
          <a-input v-model="form.mp_name" :disabled="modalTitle === '编辑公众号'" />
        </a-form-item>
        <a-form-item label="封面图" field="mp_cover">
          <a-upload
            action="/wx/mps/upload"
            :headers="headers"
            @success="handleUploadSuccess"
          />
        </a-form-item>
        <a-form-item label="简介" field="mp_intro">
          <a-textarea v-model="form.mp_intro" :disabled="modalTitle === '编辑公众号'" />
        </a-form-item>
        <a-form-item label="状态" field="status">
          <a-switch v-model="form.status" />
        </a-form-item>
        <a-form-item label="缓存图片" field="cache_images">
          <a-switch v-model="form.cache_images" />
        </a-form-item>
        <a-form-item label="备注" field="remarks">
          <a-textarea v-model="form.remarks" placeholder="添加备注..." :max-length="255" />
        </a-form-item>
        <a-form-item label="分类" field="category">
          <a-auto-complete
            v-model="form.category"
            :data="categories"
            placeholder="选择或输入分类"
            :max-length="255"
          />
        </a-form-item>
      </a-form>
    </a-modal>

    <a-modal
      v-model:visible="batchCategoryModalVisible"
      title="批量分类更新"
      @ok="handleBatchCategoryOk"
      @cancel="handleBatchCategoryCancel"
    >
      <a-form :model="{ batchCategory }">
        <a-form-item label="选择分类" field="category">
          <a-auto-complete
            v-model="batchCategory"
            :data="categories"
            placeholder="选择或输入分类"
            :max-length="255"
          />
        </a-form-item>
      </a-form>
    </a-modal>

    <a-modal      v-model:visible="refreshModalVisible"      :title="`刷新 ${currentRefreshMpName}`"      @ok="handleRefreshOk"      @cancel="refreshModalVisible = false"    >      <a-form :model="refreshForm">        <a-form-item label="起始页" field="startPage">          <a-input-number v-model="refreshForm.startPage" :min="0" />        </a-form-item>        <a-form-item label="结束页" field="endPage">          <a-input-number v-model="refreshForm.endPage" :min="1" />        </a-form-item>      </a-form>    </a-modal>
    <a-modal
      v-model:visible="articleModalVisible"
      :title="`${currentMpName} - 文章列表`"
      :width="1000"
      :footer="false"
      @cancel="articleModalVisible = false"
    >
      <a-table
        :columns="articleColumns"
        :data="articles"
        :loading="articlesLoading"
        :pagination="{
          current: articlePagination.current,
          pageSize: articlePagination.pageSize,
          total: articlePagination.total,
          showTotal: true,
          showJumper: true,
          showPageSize: true
        }"
        row-key="id"
        @page-change="handleArticlePageChange"
      >
        <template #publish_time="{ record }">
          {{ formatTimestamp(record.publish_time) }}
        </template>
        <template #created_at="{ record }">
          {{ record.created_at ? new Date(record.created_at).toLocaleString('zh-CN') : '-' }}
        </template>
        <template #actions="{ record }">
          <a-button type="text" @click="viewArticle(record)" :title="record.id">
            <template #icon><icon-eye /></template>
          </a-button>
        </template>
      </a-table>
    </a-modal>

    <a-modal
      v-model:visible="articleDetailDrawerVisible"
      title="文章详情"
      :width="1000"
      :footer="false"
      @cancel="articleDetailDrawerVisible = false"
    >
      <div v-if="currentArticle" class="article-detail">
        <h2>{{ currentArticle.title }}</h2>
        <a-descriptions :column="1" bordered size="small">
          <a-descriptions-item label="公众号">{{ currentArticle.mp_name }}</a-descriptions-item>
          <a-descriptions-item label="发布时间">{{ formatTimestamp(currentArticle.publish_time) }}</a-descriptions-item>
          <a-descriptions-item label="更新时间">{{ currentArticle.time }}</a-descriptions-item>
          <a-descriptions-item label="链接">
            <a :href="currentArticle.url || currentArticle.link" target="_blank" rel="noopener">{{ currentArticle.url || currentArticle.link }}</a>
          </a-descriptions-item>
        </a-descriptions>
        <a-divider />
        <div class="article-content" v-html="currentArticle.content"></div>
      </div>
    </a-modal>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, onMounted, onBeforeUnmount } from 'vue'
import { getSubscriptions, addSubscription, updateSubscription, deleteSubscription, getCategories, batchUpdateCategory, UpdateMps } from '@/api/subscription'
import { getArticles, getArticleDetail } from '@/api/article'
import { getToken } from '@/utils/auth'
import { Avatar, ProxyImage } from '@/utils/constants'
import { Message, Modal } from '@arco-design/web-vue'
import { IconEye } from '@arco-design/web-vue/es/icon'
import { formatTimestamp, formatDateTime } from '@/utils/date'

const headers = { Authorization: `Bearer ${getToken()}` }

const isMobile = ref(window.innerWidth < 768)
const handleResize = () => {
  isMobile.value = window.innerWidth < 768
}

const columns = [
  { title: "名称", dataIndex: "mp_name", slotName: "mp_name", width: 200 },
  { title: "分类", slotName: "category", width: 100 },
  { title: "简介", dataIndex: "mp_intro", slotName: "mp_intro", width: 200, ellipsis: true, tooltip: true },
  { title: "备注", dataIndex: "remarks", ellipsis: true, tooltip: true, width: 150 },
  { title: "最后发布", dataIndex: "last_publish_time", slotName: "last_publish_time", width: 160, sortable: { sortDirections: ['ascend', 'descend'] } },
  { title: "文章数", dataIndex: "article_count", slotName: "article_count", width: 80, sortable: { sortDirections: ['ascend', 'descend'] } },
  { title: "状态", slotName: "status", width: 80 },
  { title: "操作", slotName: "action", width: 200 }
]

const mpList = ref([])
const loading = ref(false)
const loadingMore = ref(false)
const pagination = reactive({
  current: 1,
  pageSize: 10,
  total: 0
})

const searchText = ref('')
const selectedCategory = ref('')
const visible = ref(false)
const modalTitle = ref('添加公众号')
const inlineEditModalVisible = ref(false)
const currentEditId = ref('')
const categories = ref<string[]>([])
const selectedRowKeys = ref<string[]>([])
const batchCategoryModalVisible = ref(false)
const batchCategory = ref('')

n// 刷新相关状态
const refreshModalVisible = ref(false)
const currentRefreshMpId = ref('')
const currentRefreshMpName = ref('')
const refreshForm = reactive({
  startPage: 0,
  endPage: 1
})
// 文章列表相关状态
const articleModalVisible = ref(false)
const currentMpId = ref('')
const currentMpName = ref('')
const articles = ref([])
const articlesLoading = ref(false)
const articlePagination = reactive({
  current: 1,
  pageSize: 10,
  total: 0
})

// 文章详情抽屉相关状态
const articleDetailDrawerVisible = ref(false)
const currentArticle = ref<any>(null)

const form = reactive({
  mp_id: '',
  mp_name: '',
  mp_cover: '',
  mp_intro: '',
  status: true,
  cache_images: false,
  remarks: '',
  category: ''
})

const loadData = async (kw = '', category = '', isLoadMore = false) => {
  try {
    if (isLoadMore) {
      loadingMore.value = true
    } else {
      loading.value = true
    }

    const params: any = {
      page: pagination.current - 1, // 转换为0-based
      pageSize: pagination.pageSize
    }
    if (kw) {
      params.kw = kw
    }
    if (category === '__BLANK__') {
      // Filter for blank/uncategorized categories
      params.category = ''
    } else if (category) {
      // Filter for specific category (but not empty string "All Categories")
      params.category = category
    }
    // If category is empty string ('All'), don't send category parameter
    const res = await getSubscriptions(params)

    if (isLoadMore) {
      mpList.value = [...mpList.value, ...(res.list || [])]
    } else {
      mpList.value = res.list || []
    }
    pagination.total = res.total || 0
  } catch (error) {
    console.error('获取公众号列表错误:', error)
    Message.error(error.message)
  } finally {
    if (isLoadMore) {
      loadingMore.value = false
    } else {
      loading.value = false
    }
  }
}

const handleSearch = () => {
  pagination.current = 1
  loadData(searchText.value, selectedCategory.value)
}

const handleCategoryChange = () => {
  pagination.current = 1
  loadData(searchText.value, selectedCategory.value)
}

const handleReset = () => {
  searchText.value = ''
  selectedCategory.value = ''
  pagination.current = 1
  loadData()
}

const showAddModal = () => {
  modalTitle.value = '添加公众号'
  Object.keys(form).forEach(key => {
    if (key === 'status') {
      form[key] = true
    } else if (key === 'cache_images') {
      form[key] = false
    } else {
      form[key] = ''
    }
  })
  visible.value = true
}

const editMp = (record) => {
  modalTitle.value = '编辑公众号'
  currentEditId.value = record.id
  Object.assign(form, record)
  fetchCategories() // 打开编辑弹框时刷新分类列表
  visible.value = true
}

const handleOk = async () => {
  try {
    if (modalTitle.value === '添加公众号') {
      await addSubscription(form)
      Message.success('添加成功')
    } else {
      await updateSubscription(currentEditId.value, form)
      Message.success('更新成功')
    }
    visible.value = false
    fetchCategories() // 刷新分类列表
    loadData(searchText.value, selectedCategory.value)
  } catch (error) {
    console.error('操作失败:', error)
    // 错误已在 API 层处理，这里只需记录
  }
}

const handleCancel = () => {
  visible.value = false
}

const deleteMp = async (id) => {
  try {
    await deleteSubscription(id)
    Message.success('删除成功')
    loadData(searchText.value, selectedCategory.value)
  } catch (error) {
    console.error('删除失败:', error)
    // 错误已在 API 层处理，这里只需记录
  }
}

const handlePageChange = (page) => {
  pagination.current = page
  loadData(searchText.value, selectedCategory.value)
}

const handleUploadSuccess = (file) => {
  form.mp_cover = file.response.url
}

const fetchCategories = async () => {
  try {
    const res = await getCategories()
    categories.value = res.categories || []
  } catch (error) {
    console.error('获取分类列表错误:', error)
  }
}

const getAvatarUrl = (url: string) => {
  return Avatar(url)
}

// 格式化发布时间
const formatPublishTime = (timestamp: string) => {
  if (!timestamp) return '-'
  try {
    const date = new Date(timestamp)
    const now = new Date()
    const diffMs = now.getTime() - date.getTime()
    const diffDays = Math.floor(diffMs / (1000 * 60 * 60 * 24))

    if (diffDays === 0) {
      return '今天 ' + date.toLocaleTimeString('zh-CN', { hour: '2-digit', minute: '2-digit' })
    } else if (diffDays === 1) {
      return '昨天 ' + date.toLocaleTimeString('zh-CN', { hour: '2-digit', minute: '2-digit' })
    } else if (diffDays < 7) {
      return diffDays + '天前'
    } else if (diffDays < 30) {
      const weeks = Math.floor(diffDays / 7)
      return weeks + '周前'
    } else if (diffDays < 365) {
      const months = Math.floor(diffDays / 30)
      return months + '月前'
    } else {
      return date.toLocaleDateString('zh-CN')
    }
  } catch (error) {
    console.error('时间格式化错误:', error)
    return timestamp
  }
}

// 获取移动端描述信息
const getMobileDescription = (item: { remarks?: string; article_count?: number; id: string }) => {
  const parts: string[] = []
  if (item.remarks) {
    parts.push(item.remarks)
  }
  if (item.article_count !== undefined) {
    parts.push(`${item.article_count} 篇文章`)
  }
  return parts.length > 0 ? parts.join(' · ') : 'ID: ' + item.id
}

// 文章列表列定义
const articleColumns = [
  {
    title: '文章标题',
    dataIndex: 'title',
    ellipsis: true,
    tooltip: true
  },
  {
    title: '发布时间',
    dataIndex: 'publish_time',
    width: 160,
    slotName: 'publish_time'
  },
  {
    title: '更新时间',
    dataIndex: 'created_at',
    width: 160,
    slotName: 'created_at'
  },
  {
    title: '操作',
    slotName: 'actions',
    width: 80,
    align: 'center'
  }
]

// 获取文章列表
const fetchArticles = async () => {
  try {
    articlesLoading.value = true
    const params = {
      page: articlePagination.current - 1,
      pageSize: articlePagination.pageSize,
      mp_id: currentMpId.value
    }
    const res = await getArticles(params)
    articles.value = res.list || []
    articlePagination.total = res.total || 0
  } catch (error) {
    console.error('获取文章列表错误:', error)
    Message.error('获取文章列表失败')
  } finally {
    articlesLoading.value = false
  }
}

// 显示文章列表
const showArticles = (record) => {
  currentMpId.value = record.id
  currentMpName.value = record.mp_name
  articlePagination.current = 1
  articleModalVisible.value = true
  fetchArticles()
}

// 文章列表分页变化
const handleArticlePageChange = (page) => {
  articlePagination.current = page
  fetchArticles()
}

// 查看文章详情
const viewArticle = async (record) => {
  try {
    // 获取完整的文章详情
    const article = await getArticleDetail(record.id, 0)

    // 处理文章内容（图片代理等）
    currentArticle.value = {
      id: article.id,
      title: article.title,
      content: ProxyImage(article.content),
      mp_name: article.mp_name,
      publish_time: article.publish_time,
      time: formatDateTime(article.created_at),
      url: article.url,
      link: article.link
    }

    articleDetailDrawerVisible.value = true
  } catch (error) {
    console.error('获取文章详情错误:', error)
    Message.error('获取文章详情失败')
  }
}

const showBatchCategoryModal = () => {
  batchCategory.value = ''
  fetchCategories() // 打开弹框时刷新分类列表
  batchCategoryModalVisible.value = true
}

const handleBatchCategoryOk = () => {
  if (!batchCategory.value) {
    Message.warning('请选择分类')
    return
  }

  Modal.confirm({
    title: '确认批量更新',
    content: `确定要将选中的 ${selectedRowKeys.value.length} 个公众号的分类更新为「${batchCategory.value}」吗？`,
    okText: '确认',
    cancelText: '取消',
    onOk: async () => {
      try {
        const res = await batchUpdateCategory({
          mp_ids: selectedRowKeys.value,
          category: batchCategory.value
        })
        Message.success(`成功更新 ${res.updated_count} 个公众号的分类`)
        selectedRowKeys.value = []
        batchCategoryModalVisible.value = false
        fetchCategories() // 刷新分类列表
        loadData(searchText.value, selectedCategory.value)
      } catch (error) {
        console.error('批量更新分类错误:', error)
        Message.error(error.message || '批量更新失败')
      }
    }
  })
}

const handleBatchCategoryCancel = () => {
  batchCategory.value = ''
  batchCategoryModalVisible.value = false
}

// 显示刷新弹框const showRefreshModal = (record) => {  currentRefreshMpId.value = record.id  currentRefreshMpName.value = record.mp_name  refreshForm.startPage = 0  refreshForm.endPage = 1  refreshModalVisible.value = true}// 处理刷新确认const handleRefreshOk = async () => {  try {    await UpdateMps(currentRefreshMpId.value, {      start_page: refreshForm.startPage,      end_page: refreshForm.endPage    })    Message.success("刷新任务已提交，后台正在处理")    refreshModalVisible.value = false    loadData(searchText.value, selectedCategory.value)  } catch (error) {    console.error("刷新失败:", error)    Message.error(error.message || "刷新失败")  }}
onMounted(() => {
  window.addEventListener('resize', handleResize)
  loadData()
  fetchCategories()
})

onBeforeUnmount(() => {
  window.removeEventListener('resize', handleResize)
})
</script>

<style scoped>
.wechat-mp-management {
  padding: 20px;
}

.mobile-list-item {
  padding: 12px 0;
  border-bottom: 1px solid var(--color-border-2);
}

.load-more {
  width: 120px;
  margin: 16px auto 0;
  text-align: center;
}

.total-count {
  margin-top: 8px;
  font-size: 12px;
  color: var(--color-text-3);
}

.mp-intro-cell {
  display: -webkit-box;
  -webkit-box-orient: vertical;
  -webkit-line-clamp: 2;
  overflow: hidden;
  text-overflow: ellipsis;
  line-height: 1.5;
  font-size: 13px;
  color: var(--color-text-2);
  word-break: break-word;
}

.article-detail h2 {
  margin-bottom: 16px;
  font-size: 20px;
  font-weight: 600;
}

.article-content {
  line-height: 1.8;
  font-size: 14px;
}

.article-content :deep(img) {
  max-width: 100%;
  height: auto;
}
</style>