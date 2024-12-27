<template>
    <div class="button-container">
        <!-- 使用 v-for 指令循环渲染 n-button -->
        <n-button
            v-for="(text, index) in buttonLabels"
            :key="index"
            @click="handleClick(index)"
            class="block-button"
        >
            {{ text }}
        </n-button>
    </div>
</template>

<script lang="ts" setup>
import { computed, defineProps, withDefaults } from 'vue'
import { NButton } from 'naive-ui'

// 定义 props 接口以获取类型检查
interface Props {
    labels?: string[]
}

// 使用 withDefaults 提供默认值
const props = withDefaults(defineProps<Props>(), {
    labels: () => []
})

// 定义默认按钮文案
const defaultLabels = []

// 计算属性用于决定实际使用的按钮文案
const buttonLabels = computed(() =>
    props.labels.length > 0 ? props.labels : defaultLabels
)

// 点击事件处理函数
const handleClick = (index: number) => {
    console.log(`Button ${index} clicked. Label: ${buttonLabels.value[index]}`)
}
</script>

<style scoped>
/* 添加一些样式以区分按钮 */
.button-container {
    /* 如果需要更复杂的布局，可以在这里添加更多样式 */
}

.block-button {
    display: block; /* 使每个按钮独占一行 */
    margin: 5px 0; /* 调整上下间距 */
    background-color: #ffffff;
    border-radius: 10px;
    height: 40px;
    color: #666;
    fontsize: 14px;
}
</style>
