<script lang="tsx" setup>
import { isMockDevelopment } from '@/config'
import { type InputInst } from 'naive-ui'
import { useRouter } from 'vue-router'
import { UAParser } from 'ua-parser-js'
import TableModal from './TableModal.vue'
import DefaultPage from './DefaultPage.vue'
const route = useRoute()
const router = useRouter()
const message = useMessage()

// 显示默认页面
const showDefaultPage = ref(true)

//全局存储
const businessStore = useBusinessStore()

//是否是刚登录到系统 批量渲染对话记录
const isInit = ref(false)

// 使用 onMounted 生命周期钩子加载历史对话
onMounted(() => {
    fetchConversationHistory(
        isInit,
        conversationItems,
        tableData,
        currentRenderIndex
    )
})

//管理对话
const isModalOpen = ref(false)
function openModal() {
    isModalOpen.value = true
}
//模态框关闭
function handleModalClose(value) {
    isModalOpen.value = value
    //重新加载对话记录
    fetchConversationHistory(
        isInit,
        conversationItems,
        tableData,
        currentRenderIndex
    )
}

//新建对话
function newChat() {
    showDefaultPage.value = true
    isInit.value = false
    conversationItems.value = []
}

/**
 * 默认大模型
 */
const defaultLLMTypeName = 'qwen2'
const currentChatId = computed(() => {
    return route.params.chatId
})

//主页面加载提示
const loading = ref(true)
setTimeout(() => {
    loading.value = false
})

//对话等待提示词图标
const stylizingLoading = ref(false)

//输入字符串
const inputTextString = ref('')
const refInputTextString = ref<InputInst | null>()

//输出字符串 Reader 流（风格化的）
const outputTextReader = ref<ReadableStreamDefaultReader | null>()

//markdown对象
const refReaderMarkdownPreview = ref<any>()

//主内容区域
const messagesContainer = ref<HTMLElement | null>(null)

//读取失败
const onFailedReader = (index: number) => {
    if (conversationItems.value[index]) {
        conversationItems.value[index].reader = null
        stylizingLoading.value = false
        if (refReaderMarkdownPreview.value) {
            refReaderMarkdownPreview.value.initializeEnd()
        }
        window.$ModalMessage.error('请求失败，请重试')
        setTimeout(() => {
            if (refInputTextString.value) {
                refInputTextString.value.focus()
            }
        })
    }
}

//读取完成
const onCompletedReader = (index: number) => {
    if (conversationItems.value[index]) {
        stylizingLoading.value = false
        setTimeout(() => {
            if (refInputTextString.value) {
                refInputTextString.value.focus()
            }
        })
    }
    // scrollToBottom()
}

//图表子组件渲染完毕
const currentRenderIndex = ref(0)
const onChartReady = (index) => {
    if (index < conversationItems.value.length) {
        currentRenderIndex.value = index
        stylizingLoading.value = false
    }
}

// 侧边栏对话历史
interface TableItem {
    index: number
    key: string
}
const tableData = ref<TableItem[]>([])

//保存对话历史记录
const conversationItems = ref<
    Array<{
        role: 'user' | 'assistant'
        reader: ReadableStreamDefaultReader | null
    }>
>([])

// 这里子组件 chart渲染慢需要子组件渲染完毕后通知父组件
const visibleConversationItems = computed(() => {
    return conversationItems.value.slice(0, currentRenderIndex.value + 1)
})

//提交对话
const handleCreateStylized = async (send_text = '') => {
    // isInit.value = false
    // 若正在加载，则点击后恢复初始状态
    if (stylizingLoading.value) {
        onCompletedReader(conversationItems.value.length - 1)
        return
    }

    //send_text 为空代表数据问答
    if (send_text == '') {
        if (refInputTextString.value && !inputTextString.value.trim()) {
            inputTextString.value = ''
            refInputTextString.value.focus()
            return
        }
    }

    // 新建对话 时输入新问题 清空历史数据
    if (showDefaultPage.value) {
        conversationItems.value = []
        showDefaultPage.value = false
        isInit.value = false
    }

    //加入对话历史用于左边表格渲染
    tableData.value.push({
        index: tableData.value.length,
        key: inputTextString.value
    })

    //调用大模型后台服务接口
    stylizingLoading.value = true
    const textContent = inputTextString.value
        ? inputTextString.value
        : send_text
    inputTextString.value = ''
    const { error, reader, needLogin } =
        await businessStore.createAssistantWriterStylized(currentChatId.value, {
            text: textContent,
            writer_oid: currentChatId.value
        })

    if (needLogin) {
        message.error('登录已失效，请重新登录')

        //跳转至登录页面
        setTimeout(() => {
            router.push('/login')
        }, 2000)
    }

    if (error) {
        stylizingLoading.value = false
        onCompletedReader(conversationItems.value.length - 1)
        return
    }

    if (reader) {
        outputTextReader.value = reader
        // 添加助手的回答
        conversationItems.value.push({
            role: 'assistant',
            reader: reader
        })
        // 更新 currentRenderIndex 以包含新添加的项
        currentRenderIndex.value = conversationItems.value.length - 1
    }

    // 滚动到底部
    scrollToBottom()
}

// 滚动到底部
const scrollToBottom = () => {
    nextTick(() => {
        if (messagesContainer.value) {
            messagesContainer.value.scrollTop =
                messagesContainer.value.scrollHeight
        }
    })
}

const keys = useMagicKeys()
const enterCommand = keys['Enter']
const enterCtrl = keys['Enter']

const activeElement = useActiveElement()
const notUsingInput = computed(
    () => activeElement.value?.tagName !== 'TEXTAREA'
)

const parser = new UAParser()
const isMacos = parser.getOS().name.includes('Mac')

const placeholder = computed(() => {
    if (stylizingLoading.value) {
        return `输入任意问题...`
    }
    return `输入任意问题, 按 ${
        isMacos ? 'Command' : 'Ctrl'
    } + Enter 键快捷开始...`
})

const generateRandomSuffix = function () {
    return Math.floor(Math.random() * 10000) // 生成0到9999之间的随机整数
}

watch(
    () => enterCommand.value,
    () => {
        if (!isMacos || notUsingInput.value) return

        if (stylizingLoading.value) return

        if (!enterCommand.value) {
            handleCreateStylized()
        }
    },
    {
        deep: true
    }
)

watch(
    () => enterCtrl.value,
    () => {
        if (isMacos || notUsingInput.value) return

        if (stylizingLoading.value) return

        if (!enterCtrl.value) {
            handleCreateStylized()
        }
    },
    {
        deep: true
    }
)

const handleResetState = () => {
    if (isMockDevelopment) {
        inputTextString.value = ''
    } else {
        inputTextString.value = ''
    }

    stylizingLoading.value = false
    nextTick(() => {
        refInputTextString.value?.focus()
    })
    refReaderMarkdownPreview.value?.abortReader()
    refReaderMarkdownPreview.value?.resetStatus()
}
handleResetState()

//文件上传
let file_name = ref('')
const finish_upload = (res) => {
    file_name.value = res.file.name
    if (res.event.target.responseText) {
        let json_data = JSON.parse(res.event.target.responseText)
        let file_url = json_data['data']['object_key']
        if (json_data['code'] == 200) {
            //  businessStore.update_qa_type('FILEDATA_QA')
            businessStore.update_file_url(file_url)
            window.$ModalMessage.success(`文件上传成功`)
        } else {
            window.$ModalMessage.error(`文件上传失败`)
        }
        handleCreateStylized(file_name.value + ' 总结归纳文档的关键信息')
    }
}

// 下面方法用于左侧对话列表点击 右侧内容滚动
// 用于存储每个 MarkdownPreview 容器的引用
const markdownPreviews = ref<Array<HTMLElement | null>>([]) // 初始化为空数组

// 表格行点击事件
const rowProps = (row: any) => {
    return {
        onClick: () => {
            scrollToItem(row.index)
        }
    }
}

// 设置 markdownPreviews 数组中的元素
const setMarkdownPreview = (index: number, el: any) => {
    if (el && el instanceof HTMLElement) {
        // 确保 markdownPreviews 数组的长度与 visibleConversationItems 的长度一致
        if (index >= markdownPreviews.value.length) {
            markdownPreviews.value.push(null)
        }
        markdownPreviews.value[index] = el
    } else if (el && el.value && el.value instanceof HTMLElement) {
        // 处理代理对象的情况
        if (index >= markdownPreviews.value.length) {
            markdownPreviews.value.push(null)
        }
        markdownPreviews.value[index] = el.value
    }
}

// 滚动到指定位置的方法
const scrollToItem = (index: number) => {
    //判断默认页面是否显示或对话历史是否初始化
    if (
        (!showDefaultPage.value && !isInit.value) ||
        conversationItems.value.length === 0
    ) {
        fetchConversationHistory(
            isInit,
            conversationItems,
            tableData,
            currentRenderIndex
        )
        console.log(isInit.value)
    }
    //关闭默认页面
    showDefaultPage.value = false
    if (markdownPreviews.value[index]) {
        markdownPreviews.value[index].scrollIntoView({ behavior: 'smooth' })
    }
}
</script>
<template>
    <LayoutCenterPanel :loading="loading">
        <template #sidebar-header>
            <n-button
                type="primary"
                icon-placement="left"
                color="#5e58e7"
                @click="newChat"
                strong
                style="
                    width: 160px;
                    height: 38px;
                    margin: 15px;
                    align-self: center;
                    text-align: center;
                    font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI',
                        Roboto, 'Helvetica Neue', Arial, sans-serif;
                    font-weight: bold;
                    font-size: 14px;
                "
            >
                <template #icon>
                    <n-icon style="margin-right: 5px">
                        <div class="i-hugeicons:add-01"></div>
                    </n-icon>
                </template>
                新建对话
            </n-button>
        </template>

        <template #sidebar>
            <n-data-table
                class="custom-table"
                style="
                    --n-td-color-hover: #d5dcff;
                    font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI',
                        Roboto, 'Helvetica Neue', Arial, sans-serif;
                "
                size="small"
                :bordered="false"
                :bottom-bordered="false"
                :columns="[
                    { key: 'key', align: 'left', ellipsis: { tooltip: false } }
                ]"
                :data="tableData"
                :row-props="rowProps"
            >
                <template #empty>
                    <div></div>
                </template>
            </n-data-table>
        </template>

        <template #sidebar-action>
            <n-divider style="width: 180px" />
            <n-button
                quaternary
                icon-placement="left"
                type="primary"
                strong
                @click="openModal"
                style="
                    width: 150px;
                    height: 38px;
                    align-self: center;
                    text-align: center;
                    font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI',
                        Roboto, 'Helvetica Neue', Arial, sans-serif;
                    font-size: 14px;
                "
            >
                <template #icon>
                    <n-icon>
                        <div class="i-hugeicons:voice-id"></div>
                    </n-icon>
                </template>
                管理对话
            </n-button>

            <TableModal :show="isModalOpen" @update:show="handleModalClose" />
        </template>
        <!-- 内容区域 -->
        <div flex="~ col" h-full style="background-color: #f6f7fb">
            <div flex="~ justify-between items-center">
                <NavigationNavBar />
            </div>

            <!--这里循环渲染即可实现多轮对话-->
            <div
                flex="1 ~ col"
                min-h-0
                pb-20
                class="scrollable-container"
                ref="messagesContainer"
            >
                <div v-if="showDefaultPage">
                    <DefaultPage />
                </div>

                <div
                    v-if="!showDefaultPage"
                    v-for="(item, index) in visibleConversationItems"
                    :key="index"
                    class="mb-4"
                    :ref="(el) => setMarkdownPreview(index, el)"
                >
                    <MarkdownPreview
                        :reader="item.reader"
                        :model="defaultLLMTypeName"
                        :isInit="isInit"
                        :chart-id="`${index}devID${generateRandomSuffix()}`"
                        :parentScollBottomMethod="scrollToBottom"
                        @failed="() => onFailedReader(index)"
                        @completed="() => onCompletedReader(index)"
                        @chartready="() => onChartReady(index + 1)"
                    />
                </div>
            </div>

            <div
                style="display: flex; align-items: center"
                flex-basis="10%"
                p="14px"
                py="0"
            >
                <div>
                    <n-upload
                        type="button"
                        :show-file-list="false"
                        action="sanic/file/upload_file"
                        accept=".xlsx,.xls,.csv"
                        class="mr-2"
                        v-on:finish="finish_upload"
                    >
                        <n-icon size="35"
                            ><svg
                                t="1729566080604"
                                class="icon"
                                viewBox="0 0 1024 1024"
                                version="1.1"
                                xmlns="http://www.w3.org/2000/svg"
                                p-id="38910"
                                width="64"
                                height="64"
                            >
                                <path
                                    d="M856.448 606.72v191.744a31.552 31.552 0 0 1-31.488 31.488H194.624a31.552 31.552 0 0 1-31.488-31.488V606.72a31.488 31.488 0 1 1 62.976 0v160.256h567.36V606.72a31.488 31.488 0 1 1 62.976 0zM359.872 381.248c-8.192 0-10.56-5.184-5.376-11.392L500.48 193.152a11.776 11.776 0 0 1 18.752 0l145.856 176.704c5.184 6.272 2.752 11.392-5.376 11.392H359.872z"
                                    fill="#838384"
                                    p-id="38911"
                                ></path>
                                <path
                                    d="M540.288 637.248a30.464 30.464 0 1 1-61.056 0V342.656a30.464 30.464 0 1 1 61.056 0v294.592z"
                                    fill="#838384"
                                    p-id="38912"
                                ></path>
                            </svg>
                        </n-icon>
                    </n-upload>
                </div>
                <div
                    style="
                        position: relative;
                        flex: 1;
                        width: 100%;
                        padding: 1em;
                    "
                >
                    <n-space vertical>
                        <n-input
                            ref="refInputTextString"
                            v-model:value="inputTextString"
                            type="textarea"
                            autofocus
                            h-full
                            class="textarea-resize-none text-15"
                            :style="{
                                '--n-border-radius': '100px',
                                '--n-padding-left': '20px',
                                '--n-padding-right': '20px',
                                '--n-padding-vertical': '15px'
                            }"
                            :placeholder="placeholder"
                            :autosize="{
                                minRows: 1,
                                maxRows: 5
                            }"
                        />
                        <n-float-button
                            position="absolute"
                            :right="25"
                            top="45%"
                            :type="stylizingLoading ? 'primary' : 'default'"
                            color
                            :class="[
                                stylizingLoading && 'opacity-90',
                                'text-20'
                            ]"
                            style="transform: translateY(-50%)"
                            @click.stop="handleCreateStylized()"
                        >
                            <div
                                v-if="stylizingLoading"
                                class="i-svg-spinners:pulse-2 c-#fff"
                            ></div>
                            <div
                                v-else
                                class="flex items-center justify-center c-#303133/60 i-mingcute:send-fill"
                            ></div>
                        </n-float-button>
                    </n-space>
                </div>
            </div>
        </div>
    </LayoutCenterPanel>
</template>

<style lang="scss" scoped>
.scrollable-container {
    overflow-y: auto; // 添加纵向滚动条
    max-height: calc(
        100vh - 120px
    ); // 设置最大高度，确保输入框和导航栏有足够的空间
    padding-bottom: 20px; // 底部内边距，防止内容被遮挡
    background-color: #f6f7fb;
}
/* 滚动条整体部分 */
::-webkit-scrollbar {
    width: 4px; /* 竖向滚动条宽度 */
    height: 4px; /* 横向滚动条高度 */
}

/* 滚动条的轨道 */
::-webkit-scrollbar-track {
    background: #fff; /* 轨道背景色 */
}

/* 滚动条的滑块 */
::-webkit-scrollbar-thumb {
    background: #cac9f9; /* 滑块颜色 */
    border-radius: 10px; /* 滑块圆角 */
}

/* 滚动条的滑块在悬停状态下的样式 */
::-webkit-scrollbar-thumb:hover {
    background: #cac9f9; /* 悬停时滑块颜色 */
}

:deep(.custom-table .n-data-table-thead) {
    display: none;
}
.default-page {
    display: flex;
    justify-content: center;
    align-items: center;
    height: 100vh; /* 使容器高度占满整个视口 */
    background-color: #f0f2f5; /* 可选：设置背景颜色 */
}
</style>
