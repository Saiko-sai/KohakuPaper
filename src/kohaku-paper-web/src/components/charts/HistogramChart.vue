<script setup>
import Plotly from "plotly.js-dist-min";

const props = defineProps({
  bins: { type: Array, required: true },
  counts: { type: Array, required: true },
  binEdges: { type: Array, default: () => [] },
  byStatus: { type: Object, default: () => ({}) },
  cumulativeCounts: { type: Array, default: () => [] },
  cumulativeByStatus: { type: Object, default: () => ({}) },
  statuses: { type: Array, default: () => [] },
  totalCount: { type: Number, default: 0 },
  statusTotals: { type: Object, default: () => ({}) },
  title: { type: String, default: "Rating Distribution" },
  xLabel: { type: String, default: "Rating" },
  yLabel: { type: String, default: "Count" },
  showLegend: { type: Boolean, default: true },
  stacked: { type: Boolean, default: false },
  showCumulative: { type: Boolean, default: false },
});

const chartRef = ref(null);

// Color palette for dynamic assignment
const colorPalette = [
  "#409eff", // blue
  "#e6a23c", // orange
  "#67c23a", // green
  "#f56c6c", // red
  "#909399", // gray
  "#9c27b0", // purple
  "#00bcd4", // cyan
  "#ff9800", // amber
  "#795548", // brown
  "#607d8b", // blue-gray
];

const getColorByIndex = (index) => colorPalette[index % colorPalette.length];

// Build hover text for a bin
// Bins are [start, end) - left inclusive, right exclusive
function buildHoverText(binIndex, status, count, cumCount, total) {
  const binStart = props.binEdges[binIndex]?.toFixed(2) || "?";
  const binEnd = props.binEdges[binIndex + 1]?.toFixed(2) || "?";
  const pct = total > 0 ? ((cumCount / total) * 100).toFixed(2) : "0.00";
  return `${status}<br>Rating: [${binStart}, ${binEnd})<br>Count: ${count}<br>Cumulative: ${cumCount} (${pct}%)`;
}

// Build cumulative hover text with top k% for all statuses
// Cumulative is count of papers with rating < bin_edges[i+1]
function buildCumulativeHoverText(binIndex) {
  const binEnd = props.binEdges[binIndex + 1]?.toFixed(2) || "?";

  let text = `<b>Rating < ${binEnd}</b><br>`;

  // Total
  const totalCum = props.cumulativeCounts[binIndex] || 0;
  const totalPct =
    props.totalCount > 0
      ? ((totalCum / props.totalCount) * 100).toFixed(2)
      : "0.00";
  text += `<b>All:</b> ${totalCum} (${totalPct}%)<br>`;

  // Per status
  const orderedStatuses =
    props.statuses.length > 0
      ? props.statuses
      : Object.keys(props.cumulativeByStatus);
  for (const status of orderedStatuses) {
    if (props.cumulativeByStatus[status]) {
      const cumCount = props.cumulativeByStatus[status][binIndex] || 0;
      const statusTotal = props.statusTotals[status] || 0;
      const pct =
        statusTotal > 0 ? ((cumCount / statusTotal) * 100).toFixed(2) : "0.00";
      text += `${status}: ${cumCount}/${statusTotal} (${pct}%)<br>`;
    }
  }

  return text;
}

const plotData = computed(() => {
  const orderedStatuses =
    props.statuses.length > 0 ? props.statuses : Object.keys(props.byStatus);

  const traces = [];

  // Stacked bar chart by status
  if (props.stacked && Object.keys(props.byStatus).length > 0) {
    orderedStatuses.forEach((status, index) => {
      if (props.byStatus[status]) {
        const hoverTexts = props.byStatus[status].map((count, i) => {
          const cumCount = props.cumulativeByStatus[status]?.[i] || 0;
          const statusTotal = props.statusTotals[status] || 0;
          return buildHoverText(i, status, count, cumCount, statusTotal);
        });

        traces.push({
          x: props.bins,
          y: props.byStatus[status],
          type: "bar",
          name: status,
          marker: { color: getColorByIndex(index) },
          hovertext: hoverTexts,
          hoverinfo: "text",
        });
      }
    });
  } else {
    // Simple histogram
    traces.push({
      x: props.bins,
      y: props.counts,
      type: "bar",
      name: "Papers",
      marker: { color: "#409eff" },
    });
  }

  // Add cumulative line on secondary y-axis
  if (props.showCumulative && props.cumulativeCounts.length > 0) {
    const hoverTexts = props.bins.map((_, i) => buildCumulativeHoverText(i));

    traces.push({
      x: props.bins,
      y: props.cumulativeCounts,
      type: "scatter",
      mode: "lines+markers",
      name: "Cumulative (All)",
      line: { color: "#303133", width: 3 },
      marker: { size: 6 },
      yaxis: "y2",
      hovertext: hoverTexts,
      hoverinfo: "text",
    });

    // Add cumulative lines per status
    orderedStatuses.forEach((status, index) => {
      if (props.cumulativeByStatus[status]) {
        traces.push({
          x: props.bins,
          y: props.cumulativeByStatus[status],
          type: "scatter",
          mode: "lines",
          name: `Cum. ${status}`,
          line: { color: getColorByIndex(index), width: 2, dash: "dot" },
          yaxis: "y2",
          hoverinfo: "skip",
        });
      }
    });
  }

  return traces;
});

const layout = computed(() => {
  const baseLayout = {
    title: props.title,
    xaxis: {
      title: props.xLabel,
      gridcolor: "#e4e7ed",
    },
    yaxis: {
      title: props.yLabel,
      gridcolor: "#e4e7ed",
    },
    barmode: props.stacked ? "stack" : "group",
    showlegend: props.showLegend,
    legend: {
      orientation: "h",
      y: -0.15,
      x: 0.5,
      xanchor: "center",
    },
    margin: { t: 50, r: props.showCumulative ? 80 : 30, b: 100, l: 60 },
    paper_bgcolor: "transparent",
    plot_bgcolor: "transparent",
    font: { family: "inherit" },
    hovermode: "x unified",
  };

  // Add secondary y-axis for cumulative
  if (props.showCumulative) {
    baseLayout.yaxis2 = {
      title: "Cumulative Count",
      overlaying: "y",
      side: "right",
      gridcolor: "rgba(0,0,0,0.1)",
      showgrid: false,
    };
  }

  return baseLayout;
});

const config = {
  responsive: true,
  displayModeBar: true,
  modeBarButtonsToRemove: ["lasso2d", "select2d"],
};

function renderChart() {
  if (!chartRef.value || props.bins.length === 0) return;
  Plotly.react(chartRef.value, plotData.value, layout.value, config);
}

watch(
  [
    () => props.bins,
    () => props.counts,
    () => props.stacked,
    () => props.showCumulative,
    () => props.cumulativeByStatus,
    () => props.byStatus,
    () => props.statuses,
  ],
  renderChart,
  { deep: true },
);

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
  <div ref="chartRef" class="histogram-chart"></div>
</template>

<style scoped>
.histogram-chart {
  width: 100%;
  height: 80vh;
  min-height: 500px;
}
</style>
