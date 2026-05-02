import { createVuetify } from 'vuetify'
import 'vuetify/styles'
import '@mdi/font/css/materialdesignicons.css'

export default createVuetify({
  theme: {
    defaultTheme: 'vestoLight',
    themes: {
      vestoLight: {
        dark: false,
        colors: {
          primary: '#2E4057',
          secondary: '#048A81',
          warning: '#F4B942',
          error: '#D62839',
          background: '#F8F9FA',
          surface: '#FFFFFF',
          'on-primary': '#FFFFFF',
          'on-secondary': '#FFFFFF',
        },
      },
    },
  },
  defaults: {
    VBtn: { rounded: 'lg', style: 'text-transform: none;' },
    VCard: { rounded: 'xl' },
    VTextField: { variant: 'outlined', density: 'comfortable', color: 'primary' },
    VSelect: { variant: 'outlined', density: 'comfortable', color: 'primary' },
    VTextarea: { variant: 'outlined', density: 'comfortable', color: 'primary' },
    VChip: { rounded: 'lg' },
  },
})
