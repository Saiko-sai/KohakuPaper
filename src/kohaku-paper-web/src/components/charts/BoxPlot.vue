<script setup>
import Plotly from 'plotly.js-dist-min'

const props = defineProps({
  /** @type {Array<{y: number[], name: string, color?: string}>} */
  series: { type: Array, required: true },
  /** @type {string} */
  title: { type: String, default: '' },
  /** @type {string} */
  yLabel: { type: String, default: 'Value' },
})

const chartRef = ref(null)

const colors = ['#409eff', '#67c23a', '#e6a23c', '#f56c6c', '#909399']

const plotData = computed(() => {
  return props.series.map((s, i) => ({
    y: s.y,
    type: 'box',
    name: s.name,
    marker: {
      color: s.color || colors[i % colors.length],
    },
    boxpoints: 'outliers',
  }))
})

const layout = computed(() => ({
  title: props.title,
  yaxis: {
    title: props.yLabel,
    gridcolor: '#e4e7ed',
  },
  margin: { t: 50, r: 30, b: 60, l: 60 },
  paper_bgcolor: 'transparent',
  plot_bgcolor: 'transparent',
  font: { family: 'inherit' },
}))

const config = {
  responsive: true,
  displayModeBar: true,
}

function renderChart() {
  if (!chartRef.value || props.series.length === 0) return
  Plotly.react(chartRef.value, plotData.value, layout.value, config)
}

watch(() => props.series, renderChart, { deep: true })

onMounted(() => {
  renderChart()
})

onUnmounted(() => {
  if (chartRef.value) {
    Plotly.purge(chartRef.value)
  }
})
</script>

<template>
  <div ref="chartRef" class="box-plot"></div>
</template>

<style scoped>
.box-plot {
  width: 100%;
  min-height: 400px;
}
</style>
