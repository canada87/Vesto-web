<template>
  <div class="pa-4">
    <div class="d-flex align-center justify-space-between mb-4">
      <div class="text-h6 font-weight-bold">Pianificatore viaggi</div>
      <v-btn icon="mdi-plus" color="secondary" @click="openAdd" />
    </div>

    <div v-if="loading" class="d-flex justify-center pa-8">
      <v-progress-circular indeterminate color="primary" />
    </div>

    <div v-else-if="!trips.length" class="text-center pa-8 text-medium-emphasis">
      <v-icon icon="mdi-bag-suitcase-outline" size="64" />
      <div class="mt-2">Nessun viaggio pianificato</div>
      <v-btn color="secondary" variant="flat" class="mt-3" @click="openAdd">Crea viaggio</v-btn>
    </div>

    <div v-else class="d-flex flex-column gap-3">
      <v-card
        v-for="trip in trips"
        :key="trip.id"
        :elevation="1"
        rounded="xl"
        @click="selectTrip(trip)"
        style="cursor:pointer"
      >
        <v-card-text>
          <div class="d-flex align-center justify-space-between">
            <div>
              <div class="text-subtitle-1 font-weight-bold">{{ trip.name }}</div>
              <div class="text-caption text-medium-emphasis">
                {{ trip.destination || 'Destinazione non specificata' }}
                <span v-if="trip.start_date"> · {{ formatDate(trip.start_date) }}</span>
              </div>
            </div>
            <div class="d-flex gap-1">
              <v-chip size="x-small" variant="tonal" color="primary">
                {{ USAGE_TYPE_LABELS[trip.trip_type] }}
              </v-chip>
              <v-btn icon="mdi-delete-outline" size="x-small" variant="text" color="error"
                @click.stop="deleteTrip(trip.id)" />
            </div>
          </div>
        </v-card-text>
      </v-card>
    </div>

    <!-- Trip detail dialog -->
    <v-dialog v-model="detailDialog" :fullscreen="mobile" max-width="640">
      <v-card v-if="selectedTrip">
        <v-toolbar color="primary" density="comfortable">
          <v-toolbar-title>{{ selectedTrip.name }}</v-toolbar-title>
          <v-btn icon="mdi-pencil" @click="openEdit(selectedTrip)" />
          <v-btn icon="mdi-close" @click="detailDialog = false" />
        </v-toolbar>
        <v-card-text>
          <div class="text-body-2 text-medium-emphasis mb-4">
            <span v-if="selectedTrip.destination">📍 {{ selectedTrip.destination }}</span>
            <span v-if="selectedTrip.start_date"> · {{ formatDate(selectedTrip.start_date) }}</span>
            <span v-if="selectedTrip.end_date"> → {{ formatDate(selectedTrip.end_date) }}</span>
            <span v-if="selectedTrip.duration_only && selectedTrip.custom_duration_days">
              {{ selectedTrip.custom_duration_days }} giorni
            </span>
          </div>

          <!-- Packing suggestion -->
          <div class="d-flex align-center gap-2 mb-3">
            <div class="text-subtitle-2 font-weight-bold">Lista packing</div>
            <v-btn size="small" variant="tonal" color="secondary" :loading="packingLoading" @click="loadPacking">
              <v-icon start size="16">mdi-magic-staff</v-icon>
              Suggerisci
            </v-btn>
          </div>

          <v-select
            v-if="showPackingControls"
            v-model="packingSeason"
            label="Stagione del viaggio"
            :items="seasonItems"
            density="compact"
            class="mb-3"
          />

          <PackingList
            v-if="packingItems !== null"
            :items="packingItems"
            :missing="packingMissing"
            :initial-selected="selectedTrip.item_ids"
            :saving="savingItems"
            @save="saveItemIds"
          />
        </v-card-text>
      </v-card>
    </v-dialog>

    <!-- Add/Edit form dialog -->
    <v-dialog v-model="formDialog" :fullscreen="mobile" max-width="480">
      <v-card>
        <v-toolbar color="primary" density="comfortable">
          <v-toolbar-title>{{ editingTrip ? 'Modifica viaggio' : 'Nuovo viaggio' }}</v-toolbar-title>
          <v-btn icon="mdi-close" @click="formDialog = false" />
        </v-toolbar>
        <v-card-text class="pa-4">
          <TripForm
            :trip="editingTrip"
            :loading="saving"
            @submit="saveTrip"
            @cancel="formDialog = false"
          />
        </v-card-text>
      </v-card>
    </v-dialog>

    <v-snackbar v-model="snackbar" :color="snackColor" timeout="3000">{{ snackMessage }}</v-snackbar>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'
import { useDisplay } from 'vuetify'
import type { TripPlan, TripPlanCreate, ClothingItem } from '@/types'
import TripForm from '@/components/trip/TripForm.vue'
import PackingList from '@/components/trip/PackingList.vue'
import { apiGetTrips, apiCreateTrip, apiUpdateTrip, apiDeleteTrip, apiUpdateTripItems } from '@/api/trips'
import { apiSuggestPacking } from '@/api/suggestions'
import { formatDate } from '@/utils/formatters'
import { getCurrentSeason } from '@/utils/seasons'
import { USAGE_TYPE_LABELS, SEASON_LABELS, SEASONS } from '@/utils/constants'

const { mobile } = useDisplay()
const trips = ref<TripPlan[]>([])
const loading = ref(false)
const saving = ref(false)
const formDialog = ref(false)
const detailDialog = ref(false)
const selectedTrip = ref<TripPlan | undefined>()
const editingTrip = ref<TripPlan | undefined>()
const packingItems = ref<ClothingItem[] | null>(null)
const packingMissing = ref<string[]>([])
const packingLoading = ref(false)
const savingItems = ref(false)
const packingSeason = ref(getCurrentSeason())
const showPackingControls = ref(false)
const snackbar = ref(false)
const snackMessage = ref('')
const snackColor = ref('success')

const seasonItems = SEASONS.map(k => ({ title: SEASON_LABELS[k], value: k }))

onMounted(async () => {
  loading.value = true
  trips.value = await apiGetTrips()
  loading.value = false
})

function openAdd() {
  editingTrip.value = undefined
  formDialog.value = true
}

function openEdit(trip: TripPlan) {
  editingTrip.value = trip
  detailDialog.value = false
  formDialog.value = true
}

function selectTrip(trip: TripPlan) {
  selectedTrip.value = trip
  packingItems.value = null
  packingMissing.value = []
  showPackingControls.value = false
  detailDialog.value = true
}

async function saveTrip(data: TripPlanCreate) {
  saving.value = true
  try {
    if (editingTrip.value) {
      const updated = await apiUpdateTrip(editingTrip.value.id, data)
      const idx = trips.value.findIndex(t => t.id === editingTrip.value!.id)
      if (idx !== -1) trips.value[idx] = updated
    } else {
      const created = await apiCreateTrip(data)
      trips.value.unshift(created)
    }
    formDialog.value = false
    showSnack('Viaggio salvato', 'success')
  } catch {
    showSnack('Errore nel salvataggio', 'error')
  } finally {
    saving.value = false
  }
}

async function deleteTrip(id: string) {
  await apiDeleteTrip(id)
  trips.value = trips.value.filter(t => t.id !== id)
  showSnack('Viaggio eliminato', 'success')
}

async function loadPacking() {
  if (!selectedTrip.value) return
  showPackingControls.value = true
  packingLoading.value = true
  try {
    const trip = selectedTrip.value
    let duration = trip.custom_duration_days ?? 3
    if (trip.start_date && trip.end_date) {
      const diff = (new Date(trip.end_date).getTime() - new Date(trip.start_date).getTime()) / 86400000
      duration = Math.max(1, Math.round(diff))
    }
    const res = await apiSuggestPacking({
      trip_type: trip.trip_type,
      season: packingSeason.value,
      duration_days: duration,
    })
    packingItems.value = res.items
    packingMissing.value = res.missing_categories
  } catch {
    showSnack('Errore nel suggerimento packing', 'error')
  } finally {
    packingLoading.value = false
  }
}

async function saveItemIds(ids: string[]) {
  if (!selectedTrip.value) return
  savingItems.value = true
  try {
    const updated = await apiUpdateTripItems(selectedTrip.value.id, ids)
    const idx = trips.value.findIndex(t => t.id === selectedTrip.value!.id)
    if (idx !== -1) trips.value[idx] = updated
    selectedTrip.value = updated
    showSnack('Lista aggiornata', 'success')
  } finally {
    savingItems.value = false
  }
}

function showSnack(msg: string, color: string) {
  snackMessage.value = msg
  snackColor.value = color
  snackbar.value = true
}
</script>
