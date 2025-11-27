import { defineConfig, presetUno, presetAttributify, presetIcons } from 'unocss'

export default defineConfig({
  presets: [
    presetUno(),
    presetAttributify(),
    presetIcons({
      scale: 1.2,
      extraProperties: {
        'display': 'inline-block',
        'vertical-align': 'middle'
      }
    })
  ],
  theme: {
    colors: {
      primary: {
        50: '#eff6ff',
        100: '#dbeafe',
        200: '#bfdbfe',
        300: '#93c5fd',
        400: '#60a5fa',
        500: '#3b82f6',
        600: '#2563eb',
        700: '#1d4ed8',
        800: '#1e40af',
        900: '#1e3a8a',
        DEFAULT: '#3b82f6'
      }
    }
  },
  shortcuts: {
    'btn': 'px-4 py-2 rounded-md font-medium transition-colors shadow-sm cursor-pointer',
    'btn-primary': 'btn bg-primary-600 hover:bg-primary-700 text-white',
    'btn-secondary': 'btn bg-gray-100 hover:bg-gray-200 text-gray-700 dark:bg-gray-800 dark:hover:bg-gray-700 dark:text-gray-200',
    'card': 'bg-white dark:bg-gray-900 rounded-lg shadow-md p-4 border border-gray-200 dark:border-gray-800',
    'card-title': 'text-lg font-semibold text-gray-900 dark:text-gray-100 mb-4',
    'input': 'px-3 py-2 border border-gray-300 dark:border-gray-700 rounded-md bg-white dark:bg-gray-900 text-gray-900 dark:text-gray-100 focus:ring-2 focus:ring-primary-500 focus:border-transparent outline-none',
    'container-main': 'max-w-7xl mx-auto px-4 sm:px-6 lg:px-8',
    'page-title': 'text-2xl font-bold text-gray-900 dark:text-gray-100 mb-6',
    'section-title': 'text-xl font-semibold text-gray-800 dark:text-gray-200 mb-4'
  }
})
