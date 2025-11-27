/**
 * Conference store - manages selected conference and available data
 */

import { defineStore } from "pinia";
import { fetchConferences, fetchFilters } from "@/utils/api";

export const useConferenceStore = defineStore("conference", {
  state: () => ({
    /** @type {Object<string, string>} */
    conferences: {},
    /** @type {Object<string, number[]>} */
    localData: {},
    /** @type {string|null} */
    selectedConference: null,
    /** @type {number|null} */
    selectedYear: null,
    /** @type {string[]} */
    statuses: [],
    /** @type {string[]} */
    primaryAreas: [],
    /** @type {string[]} */
    tracks: [],
    /** @type {boolean} */
    loading: false,
    /** @type {boolean} */
    initialized: false,
  }),

  getters: {
    /**
     * Get available years for selected conference
     * @returns {number[]}
     */
    availableYears(state) {
      if (
        !state.selectedConference ||
        !state.localData[state.selectedConference]
      ) {
        return [];
      }
      return state.localData[state.selectedConference];
    },

    /**
     * Get display name for selected conference
     * @returns {string}
     */
    selectedConferenceName(state) {
      if (!state.selectedConference) return "";
      return (
        state.conferences[state.selectedConference] ||
        state.selectedConference.toUpperCase()
      );
    },

    /**
     * Check if we have local data
     * @returns {boolean}
     */
    hasLocalData(state) {
      return Object.keys(state.localData).length > 0;
    },

    /**
     * Get list of conferences with local data
     * @returns {Array<{key: string, name: string, years: number[]}>}
     */
    availableConferences(state) {
      return Object.entries(state.localData).map(([key, years]) => ({
        key,
        name: state.conferences[key] || key.toUpperCase(),
        years,
      }));
    },
  },

  actions: {
    /**
     * Initialize store - fetch conferences list
     */
    async init() {
      if (this.initialized) return;

      this.loading = true;
      try {
        const data = await fetchConferences();
        this.conferences = data.conferences || {};
        this.localData = data.local || {};

        // Auto-select first conference with data
        const firstConf = Object.keys(this.localData)[0];
        if (firstConf) {
          await this.selectConference(firstConf);
        }

        this.initialized = true;
      } catch (err) {
        console.error("Failed to fetch conferences:", err);
      } finally {
        this.loading = false;
      }
    },

    /**
     * Select a conference and optionally a year
     * @param {string} conference
     * @param {number} [year]
     */
    async selectConference(conference, year = null) {
      this.selectedConference = conference;

      // Set year - use provided year or latest available
      const years = this.localData[conference] || [];
      if (year && years.includes(year)) {
        this.selectedYear = year;
      } else if (years.length > 0) {
        this.selectedYear = years[years.length - 1]; // Latest year
      } else {
        this.selectedYear = null;
      }

      // Fetch filters for this conference/year
      await this.fetchFiltersForSelection();
    },

    /**
     * Select a year within current conference
     * @param {number} year
     */
    async selectYear(year) {
      this.selectedYear = year;
      await this.fetchFiltersForSelection();
    },

    /**
     * Fetch filters for current selection
     */
    async fetchFiltersForSelection() {
      if (!this.selectedConference) return;

      try {
        const params = {
          conference: this.selectedConference,
        };
        if (this.selectedYear) {
          params.year = this.selectedYear;
        }

        const data = await fetchFilters(params);
        this.statuses = data.statuses || [];
        this.primaryAreas = data.primary_areas || [];
        this.tracks = data.tracks || [];
      } catch (err) {
        console.error("Failed to fetch filters:", err);
      }
    },

    /**
     * Alias for selectConference
     * @param {string} conference
     * @param {number} [year]
     */
    async setConference(conference, year = null) {
      await this.selectConference(conference, year);
    },

    /**
     * Reload initial data (after download)
     */
    async loadInitialData() {
      this.initialized = false;
      await this.init();
    },
  },
});
