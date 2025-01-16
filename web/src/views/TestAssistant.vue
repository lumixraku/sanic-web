<script setup>
import { ref, onMounted } from 'vue'
import { Transformer } from 'markmap-lib'
import { Markmap } from 'markmap-view'

const transformer = new Transformer()
const initValue = `# 大模型测试助手\n1. 上传需求文档\n2. 模型抽取需求\n3. 生成测试用例\n4. 导出测试用例`
const mm = ref()
const svgRef = ref()

const update = () => {
    const { root } = transformer.transform(initValue)
    mm.value.setData(root)
    mm.value.fit()
}

onMounted(() => {
    // 创建 Markmap 实例并传入 opts 参数
    mm.value = Markmap.create(svgRef.value, {
        autoFit: true, // 布尔值，如果为true，则自动调整视图以适应容器大小
        // color: (node) => '#8276f2', // 函数，根据节点返回颜色字符串
        duration: 1000, // 数字，动画持续时间，单位毫秒
        embedGlobalCSS: true, // 布尔值，是否嵌入全局CSS样式
        fitRatio: 0.5, // 数字，适配比例，用于调整自动缩放的程度
        initialExpandLevel: 1, // 数字，初始展开层级，决定首次加载时展开的节点深度
        lineWidth: (node) => 1, // 函数，根据节点返回线条宽度
        maxInitialScale: 2, // 数字，最大初始缩放比例
        maxWidth: 800, // 数字，思维导图的最大宽度
        nodeMinHeight: 20, // 数字，节点最小高度
        paddingX: 20, // 数字，水平内边距
        pan: true, // 布尔值，允许平移（拖拽）视图
        scrollForPan: true, // 布尔值，当视图到达边界时是否通过滚动来继续平移
        spacingHorizontal: 30, // 数字，水平间距
        spacingVertical: 20, // 数字，垂直间距
        // style: (id) => `#custom-style`, // 函数，基于ID返回自定义样式
        toggleRecursively: false, // 布尔值，是否递归地切换子节点的可见性
        zoom: true // 布尔值，允许缩放视图
    })

    update()
    // mm.value.handleClick = (e, d) => {
    //     console.log(e, d)
    // }
})

const loading = ref(false)
</script>
<template>
    <LayoutCenterPanel :loading="loading">
        <div
            style="
                display: flex;
                justify-content: center; /* 水平居中 */
                align-items: center; /* 垂直居中 */
                height: 100%; /* 确保父元素有高度 */
                width: 100%; /* 确保父元素有宽度 */
            "
        >
            <svg
                ref="svgRef"
                style="
                    background-color: #f6f7fb;
                    height: 98%;
                    width: 99%;
                    border-radius: 10px;
                "
            ></svg>
        </div>
    </LayoutCenterPanel>
</template>

<style scoped></style>
