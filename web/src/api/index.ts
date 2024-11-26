import { mockEventStreamText } from '@/data'
import { currentHost } from '@/utils/location'
import request from '@/utils/request'

/**
 * Event Stream 调用大模型接口 Ollama3 (Fetch 调用)
 */
export async function createOllama3Stylized(text, qa_type) {
    const userStore = useUserStore()
    const token = userStore.getUserToken()
    const businessStore = useBusinessStore()
    const url = new URL(`${location.origin}/sanic/dify/get_answer`)
    const params = {}
    Object.keys(params).forEach((key) => {
        url.searchParams.append(key, params[key])
    })

    //文件问答传文件url
    if (text.includes('总结归纳文档的关键信息')) {
        text = `${businessStore.$state.file_url}|总结归纳文档的关键信息`
    }

    const req = new Request(url, {
        mode: 'cors',
        method: 'post',
        headers: {
            'Content-Type': 'application/json',
            Authorization: `Bearer ${token}`
        },
        body: JSON.stringify({
            query: text,
            qa_type
        })
    })
    return fetch(req)
}

/**
 * 用户登录
 * @param username
 * @param password
 * @returns
 */
export async function login(username, password) {
    const url = new URL(`${location.origin}/sanic/user/login`)
    const req = new Request(url, {
        mode: 'cors',
        method: 'post',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify({
            username,
            password
        })
    })
    return fetch(req)
}

/**
 * 查询用户对话历史
 * @param page
 * @param limit
 * @returns
 */
export async function query_user_qa_record(page, limit) {
    const userStore = useUserStore()
    const token = userStore.getUserToken()
    const url = new URL(`${location.origin}/sanic/user/query_user_record`)
    const req = new Request(url, {
        mode: 'cors',
        method: 'post',
        headers: {
            'Content-Type': 'application/json',
            Authorization: `Bearer ${token}` // 添加 token 到头部
        },
        body: JSON.stringify({
            page,
            limit
        })
    })
    return fetch(req)
}

/**
 * 删除对话历史记录
 * @param page
 * @param limit
 * @returns
 */
export async function delete_user_record(ids) {
    const userStore = useUserStore()
    const token = userStore.getUserToken()
    const url = new URL(`${location.origin}/sanic/user/delete_user_record`)
    const req = new Request(url, {
        mode: 'cors',
        method: 'post',
        headers: {
            'Content-Type': 'application/json',
            Authorization: `Bearer ${token}` // 添加 token 到头部
        },
        body: JSON.stringify({
            record_ids: ids
        })
    })
    return fetch(req)
}
