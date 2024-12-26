import * as TransformUtils from '@/components/MarkdownPreview/transform'
import * as GlobalAPI from '@/api'

const businessStore = useBusinessStore()
const userStore = useUserStore()
const router = useRouter()

type StreamData = {
    dataType: string
    content?: string
    data?: any
}

// 历史对话记录数据渲染转换逻辑
const processSingleResponse = (res) => {
    if (res.body) {
        const reader = res.body
            .pipeThrough(new TextDecoderStream())
            .pipeThrough(TransformUtils.splitStream('\n'))
            .pipeThrough(
                new TransformStream<string, string>({
                    transform: (
                        chunk: string,
                        controller: TransformStreamDefaultController
                    ) => {
                        try {
                            const jsonChunk = JSON.parse(chunk)
                            switch (jsonChunk.dataType) {
                                case 't11':
                                    controller.enqueue(
                                        JSON.stringify(jsonChunk)
                                    )
                                    break
                                case 't02':
                                    if (jsonChunk.data) {
                                        controller.enqueue(
                                            JSON.stringify(jsonChunk.data)
                                        )
                                    }
                                    break
                                case 't04':
                                    businessStore.update_writerList(
                                        JSON.parse(jsonChunk.data)
                                    )
                                    break
                                default:
                                    break
                            }
                        } catch (e) {
                            console.log('Error processing chunk:', e)
                        }
                    },
                    flush: (controller: TransformStreamDefaultController) => {
                        controller.terminate()
                    }
                })
            )
            .getReader()

        return {
            error: 0,
            reader
        }
    } else {
        return {
            error: 1,
            reader: null
        }
    }
}

interface TableItem {
    index: number
    key: string
}

// 请求接口查询对话历史记录
export const fetchConversationHistory = async function fetchConversationHistory(
    isInit: Ref<boolean>,
    conversationItems: Ref<
        Array<{
            chat_id: string
            qa_type: string
            question: string
            role: 'user' | 'assistant'
            reader: ReadableStreamDefaultReader | null
        }>
    >,
    tableData: Ref<TableItem[]>,
    currentRenderIndex: Ref<number>
) {
    try {
        //初始化对话历史记录
        isInit.value = true

        // 清空现有的 conversationItems
        conversationItems.value = []

        const res = await GlobalAPI.query_user_qa_record(1, 999999)
        if (res.status == 401) {
            userStore.logout()
            setTimeout(() => {
                router.push('/login')
            }, 500)
        } else if (res.ok) {
            const data = await res.json()
            if (data && Array.isArray(data.data?.records)) {
                const records = data.data.records

                // 初始化左右对话侧列表数据
                tableData.value = records.map((chat: any, index: number) => ({
                    index,
                    key: chat.question.trim()
                }))

                const itemsToAdd: any[] = []
                for (const record of records) {
                    //用户问题
                    let question_str = ''
                    //问答类型
                    let qa_type_str = ''
                    //对话id
                    let chat_id_str = ''
                    const streamDataArray: StreamData[] = []

                    ;[
                        'question',
                        'to2_answer',
                        'to4_answer',
                        'qa_type',
                        'chat_id'
                    ].forEach((key: string) => {
                        if (record.hasOwnProperty(key)) {
                            switch (key) {
                                case 'qa_type':
                                    qa_type_str = record[key]
                                    break
                                case 'chat_id':
                                    chat_id_str = record[key]
                                    break
                                case 'question':
                                    question_str = record[key]
                                    streamDataArray.push({
                                        dataType: 't11',
                                        content: `问题:${record[key]}`
                                    })
                                    break
                                case 'to2_answer':
                                    try {
                                        streamDataArray.push({
                                            dataType: 't02',
                                            data: {
                                                content: JSON.parse(record[key])
                                                    .data.content
                                            }
                                        })
                                    } catch (e) {
                                        console.log(e)
                                    }
                                    break
                                case 'to4_answer':
                                    if (
                                        record[key] !== null &&
                                        record[key] !== undefined
                                    ) {
                                        streamDataArray.push({
                                            dataType: 't04',
                                            data: record[key]
                                        })
                                    }
                                    break
                            }
                        }
                    })

                    if (streamDataArray.length > 0) {
                        const stream = createStreamFromValue(streamDataArray) // 创建新的流
                        const { error, reader } = processSingleResponse({
                            status: 200, // 假设状态码总是 200
                            body: stream
                        })

                        if (error === 0 && reader) {
                            itemsToAdd.push({
                                chat_id: chat_id_str,
                                qa_type: qa_type_str,
                                question: question_str,
                                role: 'assistant', // 根据实际情况设置role
                                reader
                            })
                        }
                    }
                }

                conversationItems.value = itemsToAdd
                // 这里删除对话后需要重置当前渲染索引
                currentRenderIndex.value = 0
            }
        } else {
            console.log('Request failed with status:', res.status)
        }
    } catch (error) {
        console.log('An error occurred while querying QA records:', error)
    }
}

function createStreamFromValue(valueArray: StreamData[]) {
    const encoder = new TextEncoder()
    return new ReadableStream({
        start(controller: ReadableStreamDefaultController) {
            valueArray.forEach((value) => {
                controller.enqueue(encoder.encode(`${JSON.stringify(value)}\n`))
            })
            controller.close()
        }
    })
}
