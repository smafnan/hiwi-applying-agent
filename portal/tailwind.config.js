/** @type {import('tailwindcss').Config} */
export default {
  content: [
    "./index.html",
    "./main.tsx",
    "./App.tsx",
  ],
  theme: {
    extend: {
      colors: {
        btu: {
          primary: '#1e40af',
          secondary: '#0ea5e9',
          accent: '#f59e0b',
        }
      }
    },
  },
  plugins: [],
}
