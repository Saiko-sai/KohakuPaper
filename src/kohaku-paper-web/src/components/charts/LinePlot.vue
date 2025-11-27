<script setup>
import Plotly from "plotly.js-dist-min";

const props = defineProps({
  /** @type {Array<{x: number[], y: number[], name: string, color?: string}>} */
  series: { type: Array, required: true },
  /** @type {string} */
  title: { type: String, default: "" },
  /** @type {string} */
  xLabel: { type: String, default: "X" },
  /** @type {string} */
  yLabel: { type: String, default: "Y" },
  /** @type {boolean} */
  showLegend: { type: Boolean, default: true },
  /** @type {boolean} */
  useWebGL: { type: Boolean, default: true },
});

const chartRef = ref(null);

const colors = [
  "#409eff",
  "#67c23a",
  "#e6a23c",
  "#f56c6c",
  "#909399",
  "#b37feb",
  "#36cfc9",
];

const plotData = computed(() => {
  return props.series.map((s, i) => ({
    x: s.x,
    y: s.y,
    type: props.useWebGL ? "scattergl" : "scatter",
    mode: "lines+markers",
    name: s.name,
    line: {
      color: s.color || colors[i % colors.length],
      width: 2,
    },
    marker: {
      size: 6,
    },
  }));
});

const layout = computed(() => ({
  title: props.title,
  xaxis: {
    title: props.xLabel,
    gridcolor: "#e4e7ed",
  },
  yaxis: {
    title: props.yLabel,
    gridcolor: "#e4e7ed",
  },
  showlegend: props.showLegend,
  legend: {
    orientation: "h",
    y: -0.2,
  },
  margin: { t: 50, r: 30, b: 80, l: 60 },
  paper_bgcolor: "transparent",
  plot_bgcolor: "transparent",
  font: { family: "inherit" },
  hovermode: "x unified",
}));

const config = {
  responsive: true,
  displayModeBar: true,
  modeBarButtonsToRemove: ["lasso2d", "select2d"],
};

function renderChart() {
  if (!chartRef.value || props.series.length === 0) return;
  Plotly.react(chartRef.value, plotData.value, layout.value, config);
}

watch(() => props.series, renderChart, { deep: true });

onMounted(() => {
  renderChart();
});

onUnmounted(() => {
  if (chartRef.value) {
    Plotly.purge(chartRef.value);
  }
});
</script>

<template>
  <div ref="chartRef" class="line-plot"></div>
</template>

<style scoped>
.line-plot {
  width: 100%;
  min-height: 400px;
}
</style>
