import react from '@vitejs/plugin-react'
import { defineConfig } from 'vite'
import { viteSingleFile } from 'vite-plugin-singlefile'

// https://vite.dev/config/
export default defineConfig({
  base: './',
  plugins: [react(), viteSingleFile()],
  build: {
    // Один самодостаточный index.html: можно открыть двойным щелчком
    // без CORS-ограничений браузера на модули, загружаемые через file://
    cssCodeSplit: false,
  },
})
