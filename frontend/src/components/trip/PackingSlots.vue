<template>
  <div>
    <v-alert v-if="missing.length" type="warning" variant="tonal" density="compact" class="mb-3">
      Categorie mancanti nel guardaroba:
      <strong>{{ missing.map(c => CATEGORY_LABELS[c] ?? c).join(', ') }}</strong>
    </v-alert>

    <div v-if="duration === 0" class="text-center text-medium-emphasis pa-4 text-body-2">
      Nessuna durata specificata per il viaggio
    </div>

    <v-expansion-panels v-else v-model="openPanels" multiple variant="accordion">
      <v-expansion-panel
        v-for="day in duration"
        :key="day"
        :value="day - 1"
        rounded="lg"
        class="mb-1"
      >
        <v-expansion-panel-title class="py-2 px-3">
          <div class="d-flex align-center gap-3 w-100">
            <span class="text-subtitle-2 font-weight-bold">Giorno {{ day }}</span>
            <div class="d-flex gap-1">
              <v-icon
                v-for="cat in DISPLAY_CATEGORIES"
                :key="cat"
                :icon="CATEGORY_ICONS[cat]"
                size="13"
                :color="daySlotColor(cat, day - 1)"
              />
            </div>
          </div>
        </v-expansion-panel-title>

        <v-expansion-panel-text class="pa-0">
          <div class="px-3 pb-3">
            <div v-for="category in DISPLAY_CATEGORIES" :key="category" class="mt-2">
              <div class="d-flex align-center gap-1 mb-1">
                <v-icon :icon="CATEGORY_ICONS[category]" size="14" color="medium-emphasis" />
                <span class="text-caption text-medium-emphasis">{{ CATEGORY_LABELS[category] }}</span>
              </div>

              <!-- Filled slot -->
              <div
                v-if="getSlot(day - 1, category)"
                class="d-flex align-center gap-2 pa-2 rounded-lg"
                :style="slotStyle(day - 1, category)"
              >
                <v-avatar size="32" rounded="sm">
                  <v-img
                    v-if="getItem(getSlot(day - 1, category)!.item_id)?.photo_url"
                    :src="getItem(getSlot(day - 1, category)!.item_id)!.photo_url"
                    cover
                  />
                  <v-icon v-else :icon="CATEGORY_ICONS[category]" size="18" />
                </v-avatar>

                <div class="flex-grow-1 min-width-0">
                  <div class="text-body-2 text-truncate">
                    {{ getItem(getSlot(day - 1, category)!.item_id)?.name ?? '—' }}
                  </div>
                  <div
                    v-if="getItem(getSlot(day - 1, category)!.item_id)?.color"
                    class="text-caption text-medium-emphasis"
                  >
                    {{ getItem(getSlot(day - 1, category)!.item_id)!.color }}
                  </div>
                </div>

                <v-btn
                  icon="mdi-shuffle"
                  size="x-small"
                  variant="text"
                  color="grey"
                  title="Suggerisci un'alternativa per questo slot"
                  @click="$emit('regenerateSlot', { day: day - 1, category })"
                />

                <v-btn
                  icon="mdi-delete-outline"
                  size="x-small"
                  variant="text"
                  color="error"
                  title="Rimuovi dalla valigia"
                  @click="$emit('removeSlot', { day: day - 1, category })"
                />
              </div>

              <!-- Empty slot -->
              <v-btn
                v-else
                variant="outlined"
                color="grey-lighten-1"
                size="small"
                block
                class="justify-start"
                style="border-style: dashed; border-color: rgba(var(--v-border-color), 0.3)"
                @click="$emit('addSlot', { category, dayIndex: day - 1 })"
              >
                <v-icon start size="16">mdi-plus</v-icon>
                <span class="text-caption">Scegli {{ CATEGORY_LABELS[category].toLowerCase() }}</span>
              </v-btn>
            </div>
          </div>
        </v-expansion-panel-text>
      </v-expansion-panel>
    </v-expansion-panels>

    <div v-if="duration > 0 && slots.length === 0" class="text-center text-medium-emphasis pa-6">
      <v-icon icon="mdi-bag-suitcase-outline" size="48" class="mb-2 d-block" />
      <div class="text-body-2">Valigia vuota</div>
      <div class="text-caption mt-1">
        Premi Suggerisci per ricevere suggerimenti automatici,<br>
        o scegli tu i capi giorno per giorno.
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed } from 'vue'
import type { ClothingItem, TripSlot } from '@/types'
import { CATEGORY_LABELS, CATEGORY_ICONS } from '@/utils/constants'

const DISPLAY_CATEGORIES = ['top', 'bottom', 'shoes', 'outerwear', 'underwear', 'accessory', 'sportswear']

const props = defineProps<{
  slots: TripSlot[]
  items: ClothingItem[]
  missing: string[]
  duration: number
}>()

defineEmits<{
  regenerateSlot: [payload: { day: number; category: string }]
  removeSlot: [payload: { day: number; category: string }]
  addSlot: [payload: { category: string; dayIndex: number }]
}>()

const openPanels = ref<number[]>(Array.from({ length: Math.min(props.duration, 3) }, (_, i) => i))

const itemsById = computed<Record<string, ClothingItem>>(() => {
  const map: Record<string, ClothingItem> = {}
  for (const item of props.items) {
    map[item.id] = item
  }
  return map
})

function getSlot(day: number, category: string): TripSlot | null {
  return props.slots.find(s => s.day === day && s.category === category) ?? null
}

function getItem(itemId: string): ClothingItem | null {
  return itemsById.value[itemId] ?? null
}

function slotStyle(_day: number, _category: string): string {
  return 'background: rgba(var(--v-border-color), 0.06)'
}

function daySlotColor(category: string, day: number): string {
  return getSlot(day, category) ? 'success' : 'grey-lighten-3'
}
</script>
