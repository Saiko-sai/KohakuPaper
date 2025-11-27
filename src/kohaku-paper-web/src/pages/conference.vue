<script setup>
import { useConferenceStore } from "@/stores/conference";
import {
  fetchPapers,
  fetchRatingDistribution,
  fetchStatsByStatus,
  fetchStatsByArea,
} from "@/utils/api";
import HistogramChart from "@/components/charts/HistogramChart.vue";
import { InfoFilled } from "@element-plus/icons-vue";

const conferenceStore = useConferenceStore();

// Tab state
const activeTab = ref("charts");

// Charts tab state
const chartType = ref("histogram");
const histogramData = ref({
  bins: [],
  counts: [],
  bin_edges: [],
  by_status: {},
  cumulative_counts: [],
  cumulative_by_status: {},
  statuses: [],
  total_count: 0,
  status_totals: {},
});
const showStacked = ref(true);
const showCumulative = ref(true);
const histogramStep = ref(0.1);
const stepOptions = [0.05, 0.1, 0.2, 0.25, 0.5];
const chartAreaFilter = ref(""); // Area filter for charts

// Stats for status breakdown
const statusStats = ref([]);
const areaStats = ref([]);

// Papers tab state
const papers = ref([]);
const totalPapers = ref(0);
const papersLoading = ref(false);
const searchQuery = ref("");
const selectedStatus = ref("");
const selectedArea = ref("");
const currentPage = ref(1);
const pageSize = ref(50);
const pageSizeOptions = [20, 50, 100, 200];
const sortField = ref("rating_avg");
const sortOrder = ref("DESC");

// Column filters
const columnFilters = ref({
  title: "",
  rating: "",
  ratingAvg: "",
  ratingInit: "",
  ratingDiff: "",
  confidence: "",
  confidenceAvg: "",
  confidenceInit: "",
  confidenceDiff: "",
  primaryArea: "",
  status: "",
});

// Chart loading
const chartLoading = ref(false);

// Computed params for API calls
const queryParams = computed(() => ({
  conference: conferenceStore.selectedConference,
  year: conferenceStore.selectedYear,
}));

// Load histogram data
async function loadHistogram() {
  if (!conferenceStore.selectedConference) return;

  chartLoading.value = true;
  try {
    const params = {
      ...queryParams.value,
      step: histogramStep.value,
    };
    if (chartAreaFilter.value) {
      params.primary_area = chartAreaFilter.value;
    }
    histogramData.value = await fetchRatingDistribution(params);
  } catch (err) {
    console.error("Failed to load histogram:", err);
  } finally {
    chartLoading.value = false;
  }
}

// Load status stats
async function loadStatusStats() {
  if (!conferenceStore.selectedConference) return;

  try {
    statusStats.value = await fetchStatsByStatus(queryParams.value);
  } catch (err) {
    console.error("Failed to load status stats:", err);
  }
}

// Load area stats
async function loadAreaStats() {
  if (!conferenceStore.selectedConference) return;

  try {
    areaStats.value = await fetchStatsByArea(queryParams.value);
  } catch (err) {
    console.error("Failed to load area stats:", err);
  }
}

// Parse numeric filter (e.g., ">=6", "<4.5", "5")
function parseNumericFilter(filterValue) {
  const trimmed = (filterValue || "").trim();
  if (!trimmed) return { min: null, max: null };

  const match = trimmed.match(/^(>=|<=|>|<|=)?\s*(\d+\.?\d*)$/);
  if (!match) return { min: null, max: null };

  const op = match[1] || "=";
  const val = parseFloat(match[2]);

  switch (op) {
    case ">=":
      return { min: val, max: null };
    case ">":
      return { min: val + 0.01, max: null };
    case "<=":
      return { min: null, max: val };
    case "<":
      return { min: null, max: val - 0.01 };
    default:
      return { min: val - 0.01, max: val + 0.01 };
  }
}

// Load papers
async function loadPapers() {
  if (!conferenceStore.selectedConference) return;

  papersLoading.value = true;
  try {
    const params = {
      ...queryParams.value,
      limit: pageSize.value,
      offset: (currentPage.value - 1) * pageSize.value,
      order_by: sortField.value,
      order_dir: sortOrder.value,
    };

    if (searchQuery.value) {
      params.search = searchQuery.value;
    }
    if (selectedStatus.value) {
      params.status = selectedStatus.value;
    }
    if (selectedArea.value) {
      params.primary_area = selectedArea.value;
    }

    // Column filters - title filter
    if (columnFilters.value.title) {
      params.title_filter = columnFilters.value.title;
    }

    // Primary area filter (from column)
    if (columnFilters.value.primaryArea) {
      params.primary_area = columnFilters.value.primaryArea;
    }

    // Rating filter - check for "diff" keyword
    if (columnFilters.value.rating) {
      const ratingFilter = columnFilters.value.rating.toLowerCase().trim();
      if (ratingFilter === "diff") {
        params.has_rating_diff = true;
      }
    }

    // Avg rating filter
    if (columnFilters.value.ratingAvg) {
      const { min, max } = parseNumericFilter(columnFilters.value.ratingAvg);
      if (min !== null) params.min_rating = min;
      if (max !== null) params.max_rating = max;
    }

    // Confidence filter - check for "diff" keyword
    if (columnFilters.value.confidence) {
      const confFilter = columnFilters.value.confidence.toLowerCase().trim();
      if (confFilter === "diff") {
        params.has_confidence_diff = true;
      }
    }

    // Avg confidence filter
    if (columnFilters.value.confidenceAvg) {
      const { min, max } = parseNumericFilter(
        columnFilters.value.confidenceAvg,
      );
      if (min !== null) params.min_confidence = min;
      if (max !== null) params.max_confidence = max;
    }

    // Init rating filter
    if (columnFilters.value.ratingInit) {
      const { min, max } = parseNumericFilter(columnFilters.value.ratingInit);
      if (min !== null) params.min_rating_init = min;
      if (max !== null) params.max_rating_init = max;
    }

    // Rating diff filter
    if (columnFilters.value.ratingDiff) {
      const { min, max } = parseNumericFilter(columnFilters.value.ratingDiff);
      if (min !== null) params.min_rating_diff = min;
      if (max !== null) params.max_rating_diff = max;
    }

    // Init confidence filter
    if (columnFilters.value.confidenceInit) {
      const { min, max } = parseNumericFilter(
        columnFilters.value.confidenceInit,
      );
      if (min !== null) params.min_confidence_init = min;
      if (max !== null) params.max_confidence_init = max;
    }

    // Confidence diff filter
    if (columnFilters.value.confidenceDiff) {
      const { min, max } = parseNumericFilter(
        columnFilters.value.confidenceDiff,
      );
      if (min !== null) params.min_confidence_diff = min;
      if (max !== null) params.max_confidence_diff = max;
    }

    const data = await fetchPapers(params);
    papers.value = data.papers;
    totalPapers.value = data.total;
  } catch (err) {
    console.error("Failed to load papers:", err);
  } finally {
    papersLoading.value = false;
  }
}

// Check if any column filters are active
const hasActiveColumnFilters = computed(() => {
  return Object.values(columnFilters.value).some((v) => v && v.trim());
});

// Area bar chart data
const areaCumulativeData = computed(() => {
  if (areaStats.value.length === 0) return { bins: [], counts: [] };

  const sorted = [...areaStats.value].sort(
    (a, b) => b.paper_count - a.paper_count,
  );
  const top20 = sorted.slice(0, 20);

  return {
    bins: top20.map((a) => (a.primary_area || "Unknown").slice(0, 30)),
    counts: top20.map((a) => a.paper_count),
  };
});

// Debounce for column filters
let filterDebounceTimer = null;

// Watch column filters and reload with debounce
watch(
  columnFilters,
  () => {
    if (filterDebounceTimer) clearTimeout(filterDebounceTimer);
    filterDebounceTimer = setTimeout(() => {
      currentPage.value = 1;
      loadPapers();
    }, 300);
  },
  { deep: true },
);

// Watch for conference/year changes
watch(
  () => [conferenceStore.selectedConference, conferenceStore.selectedYear],
  () => {
    if (conferenceStore.selectedConference) {
      loadHistogram();
      loadStatusStats();
      loadAreaStats();
      if (activeTab.value === "papers") {
        currentPage.value = 1;
        loadPapers();
      }
    }
  },
  { immediate: true },
);

// Watch histogram step and area filter
watch([histogramStep, chartAreaFilter], loadHistogram);

// Watch tab changes
watch(activeTab, (tab) => {
  if (tab === "papers" && papers.value.length === 0) {
    loadPapers();
  }
});

// Watch paper filters
watch([searchQuery, selectedStatus, selectedArea], () => {
  currentPage.value = 1;
  loadPapers();
});

// Watch page size changes
watch(pageSize, () => {
  currentPage.value = 1;
  loadPapers();
});

// Pagination handler
function handlePageChange(page) {
  currentPage.value = page;
  loadPapers();
}

// Sort handler
function handleSort({ prop, order }) {
  sortField.value = prop;
  sortOrder.value = order === "ascending" ? "ASC" : "DESC";
  loadPapers();
}

// Open paper link
function openPaper(row) {
  if (row.site) {
    window.open(row.site, "_blank");
  }
}

// Format scores array (already sorted high to low from backend)
function formatScores(scores) {
  if (!scores || !Array.isArray(scores) || scores.length === 0) return "-";
  return scores.map((s) => (Number.isInteger(s) ? s : s.toFixed(1))).join(", ");
}

// Check if diff array has any non-zero values
function hasDiff(diffArr) {
  if (!diffArr || !Array.isArray(diffArr)) return false;
  return diffArr.some((d) => d !== 0);
}

// Format diff array with +/- signs
function formatDiff(diffArr) {
  if (!diffArr || !Array.isArray(diffArr)) return "";
  return diffArr
    .map((d) => {
      if (d > 0) return `+${Number.isInteger(d) ? d : d.toFixed(1)}`;
      if (d < 0) return `${Number.isInteger(d) ? d : d.toFixed(1)}`;
      return "0";
    })
    .join(", ");
}

// Get correlation color class
function getCorrClass(corr) {
  if (corr == null) return "";
  if (corr > 0.5) return "corr-positive";
  if (corr < -0.5) return "corr-negative";
  return "";
}

// Calculate average from array of scores
function calcAvg(scores) {
  // Handle null, undefined, non-array, or empty array
  if (!scores || !Array.isArray(scores) || scores.length === 0) return null;
  // Also check if all values are valid numbers
  const validScores = scores.filter((s) => typeof s === "number" && !isNaN(s));
  if (validScores.length === 0) return null;
  const sum = validScores.reduce((a, b) => a + b, 0);
  return sum / validScores.length;
}

// Format average diff (current - init)
function formatAvgDiff(current, init) {
  // Both must be valid numbers
  if (current == null || init == null || isNaN(current) || isNaN(init))
    return "-";
  const diff = current - init;
  if (Math.abs(diff) < 0.01) return "0";
  const sign = diff > 0 ? "+" : "";
  return `${sign}${diff.toFixed(1)}`;
}

// Get class for avg diff coloring
function getAvgDiffClass(current, init) {
  if (current == null || init == null || isNaN(current) || isNaN(init))
    return "";
  const diff = current - init;
  if (diff > 0.1) return "diff-positive";
  if (diff < -0.1) return "diff-negative";
  return "";
}

// Format rating/confidence values from string: "4;4;6;6" -> "4, 4, 6, 6"
function formatRatingValues(valueStr) {
  if (!valueStr) return "-";
  const values = valueStr.split(";").map((v) => v.trim());
  return values.join(", ");
}

// Get status tag type
function getStatusType(status) {
  if (!status) return "info";
  const s = status.toLowerCase();
  if (s === "accept" || s === "oral" || s === "spotlight" || s === "poster")
    return "success";
  if (s === "reject") return "danger";
  if (s === "withdraw" || s === "withdrawn") return "warning";
  if (s === "active") return "primary";
  return "info";
}
</script>

<template>
  <div class="conference-page">
    <div class="page-header">
      <h1>
        {{ conferenceStore.selectedConferenceName }}
        {{ conferenceStore.selectedYear }}
      </h1>
    </div>

    <el-tabs v-model="activeTab" class="main-tabs">
      <!-- Charts Tab -->
      <el-tab-pane label="Charts" name="charts">
        <div class="charts-controls">
          <el-radio-group v-model="chartType" size="default">
            <el-radio-button value="histogram"
              >Rating Distribution</el-radio-button
            >
            <el-radio-button value="areas">Top Areas</el-radio-button>
          </el-radio-group>

          <div class="chart-options" v-if="chartType === 'histogram'">
            <el-select
              v-model="chartAreaFilter"
              placeholder="All Areas"
              clearable
              filterable
              class="area-filter-select"
            >
              <el-option
                v-for="area in conferenceStore.primaryAreas"
                :key="area"
                :label="area"
                :value="area"
              />
            </el-select>
            <el-checkbox v-model="showStacked">Stacked</el-checkbox>
            <el-checkbox v-model="showCumulative">Cumulative</el-checkbox>
            <span class="step-label">Step:</span>
            <el-select v-model="histogramStep" class="step-select">
              <el-option
                v-for="s in stepOptions"
                :key="s"
                :label="s.toString()"
                :value="s"
              />
            </el-select>
          </div>
        </div>

        <div class="chart-container" v-loading="chartLoading">
          <HistogramChart
            v-if="chartType === 'histogram'"
            :bins="histogramData.bins"
            :counts="histogramData.counts"
            :bin-edges="histogramData.bin_edges"
            :by-status="histogramData.by_status"
            :cumulative-counts="histogramData.cumulative_counts"
            :cumulative-by-status="histogramData.cumulative_by_status"
            :statuses="histogramData.statuses"
            :total-count="histogramData.total_count"
            :status-totals="histogramData.status_totals"
            :stacked="showStacked"
            :show-cumulative="showCumulative"
            title="Rating Distribution"
            x-label="Average Rating"
            y-label="Number of Papers"
          />

          <HistogramChart
            v-else-if="chartType === 'areas'"
            :bins="areaCumulativeData.bins"
            :counts="areaCumulativeData.counts"
            :stacked="false"
            title="Top 20 Research Areas"
            x-label="Primary Area"
            y-label="Number of Papers"
          />
        </div>

        <!-- Status breakdown -->
        <div class="stats-section" v-if="statusStats.length > 0">
          <h3>Status Breakdown</h3>
          <div class="status-cards">
            <div
              v-for="stat in statusStats"
              :key="stat.status"
              class="status-card"
            >
              <div class="status-name">
                <el-tag :type="getStatusType(stat.status)" size="small">
                  {{ stat.status || "Unknown" }}
                </el-tag>
              </div>
              <div class="status-count">
                {{ stat.paper_count?.toLocaleString() }} papers
              </div>
              <div class="status-rating" v-if="stat.avg_rating">
                Avg: {{ stat.avg_rating.toFixed(2) }}
              </div>
            </div>
          </div>
        </div>
      </el-tab-pane>

      <!-- Papers Tab -->
      <el-tab-pane label="Papers" name="papers">
        <div class="papers-filters">
          <el-input
            v-model="searchQuery"
            placeholder="Search title, abstract, keywords..."
            clearable
            class="search-input"
            @keyup.enter="loadPapers"
          >
            <template #prefix>
              <span class="i-carbon-search"></span>
            </template>
          </el-input>

          <el-select
            v-model="selectedStatus"
            placeholder="Status"
            clearable
            class="filter-select"
          >
            <el-option
              v-for="status in conferenceStore.statuses"
              :key="status"
              :label="status"
              :value="status"
            />
          </el-select>

          <el-select
            v-model="selectedArea"
            placeholder="Primary Area"
            clearable
            filterable
            class="filter-select area-select"
          >
            <el-option
              v-for="area in conferenceStore.primaryAreas"
              :key="area"
              :label="area"
              :value="area"
            />
          </el-select>

          <el-select v-model="pageSize" class="page-size-select">
            <el-option
              v-for="size in pageSizeOptions"
              :key="size"
              :label="`${size} / page`"
              :value="size"
            />
          </el-select>
        </div>

        <div class="papers-info">
          <span>{{ totalPapers.toLocaleString() }} papers</span>
          <span v-if="hasActiveColumnFilters" class="filtered-info">
            (filtered)
          </span>
        </div>

        <el-table
          :data="papers"
          v-loading="papersLoading"
          stripe
          @sort-change="handleSort"
          @row-click="openPaper"
          class="papers-table"
          row-class-name="clickable-row"
        >
          <!-- Title -->
          <el-table-column prop="title" label="Title">
            <template #header>
              <div class="column-header">
                <span>Title</span>
                <el-input
                  v-model="columnFilters.title"
                  size="small"
                  placeholder="Filter..."
                  clearable
                  class="column-filter"
                  @click.stop
                />
              </div>
            </template>
            <template #default="{ row }">
              <el-tooltip
                :content="row.title"
                placement="top-start"
                :show-after="500"
              >
                <div class="title-cell">{{ row.title }}</div>
              </el-tooltip>
            </template>
          </el-table-column>

          <!-- Primary Area -->
          <el-table-column prop="primary_area" label="Area" width="80">
            <template #header>
              <div class="column-header">
                <span>Area</span>
                <el-input
                  v-model="columnFilters.primaryArea"
                  size="small"
                  placeholder=""
                  clearable
                  class="column-filter"
                  @click.stop
                />
              </div>
            </template>
            <template #default="{ row }">
              <el-tooltip
                v-if="row.primary_area"
                :content="row.primary_area"
                placement="top-start"
              >
                <el-icon class="area-icon"><InfoFilled /></el-icon>
              </el-tooltip>
              <span v-else>-</span>
            </template>
          </el-table-column>

          <!-- Status -->
          <el-table-column
            prop="status"
            label="Status"
            width="85"
            sortable="custom"
          >
            <template #header>
              <div class="column-header">
                <span>Status</span>
                <el-input
                  v-model="columnFilters.status"
                  size="small"
                  placeholder=""
                  clearable
                  class="column-filter"
                  @click.stop
                />
              </div>
            </template>
            <template #default="{ row }">
              <el-tag :type="getStatusType(row.status)" size="small">
                {{ row.status }}
              </el-tag>
            </template>
          </el-table-column>

          <!-- Rating with diff -->
          <el-table-column prop="rating" label="Rating" width="150">
            <template #header>
              <div class="column-header">
                <span>Rating</span>
                <el-input
                  v-model="columnFilters.rating"
                  size="small"
                  placeholder="diff"
                  clearable
                  class="column-filter"
                  @click.stop
                />
              </div>
            </template>
            <template #default="{ row }">
              <div class="score-cell">
                <span class="score-current">{{
                  formatScores(row._diff?.rating_current)
                }}</span>
                <span v-if="hasDiff(row._diff?.rating_diff)" class="score-diff">
                  ({{ formatDiff(row._diff?.rating_diff) }})
                </span>
              </div>
            </template>
          </el-table-column>

          <!-- Avg Rating -->
          <el-table-column
            prop="rating_avg"
            label="Avg"
            width="80"
            sortable="custom"
          >
            <template #header>
              <div class="column-header">
                <span>Avg</span>
                <el-input
                  v-model="columnFilters.ratingAvg"
                  size="small"
                  placeholder=">=6"
                  clearable
                  class="column-filter"
                  @click.stop
                />
              </div>
            </template>
            <template #default="{ row }">
              {{ row.rating_avg?.toFixed(2) ?? "-" }}
            </template>
          </el-table-column>

          <!-- Init Avg Rating -->
          <el-table-column
            prop="rating_init"
            label="Init"
            width="80"
            sortable="custom"
          >
            <template #header>
              <div class="column-header">
                <span>Init</span>
                <el-input
                  v-model="columnFilters.ratingInit"
                  size="small"
                  placeholder=">=6"
                  clearable
                  class="column-filter"
                  @click.stop
                />
              </div>
            </template>
            <template #default="{ row }">
              {{ calcAvg(row._diff?.rating_first)?.toFixed(2) ?? "-" }}
            </template>
          </el-table-column>

          <!-- Avg Diff Rating -->
          <el-table-column
            prop="rating_diff"
            label="Diff"
            width="80"
            sortable="custom"
          >
            <template #header>
              <div class="column-header">
                <span>Diff</span>
                <el-input
                  v-model="columnFilters.ratingDiff"
                  size="small"
                  placeholder=">0"
                  clearable
                  class="column-filter"
                  @click.stop
                />
              </div>
            </template>
            <template #default="{ row }">
              <span
                :class="
                  getAvgDiffClass(
                    row.rating_avg,
                    calcAvg(row._diff?.rating_first),
                  )
                "
              >
                {{
                  formatAvgDiff(
                    row.rating_avg,
                    calcAvg(row._diff?.rating_first),
                  )
                }}
              </span>
            </template>
          </el-table-column>

          <!-- Confidence with diff -->
          <el-table-column prop="confidence" label="Conf" width="150">
            <template #header>
              <div class="column-header">
                <span>Conf</span>
                <el-input
                  v-model="columnFilters.confidence"
                  size="small"
                  placeholder="diff"
                  clearable
                  class="column-filter"
                  @click.stop
                />
              </div>
            </template>
            <template #default="{ row }">
              <div class="score-cell">
                <span class="score-current">{{
                  formatScores(row._diff?.confidence_current)
                }}</span>
                <span
                  v-if="hasDiff(row._diff?.confidence_diff)"
                  class="score-diff"
                >
                  ({{ formatDiff(row._diff?.confidence_diff) }})
                </span>
              </div>
            </template>
          </el-table-column>

          <!-- Avg Confidence -->
          <el-table-column
            prop="confidence_avg"
            label="Avg"
            width="80"
            sortable="custom"
          >
            <template #header>
              <div class="column-header">
                <span>Avg</span>
                <el-input
                  v-model="columnFilters.confidenceAvg"
                  size="small"
                  placeholder=">=3"
                  clearable
                  class="column-filter"
                  @click.stop
                />
              </div>
            </template>
            <template #default="{ row }">
              {{ row.confidence_avg?.toFixed(2) ?? "-" }}
            </template>
          </el-table-column>

          <!-- Init Avg Confidence -->
          <el-table-column
            prop="confidence_init"
            label="Init"
            width="80"
            sortable="custom"
          >
            <template #header>
              <div class="column-header">
                <span>Init</span>
                <el-input
                  v-model="columnFilters.confidenceInit"
                  size="small"
                  placeholder=">=3"
                  clearable
                  class="column-filter"
                  @click.stop
                />
              </div>
            </template>
            <template #default="{ row }">
              {{ calcAvg(row._diff?.confidence_first)?.toFixed(2) ?? "-" }}
            </template>
          </el-table-column>

          <!-- Avg Diff Confidence -->
          <el-table-column
            prop="confidence_diff"
            label="Diff"
            width="80"
            sortable="custom"
          >
            <template #header>
              <div class="column-header">
                <span>Diff</span>
                <el-input
                  v-model="columnFilters.confidenceDiff"
                  size="small"
                  placeholder=">0"
                  clearable
                  class="column-filter"
                  @click.stop
                />
              </div>
            </template>
            <template #default="{ row }">
              <span
                :class="
                  getAvgDiffClass(
                    row.confidence_avg,
                    calcAvg(row._diff?.confidence_first),
                  )
                "
              >
                {{
                  formatAvgDiff(
                    row.confidence_avg,
                    calcAvg(row._diff?.confidence_first),
                  )
                }}
              </span>
            </template>
          </el-table-column>

          <!-- Correlation -->
          <el-table-column
            prop="corr_rating_confidence"
            label="Corr"
            width="80"
            sortable="custom"
          >
            <template #default="{ row }">
              <span :class="getCorrClass(row.corr_rating_confidence)">
                {{ row.corr_rating_confidence?.toFixed(2) ?? "-" }}
              </span>
            </template>
          </el-table-column>
        </el-table>

        <div class="pagination-wrapper">
          <el-pagination
            v-model:current-page="currentPage"
            :page-size="pageSize"
            :total="totalPapers"
            layout="total, prev, pager, next, jumper"
            @current-change="handlePageChange"
          />
        </div>
      </el-tab-pane>
    </el-tabs>
  </div>
</template>

<style scoped>
.conference-page {
  max-width: 100%;
  margin: 0 auto;
  padding: 1.5rem;
}

.page-header {
  margin-bottom: 1.5rem;
}

.page-header h1 {
  font-size: 1.75rem;
  font-weight: 600;
  color: var(--el-text-color-primary);
}

.main-tabs {
  background: var(--el-bg-color);
  border-radius: 8px;
  padding: 1rem;
}

.charts-controls {
  display: flex;
  align-items: center;
  gap: 2rem;
  margin-bottom: 1rem;
  flex-wrap: wrap;
}

.chart-options {
  display: flex;
  align-items: center;
  gap: 1rem;
}

.step-label {
  color: var(--el-text-color-secondary);
  margin-left: 1rem;
}

.step-select {
  width: 80px;
}

.chart-container {
  width: 100%;
  margin-bottom: 2rem;
}

.stats-section {
  margin-top: 2rem;
}

.stats-section h3 {
  font-size: 1.125rem;
  font-weight: 600;
  margin-bottom: 1rem;
  color: var(--el-text-color-primary);
}

.status-cards {
  display: flex;
  gap: 1rem;
  flex-wrap: wrap;
}

.status-card {
  background: var(--el-fill-color-light);
  border-radius: 8px;
  padding: 1rem 1.5rem;
  min-width: 150px;
}

.status-name {
  margin-bottom: 0.5rem;
}

.status-count {
  font-size: 0.875rem;
  color: var(--el-text-color-secondary);
}

.status-rating {
  font-size: 0.75rem;
  color: var(--el-text-color-placeholder);
  margin-top: 0.25rem;
}

/* Papers tab styles */
.papers-filters {
  display: flex;
  gap: 1rem;
  margin-bottom: 1rem;
  flex-wrap: wrap;
  align-items: center;
}

.search-input {
  width: 350px;
}

.filter-select {
  width: 150px;
}

.area-select {
  width: 250px;
}

.page-size-select {
  width: 120px;
}

.papers-info {
  margin-bottom: 0.75rem;
  color: var(--el-text-color-secondary);
  font-size: 0.875rem;
}

.filtered-info {
  color: var(--el-color-warning);
}

.papers-table {
  width: 100%;
}

.papers-table :deep(.clickable-row) {
  cursor: pointer;
}

.papers-table :deep(.clickable-row:hover) {
  background-color: var(--el-fill-color-light);
}

.column-header {
  display: flex;
  flex-direction: column;
  gap: 4px;
}

/* Make sort icon stay on same line as label */
.papers-table :deep(.el-table__column-header-wrapper) {
  display: flex;
  flex-direction: column;
}

.papers-table :deep(.caret-wrapper) {
  position: absolute;
  right: 0;
  top: 0;
}

.column-filter {
  width: 100%;
}

.title-cell {
  display: -webkit-box;
  -webkit-line-clamp: 2;
  -webkit-box-orient: vertical;
  overflow: hidden;
  text-overflow: ellipsis;
  line-height: 1.3;
  font-size: 0.8rem;
}

.area-icon {
  cursor: pointer;
  color: var(--el-color-primary);
  font-size: 16px;
}

.score-cell {
  font-size: 0.75rem;
  line-height: 1.4;
}

.score-current {
  display: block;
  white-space: nowrap;
}

.score-diff {
  display: block;
  color: var(--el-color-warning);
  font-size: 0.7rem;
  white-space: nowrap;
}

.corr-positive {
  color: var(--el-color-success);
}

.corr-negative {
  color: var(--el-color-danger);
}

.diff-positive {
  color: var(--el-color-success);
  font-weight: 500;
}

.diff-negative {
  color: var(--el-color-danger);
  font-weight: 500;
}

.area-filter-select {
  width: 200px;
}

.pagination-wrapper {
  display: flex;
  justify-content: center;
  margin-top: 1.5rem;
}
</style>
