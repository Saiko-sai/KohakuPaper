import { defineConfig } from 'vite'
import { fileURLToPath, URL } from 'node:url'
import vue from '@vitejs/plugin-vue'
import VueRouter from 'unplugin-vue-router/vite'
import UnoCSS from 'unocss/vite'
import AutoImport from 'unplugin-auto-import/vite'
import Components from 'unplugin-vue-components/vite'
import { ElementPlusResolver } from 'unplugin-vue-components/resolvers'

// https://vite.dev/config/
export default defineConfig({
  plugins: [
    // File-based routing - must be before vue()
    VueRouter({
      routesFolder: 'src/pages',
      dts: 'src/typed-router.d.ts',
      extensions: ['.vue'],
      exclude: ['**/components/**']
    }),
    vue(),
    // Utility-first CSS
    UnoCSS(),
    // Auto-import Vue, Pinia, Vue Router APIs
    AutoImport({
      imports: [
        'vue',
        'pinia',
        'vue-router',
        { 'vue-router/auto': ['useRoute', 'useRouter'] }
      ],
      resolvers: [ElementPlusResolver()],
      dts: 'src/auto-imports.d.ts'
    }),
    // Auto-register components
    Components({
      resolvers: [ElementPlusResolver()],
      dts: 'src/components.d.ts',
      dirs: ['src/components']
    })
  ],
  resolve: {
    alias: {
      '@': fileURLToPath(new URL('./src', import.meta.url))
    }
  },
  server: {
    port: 5173,
    proxy: {
      '/api': {
        target: 'http://localhost:48880',
        changeOrigin: true
      }
    }
  }
})
