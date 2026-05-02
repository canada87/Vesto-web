<template>
  <v-app :theme="'vestoLight'">
    <!-- Layout con navigazione solo per utenti autenticati -->
    <template v-if="isAuthenticated && !isLoginPage">
      <!-- Sidebar desktop -->
      <v-navigation-drawer v-if="!mobile" permanent width="220" color="primary">
        <div class="pa-4 d-flex align-center gap-2">
          <v-icon icon="mdi-hanger" color="white" size="28" />
          <span class="text-h6 font-weight-bold text-white">Vesto</span>
        </div>
        <v-divider color="rgba(255,255,255,0.2)" />
        <v-list nav density="compact" class="mt-2">
          <v-list-item
            v-for="item in navItems"
            :key="item.to"
            :prepend-icon="item.icon"
            :title="item.label"
            :to="item.to"
            active-color="white"
            base-color="rgba(255,255,255,0.7)"
            rounded="lg"
          />
        </v-list>
        <template #append>
          <v-divider color="rgba(255,255,255,0.2)" />
          <div class="pa-3">
            <div class="text-caption text-white opacity-60 text-truncate">
              {{ authStore.user?.username }}
            </div>
            <v-btn
              variant="text"
              color="white"
              size="small"
              @click="logout"
              class="mt-1"
              prepend-icon="mdi-logout"
            >
              Esci
            </v-btn>
          </div>
        </template>
      </v-navigation-drawer>

      <!-- App bar mobile -->
      <v-app-bar v-if="mobile" color="primary" density="compact" elevation="2">
        <v-app-bar-title>
          <span class="text-h6 font-weight-bold">{{ currentPageTitle }}</span>
        </v-app-bar-title>
      </v-app-bar>

      <!-- Main content -->
      <v-main :style="mobile ? 'padding-bottom:56px' : ''">
        <v-container fluid class="pa-0">
          <router-view />
        </v-container>
      </v-main>

      <!-- Bottom nav mobile -->
      <v-bottom-navigation
        v-if="mobile"
        :model-value="currentRoute"
        color="primary"
        bg-color="white"
        elevation="8"
        style="position:fixed; bottom:0; left:0; right:0; z-index:200"
      >
        <v-btn
          v-for="item in bottomNavItems"
          :key="item.to"
          :value="item.to"
          :to="item.to"
        >
          <v-icon :icon="item.icon" />
          <span style="font-size:10px">{{ item.label }}</span>
        </v-btn>
      </v-bottom-navigation>
    </template>

    <!-- Layout senza nav (login) -->
    <template v-else>
      <v-main>
        <router-view />
      </v-main>
    </template>
  </v-app>
</template>

<script setup lang="ts">
import { computed } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { useDisplay } from 'vuetify'
import { useAuthStore } from '@/stores/auth'

const route = useRoute()
const router = useRouter()
const { mobile } = useDisplay()
const authStore = useAuthStore()

const isAuthenticated = computed(() => !!authStore.token)
const isLoginPage = computed(() => route.path === '/login')
const currentRoute = computed(() => route.path)

const navItems = computed(() => {
  const base = [
    { to: '/', icon: 'mdi-hanger', label: 'Guardaroba' },
    { to: '/today', icon: 'mdi-weather-sunny', label: 'Oggi' },
    { to: '/discovery', icon: 'mdi-auto-fix', label: 'Prova' },
    { to: '/history', icon: 'mdi-history', label: 'Storico' },
    { to: '/trips', icon: 'mdi-bag-suitcase', label: 'Valigia' },
    { to: '/settings', icon: 'mdi-cog', label: 'Impostazioni' },
  ]
  if (authStore.isAdmin()) {
    base.push({ to: '/admin/users', icon: 'mdi-account-group', label: 'Utenti' })
  }
  return base
})

const bottomNavItems = computed(() => [
  { to: '/', icon: 'mdi-hanger', label: 'Armadio' },
  { to: '/today', icon: 'mdi-weather-sunny', label: 'Oggi' },
  { to: '/discovery', icon: 'mdi-auto-fix', label: 'Prova' },
  { to: '/trips', icon: 'mdi-bag-suitcase', label: 'Valigia' },
  { to: '/settings', icon: 'mdi-cog', label: 'Info' },
])

const pageTitles: Record<string, string> = {
  '/': 'Guardaroba',
  '/today': 'Oggi',
  '/discovery': 'Prova',
  '/history': 'Storico',
  '/trips': 'Valigia',
  '/settings': 'Impostazioni',
  '/admin/users': 'Utenti',
}

const currentPageTitle = computed(() => pageTitles[route.path] ?? 'Vesto')

function logout() {
  authStore.logout()
  router.push('/login')
}
</script>
