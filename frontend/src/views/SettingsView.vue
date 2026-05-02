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
    <v-card :elevation="1" rounded="xl" class="mb-4">
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

    <!-- Autenticazione a due fattori -->
    <v-card :elevation="1" rounded="xl">
      <v-card-title class="text-subtitle-1 pa-4 pb-2">
        Autenticazione a due fattori
        <v-chip
          class="ml-2"
          size="x-small"
          :color="authStore.user?.totp_enabled ? 'success' : 'default'"
          variant="flat"
        >
          {{ authStore.user?.totp_enabled ? 'Attiva' : 'Non attiva' }}
        </v-chip>
      </v-card-title>
      <v-card-text>
        <!-- Attiva 2FA -->
        <template v-if="!authStore.user?.totp_enabled">
          <div class="text-body-2 text-medium-emphasis mb-3">
            Proteggi il tuo account con un'app di autenticazione (Google Authenticator, Authy, ecc.).
          </div>
          <div v-if="!qrCode">
            <v-btn color="primary" variant="tonal" :loading="twoFaLoading" @click="startSetup2FA">
              <v-icon start>mdi-shield-key</v-icon>
              Configura 2FA
            </v-btn>
          </div>
          <div v-else>
            <div class="text-body-2 mb-2">1. Scansiona il QR code con la tua app:</div>
            <v-img :src="`data:image/png;base64,${qrCode}`" max-width="200" class="mb-3 rounded" />
            <div class="text-caption text-medium-emphasis mb-3">
              Codice manuale: <strong>{{ totpSecret }}</strong>
            </div>
            <div class="text-body-2 mb-2">2. Inserisci il codice generato per confermare:</div>
            <div class="d-flex gap-2 align-center flex-wrap">
              <v-text-field
                v-model="enableOtpCode"
                label="Codice OTP"
                density="compact"
                hide-details
                maxlength="6"
                inputmode="numeric"
                style="max-width:160px"
              />
              <v-btn color="success" :loading="twoFaLoading" @click="confirmEnable2FA">Attiva</v-btn>
              <v-btn variant="text" @click="cancelSetup">Annulla</v-btn>
            </div>
          </div>
        </template>

        <!-- Disabilita 2FA -->
        <template v-else>
          <div class="text-body-2 text-medium-emphasis mb-3">
            Il 2FA è attivo. Per disabilitarlo inserisci un codice OTP valido.
          </div>
          <div class="d-flex gap-2 align-center flex-wrap">
            <v-text-field
              v-model="disableOtpCode"
              label="Codice OTP"
              density="compact"
              hide-details
              maxlength="6"
              inputmode="numeric"
              style="max-width:160px"
            />
            <v-btn color="error" variant="tonal" :loading="twoFaLoading" @click="confirmDisable2FA">
              Disabilita
            </v-btn>
          </div>
        </template>
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
import { apiSetup2FA, apiEnable2FA, apiDisable2FA } from '@/api/auth'

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

const twoFaLoading = ref(false)
const qrCode = ref('')
const totpSecret = ref('')
const enableOtpCode = ref('')
const disableOtpCode = ref('')

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

async function startSetup2FA() {
  twoFaLoading.value = true
  try {
    const data = await apiSetup2FA()
    qrCode.value = data.qr_code
    totpSecret.value = data.secret
  } catch {
    showSnack('Errore nel setup 2FA', 'error')
  } finally {
    twoFaLoading.value = false
  }
}

async function confirmEnable2FA() {
  twoFaLoading.value = true
  try {
    const data = await apiEnable2FA(enableOtpCode.value)
    localStorage.setItem('vesto_trusted_device', data.trusted_device_token)
    await authStore.fetchMe()
    qrCode.value = ''
    totpSecret.value = ''
    enableOtpCode.value = ''
    showSnack('2FA attivato', 'success')
  } catch (e: any) {
    showSnack(e.response?.data?.detail || 'Codice OTP non valido', 'error')
  } finally {
    twoFaLoading.value = false
  }
}

function cancelSetup() {
  qrCode.value = ''
  totpSecret.value = ''
  enableOtpCode.value = ''
}

async function confirmDisable2FA() {
  twoFaLoading.value = true
  try {
    await apiDisable2FA(disableOtpCode.value)
    await authStore.fetchMe()
    disableOtpCode.value = ''
    showSnack('2FA disabilitato', 'success')
  } catch (e: any) {
    showSnack(e.response?.data?.detail || 'Codice OTP non valido', 'error')
  } finally {
    twoFaLoading.value = false
  }
}

function showSnack(msg: string, color: string) {
  snackMessage.value = msg
  snackColor.value = color
  snackbar.value = true
}
</script>
