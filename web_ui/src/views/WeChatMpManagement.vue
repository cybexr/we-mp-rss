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

          <template #action="{ record }">
            <a-space>
              <a-button size="mini" @click="editMp(record)">编辑</a-button>
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
                :description="`ID: ${item.mp_id}`"
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
                  <a-tag v-if="item.category" color="blue" size="small">{{ item.category }}</a-tag>
                  <a-tag :color="item.status ? 'green' : 'red'" size="small">
                    {{ item.status ? '已启用' : '已禁用' }}
                  </a-tag>
                  <a-space :size="4">
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
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, onMounted, onBeforeUnmount } from 'vue'
import { getSubscriptions, addSubscription, updateSubscription, deleteSubscription, getCategories, batchUpdateCategory } from '@/api/subscription'
import { getToken } from '@/utils/auth'
import { Avatar } from '@/utils/constants'
import { Message, Modal } from '@arco-design/web-vue'

const headers = { Authorization: `Bearer ${getToken()}` }

const isMobile = ref(window.innerWidth < 768)
const handleResize = () => {
  isMobile.value = window.innerWidth < 768
}

const columns = [    {      title: "名称",      dataIndex: "mp_name",      slotName: "mp_name"    },    { title: "分类", slotName: "category" },    { title: "备注", dataIndex: "remarks", ellipsis: true, tooltip: true },    { title: "状态", slotName: "status" },    { title: "操作", slotName: "action" }  ]

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
    if (category) {
      params.category = category
    }
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
</style>