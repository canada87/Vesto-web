<template>
  <v-card :elevation="1">
    <v-card-text class="pa-3">
      <div class="d-flex align-center justify-space-between">
        <div>
          <div class="text-subtitle-2 font-weight-bold">{{ formatDate(log.date) }}</div>
          <div class="text-caption text-medium-emphasis">
            {{ USAGE_TYPE_LABELS[log.occasion] }}
            <span v-if="log.weather"> · {{ WEATHER_LABELS[log.weather] }}</span>
          </div>
        </div>
        <v-btn icon="mdi-delete-outline" size="small" variant="text" color="error" @click="$emit('delete', log.id)" />
      </div>

      <div class="d-flex flex-wrap gap-1 mt-2">
        <v-chip
          v-for="item in resolvedItems"
          :key="item.id"
          size="x-small"
          variant="tonal"
          color="primary"
        >
          <v-icon :icon="CATEGORY_ICONS[item.category]" start size="12" />
          {{ item.name }}
        </v-chip>
        <v-chip v-if="unknownCount > 0" size="x-small" variant="tonal">+{{ unknownCount }}</v-chip>
      </div>

      <div v-if="log.notes" class="text-caption text-medium-emphasis mt-1 font-italic">
        "{{ log.notes }}"
      </div>
    </v-card-text>
  </v-card>
</template>

<script setup lang="ts">
import { computed } from 'vue'
import type { OutfitLog, ClothingItem } from '@/types'
import { CATEGORY_ICONS, USAGE_TYPE_LABELS, WEATHER_LABELS } from '@/utils/constants'
import { formatDate } from '@/utils/formatters'

const props = defineProps<{
  log: OutfitLog
  allItems: ClothingItem[]
}>()

defineEmits<{ delete: [id: string] }>()

const resolvedItems = computed(() =>
  props.log.item_ids
    .map(id => props.allItems.find(i => i.id === id))
    .filter(Boolean) as ClothingItem[]
)

const unknownCount = computed(() =>
  props.log.item_ids.filter(id => !props.allItems.find(i => i.id === id)).length
)
</script>
