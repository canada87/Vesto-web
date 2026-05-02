<template>
  <div class="pa-4">
    <div class="text-h6 font-weight-bold mb-4">Outfit del giorno</div>

    <!-- Selettori -->
    <v-card :elevation="1" class="mb-4 pa-4" rounded="xl">
      <div class="d-flex flex-wrap gap-3">
        <div>
          <div class="text-caption text-medium-emphasis mb-1">Occasione</div>
          <v-btn-toggle v-model="occasion" mandatory color="primary" density="compact">
            <v-btn value="work" size="small">Lavoro</v-btn>
            <v-btn value="personal" size="small">Personale</v-btn>
            <v-btn value="both" size="small">Entrambi</v-btn>
          </v-btn-toggle>
        </div>
        <div>
          <div class="text-caption text-medium-emphasis mb-1">Meteo</div>
          <v-btn-toggle v-model="weather" color="secondary" density="compact">
            <v-btn v-for="w in WEATHERS" :key="w" :value="w" size="small">
              <v-icon :icon="WEATHER_ICONS[w]" size="16" />
            </v-btn>
          </v-btn-toggle>
        </div>
      </div>
      <v-btn color="primary" class="mt-4" :loading="loading" @click="getSuggestion">
        <v-icon start>mdi-magic-staff</v-icon>
        Suggerisci outfit
      </v-btn>
    </v-card>

    <!-- Risultato -->
    <template v-if="suggestion">
      <OutfitSuggestion
        :suggestion="suggestion"
        :wear-loading="wearLoading"
        @wear="logDialog = true"
        @regenerate="getSuggestion"
      />
    </template>

    <div v-else-if="!loading" class="text-center pa-8 text-medium-emphasis">
      <v-icon icon="mdi-weather-sunny" size="64" />
      <div class="mt-2">Premi "Suggerisci outfit" per iniziare</div>
    </div>

    <LogOutfitDialog
      :open="logDialog"
      :item-ids="outfitItemIds"
      :loading="wearLoading"
      @close="logDialog = false"
      @submit="logOutfit"
    />

    <v-snackbar v-model="snackbar" :color="snackColor" timeout="3000">{{ snackMessage }}</v-snackbar>
  </div>
</template>

<script setup lang="ts">
import { ref, computed } from 'vue'
import type { OutfitSuggestionResponse } from '@/types'
import OutfitSuggestion from '@/components/outfit/OutfitSuggestion.vue'
import LogOutfitDialog from '@/components/outfit/LogOutfitDialog.vue'
import { apiSuggestOutfit } from '@/api/suggestions'
import { apiCreateLog } from '@/api/outfitLogs'
import { WEATHERS, WEATHER_ICONS } from '@/utils/constants'
import { getCurrentSeason } from '@/utils/seasons'

const occasion = ref('both')
const weather = ref<string | undefined>(undefined)
const suggestion = ref<OutfitSuggestionResponse | null>(null)
const loading = ref(false)
const logDialog = ref(false)
const wearLoading = ref(false)
const snackbar = ref(false)
const snackMessage = ref('')
const snackColor = ref('success')

const outfitItemIds = computed(() => {
  if (!suggestion.value) return []
  return [
    suggestion.value.top?.id,
    suggestion.value.bottom?.id,
    suggestion.value.shoes?.id,
    suggestion.value.outerwear?.id,
    ...suggestion.value.accessories.map(a => a.id),
  ].filter(Boolean) as string[]
})

async function getSuggestion() {
  loading.value = true
  try {
    suggestion.value = await apiSuggestOutfit({
      occasion: occasion.value,
      weather: weather.value || undefined,
      season: getCurrentSeason(),
      novelty: false,
    })
  } catch {
    showSnack('Errore nel caricamento del suggerimento', 'error')
  } finally {
    loading.value = false
  }
}

async function logOutfit(data: any) {
  wearLoading.value = true
  try {
    await apiCreateLog(data)
    logDialog.value = false
    showSnack('Outfit registrato!', 'success')
  } catch {
    showSnack('Errore nel salvataggio', 'error')
  } finally {
    wearLoading.value = false
  }
}

function showSnack(msg: string, color: string) {
  snackMessage.value = msg
  snackColor.value = color
  snackbar.value = true
}
</script>
