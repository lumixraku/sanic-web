<template>
    <n-layout>
        <n-layout-header class="header">
            <div class="header-content">
                <!-- 这里可以放置一些顶部的内容或导航 -->
            </div>
            <button class="create-project-btn" @click="createProject">
                + 创建项目
            </button>
        </n-layout-header>
        <n-layout-content>
            <div class="container">
                <div class="card" v-for="(item, index) in items" :key="index">
                    <div class="card-header">
                        <img :src="item.icon" alt="" class="card-icon" />
                        <span class="card-title">{{ item.title }}</span>
                    </div>
                    <div class="card-body">
                        <p>{{ item.description }}</p>
                    </div>
                    <div class="card-footer">
                        <span class="card-info"
                            >用户需求: {{ item.userDemand }}</span
                        >
                        <span class="card-date">{{ item.date }}</span>
                        <button class="card-button" @click="showMore(item)">
                            ...
                        </button>
                    </div>
                </div>
            </div>
        </n-layout-content>
    </n-layout>
</template>

<script setup>
import { ref } from 'vue'
import { NLayout, NLayoutHeader, NLayoutContent } from 'naive-ui'

const items = ref([
    {
        icon: 'https://example.com/icon.png',
        title: '需求1',
        description: '这是第一个需求的描述。',
        userDemand: '5',
        date: '2025-01-21 10:17'
    },
    {
        icon: 'https://example.com/icon2.png',
        title: '需求2',
        description: '这是第二个需求的描述。',
        userDemand: '7',
        date: '2025-01-21 10:25'
    }
    // 继续添加更多项目...
])

const showMore = (item) => {
    console.log(`Showing more details for ${item.title}`)
}

const createProject = () => {
    console.log('Creating a new project')
}
</script>

<style scoped>
.header {
    display: flex;
    justify-content: space-between;
    align-items: center;
    padding: 10px 20px; /* 调整padding以适应设计 */
    background-color: #f8f8f8; /* 根据需要调整背景颜色 */
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
</style>
