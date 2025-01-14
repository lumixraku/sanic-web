<script setup>
import { ref, onMounted } from 'vue'
import { Transformer } from 'markmap-lib'
import { Markmap } from 'markmap-view'

const transformer = new Transformer()
const initValue = `# 思维导图\n1. 标题1\n - 子标题1\n - 子标题2\n2. 标题2\n3. 标题3`
const mm = ref()
const svgRef = ref()

const update = () => {
    const { root } = transformer.transform(initValue)
    mm.value.setData(root)
    mm.value.fit()
}

onMounted(() => {
    mm.value = Markmap.create(svgRef.value)
    update()
})
const loading = ref(false)
</script>
<template>
    <LayoutCenterPanel :loading="loading">
        <template #sidebar>
            <div flex="~ col" h-full style="background-color: #f6f7fb">
                <div flex="~ justify-between items-center">
                    <NavigationNavBar />
                </div>

                <div flex="1 ~ col" min-h-0 pb-20>
                    <div class="mind">
                        <div
                            class="svg-container"
                            style="height: 100%; width: 100%"
                        >
                            <svg
                                ref="svgRef"
                                style="
                                    display: block;
                                    height: 100%;
                                    width: 100%;
                                "
                            ></svg>
                        </div>
                    </div>
                </div>
            </div>
        </template>
    </LayoutCenterPanel>
</template>

<style scoped>
html,
body,
.mind {
    margin: 0;
    padding: 0;
    height: 100%;
    overflow: hidden;
}
.mind {
    display: flex;
    justify-content: center;
    align-items: center;
}
</style>
