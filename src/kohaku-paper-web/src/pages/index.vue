<script setup>
import { useConferenceStore } from '@/stores/conference'
import { fetchSummary, fetchAvailableConferences, syncConference, updateRepo } from '@/utils/api'
import { ElMessage } from 'element-plus'

const conferenceStore = useConferenceStore()
const router = useRouter()

const summary = ref(null)
const loading = ref(false)

// Available conferences from papercopilot
const availableConferences = ref([])
const conferencesLoading = ref(false)

// Selected conference/year for download
const selectedDownloadConf = ref('')
const selectedDownloadYear = ref(null)

// Download state
const downloading = ref(false)
const downloadProgress = ref('')

// Get years for selected conference
const availableYears = computed(() => {
  if (!selectedDownloadConf.value) return []
  const conf = availableConferences.value.find(c => c.conference === selectedDownloadConf.value)
  return conf?.years || []
})

// Check if selected conference/year is already downloaded
const isDownloaded = computed(() => {
  if (!selectedDownloadConf.value || !selectedDownloadYear.value) return false
  const conf = availableConferences.value.find(c => c.conference === selectedDownloadConf.value)
  const yearInfo = conf?.years?.find(y => y.year === selectedDownloadYear.value)
  return yearInfo?.downloaded || false
})

// Load available conferences from papercopilot
async function loadAvailableConferences() {
  conferencesLoading.value = true
  try {
    const data = await fetchAvailableConferences()
    availableConferences.value = data.conferences || []
  } catch (err) {
    console.error('Failed to load conferences:', err)
    ElMessage.error('Failed to load available conferences')
  } finally {
    conferencesLoading.value = false
  }
}

// Download/sync selected conference
async function downloadConference() {
  if (!selectedDownloadConf.value || !selectedDownloadYear.value) {
    ElMessage.warning('Please select a conference and year')
    return
  }

  downloading.value = true
  downloadProgress.value = 'Updating repository...'

  try {
    // First update repo
    await updateRepo()
    downloadProgress.value = `Syncing ${selectedDownloadConf.value} ${selectedDownloadYear.value}...`

    // Then sync the conference
    const result = await syncConference(selectedDownloadConf.value, selectedDownloadYear.value)

    if (result.success) {
      ElMessage.success(`Downloaded ${selectedDownloadConf.value} ${selectedDownloadYear.value}`)
      downloadProgress.value = 'Done!'

      // Reload conferences to update download status
      await loadAvailableConferences()

      // Reload store data
      await conferenceStore.loadInitialData()

      // Auto-select the downloaded conference
      conferenceStore.setConference(selectedDownloadConf.value, selectedDownloadYear.value)
    } else {
      ElMessage.error(result.error || 'Download failed')
      downloadProgress.value = ''
    }
  } catch (err) {
    console.error('Download error:', err)
    ElMessage.error('Failed to download conference data')
    downloadProgress.value = ''
  } finally {
    downloading.value = false
  }
}

// Go to conference page
function goToConference() {
  router.push('/conference')
}

// View selected conference (navigate to conference page)
function viewConference() {
  if (selectedDownloadConf.value && selectedDownloadYear.value && isDownloaded.value) {
    conferenceStore.setConference(selectedDownloadConf.value, selectedDownloadYear.value)
    router.push('/conference')
  }
}

async function loadSummary() {
  if (!conferenceStore.selectedConference) return

  loading.value = true
  try {
    summary.value = await fetchSummary({
      conference: conferenceStore.selectedConference,
      year: conferenceStore.selectedYear,
    })
  } catch (err) {
    console.error('Failed to load summary:', err)
  } finally {
    loading.value = false
  }
}

watch(
  () => [conferenceStore.selectedConference, conferenceStore.selectedYear],
  () => {
    if (conferenceStore.selectedConference) {
      loadSummary()
    }
  },
  { immediate: true }
)

// Load conferences on mount
onMounted(() => {
  loadAvailableConferences()
})
</script>

<template>
  <div class="home-page">
    <section class="hero">
      <h1 class="hero-title">KohakuPaper</h1>
      <p class="hero-subtitle">Local Paper Copilot for Academic Conference Analysis</p>
    </section>

    <!-- Conference Selector Section -->
    <section class="conference-selector">
      <h2>Select Conference</h2>
      <div class="selector-row" v-loading="conferencesLoading">
        <el-select
          v-model="selectedDownloadConf"
          placeholder="Conference"
          filterable
          class="conf-select"
          @change="selectedDownloadYear = null"
        >
          <el-option
            v-for="conf in availableConferences"
            :key="conf.conference"
            :label="conf.conference.toUpperCase()"
            :value="conf.conference"
          />
        </el-select>

        <el-select
          v-model="selectedDownloadYear"
          placeholder="Year"
          :disabled="!selectedDownloadConf"
          class="year-select"
        >
          <el-option
            v-for="yearInfo in availableYears"
            :key="yearInfo.year"
            :label="`${yearInfo.year}${yearInfo.downloaded ? ' (local)' : ''}`"
            :value="yearInfo.year"
          >
            <span>{{ yearInfo.year }}</span>
            <span v-if="yearInfo.downloaded" class="local-badge">local</span>
            <span v-else class="size-badge">{{ yearInfo.size_mb }} MB</span>
          </el-option>
        </el-select>

        <el-button
          v-if="isDownloaded"
          type="primary"
          @click="viewConference"
          :disabled="!selectedDownloadConf || !selectedDownloadYear"
        >
          <span class="i-carbon-view mr-1"></span>
          View
        </el-button>

        <el-button
          v-else
          type="success"
          @click="downloadConference"
          :loading="downloading"
          :disabled="!selectedDownloadConf || !selectedDownloadYear"
        >
          <span class="i-carbon-download mr-1" v-if="!downloading"></span>
          {{ downloading ? 'Downloading...' : 'Download' }}
        </el-button>
      </div>

      <div class="download-progress" v-if="downloadProgress">
        {{ downloadProgress }}
      </div>
    </section>

    <!-- Current Conference Stats -->
    <section class="content" v-if="conferenceStore.hasLocalData">
      <div class="current-conf-header">
        <h3>
          {{ conferenceStore.selectedConferenceName }}
          <span v-if="conferenceStore.selectedYear">({{ conferenceStore.selectedYear }})</span>
        </h3>
      </div>

      <div class="stats-grid" v-if="summary">
        <div class="stat-card">
          <div class="stat-value">{{ summary.total_papers?.toLocaleString() || 0 }}</div>
          <div class="stat-label">Total Papers</div>
        </div>
        <div class="stat-card">
          <div class="stat-value">{{ summary.avg_rating?.toFixed(2) || 'N/A' }}</div>
          <div class="stat-label">Average Rating</div>
        </div>
        <div class="stat-card">
          <div class="stat-value">{{ summary.accepted_count?.toLocaleString() || 0 }}</div>
          <div class="stat-label">Accepted</div>
        </div>
        <div class="stat-card">
          <div class="stat-value">{{ summary.rejected_count?.toLocaleString() || 0 }}</div>
          <div class="stat-label">Rejected/Withdrawn</div>
        </div>
      </div>

      <div class="actions">
        <el-button type="primary" size="large" @click="goToConference">
          <span class="i-carbon-chart-histogram mr-2"></span>
          View Detailed Analysis
        </el-button>
      </div>
    </section>

    <!-- No Data Hint -->
    <section class="no-data" v-if="!conferenceStore.hasLocalData && !conferencesLoading">
      <div class="no-data-icon i-carbon-cloud-download"></div>
      <p>Select a conference above and download to get started</p>
    </section>
  </div>
</template>

<style scoped>
.home-page {
  max-width: 1200px;
  margin: 0 auto;
  padding: 2rem;
}

.hero {
  text-align: center;
  padding: 2rem 0 1rem;
}

.hero-title {
  font-size: 2.5rem;
  font-weight: 700;
  color: var(--el-text-color-primary);
  margin-bottom: 0.5rem;
}

.hero-subtitle {
  font-size: 1.125rem;
  color: var(--el-text-color-secondary);
}

/* Conference Selector */
.conference-selector {
  background: var(--el-bg-color);
  border: 1px solid var(--el-border-color-light);
  border-radius: 12px;
  padding: 1.5rem;
  margin-bottom: 2rem;
}

.conference-selector h2 {
  font-size: 1.125rem;
  font-weight: 600;
  margin-bottom: 1rem;
  color: var(--el-text-color-primary);
}

.selector-row {
  display: flex;
  gap: 1rem;
  align-items: center;
  flex-wrap: wrap;
}

.conf-select {
  width: 180px;
}

.year-select {
  width: 160px;
}

.local-badge {
  margin-left: auto;
  font-size: 0.75rem;
  color: var(--el-color-success);
  background: var(--el-color-success-light-9);
  padding: 2px 6px;
  border-radius: 4px;
}

.size-badge {
  margin-left: auto;
  font-size: 0.75rem;
  color: var(--el-text-color-secondary);
}

.download-progress {
  margin-top: 0.75rem;
  font-size: 0.875rem;
  color: var(--el-color-primary);
}

/* Current Conference Header */
.current-conf-header {
  margin-bottom: 1.5rem;
}

.current-conf-header h3 {
  font-size: 1.25rem;
  font-weight: 600;
  color: var(--el-text-color-primary);
}

.content {
  margin-top: 1rem;
}

.stats-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(180px, 1fr));
  gap: 1rem;
  margin-bottom: 1.5rem;
}

.stat-card {
  background: var(--el-bg-color);
  border: 1px solid var(--el-border-color-light);
  border-radius: 12px;
  padding: 1.25rem;
  text-align: center;
  transition: box-shadow 0.2s;
}

.stat-card:hover {
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
}

.stat-value {
  font-size: 1.75rem;
  font-weight: 700;
  color: var(--el-color-primary);
}

.stat-label {
  font-size: 0.8rem;
  color: var(--el-text-color-secondary);
  margin-top: 0.5rem;
}

.actions {
  text-align: center;
  margin: 1.5rem 0;
}

.no-data {
  text-align: center;
  padding: 3rem 2rem;
}

.no-data-icon {
  font-size: 3rem;
  color: var(--el-text-color-placeholder);
  margin-bottom: 1rem;
}

.no-data p {
  color: var(--el-text-color-secondary);
}
</style>
