<template>
  <v-form ref="formRef" @submit.prevent="submit">
    <v-row dense>
      <v-col cols="12">
        <v-text-field v-model="form.name" label="Nome viaggio *" :rules="[required]" />
      </v-col>
      <v-col cols="12">
        <v-text-field v-model="form.destination" label="Destinazione" />
      </v-col>
      <v-col cols="12">
        <v-select v-model="form.trip_type" label="Tipo viaggio" :items="usageTypeItems" />
      </v-col>

      <v-col cols="12">
        <v-switch v-model="form.duration_only" label="Specifica solo la durata (senza date)" color="primary" />
      </v-col>

      <template v-if="form.duration_only">
        <v-col cols="12">
          <v-text-field
            v-model.number="form.custom_duration_days"
            label="Durata (giorni)"
            type="number"
            min="1"
          />
        </v-col>
      </template>
      <template v-else>
        <v-col cols="12" sm="6">
          <v-text-field v-model="form.start_date" label="Data partenza" type="date" />
        </v-col>
        <v-col cols="12" sm="6">
          <v-text-field v-model="form.end_date" label="Data ritorno" type="date" />
        </v-col>
      </template>
    </v-row>

    <div class="d-flex gap-3 mt-4">
      <v-btn variant="text" @click="$emit('cancel')">Annulla</v-btn>
      <v-spacer />
      <v-btn color="primary" type="submit" :loading="loading">
        {{ trip ? 'Salva' : 'Crea viaggio' }}
      </v-btn>
    </div>
  </v-form>
</template>

<script setup lang="ts">
import { ref, reactive, watch } from 'vue'
import type { TripPlan, TripPlanCreate } from '@/types'
import { USAGE_TYPE_LABELS, USAGE_TYPES } from '@/utils/constants'

const props = defineProps<{
  trip?: TripPlan
  loading?: boolean
}>()

const emit = defineEmits<{
  submit: [data: TripPlanCreate]
  cancel: []
}>()

const formRef = ref()
const form = reactive<TripPlanCreate & { start_date?: string; end_date?: string }>({
  name: '',
  destination: '',
  trip_type: 'both',
  duration_only: false,
  custom_duration_days: undefined,
  start_date: undefined,
  end_date: undefined,
})

watch(() => props.trip, (val) => {
  if (val) Object.assign(form, {
    name: val.name,
    destination: val.destination ?? '',
    trip_type: val.trip_type,
    duration_only: val.duration_only,
    custom_duration_days: val.custom_duration_days,
    start_date: val.start_date?.split('T')[0],
    end_date: val.end_date?.split('T')[0],
  })
}, { immediate: true })

const required = (v: string) => !!v || 'Campo obbligatorio'
const usageTypeItems = USAGE_TYPES.map(k => ({ title: USAGE_TYPE_LABELS[k], value: k }))

async function submit() {
  const { valid } = await formRef.value.validate()
  if (!valid) return
  emit('submit', {
    name: form.name,
    destination: form.destination || undefined,
    trip_type: form.trip_type,
    duration_only: form.duration_only,
    custom_duration_days: form.custom_duration_days,
    start_date: form.start_date ? new Date(form.start_date).toISOString() : undefined,
    end_date: form.end_date ? new Date(form.end_date).toISOString() : undefined,
  })
}
</script>
