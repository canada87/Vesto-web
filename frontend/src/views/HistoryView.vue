<template>
  <div class="pa-4">
    <div class="d-flex align-center justify-space-between mb-4">
      <div class="text-h6 font-weight-bold">Storico outfit</div>
      <v-select
        v-model="days"
        :items="[{ title: '30 giorni', value: 30 }, { title: '60 giorni', value: 60 }, { title: '90 giorni', value: 90 }]"
        density="compact"
        hide-details
        style="max-width:130px"
        @update:model-value="load"
      />
    </div>

    <div v-if="loading" class="d-flex justify-center pa-8">
      <v-progress-circular indeterminate color="primary" />
    </div>

    <div v-else-if="!logs.length" class="text-center pa-8 text-medium-emphasis">
      <v-icon icon="mdi-calendar-blank" size="64" />
      <div class="mt-2">Nessun outfit registrato</div>
    </div>

    <div v-else class="d-flex flex-column gap-3">
      <OutfitCard
        v-for="log in logs"
        :key="log.id"
        :log="log"
        :all-items="allItems"
        @delete="deleteLog"
      />
    </div>

    <v-snackbar v-model="snackbar" timeout="3000">{{ snackMessage }}</v-snackbar>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'
import type { OutfitLog, ClothingItem } from '@/types'
import OutfitCard from '@/components/outfit/OutfitCard.vue'
import { apiGetLogs, apiDeleteLog } from '@/api/outfitLogs'
import { apiGetItems } from '@/api/items'

const logs = ref<OutfitLog[]>([])
const allItems = ref<ClothingItem[]>([])
const loading = ref(false)
const days = ref(90)
const snackbar = ref(false)
const snackMessage = ref('')

async function load() {
  loading.value = true
  try {
    const [logsRes, itemsRes] = await Promise.all([
      apiGetLogs(days.value),
      apiGetItems(),
    ])
    logs.value = logsRes
    allItems.value = itemsRes.items
  } finally {
    loading.value = false
  }
}

onMounted(load)

async function deleteLog(id: string) {
  await apiDeleteLog(id)
  logs.value = logs.value.filter(l => l.id !== id)
  snackMessage.value = 'Log eliminato'
  snackbar.value = true
}
</script>
