import type { Config } from 'tailwindcss'

const config: Config = {
  content: ['./src/**/*.{ts,tsx}'],
  theme: {
    extend: {
      colors: {
        brand: {
          navy:  '#0F2B5B',
          teal:  '#0D7377',
          sky:   '#1A73C8',
          ice:   '#DFF0FB',
          light: '#F0F5FB',
        }
      },
      fontFamily: {
        sans: ['Inter', 'system-ui', 'sans-serif'],
      }
    }
  },
  plugins: [],
}
export default config
