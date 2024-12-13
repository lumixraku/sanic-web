<script lang="ts" setup>
import { isMockDevelopment } from '@/config'
import MarkdownInstance from './plugins/markdown'
import MarkdownEcharts from './MarkdownEcharts.vue'

import {
    type TransformStreamModelTypes,
    transformStreamValue
} from './transform'
import MarkdownTable from './MarkdownTable.vue'
import { watch } from 'vue'

interface Props {
    isInit: boolean
    chartId: string
    reader: ReadableStreamDefaultReader<Uint8Array> | null
    model?: TransformStreamModelTypes
    parentScollBottomMethod: () => void //父组件滚动方法
}

const props = withDefaults(defineProps<Props>(), {
    isInit: false, //用于控制 页面渲染速度 初始化时快一点 问答时慢一点
    chartId: '', //用于区分多个图表实例
    reader: null,
    model: 'standard',
    parentScollBottomMethod: () => {}
})

// 解构 props
const { parentScollBottomMethod } = toRefs(props)

// 定义响应式变量
const displayText = ref('')
const textBuffer = ref('')

const readerLoading = ref(false)

const isAbort = ref(false)

const isCompleted = ref(false)

// 自定义事件用于 子父组件传递事件信息
const emit = defineEmits(['failed', 'completed', 'update:reader', 'chartready'])

const refWrapperContent = ref<HTMLElement>()

let typingAnimationFrame: number | null = null

//全局存储
const businessStore = useBusinessStore()

/**
 * reader 读取是否结束
 */
const readIsOver = ref(false)

const renderedMarkdown = computed(() => {
    return MarkdownInstance.render(displayText.value)
})

const renderedContent = computed(() => {
    // 在 renderedMarkdown 末尾插入光标标记
    return `${renderedMarkdown.value}`
})

const abortReader = () => {
    if (props.reader) {
        props.reader.cancel()
    }

    isAbort.value = true
    readIsOver.value = false
    emit('update:reader', null)
    initializeEnd()
    isCompleted.value = true
}

const resetStatus = () => {
    isAbort.value = false
    isCompleted.value = false
    readIsOver.value = false

    emit('update:reader', null)

    initializeEnd()
    displayText.value = ''
    textBuffer.value = ''
    readerLoading.value = false
    if (typingAnimationFrame) {
        cancelAnimationFrame(typingAnimationFrame)
        typingAnimationFrame = null
    }
}

/**
 * 检查是否有实际内容
 */
function hasActualContent(html) {
    const text = html.replace(/<[^>]*>/g, '')
    return /\S/.test(text)
}

const showCopy = computed(() => {
    if (!isCompleted.value) return false

    if (hasActualContent(displayText.value)) {
        return true
    }

    return false
})

const initialized = ref(false)

const initializeStart = () => {
    initialized.value = true
}

const initializeEnd = () => {
    initialized.value = false
}

// 定义图表类型
const currentChartType = ref('')
const readTextStream = async () => {
    if (!props.reader) return

    const textDecoder = new TextDecoder('utf-8')
    readerLoading.value = true
    while (true) {
        if (isAbort.value) {
            break
        }
        try {
            if (!props.reader) {
                readIsOver.value = true
                break
            }
            const { value, done } = await props.reader.read()
            if (!props.reader) {
                readIsOver.value = true
                break
            }
            if (done) {
                readIsOver.value = true
                break
            }

            const transformer = transformStreamValue[props.model]
            if (!transformer) {
                break
            }

            const stream = transformer.call(
                transformStreamValue,
                value,
                textDecoder
            )
            if (stream.done) {
                readIsOver.value = true

                break
            }
            //每条消息换行显示
            textBuffer.value += stream.content + '\n'

            if (typingAnimationFrame === null) {
                showText()
            }
        } catch (error) {
            console.log('渲染失败信息', error)
            readIsOver.value = true
            emit('failed', error)
            resetStatus()
            break
        } finally {
            initializeEnd()
        }
    }
}

const scrollToBottom = async () => {
    await nextTick()
    if (!refWrapperContent.value) return

    refWrapperContent.value.scrollTop = refWrapperContent.value.scrollHeight
}
const scrollToBottomByThreshold = async () => {
    if (!refWrapperContent.value) return

    const threshold = 100
    const distanceToBottom =
        refWrapperContent.value.scrollHeight -
        refWrapperContent.value.scrollTop -
        refWrapperContent.value.clientHeight
    if (distanceToBottom <= threshold) {
        scrollToBottom()
    }
}

const scrollToBottomIfAtBottom = async () => {
    scrollToBottomByThreshold()
}

/**
 * 读取 buffer 内容，逐字追加到 displayText
 */
const runReadBuffer = (readCallback = () => {}, endCallback = () => {}) => {
    if (textBuffer.value.length > 0) {
        const lengthToExtract = props.isInit ? 1000 : 1
        const nextChunk = textBuffer.value.substring(0, lengthToExtract)
        displayText.value += nextChunk
        textBuffer.value = textBuffer.value.substring(lengthToExtract)
        readCallback()
    } else {
        endCallback()
    }

    //动态渲染时实时调用父组件滚动条至最底端
    parentScollBottomMethod.value()
}

const showText = () => {
    if (isAbort.value && typingAnimationFrame) {
        cancelAnimationFrame(typingAnimationFrame)
        typingAnimationFrame = null
        readerLoading.value = false
        return
    }

    // 若 reader 还没结束，则保持打字行为
    if (!readIsOver.value) {
        runReadBuffer()
        typingAnimationFrame = requestAnimationFrame(showText)
    } else {
        // 读取剩余的 buffer
        runReadBuffer(
            () => {
                typingAnimationFrame = requestAnimationFrame(showText)
            },
            () => {
                let dataType = businessStore.writerList.dataType
                //这里只有需要显示图表数据时才显示图表
                if (dataType && dataType === 't04') {
                    currentChartType.value =
                        businessStore.writerList.data.template_code
                }

                emit('update:reader', null)
                emit('completed')
                emit('chartready')
                readerLoading.value = false
                isCompleted.value = true
                nextTick(() => {
                    readIsOver.value = false
                })
                typingAnimationFrame = null
            }
        )
    }
    scrollToBottomIfAtBottom()
}

watch(
    () => props.reader,
    () => {
        if (props.reader) {
            readTextStream()
        }
    },
    {
        immediate: true,
        deep: true
    }
)

onUnmounted(() => {
    resetStatus()
})

defineExpose({
    abortReader,
    resetStatus,
    initializeStart,
    initializeEnd
})

const showLoading = computed(() => {
    if (initialized.value) {
        return true
    }

    if (!props.reader) {
        return false
    }

    if (!readerLoading) {
        return false
    }
    if (displayText.value) {
        return false
    }

    return false
})

const refClipBoard = ref()
const handlePassClip = () => {
    if (refClipBoard.value) {
        refClipBoard.value.copyText()
    }
}

// 监控表格图表是否渲染完毕
const onTableCompletedReader = function () {
    emit('chartready')
}
// 监控表格图表是否渲染完毕
const onChartCompletedReader = function () {
    emit('chartready')
}
</script>

<template>
    <n-spin
        relative
        flex="1 ~"
        min-h-0
        w-full
        h-full
        content-class="w-full h-full flex"
        :show="showLoading"
        :rotate="false"
        class="bg-#f6f7fb"
        :style="{
            '--n-opacity-spinning': '0.3'
        }"
    >
        <transition name="fade">
            <n-float-button
                v-if="showCopy"
                position="absolute"
                :top="30"
                :right="30"
                color
                class="c-warning bg-#fff/80 hover:bg-#fff/90 transition-all-200 z-2"
                @click="handlePassClip()"
            >
                <clip-board
                    ref="refClipBoard"
                    :auto-color="false"
                    no-copy
                    :text="displayText"
                />
            </n-float-button>
        </transition>
        <template #icon>
            <div class="i-svg-spinners:3-dots-rotate"></div>
        </template>
        <!-- b="~ solid #ddd" -->
        <div
            flex="1 ~"
            min-w-0
            min-h-0
            :class="[reader ? '' : 'justify-center items-center']"
        >
            <div
                text-16
                class="w-full h-full overflow-hidden"
                :class="[!displayText && 'flex items-center justify-center']"
            >
                <n-empty v-if="!displayText" size="large" class="font-bold">
                    <!-- 
                        显示默认文本
                    <div
                        whitespace-break-spaces
                        text-center
                        v-html="emptyPlaceholder"
                    ></div> -->
                    <template #icon>
                        <n-icon>
                            <div class="i-hugeicons:ai-chat-02"></div>
                        </n-icon>
                    </template>
                </n-empty>
                <div
                    v-else
                    ref="refWrapperContent"
                    text-16
                    class="w-full h-full overflow-y-auto"
                    p-24px
                >
                    <div
                        class="markdown-wrapper"
                        v-html="renderedContent"
                    ></div>

                    <div
                        v-if="readerLoading"
                        size-24
                        style="margin-left: 10%"
                        class="i-svg-spinners:pulse-3"
                    ></div>

                    <div
                        v-if="
                            currentChartType &&
                            currentChartType != 'temp01' &&
                            isCompleted
                        "
                        whitespace-break-spaces
                        text-center
                        style="
                            align-items: center;
                            width: 80%;
                            margin-left: 10%;
                            margin-right: 10%;
                        "
                    >
                        <MarkdownEcharts
                            :chart-id="props.chartId"
                            @chartRendered="() => onChartCompletedReader()"
                        />
                    </div>

                    <div
                        v-if="
                            currentChartType &&
                            currentChartType == 'temp01' &&
                            isCompleted
                        "
                        whitespace-break-spaces
                        text-center
                        style="
                            align-items: center;
                            width: 80%;
                            margin-left: 10%;
                            margin-right: 10%;
                        "
                    >
                        <MarkdownTable
                            @tableRendered="() => onTableCompletedReader()"
                        />
                    </div>
                </div>
            </div>
        </div>
    </n-spin>
</template>

<style lang="scss">
.markdown-wrapper {
    margin-left: 10%;
    margin-right: 10%;
    background-color: #ffffff;
    // background: linear-gradient(to right, #f0effe, #d4eefc);
    padding: 30px;
    // font-family: 'PMingLiU';
    font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto,
        'Helvetica Neue', Arial, sans-serif;
    h1 {
        font-size: 2em;
    }

    h2 {
        font-size: 1.5em;
        padding-bottom: 0.3em;
        border-bottom: 1px solid #f6f7fb;
    }

    h3 {
        font-size: 1.25em;
    }

    h4 {
        font-size: 1em;
    }

    h5 {
        font-size: 0.875em;
    }

    h6 {
        font-size: 0.85em;
    }

    h1,
    h2,
    h3,
    h4,
    h5,
    h6 {
        margin: 0 auto;
        line-height: 1.25;
        margin-top: 20px; /* 添加顶部外边距，这里设置为20像素，你可以根据需要调整这个值 */
        margin-bottom: 15px;
    }

    & ul,
    ol {
        padding-left: 1.5em;
        line-height: 0.8;
    }

    & ul,
    li,
    ol {
        list-style-position: outside;
        white-space: normal;
    }

    li {
        line-height: 2;
    }

    ol ol {
        padding-left: 20px;
    }

    ul ul {
        padding-left: 20px;
    }

    hr {
        margin: 16px 0;
    }

    a {
        color: $color-default;
        font-weight: bolder;
        text-decoration: underline;
        padding: 0 3px;
    }

    p {
        line-height: 2;
        & > code {
            --at-apply: 'bg-#e5e5e5';
            --at-apply: whitespace-pre mx-4px px-6px py-3px rounded-5px;
        }

        img {
            display: inline-block;
        }
    }

    li > p {
        line-height: 2;
    }

    blockquote {
        padding: 10px;
        margin: 20px 0;
        border-left: 5px solid #ccc;
        background-color: #f9f9f9;
        color: #555;

        & > p {
            margin: 0;
        }
    }

    table {
        border-collapse: collapse; /* 合并相邻单元格的边框 */
        width: 100%;
    }
    th,
    td {
        border: 1px solid #f6f7fb; /* 将边框颜色设为红色 */
        padding: 8px;
        text-align: left;
    }
    th {
        background-color: #f2f2f2; /* 可选：给表头设置背景色 */
    }
    code {
        background-color: #f5f5f5;
        color: #333;
    }
}
</style>
