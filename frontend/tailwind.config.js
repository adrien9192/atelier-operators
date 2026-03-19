/** @type {import('tailwindcss').Config} */
export default {
  content: ['./index.html', './src/**/*.{js,ts,jsx,tsx}'],
  theme: {
    extend: {
      colors: {
        base: '#090909',
        panel: '#141414',
        line: 'rgba(255,255,255,0.09)',
        soft: '#a59f95',
        accent: '#c79a3b',
        mint: '#d8c7a1',
        violet: '#847463',
      },
      boxShadow: {
        glow: '0 0 0 1px rgba(255,255,255,0.06), 0 30px 90px rgba(0,0,0,0.52)',
      },
      backgroundImage: {
        grid: 'radial-gradient(circle at 1px 1px, rgba(255,255,255,0.08) 1px, transparent 0)',
      },
    },
  },
  plugins: [],
}
