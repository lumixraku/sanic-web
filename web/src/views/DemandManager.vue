<template>
    <LayoutCenterPanel :loading="loading">
        <n-layout style="height: 99%; border-radius: 10px; margin-bottom: 10px">
            <n-layout-header class="header">
                <div class="header-content">
                    <!-- 这里可以放置一些顶部的内容或导航 -->
                </div>
                <button class="create-project-btn" @click="showModal = true">
                    + 创建项目
                </button>
            </n-layout-header>
            <n-layout-content>
                <div class="container">
                    <div
                        class="card"
                        v-for="(item, index) in items"
                        :key="index"
                    >
                        <div class="card-header">
                            <n-icon style="margin-right: 5px" size="18">
                                <div class="i-formkit:filedoc"></div>
                            </n-icon>
                            <span class="card-title">需求</span>
                        </div>
                        <div class="card-body">
                            <p>{{ item.doc_desc }}</p>
                        </div>
                        <div class="card-footer">
                            <span class="card-info"
                                >抽取功能: {{ item.fun_num }}</span
                            >
                            <span class="card-date">{{
                                item.create_time
                            }}</span>
                            <!-- 使用 n-dropdown 组件替换原有的按钮 -->
                            <n-dropdown
                                trigger="click"
                                :options="dropdownOptions"
                                @select="(key) => handleSelect(key, index)"
                            >
                                <button class="card-button">...</button>
                            </n-dropdown>
                        </div>
                    </div>
                </div>
            </n-layout-content>
        </n-layout>

        <!-- 模态框 -->
        <n-modal
            v-model:show="showModal"
            preset="dialog"
            title="创建新项目"
            style="width: 600px"
            @close="closeModal"
        >
            <n-form :model="projectForm">
                <n-form-item label="项目名称" required>
                    <n-input
                        v-model:value="projectForm.doc_name"
                        placeholder="请输入项目名称"
                    />
                </n-form-item>
                <n-form-item label="项目描述" required>
                    <n-input
                        v-model:value="projectForm.doc_desc"
                        type="textarea"
                        placeholder="请输入项目描述"
                    />
                </n-form-item>
                <n-form-item label="项目附件" hidden>
                    <n-input v-model:value="projectForm.file_key" />
                </n-form-item>
                <n-upload
                    multiple
                    :show-file-list="true"
                    action="sanic/file/upload_file"
                    accept=".doc, .docx"
                    ref="uploadDocRef"
                    @finish="finish_upload"
                >
                    <n-button>上传附件</n-button>
                </n-upload>
            </n-form>
            <template #action>
                <n-button @click="submitProject">提交</n-button>
                <n-button @click="closeModal">取消</n-button>
            </template>
        </n-modal>
    </LayoutCenterPanel>
</template>

<script setup>
import { ref } from 'vue'
import { NLayout, NLayoutHeader, NLayoutContent } from 'naive-ui'
import * as GlobalAPI from '@/api'

const loading = ref(true)

const uploadDocRef = ref()
const finish_upload = (res) => {
    if (res.event.target.responseText) {
        let json_data = JSON.parse(res.event.target.responseText)
        let file_key = json_data['data']['object_key']
        if (json_data['code'] == 200) {
            window.$ModalMessage.success(`文件上传成功`)
            projectForm.value.file_key = file_key
            projectForm.value.doc_name = file_key.split('.')[0]
            projectForm.value.doc_desc = file_key.split('.')[0]
        } else {
            window.$ModalMessage.error(`文件上传失败`)
            return
        }
    }
}

const showModal = ref(false)
const items = ref([])

const projectForm = ref({
    doc_name: '',
    doc_desc: '',
    file_key: ''
})
const submitProject = async () => {
    const res = await GlobalAPI.insert_demand_manager(projectForm.value)
    const json = await res.json()
    if (json?.data !== undefined && json?.data) {
        window.$ModalMessage.success(`项目创建成功`)
        closeModal()
    }

    query_demand_records()
}

const closeModal = () => {
    showModal.value = false
    // 清空表单
    projectForm.value = {
        doc_name: '',
        doc_desc: '',
        file_key: ''
    }
}

const dropdownOptions = [
    {
        label: '编辑',
        key: 'edit'
    },
    {
        label: '删除',
        key: 'delete'
    }
    // 可以根据需要添加更多选项
]

const handleSelect = async (key, index) => {
    switch (key) {
        case 'edit':
            console.log(`Editing item at index ${index}`)
            // 编辑项目的逻辑
            break
        case 'delete':
            // if (confirm('确定要删除此项目吗？')) {
            GlobalAPI.delete_demand_records(items.value[index].id)
            await query_demand_records()
            // }
            break
        default:
            console.log(`Selected option not handled: ${key}`)
    }
}

const query_demand_records = async () => {
    const res = await GlobalAPI.query_demand_records(1, 999999)
    const json = await res.json()
    if (json?.data !== undefined) {
        items.value = json.data.records
        loading.value = false
    } else {
        items.value = []
    }
}

onMounted(() => {
    query_demand_records()
})
</script>

<style scoped>
.header {
    display: flex;
    justify-content: space-between;
    align-items: center;
    padding: 10px 20px; /* 调整padding以适应设计 */
    background-color: #f6f7fb; /* 根据需要调整背景颜色 */
}

.header-content {
    /* 这里可以添加任何必要的样式，比如logo或导航链接 */
}

.create-project-btn {
    background-color: #2c7be5;
    color: #fff;
    border: none;
    padding: 10px 20px;
    border-radius: 20px;
    cursor: pointer;
    font-size: 14px;
}

.container {
    display: flex;
    flex-wrap: wrap;
    gap: 20px;
    padding: 20px;
}

.card {
    width: 250px;
    margin-top: 40px;
    border-radius: 8px;
    box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
    background-color: #ffffff;
    overflow: hidden;
}

.card-header {
    display: flex;
    align-items: center;
    padding: 10px;
    background-color: #f9f9f9;
}

.card-icon {
    width: 20px;
    height: 20px;
    margin-right: 10px;
}

.card-title {
    font-weight: bold;
}

.card-body {
    padding: 10px;
}

.card-footer {
    display: flex;
    justify-content: space-between;
    padding: 10px;
    background-color: #fff;
}

.card-info,
.card-date {
    font-size: 12px;
    color: #666;
}

.card-button {
    background-color: #e0e0e0;
    border: none;
    padding: 5px 10px;
    border-radius: 4px;
    cursor: pointer;
    font-size: 12px;
}

form-item-inline {
    display: flex;
    align-items: center;
}

.form-item-inline .n-form-item__label {
    width: 120px; /* 设置标签宽度 */
    margin-right: 15px; /* 设置标签与输入框之间的间距 */
}
</style>
