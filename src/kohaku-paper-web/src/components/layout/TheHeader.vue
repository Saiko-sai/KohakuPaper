<script setup>
import { useConferenceStore } from '@/stores/conference'

const conferenceStore = useConferenceStore()

function onConferenceChange(conf) {
  conferenceStore.selectConference(conf)
}

function onYearChange(year) {
  conferenceStore.selectYear(year)
}
</script>

<template>
  <header class="header">
    <div class="header-content">
      <div class="logo">
        <router-link to="/" class="logo-link">
          <span class="logo-icon i-carbon-document-multiple"></span>
          <span class="logo-text">KohakuPaper</span>
        </router-link>
      </div>

      <nav class="nav">
        <router-link to="/" class="nav-link">Home</router-link>
        <router-link to="/conference" class="nav-link">Conference</router-link>
      </nav>

      <div class="selectors" v-if="conferenceStore.hasLocalData">
        <el-select
          :model-value="conferenceStore.selectedConference"
          @change="onConferenceChange"
          placeholder="Select Conference"
          class="conf-select"
          size="default"
        >
          <el-option
            v-for="conf in conferenceStore.availableConferences"
            :key="conf.key"
            :label="`${conf.name} (${conf.years.length} years)`"
            :value="conf.key"
          />
        </el-select>

        <el-select
          v-if="conferenceStore.availableYears.length > 0"
          :model-value="conferenceStore.selectedYear"
          @change="onYearChange"
          placeholder="Year"
          class="year-select"
          size="default"
        >
          <el-option
            v-for="year in conferenceStore.availableYears"
            :key="year"
            :label="year"
            :value="year"
          />
        </el-select>
      </div>
    </div>
  </header>
</template>

<style scoped>
.header {
  background: var(--el-bg-color);
  border-bottom: 1px solid var(--el-border-color-light);
  position: sticky;
  top: 0;
  z-index: 100;
}

.header-content {
  max-width: 1400px;
  margin: 0 auto;
  padding: 0 1rem;
  height: 60px;
  display: flex;
  align-items: center;
  gap: 2rem;
}

.logo-link {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  text-decoration: none;
  color: var(--el-text-color-primary);
  font-weight: 600;
  font-size: 1.25rem;
}

.logo-icon {
  font-size: 1.5rem;
  color: var(--el-color-primary);
}

.nav {
  display: flex;
  gap: 1rem;
}

.nav-link {
  text-decoration: none;
  color: var(--el-text-color-regular);
  padding: 0.5rem 0.75rem;
  border-radius: 6px;
  transition: all 0.2s;
}

.nav-link:hover {
  color: var(--el-color-primary);
  background: var(--el-fill-color-light);
}

.nav-link.router-link-active {
  color: var(--el-color-primary);
  background: var(--el-color-primary-light-9);
}

.selectors {
  margin-left: auto;
  display: flex;
  gap: 0.75rem;
}

.conf-select {
  width: 200px;
}

.year-select {
  width: 100px;
}
</style>
