/** @type {import('tailwindcss').Config} */
module.exports = {
  content: [
    './pages/**/*.{js,ts,jsx,tsx}',
    './components/**/*.{js,ts,jsx,tsx}',
    './app/**/*.{js,ts,jsx,tsx}',
    './src/**/*.{js,ts,jsx,tsx}',
  ],
  theme: {
    extend: {
      colors: {
        oracle: '#8884d8',
        conjuror: '#82ca9d',
        gemini: '#ffc658',
        aria: '#ff8042',
        capri: '#0088fe',
      },
      fontFamily: {
        mono: ['Monaco', 'Menlo', 'monospace'],
      },
    },
  },
  plugins: [],
}