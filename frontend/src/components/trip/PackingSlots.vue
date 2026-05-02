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
                :color="slotColor(cat, day - 1)"
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
                v-if="getSlotItem(category, day - 1)"
                class="d-flex align-center gap-2 pa-2 rounded-lg"
                :style="slotStyle(getSlotItem(category, day - 1)!.id)"
              >
                <v-avatar size="32" rounded="sm">
                  <v-img
                    v-if="getSlotItem(category, day - 1)!.photo_url"
                    :src="getSlotItem(category, day - 1)!.photo_url"
                    cover
                  />
                  <v-icon v-else :icon="CATEGORY_ICONS[category]" size="18" />
                </v-avatar>

                <div class="flex-grow-1 min-width-0">
                  <div class="text-body-2 text-truncate">{{ getSlotItem(category, day - 1)!.name }}</div>
                  <div v-if="getSlotItem(category, day - 1)!.color" class="text-caption text-medium-emphasis">
                    {{ getSlotItem(category, day - 1)!.color }}
                  </div>
                </div>

                <v-chip
                  v-if="sharedDays(category, getSlotIndex(category, day - 1)) > 1"
                  size="x-small"
                  variant="tonal"
                  color="grey"
                  class="px-1"
                >
                  ×{{ sharedDays(category, getSlotIndex(category, day - 1)) }}gg
                </v-chip>

                <v-btn
                  :icon="isLocked(getSlotItem(category, day - 1)!.id) ? 'mdi-lock' : 'mdi-lock-open-variant'"
                  size="x-small"
                  variant="text"
                  :color="isLocked(getSlotItem(category, day - 1)!.id) ? 'primary' : 'grey'"
                  :title="isLocked(getSlotItem(category, day - 1)!.id) ? 'Sblocca (Suggerisci potrà cambiarlo)' : 'Blocca (Suggerisci non lo cambierà)'"
                  @click="$emit('toggleLock', getSlotItem(category, day - 1)!.id)"
                />

                <v-btn
                  icon="mdi-delete-outline"
                  size="x-small"
                  variant="text"
                  color="error"
                  title="Rimuovi dalla valigia"
                  @click="$emit('removeItem', getSlotItem(category, day - 1)!.id)"
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

    <div v-if="duration > 0 && items.length === 0" class="text-center text-medium-emphasis pa-6">
      <v-icon icon="mdi-bag-suitcase-outline" size="48" class="mb-2 d-block" />
      <div class="text-body-2">Valigia vuota</div>
      <div class="text-caption mt-1">Premi Suggerisci per ricevere suggerimenti automatici,<br>o scegli tu i capi giorno per giorno.</div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed } from 'vue'
import type { ClothingItem } from '@/types'
import { CATEGORY_LABELS, CATEGORY_ICONS } from '@/utils/constants'

const DISPLAY_CATEGORIES = ['top', 'bottom', 'shoes', 'outerwear', 'underwear', 'accessory', 'sportswear']

const props = defineProps<{
  items: ClothingItem[]
  lockedIds: string[]
  missing: string[]
  duration: number
}>()

defineEmits<{
  toggleLock: [id: string]
  removeItem: [id: string]
  addSlot: [payload: { category: string; dayIndex: number }]
}>()

const openPanels = ref<number[]>(Array.from({ length: Math.min(props.duration, 3) }, (_, i) => i))

const itemsByCategory = computed<Record<string, ClothingItem[]>>(() => {
  const map: Record<string, ClothingItem[]> = {}
  for (const item of props.items) {
    if (!map[item.category]) map[item.category] = []
    map[item.category].push(item)
  }
  return map
})

function getSlotIndex(category: string, dayIndex: number): number {
  const count = itemsByCategory.value[category]?.length ?? 0
  if (count === 0) return -1
  return dayIndex % count
}

function getSlotItem(category: string, dayIndex: number): ClothingItem | null {
  const items = itemsByCategory.value[category]
  if (!items?.length) return null
  return items[dayIndex % items.length]
}

function isLocked(id: string): boolean {
  return props.lockedIds.includes(id)
}

function sharedDays(category: string, itemIndex: number): number {
  const count = itemsByCategory.value[category]?.length ?? 0
  if (count === 0 || itemIndex < 0) return 0
  let days = 0
  for (let d = 0; d < props.duration; d++) {
    if (d % count === itemIndex) days++
  }
  return days
}

function slotStyle(itemId: string): string {
  const locked = isLocked(itemId)
  return locked
    ? 'background: rgba(var(--v-theme-primary), 0.08); border: 1px solid rgba(var(--v-theme-primary), 0.2)'
    : 'background: rgba(var(--v-border-color), 0.06)'
}

function slotColor(category: string, dayIndex: number): string {
  const item = getSlotItem(category, dayIndex)
  if (!item) return 'grey-lighten-3'
  return isLocked(item.id) ? 'primary' : 'success'
}
</script>
