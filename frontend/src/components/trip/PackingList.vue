<template>
  <div>
    <v-alert v-if="missing.length" type="warning" variant="tonal" class="mb-3">
      Categorie mancanti: <strong>{{ missing.map(c => CATEGORY_LABELS[c] ?? c).join(', ') }}</strong>
    </v-alert>

    <v-list lines="two">
      <v-list-item
        v-for="item in items"
        :key="item.id"
        :prepend-icon="CATEGORY_ICONS[item.category]"
        :subtitle="CATEGORY_LABELS[item.category]"
      >
        <template #title>
          <span class="text-body-2 font-weight-medium">{{ item.name }}</span>
        </template>
        <template #append>
          <v-checkbox
            :model-value="selected.includes(item.id)"
            @update:model-value="toggle(item.id)"
            color="secondary"
            hide-details
          />
        </template>
      </v-list-item>
    </v-list>

    <v-btn
      v-if="changed"
      color="primary"
      variant="flat"
      class="mt-3"
      :loading="saving"
      @click="$emit('save', selected)"
    >
      Salva selezione
    </v-btn>
  </div>
</template>

<script setup lang="ts">
import { ref, watch, computed } from 'vue'
import type { ClothingItem } from '@/types'
import { CATEGORY_LABELS, CATEGORY_ICONS } from '@/utils/constants'

const props = defineProps<{
  items: ClothingItem[]
  missing: string[]
  initialSelected: string[]
  saving?: boolean
}>()

const emit = defineEmits<{ save: [ids: string[]] }>()

const selected = ref<string[]>([...props.initialSelected])

watch(() => props.initialSelected, (val) => { selected.value = [...val] })

const changed = computed(() => {
  const a = [...selected.value].sort().join()
  const b = [...props.initialSelected].sort().join()
  return a !== b
})

function toggle(id: string) {
  const idx = selected.value.indexOf(id)
  if (idx === -1) selected.value.push(id)
  else selected.value.splice(idx, 1)
}
</script>
