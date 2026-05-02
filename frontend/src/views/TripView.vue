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
            <div class="d-flex gap-1 align-center">
              <v-chip size="x-small" variant="tonal" color="primary">
                {{ USAGE_TYPE_LABELS[trip.trip_type] }}
              </v-chip>
              <v-chip v-if="trip.item_ids.length" size="x-small" variant="tonal" color="success">
                {{ trip.item_ids.length }} capi
              </v-chip>
              <v-btn icon="mdi-delete-outline" size="x-small" variant="text" color="error"
                @click.stop="deleteTrip(trip.id)" />
            </div>
          </div>
        </v-card-text>
      </v-card>
    </div>

    <!-- Trip detail dialog -->
    <v-dialog v-model="detailDialog" :fullscreen="mobile" max-width="640" scrollable>
      <v-card v-if="selectedTrip">
        <v-toolbar color="primary" density="comfortable">
          <v-toolbar-title>{{ selectedTrip.name }}</v-toolbar-title>
          <v-btn icon="mdi-pencil" @click="openEdit(selectedTrip)" />
          <v-btn icon="mdi-close" @click="detailDialog = false" />
        </v-toolbar>

        <v-card-text class="pa-4">
          <!-- Trip info -->
          <div class="text-body-2 text-medium-emphasis mb-4">
            <span v-if="selectedTrip.destination">📍 {{ selectedTrip.destination }}</span>
            <span v-if="selectedTrip.start_date"> · {{ formatDate(selectedTrip.start_date) }}</span>
            <span v-if="selectedTrip.end_date"> → {{ formatDate(selectedTrip.end_date) }}</span>
            <span v-if="selectedTrip.duration_only && selectedTrip.custom_duration_days">
              {{ selectedTrip.custom_duration_days }} giorni
            </span>
          </div>

          <!-- Packing controls -->
          <div class="d-flex align-center gap-3 mb-3 flex-wrap">
            <v-select
              v-model="packingSeason"
              label="Stagione"
              :items="seasonItems"
              density="compact"
              hide-details
              style="max-width: 160px"
            />
            <v-btn
              variant="tonal"
              color="secondary"
              :loading="packingLoading"
              @click="loadPacking"
            >
              <v-icon start size="16">mdi-magic-staff</v-icon>
              Suggerisci
            </v-btn>
            <v-progress-circular v-if="savingItems" size="20" width="2" indeterminate color="primary" />
          </div>

          <!-- Items loading -->
          <div v-if="packingItemsLoading" class="d-flex justify-center pa-6">
            <v-progress-circular indeterminate color="primary" />
          </div>

          <!-- Packing slots (day view) -->
          <PackingSlots
            v-else
            :items="packingItems"
            :locked-ids="lockedIds"
            :missing="packingMissing"
            :duration="tripDuration"
            @toggle-lock="toggleLock"
            @remove-item="removeItem"
            @add-slot="openPicker"
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

    <!-- Item picker dialog -->
    <v-dialog v-model="pickerDialog" max-width="400" scrollable>
      <v-card>
        <v-toolbar density="compact">
          <v-toolbar-title class="text-body-1">
            Scegli {{ CATEGORY_LABELS[pickerCategory] ?? pickerCategory }}
          </v-toolbar-title>
          <v-btn icon="mdi-close" @click="pickerDialog = false" />
        </v-toolbar>
        <v-card-text class="pa-2">
          <div v-if="pickerLoading" class="d-flex justify-center pa-4">
            <v-progress-circular indeterminate color="primary" />
          </div>
          <div v-else-if="!pickerItems.length" class="text-center text-medium-emphasis pa-4 text-body-2">
            Nessun capo di questa categoria nel guardaroba
          </div>
          <v-list v-else density="compact">
            <v-list-item
              v-for="item in pickerItems"
              :key="item.id"
              :disabled="packingItems.some(i => i.id === item.id)"
              :prepend-icon="item.photo_url ? undefined : CATEGORY_ICONS[item.category]"
              @click="addPickedItem(item)"
            >
              <template v-if="item.photo_url" #prepend>
                <v-avatar size="32" rounded="sm" class="mr-2">
                  <v-img :src="item.photo_url" cover />
                </v-avatar>
              </template>
              <template #title>
                <span class="text-body-2">{{ item.name }}</span>
              </template>
              <template #subtitle>
                <span class="text-caption">{{ item.color }}</span>
              </template>
              <template #append>
                <v-icon v-if="packingItems.some(i => i.id === item.id)" icon="mdi-check" color="success" size="16" />
              </template>
            </v-list-item>
          </v-list>
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
import PackingSlots from '@/components/trip/PackingSlots.vue'
import { apiGetTrips, apiCreateTrip, apiUpdateTrip, apiDeleteTrip, apiUpdateTripItems } from '@/api/trips'
import { apiGetItems } from '@/api/items'
import { apiSuggestPacking } from '@/api/suggestions'
import { formatDate } from '@/utils/formatters'
import { getCurrentSeason } from '@/utils/seasons'
import { USAGE_TYPE_LABELS, SEASON_LABELS, SEASONS, CATEGORY_LABELS, CATEGORY_ICONS } from '@/utils/constants'

const { mobile } = useDisplay()
const trips = ref<TripPlan[]>([])
const loading = ref(false)
const saving = ref(false)
const formDialog = ref(false)
const detailDialog = ref(false)
const selectedTrip = ref<TripPlan | undefined>()
const editingTrip = ref<TripPlan | undefined>()

// Packing state
const packingItems = ref<ClothingItem[]>([])
const lockedIds = ref<string[]>([])
const packingMissing = ref<string[]>([])
const packingLoading = ref(false)
const packingItemsLoading = ref(false)
const savingItems = ref(false)
const packingSeason = ref(getCurrentSeason())

// Item picker
const pickerDialog = ref(false)
const pickerCategory = ref('')
const pickerLoading = ref(false)
const wardrobeCache = ref<ClothingItem[]>([])

const snackbar = ref(false)
const snackMessage = ref('')
const snackColor = ref('success')

const seasonItems = SEASONS.map(k => ({ title: SEASON_LABELS[k], value: k }))

const tripDuration = computed((): number => {
  const trip = selectedTrip.value
  if (!trip) return 0
  if (trip.start_date && trip.end_date) {
    const diff = (new Date(trip.end_date).getTime() - new Date(trip.start_date).getTime()) / 86400000
    return Math.max(1, Math.round(diff))
  }
  return trip.custom_duration_days ?? 0
})

const pickerItems = computed((): ClothingItem[] =>
  wardrobeCache.value.filter(i => i.category === pickerCategory.value)
)

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

async function selectTrip(trip: TripPlan) {
  selectedTrip.value = trip
  lockedIds.value = trip.locked_item_ids ?? []
  packingMissing.value = []
  packingItems.value = []
  detailDialog.value = true

  if (trip.item_ids.length > 0) {
    packingItemsLoading.value = true
    try {
      const idSet = new Set(trip.item_ids)
      const res = await apiGetItems()
      packingItems.value = res.items.filter(i => idSet.has(i.id))
    } finally {
      packingItemsLoading.value = false
    }
  }
}

async function saveTrip(data: TripPlanCreate) {
  saving.value = true
  try {
    if (editingTrip.value) {
      const updated = await apiUpdateTrip(editingTrip.value.id, data)
      const idx = trips.value.findIndex(t => t.id === editingTrip.value!.id)
      if (idx !== -1) trips.value[idx] = updated
      formDialog.value = false
      showSnack('Viaggio aggiornato', 'success')
    } else {
      const created = await apiCreateTrip(data)
      trips.value.unshift(created)
      formDialog.value = false
      showSnack('Viaggio creato', 'success')
      // Apre direttamente il dettaglio del nuovo viaggio
      await selectTrip(created)
    }
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
  packingLoading.value = true
  try {
    const duration = tripDuration.value || 3
    const res = await apiSuggestPacking({
      trip_type: selectedTrip.value.trip_type,
      season: packingSeason.value,
      duration_days: duration,
    })
    packingMissing.value = res.missing_categories

    // Mantieni gli item locked, rimpiazza quelli non locked con i suggerimenti
    const locked = packingItems.value.filter(i => lockedIds.value.includes(i.id))
    const lockedIdSet = new Set(lockedIds.value)

    const result = [...locked]
    const resultIds = new Set(locked.map(i => i.id))

    for (const item of res.items) {
      if (!lockedIdSet.has(item.id) && !resultIds.has(item.id)) {
        result.push(item)
        resultIds.add(item.id)
      }
    }

    // Auto-lock tutto (anche i nuovi suggerimenti)
    packingItems.value = result
    lockedIds.value = result.map(i => i.id)

    await savePackingData()
  } catch {
    showSnack('Errore nel suggerimento packing', 'error')
  } finally {
    packingLoading.value = false
  }
}

async function toggleLock(itemId: string) {
  if (lockedIds.value.includes(itemId)) {
    lockedIds.value = lockedIds.value.filter(id => id !== itemId)
  } else {
    lockedIds.value = [...lockedIds.value, itemId]
  }
  await savePackingData()
}

async function removeItem(itemId: string) {
  packingItems.value = packingItems.value.filter(i => i.id !== itemId)
  lockedIds.value = lockedIds.value.filter(id => id !== itemId)
  await savePackingData()
}

async function openPicker(payload: { category: string; dayIndex: number }) {
  pickerCategory.value = payload.category
  pickerDialog.value = true
  if (wardrobeCache.value.length === 0) {
    pickerLoading.value = true
    try {
      const res = await apiGetItems()
      wardrobeCache.value = res.items
    } finally {
      pickerLoading.value = false
    }
  }
}

async function addPickedItem(item: ClothingItem) {
  if (!packingItems.value.find(i => i.id === item.id)) {
    packingItems.value = [...packingItems.value, item]
    lockedIds.value = [...lockedIds.value, item.id]
    await savePackingData()
  }
  pickerDialog.value = false
}

async function savePackingData() {
  if (!selectedTrip.value) return
  savingItems.value = true
  try {
    const updated = await apiUpdateTripItems(
      selectedTrip.value.id,
      packingItems.value.map(i => i.id),
      lockedIds.value,
    )
    const idx = trips.value.findIndex(t => t.id === selectedTrip.value!.id)
    if (idx !== -1) trips.value[idx] = updated
    selectedTrip.value = updated
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
