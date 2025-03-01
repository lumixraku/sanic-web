<template>
    <LayoutCenterPanel :loading="loading">
        <n-layout class="main-layout">
            <n-layout-header class="header">
                <div class="size-26 i-hugeicons:ai-chat-02" />
                <div class="header-content">测试用例生成工具</div>
            </n-layout-header>
            <n-layout-content>
                <n-layout class="sub-layout">
                    <n-layout-header class="sub-header">
                        <n-button
                            quaternary
                            icon-placement="left"
                            type="primary"
                            strong
                            @click="call_back"
                            style="
                                width: 35px;
                                height: 38px;
                                margin-top: 8px;
                                margin-left: 10px;
                                align-self: center;
                            "
                        >
                            <template #icon>
                                <n-icon size="24">
                                    <svg
                                        t="1740725444100"
                                        class="icon"
                                        viewBox="0 0 1024 1024"
                                        version="1.1"
                                        xmlns="http://www.w3.org/2000/svg"
                                        p-id="16679"
                                        width="200"
                                        height="200"
                                    >
                                        <path
                                            d="M671.3 480.1H301.7L473.8 308c12.4-12.4 12.4-32.8 0-45.3-12.4-12.4-32.8-12.4-45.3 0L201.9 489.5c-5 5-8 11.2-9 17.7v0.1c-0.1 0.4-0.1 0.9-0.2 1.3v0.3c0 0.4-0.1 0.8-0.1 1.2v4c0 0.4 0.1 0.8 0.1 1.2v0.3c0 0.4 0.1 0.9 0.2 1.3v0.1c1 6.5 4 12.7 9 17.7l226.7 226.7c12.4 12.4 32.8 12.4 45.3 0 12.4-12.4 12.4-32.8 0-45.3l-172.2-172h369.6c17.6 0 32-14.4 32-32s-14.4-32-32-32z"
                                            p-id="16680"
                                            fill="#2c2c2c"
                                        ></path>
                                    </svg>
                                </n-icon>
                            </template>
                        </n-button>
                    </n-layout-header>
                    <n-layout-content>
                        <n-split
                            direction="horizontal"
                            style="height: 100%"
                            size="300px"
                            min="300px"
                            max="500px"
                        >
                            <template #1>
                                <n-space vertical :size="12">
                                    <n-space
                                        style="justify-content: space-between"
                                    >
                                        <n-button
                                            quaternary
                                            icon-placement="right"
                                            strong
                                            style="
                                                width: 30px;
                                                height: 38px;
                                                margin-top: 8px;
                                                align-self: center;
                                            "
                                        >
                                            功能点
                                        </n-button>
                                        <n-button
                                            quaternary
                                            icon-placement="right"
                                            strong
                                            style="
                                                width: 35px;
                                                height: 38px;
                                                margin-top: 8px;
                                                align-self: center;
                                            "
                                            >功能点
                                        </n-button>
                                    </n-space>
                                    <n-data-table
                                        class="custom-table"
                                        style="
                                            font-size: 14px;
                                            height: 500px;
                                            --n-td-color-hover: #d5dcff;
                                            font-family: -apple-system,
                                                BlinkMacSystemFont, 'Segoe UI',
                                                Roboto, 'Helvetica Neue', Arial,
                                                sans-serif;
                                        "
                                        size="small"
                                        :bordered="false"
                                        :bottom-bordered="false"
                                        :single-line="false"
                                        :columns="[
                                            { title: 'ID', key: 'id' },
                                            {
                                                title: '描述',
                                                key: 'description'
                                            }
                                        ]"
                                        :data="tableData"
                                        ref="tableRef"
                                        :row-props="rowProps"
                                    ></n-data-table>
                                </n-space>
                            </template>
                            <template #2>Content Area 2</template>
                        </n-split>
                    </n-layout-content>
                </n-layout>
            </n-layout-content>
        </n-layout>
    </LayoutCenterPanel>
</template>
<script setup>
import { ref } from 'vue'
const loading = ref(false)

const router = useRouter()
function call_back() {
    router.push('/testAssitant')
}

const tableData = ref([
    { id: 'US01', description: '创建新帐户' },
    { id: 'US02', description: '重命名帐户' },
    { id: 'US03', description: '更新个人信息' },
    { id: 'US04', description: '设置支付方式' }
])
</script>

<style scoped>
.header {
    display: flex;
    height: 52px;
    justify-content: center;
    align-items: center;
    padding: 10px 20px; /* 调整padding以适应设计 */
    background-color: #f6f7fb; /* 根据需要调整背景颜色 */
}
.header-content {
    font-size: 18px; /* 根据需要调整字体大小 */
    font-weight: bold; /* 根据需要调整字体粗细 */
    color: #26244c; /* 根据需要调整字体颜色 */
    text-align: center;
}
.main-layout,
.sub-layout {
    height: 99%;
    border-radius: 10px;
    margin-bottom: 10px;
    margin-right: 2px;
}
.sub-header {
    margin-top: 5px;
    margin-bottom: 5px;
    height: 52px;
    background: #f6f7fb;
}
:deep(.custom-table .n-data-table-thead) {
    display: none;
}
</style>
