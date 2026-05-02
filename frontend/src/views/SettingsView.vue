<template>
  <div class="pa-4">
    <div class="text-h6 font-weight-bold mb-4">Impostazioni</div>

    <!-- Statistiche -->
    <v-card :elevation="1" rounded="xl" class="mb-4">
      <v-card-title class="text-subtitle-1 pa-4 pb-2">Statistiche</v-card-title>
      <v-card-text>
        <v-row>
          <v-col cols="4" class="text-center">
            <div class="text-h4 font-weight-bold text-primary">{{ stats?.total_items ?? '—' }}</div>
            <div class="text-caption text-medium-emphasis">Capi</div>
          </v-col>
          <v-col cols="4" class="text-center">
            <div class="text-h4 font-weight-bold text-secondary">{{ stats?.total_logs ?? '—' }}</div>
            <div class="text-caption text-medium-emphasis">Outfit</div>
          </v-col>
          <v-col cols="4" class="text-center">
            <div class="text-h4 font-weight-bold" style="color:#F4B942">{{ stats?.total_trips ?? '—' }}</div>
            <div class="text-caption text-medium-emphasis">Viaggi</div>
          </v-col>
        </v-row>
      </v-card-text>
    </v-card>

    <!-- Locazioni -->
    <v-card :elevation="1" rounded="xl" class="mb-4">
      <v-card-title class="text-subtitle-1 pa-4 pb-2">Locazioni</v-card-title>
      <v-list density="compact">
        <v-list-item
          v-for="loc in locations"
          :key="loc"
          :title="loc"
          prepend-icon="mdi-map-marker"
        >
          <template #append>
            <v-btn icon="mdi-delete-outline" size="x-small" variant="text" color="error"
              @click="removeLocation(loc)" />
          </template>
        </v-list-item>
      </v-list>
      <v-card-text class="pt-0">
        <div class="d-flex gap-2">
          <v-text-field
            v-model="newLocation"
            placeholder="Aggiungi locazione"
            density="compact"
            hide-details
            @keyup.enter="addLocation"
          />
          <v-btn icon="mdi-plus" color="secondary" @click="addLocation" :disabled="!newLocation.trim()" />
        </div>
      </v-card-text>
    </v-card>

    <!-- Backup -->
    <v-card :elevation="1" rounded="xl" class="mb-4">
      <v-card-title class="text-subtitle-1 pa-4 pb-2">Backup dati</v-card-title>
      <v-card-text>
        <div class="d-flex flex-wrap gap-3">
          <v-btn color="primary" variant="outlined" :loading="exportLoading" @click="exportBackup">
            <v-icon start>mdi-download</v-icon>
            Esporta JSON
          </v-btn>
          <v-btn color="primary" variant="outlined" @click="importInput?.click()">
            <v-icon start>mdi-upload</v-icon>
            Importa JSON
          </v-btn>
          <input ref="importInput" type="file" accept=".json" style="display:none" @change="importBackup" />
        </div>
        <v-alert v-if="importSuccess" type="success" variant="tonal" class="mt-3">
          Backup importato con successo
        </v-alert>
      </v-card-text>
    </v-card>

    <!-- Dati di test -->
    <v-card :elevation="1" rounded="xl" class="mb-4">
      <v-card-title class="text-subtitle-1 pa-4 pb-2">Dati di esempio</v-card-title>
      <v-card-text>
        <div class="text-body-2 text-medium-emphasis mb-3">
          Carica 19 capi di esempio nel guardaroba (utile per testare l'app).
        </div>
        <v-btn color="warning" variant="tonal" :loading="seedLoading" @click="seedData">
          <v-icon start>mdi-database-plus</v-icon>
          Carica capi di esempio
        </v-btn>
      </v-card-text>
    </v-card>

    <!-- Account -->
    <v-card :elevation="1" rounded="xl">
      <v-card-title class="text-subtitle-1 pa-4 pb-2">Account</v-card-title>
      <v-card-text>
        <div class="text-body-2 mb-1">
          <v-icon start size="16">mdi-account</v-icon>
          <strong>{{ authStore.user?.username }}</strong>
          <v-chip class="ml-2" size="x-small" :color="authStore.isAdmin() ? 'primary' : 'default'">
            {{ authStore.isAdmin() ? 'Admin' : 'Utente' }}
          </v-chip>
        </div>
        <v-btn
          v-if="authStore.isAdmin()"
          variant="tonal"
          color="primary"
          size="small"
          class="mt-2 mr-2"
          @click="$router.push('/admin/users')"
        >
          <v-icon start size="16">mdi-account-group</v-icon>
          Gestione utenti
        </v-btn>
        <v-btn color="error" variant="tonal" size="small" class="mt-2" @click="logout">
          <v-icon start size="16">mdi-logout</v-icon>
          Esci
        </v-btn>
      </v-card-text>
    </v-card>

    <v-snackbar v-model="snackbar" :color="snackColor" timeout="3000">{{ snackMessage }}</v-snackbar>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { useAuthStore } from '@/stores/auth'
import type { Stats } from '@/types'
import {
  apiGetStats, apiGetLocations, apiAddLocation, apiDeleteLocation,
  apiExportBackup, apiImportBackup, apiSeedTestData,
} from '@/api/settings'

const router = useRouter()
const authStore = useAuthStore()

const stats = ref<Stats | null>(null)
const locations = ref<string[]>([])
const newLocation = ref('')
const exportLoading = ref(false)
const importInput = ref<HTMLInputElement | null>(null)
const importSuccess = ref(false)
const seedLoading = ref(false)
const snackbar = ref(false)
const snackMessage = ref('')
const snackColor = ref('success')

onMounted(async () => {
  const [s, l] = await Promise.all([apiGetStats(), apiGetLocations()])
  stats.value = s
  locations.value = l
})

async function addLocation() {
  const name = newLocation.value.trim()
  if (!name) return
  locations.value = await apiAddLocation(name)
  newLocation.value = ''
}

async function removeLocation(name: string) {
  locations.value = await apiDeleteLocation(name)
}

async function exportBackup() {
  exportLoading.value = true
  try {
    await apiExportBackup()
  } finally {
    exportLoading.value = false
  }
}

async function importBackup(event: Event) {
  const file = (event.target as HTMLInputElement).files?.[0]
  if (!file) return
  try {
    await apiImportBackup(file)
    importSuccess.value = true
    showSnack('Backup importato con successo', 'success')
  } catch {
    showSnack('Errore nell\'importazione', 'error')
  }
}

async function seedData() {
  seedLoading.value = true
  try {
    await apiSeedTestData()
    showSnack('19 capi di esempio aggiunti!', 'success')
    stats.value = await apiGetStats()
  } catch {
    showSnack('Errore nel caricamento dati', 'error')
  } finally {
    seedLoading.value = false
  }
}

function logout() {
  authStore.logout()
  router.push('/login')
}

function showSnack(msg: string, color: string) {
  snackMessage.value = msg
  snackColor.value = color
  snackbar.value = true
}
</script>
