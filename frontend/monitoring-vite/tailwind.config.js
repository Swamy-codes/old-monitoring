/** @type {import('tailwindcss').Config} */
export default {
  content: [
    './public/**/*.html',
    "./src/**/*.{vue,js,ts,jsx,tsx}",
  ],
  theme: {
    extend: {
      colors:{
        'primary1': '#64B5F6',
        'primary': '#070F2B',
        'secondary': '#1B1A55',
        'third' :'#535C91'
      }
    },
  },
  plugins: [],
}

