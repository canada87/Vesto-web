<template>
  <v-card
    class="item-card"
    :elevation="2"
    @click="$emit('click', item)"
    style="cursor: pointer;"
  >
    <v-img
      v-if="item.photo_url"
      :src="item.photo_url"
      :aspect-ratio="1"
      cover
      class="bg-grey-lighten-3"
    >
      <template #error>
        <div class="d-flex align-center justify-center fill-height bg-grey-lighten-3">
          <v-icon :icon="categoryIcon" size="48" color="grey-lighten-1" />
        </div>
      </template>
    </v-img>
    <div v-else class="d-flex align-center justify-center bg-grey-lighten-3" style="aspect-ratio:1">
      <v-icon :icon="categoryIcon" size="48" color="grey-lighten-1" />
    </div>

    <v-card-text class="pa-3">
      <div class="text-subtitle-2 font-weight-bold text-truncate">{{ item.name }}</div>
      <div class="d-flex align-center justify-space-between mt-1">
        <v-chip :color="statusColor" size="x-small" variant="flat">
          {{ statusLabel }}
        </v-chip>
        <div class="d-flex align-center gap-0">
          <v-icon
            v-for="n in 5"
            :key="n"
            :icon="n <= item.like_score ? 'mdi-star' : 'mdi-star-outline'"
            size="12"
            :color="n <= item.like_score ? 'warning' : 'grey'"
          />
        </div>
      </div>
      <div class="text-caption text-medium-emphasis mt-1 text-truncate">
        {{ categoryLabel }} · {{ item.location }}
      </div>
    </v-card-text>
  </v-card>
</template>

<script setup lang="ts">
import type { ClothingItem } from '@/types'
import { CATEGORY_LABELS, CATEGORY_ICONS, STATUS_LABELS, STATUS_COLORS } from '@/utils/constants'
import { computed } from 'vue'

const props = defineProps<{ item: ClothingItem }>()
defineEmits<{ click: [item: ClothingItem] }>()

const categoryLabel = computed(() => CATEGORY_LABELS[props.item.category] ?? props.item.category)
const categoryIcon = computed(() => CATEGORY_ICONS[props.item.category] ?? 'mdi-hanger')
const statusLabel = computed(() => STATUS_LABELS[props.item.status] ?? props.item.status)
const statusColor = computed(() => STATUS_COLORS[props.item.status] ?? 'default')
</script>
