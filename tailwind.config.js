/** @type {import('tailwindcss').Config} */
module.exports = {
  content: [
    "./app/templates/**/*.{html,js}",
    "./app/static/**/*.{js,css}",
    "./frontend/src/**/*.{js,jsx,ts,tsx}",
    "./frontend/index.html",
  ],
  theme: {
    extend: {
      colors: {
        'capital-one': {
          blue: '#004B8D',
          light: '#00A0DC',
          success: '#28a745',
          danger: '#dc3545',
          warning: '#ffc107',
          gray: {
            light: '#f8f9fa',
            dark: '#343a40',
          },
          border: '#dee2e6',
        },
      },
      boxShadow: {
        'capital': '0 2px 4px rgba(0,0,0,0.1)',
        'capital-hover': '0 4px 6px rgba(0,0,0,0.1)',
      },
      animation: {
        'spin-slow': 'spin 1s linear infinite',
        'slide-in': 'slideIn 0.3s ease-out',
      },
      keyframes: {
        slideIn: {
          'from': { transform: 'translateX(100%)', opacity: '0' },
          'to': { transform: 'translateX(0)', opacity: '1' },
        },
      },
    },
  },
  plugins: [
    require('@tailwindcss/forms'),
    require('@tailwindcss/typography'),
  ],
} 