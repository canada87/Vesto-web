<template>
  <v-dialog :model-value="open" @update:model-value="$emit('close')" max-width="440">
    <v-card>
      <v-toolbar color="primary" density="compact">
        <v-toolbar-title>Registra outfit indossato</v-toolbar-title>
        <v-btn icon="mdi-close" @click="$emit('close')" />
      </v-toolbar>

      <v-card-text>
        <v-row dense>
          <v-col cols="12">
            <v-text-field
              v-model="form.date"
              label="Data"
              type="date"
            />
          </v-col>
          <v-col cols="12">
            <v-select
              v-model="form.occasion"
              label="Occasione"
              :items="occasionItems"
            />
          </v-col>
          <v-col cols="12">
            <v-select
              v-model="form.weather"
              label="Meteo (opzionale)"
              :items="weatherItems"
              clearable
            />
          </v-col>
          <v-col cols="12">
            <v-textarea
              v-model="form.notes"
              label="Note (opzionale)"
              rows="2"
              auto-grow
            />
          </v-col>
        </v-row>
      </v-card-text>

      <v-card-actions>
        <v-spacer />
        <v-btn variant="text" @click="$emit('close')">Annulla</v-btn>
        <v-btn color="secondary" variant="flat" :loading="loading" @click="submit">
          Salva
        </v-btn>
      </v-card-actions>
    </v-card>
  </v-dialog>
</template>

<script setup lang="ts">
import { reactive } from 'vue'
import { USAGE_TYPE_LABELS, WEATHER_LABELS, USAGE_TYPES, WEATHERS } from '@/utils/constants'

const props = defineProps<{
  open: boolean
  itemIds: string[]
  loading?: boolean
}>()

const emit = defineEmits<{
  close: []
  submit: [data: { date: string; item_ids: string[]; occasion: string; weather?: string; notes?: string }]
}>()

const today = new Date().toISOString().split('T')[0]

const form = reactive({
  date: today,
  occasion: 'both',
  weather: undefined as string | undefined,
  notes: '',
})

const occasionItems = USAGE_TYPES.map(k => ({ title: USAGE_TYPE_LABELS[k], value: k }))
const weatherItems = WEATHERS.map(k => ({ title: WEATHER_LABELS[k], value: k }))

function submit() {
  emit('submit', {
    date: new Date(form.date).toISOString(),
    item_ids: props.itemIds,
    occasion: form.occasion,
    weather: form.weather || undefined,
    notes: form.notes || undefined,
  })
}
</script>
