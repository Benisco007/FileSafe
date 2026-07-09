/** @type {import('tailwindcss').Config} */
export default {
  content: [
    "./index.html",
    "./src/**/*.{vue,js,ts,jsx,tsx}",
  ],
  darkMode: 'class',
  theme: {
    extend: {
      colors: {
        primary: '#F4B400',
        'primary-hover': '#D89E00',
        dark: '#121212',
        'dark-2': '#1E1E1E',
        'app-text': '#2C2C2C',
        success: '#22C55E',
        danger: '#EF4444',
      },
      fontFamily: {
        sans: ['Inter', 'sans-serif'],
      },
      borderRadius: {
        card: '18px',
      }
    },
  },
  plugins: [],
}