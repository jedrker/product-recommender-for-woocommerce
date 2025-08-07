import { defineConfig } from 'vite';
import { resolve } from 'path';

export default defineConfig({
  // Root directory
  root: '.',

  // Public directory for static assets
  publicDir: 'public',

  // Build configuration
  build: {
    outDir: 'dist',
    emptyOutDir: true,
    sourcemap: true,
    rollupOptions: {
      input: {
        main: resolve(__dirname, 'index.html'),
        iframe: resolve(__dirname, 'iframe.html'),
        wordpress: resolve(__dirname, 'wordpress-integration.html'),
      },
      output: {
        // Clean filenames for better caching
        entryFileNames: 'assets/[name]-[hash].js',
        chunkFileNames: 'assets/[name]-[hash].js',
        assetFileNames: 'assets/[name]-[hash].[ext]',
      },
    },
    // Optimize for production
    minify: 'terser',
    target: 'es2020',
    // Generate manifest for SSR if needed
    manifest: true,
  },

  // Development server
  server: {
    port: 8080,
    host: true,
    open: false,
    cors: true,
    proxy: {
      // Proxy API calls during development
      '/api': {
        target: 'http://localhost:5000',
        changeOrigin: true,
        rewrite: path => path.replace(/^\/api/, ''),
      },
    },
  },

  // Preview server (for production builds)
  preview: {
    port: 8080,
    host: true,
    cors: true,
  },

  // TypeScript configuration
  esbuild: {
    target: 'es2020',
  },

  // Environment variables
  define: {
    __APP_VERSION__: JSON.stringify(process.env.npm_package_version),
    __BUILD_TIME__: JSON.stringify(new Date().toISOString()),
  },

  // Path resolution
  resolve: {
    alias: {
      '@': resolve(__dirname, 'src'),
      '@types': resolve(__dirname, 'types'),
      '@assets': resolve(__dirname, 'public'),
    },
  },

  // Optimizations
  optimizeDeps: {
    include: [],
    exclude: [],
  },

  // CSS configuration
  css: {
    devSourcemap: true,
  },
});
