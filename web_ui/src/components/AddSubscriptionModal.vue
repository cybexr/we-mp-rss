<template>
  <a-modal
    :visible="visible"
    title="添加订阅"
    :on-before-ok="handleSubmit"
    :on-before-cancel="handleCancel"
    @cancel="handleModalCancel"
    @close="handleModalCancel"
  >
    <a-form
      ref="formRef"
      :model="form"
      :rules="rules"
      layout="vertical"
    >
      <a-form-item label="公众号名称" field="name">
        <a-input
          v-model="form.name"
          placeholder="请输入公众号名称"
          allow-clear
        >
          <template #prefix><icon-user /></template>
        </a-input>
      </a-form-item>
      
      <a-form-item label="公众号ID" field="accountId">
        <a-input
          v-model="form.accountId"
          placeholder="请输入公众号ID"
          allow-clear
        >
          <template #prefix><icon-idcard /></template>
        </a-input>
      </a-form-item>
      
      <a-form-item label="RSS链接" field="rssUrl">
        <a-input
          v-model="form.rssUrl"
          placeholder="请输入RSS链接"
          allow-clear
        >
          <template #prefix><icon-link /></template>
        </a-input>
      </a-form-item>
      
      <a-form-item label="分类" field="category">
        <a-select
          v-model="form.category"
          placeholder="请选择分类"
          allow-clear
        >
          <a-option value="news">新闻</a-option>
          <a-option value="tech">科技</a-option>
          <a-option value="finance">财经</a-option>
          <a-option value="entertainment">娱乐</a-option>
          <a-option value="sports">体育</a-option>
        </a-select>
      </a-form-item>
      
      <a-form-item label="描述" field="description">
        <a-textarea
          v-model="form.description"
          placeholder="请输入公众号描述"
          :auto-size="{ minRows: 3, maxRows: 5 }"
          allow-clear
        />
      </a-form-item>
    </a-form>
  </a-modal>
</template>

<script setup lang="ts">
import { ref } from 'vue'
import { FormInstance, Message } from '@arco-design/web-vue'
import { addSubscription } from '@/api/subscription'

const props = defineProps({
  visible: {
    type: Boolean,
    required: true
  }
})

const emit = defineEmits(['update:visible', 'success'])

const formRef = ref<FormInstance>()
const loading = ref(false)

const form = ref({
  name: '',
  accountId: '',
  rssUrl: '',
  category: '',
  description: ''
})

const rules = {
  name: [{ required: true, message: '请输入公众号名称' }],
  accountId: [{ required: true, message: '请输入公众号ID' }],
  rssUrl: [
    { required: true, message: '请输入RSS链接' },
    { type: 'url', message: '请输入有效的URL' }
  ],
  category: [{ required: true, message: '请选择分类' }]
}

const handleSubmit = async () => {
  const validate = await formRef.value?.validate()
  if (validate) {
    return false
  }

  try {
    loading.value = true
    await addSubscription(form.value)
    Message.success('订阅添加成功')
    emit('update:visible', false)
    emit('success')
    return true
  } catch (error) {
    Message.error('订阅添加失败')
    return false
  } finally {
    loading.value = false
  }
}

const handleCancel = () => {
  formRef.value?.resetFields()
  return true
}

const handleModalCancel = () => {
  emit('update:visible', false)
}
</script>

<style scoped>
.arco-form-item {
  margin-bottom: 16px;
}
</style>