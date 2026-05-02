<template>
  <div>
    <v-alert v-if="suggestion.missing_categories.length" type="warning" variant="tonal" class="mb-4">
      Categorie mancanti nel guardaroba:
      <strong>{{ suggestion.missing_categories.map(c => CATEGORY_LABELS[c] ?? c).join(', ') }}</strong>
    </v-alert>

    <v-row dense>
      <v-col v-for="slot in slots" :key="slot.key" cols="6" sm="3">
        <v-card :elevation="1" class="outfit-slot">
          <div class="slot-label text-caption text-medium-emphasis pa-2 pb-0">{{ slot.label }}</div>
          <template v-if="slot.item">
            <v-img
              v-if="slot.item.photo_url"
              :src="slot.item.photo_url"
              :aspect-ratio="1"
              cover
              class="bg-grey-lighten-3"
            />
            <div v-else class="d-flex align-center justify-center bg-grey-lighten-3" style="aspect-ratio:1">
              <v-icon :icon="CATEGORY_ICONS[slot.item.category]" size="40" color="grey-lighten-1" />
            </div>
            <v-card-text class="pa-2">
              <div class="text-caption font-weight-medium text-truncate">{{ slot.item.name }}</div>
              <div v-if="slot.item.color" class="text-caption text-medium-emphasis">{{ slot.item.color }}</div>
            </v-card-text>
          </template>
          <div v-else class="d-flex align-center justify-center bg-grey-lighten-4 text-medium-emphasis text-caption" style="aspect-ratio:1">
            Nessuno
          </div>
        </v-card>
      </v-col>
    </v-row>

    <div class="d-flex gap-3 mt-4 flex-wrap">
      <v-btn color="secondary" variant="flat" :loading="wearLoading" @click="$emit('wear')">
        <v-icon start>mdi-check-circle</v-icon>
        Indossa questo outfit
      </v-btn>
      <v-btn variant="outlined" color="primary" @click="$emit('regenerate')">
        <v-icon start>mdi-refresh</v-icon>
        Rigenera
      </v-btn>
    </div>
  </div>
</template>

<script setup lang="ts">
import { computed } from 'vue'
import type { OutfitSuggestionResponse } from '@/types'
import { CATEGORY_LABELS, CATEGORY_ICONS } from '@/utils/constants'

const props = defineProps<{
  suggestion: OutfitSuggestionResponse
  wearLoading?: boolean
}>()

defineEmits<{ wear: []; regenerate: [] }>()

const slots = computed(() => [
  { key: 'top', label: 'Parte sopra', item: props.suggestion.top },
  { key: 'bottom', label: 'Parte sotto', item: props.suggestion.bottom },
  { key: 'shoes', label: 'Scarpe', item: props.suggestion.shoes },
  { key: 'outerwear', label: 'Capospalla', item: props.suggestion.outerwear },
])
</script>

<style scoped>
.outfit-slot { min-height: 120px; }
</style>
