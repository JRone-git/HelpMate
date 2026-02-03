import { defineConfig } from 'vite'
import { svelte } from '@sveltejs/vite-plugin-svelte'

export default defineConfig({
  plugins: [
    svelte({
      compilerOptions: {
        runes: false
      }
    })
  ],
  server: {
    port: 3000
  },
  build: {
    outDir: 'dist',
    sourcemap: true
  }
})
