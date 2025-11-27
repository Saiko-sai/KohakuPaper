import { createApp } from "vue";
import { createPinia } from "pinia";
import { createRouter, createWebHistory } from "vue-router";
import { routes } from "vue-router/auto-routes";
import ElementPlus from "element-plus";

import "element-plus/dist/index.css";
import "uno.css";
import "./style.css";

import App from "./App.vue";
import { useConferenceStore } from "./stores/conference";

const app = createApp(App);

// Pinia
const pinia = createPinia();
app.use(pinia);

// Router
const router = createRouter({
  history: createWebHistory(),
  routes,
});
app.use(router);

// Element Plus
app.use(ElementPlus);

// Initialize conference store before mounting
const conferenceStore = useConferenceStore();
conferenceStore.init().finally(() => {
  app.mount("#app");
});
