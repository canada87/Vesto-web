<template>
  <v-form ref="formRef" @submit.prevent="submit">
    <v-row dense>
      <v-col cols="12">
        <v-text-field
          v-model="form.name"
          label="Nome capo *"
          :rules="[required]"
        />
      </v-col>

      <v-col cols="12" sm="6">
        <v-select
          v-model="form.category"
          label="Categoria *"
          :items="categoryItems"
          :rules="[required]"
        />
      </v-col>

      <v-col cols="12" sm="6">
        <v-select
          v-model="form.usage_type"
          label="Utilizzo"
          :items="usageTypeItems"
        />
      </v-col>

      <v-col cols="12" sm="6">
        <v-select
          v-model="form.weight"
          label="Peso"
          :items="weightItems"
        />
      </v-col>

      <v-col cols="12" sm="6">
        <v-select
          v-model="form.condition"
          label="Condizioni"
          :items="conditionItems"
        />
      </v-col>

      <v-col cols="12" sm="6">
        <v-select
          v-model="form.status"
          label="Stato"
          :items="statusItems"
        />
      </v-col>

      <v-col cols="12" sm="6">
        <v-select
          v-model="form.location"
          label="Posizione"
          :items="locations"
        />
      </v-col>

      <v-col cols="12">
        <div class="text-caption text-medium-emphasis mb-2">Stagioni</div>
        <div class="d-flex flex-wrap gap-2">
          <v-chip
            v-for="s in SEASONS"
            :key="s"
            :color="form.seasons.includes(s) ? 'primary' : 'default'"
            :variant="form.seasons.includes(s) ? 'flat' : 'outlined'"
            @click="toggleSeason(s)"
            style="cursor:pointer"
          >
            <v-icon :icon="SEASON_ICONS[s]" start size="16" />
            {{ SEASON_LABELS[s] }}
          </v-chip>
        </div>
      </v-col>

      <v-col cols="12" sm="6">
        <v-text-field
          v-model="form.color"
          label="Colore"
        />
      </v-col>

      <v-col cols="12" sm="6">
        <v-text-field
          v-model.number="form.age_years"
          label="Anni possesso"
          type="number"
          min="0"
          step="0.5"
        />
      </v-col>

      <v-col cols="12">
        <div class="text-caption text-medium-emphasis mb-1">Preferenza ({{ form.like_score }}/5)</div>
        <v-slider
          v-model="form.like_score"
          :min="1"
          :max="5"
          :step="1"
          color="warning"
          track-color="grey-lighten-3"
          show-ticks="always"
          thumb-label
        />
      </v-col>

      <v-col cols="12">
        <v-textarea
          v-model="form.notes"
          label="Note"
          rows="2"
          auto-grow
        />
      </v-col>

      <v-col cols="12">
        <v-file-input
          v-model="photoFile"
          label="Foto (opzionale)"
          accept="image/*"
          prepend-icon="mdi-camera"
          variant="outlined"
          density="comfortable"
          clearable
          @update:model-value="onPhotoChange"
        />
        <v-img
          v-if="photoPreview || form.photo_url"
          :src="photoPreview || form.photo_url"
          max-height="200"
          class="mt-2 rounded-lg"
          cover
        />
      </v-col>
    </v-row>

    <div class="d-flex gap-3 mt-4">
      <v-btn variant="text" @click="$emit('cancel')">Annulla</v-btn>
      <v-spacer />
      <v-btn color="primary" type="submit" :loading="loading">
        {{ item ? 'Salva' : 'Aggiungi' }}
      </v-btn>
    </div>
  </v-form>
</template>

<script setup lang="ts">
import { ref, reactive, watch } from 'vue'
import type { ClothingItem } from '@/types'
import {
  CATEGORY_LABELS, WEIGHT_LABELS, CONDITION_LABELS,
  USAGE_TYPE_LABELS, STATUS_LABELS, SEASON_LABELS, SEASON_ICONS, SEASONS,
  CATEGORIES, WEIGHTS, CONDITIONS, USAGE_TYPES, STATUSES,
} from '@/utils/constants'

const props = defineProps<{
  item?: ClothingItem
  locations: string[]
  loading?: boolean
}>()

const emit = defineEmits<{
  submit: [formData: FormData]
  cancel: []
}>()

const formRef = ref()
const photoFile = ref<File[]>([])
const photoPreview = ref<string | null>(null)

const form = reactive({
  name: '',
  category: 'top',
  age_years: 0,
  weight: 'medium',
  condition: 'good',
  like_score: 3,
  usage_type: 'both',
  seasons: [] as string[],
  status: 'inWardrobe',
  location: 'Casa',
  color: '',
  notes: '',
  photo_url: '',
})

watch(() => props.item, (val) => {
  if (val) {
    Object.assign(form, {
      name: val.name,
      category: val.category,
      age_years: val.age_years,
      weight: val.weight,
      condition: val.condition,
      like_score: val.like_score,
      usage_type: val.usage_type,
      seasons: [...val.seasons],
      status: val.status,
      location: val.location,
      color: val.color ?? '',
      notes: val.notes ?? '',
      photo_url: val.photo_url ?? '',
    })
  }
}, { immediate: true })

const required = (v: string) => !!v || 'Campo obbligatorio'

const categoryItems = CATEGORIES.map(k => ({ title: CATEGORY_LABELS[k], value: k }))
const weightItems = WEIGHTS.map(k => ({ title: WEIGHT_LABELS[k], value: k }))
const conditionItems = CONDITIONS.map(k => ({ title: CONDITION_LABELS[k], value: k }))
const usageTypeItems = USAGE_TYPES.map(k => ({ title: USAGE_TYPE_LABELS[k], value: k }))
const statusItems = STATUSES.map(k => ({ title: STATUS_LABELS[k], value: k }))

function toggleSeason(s: string) {
  const idx = form.seasons.indexOf(s)
  if (idx === -1) form.seasons.push(s)
  else form.seasons.splice(idx, 1)
}

function onPhotoChange(files: File | File[]) {
  const file = Array.isArray(files) ? files[0] : files
  if (file) {
    const reader = new FileReader()
    reader.onload = (e) => { photoPreview.value = e.target?.result as string }
    reader.readAsDataURL(file)
  } else {
    photoPreview.value = null
  }
}

async function submit() {
  const { valid } = await formRef.value.validate()
  if (!valid) return

  const fd = new FormData()
  fd.append('name', form.name)
  fd.append('category', form.category)
  fd.append('age_years', String(form.age_years))
  fd.append('weight', form.weight)
  fd.append('condition', form.condition)
  fd.append('like_score', String(form.like_score))
  fd.append('usage_type', form.usage_type)
  fd.append('seasons', JSON.stringify(form.seasons))
  fd.append('status', form.status)
  fd.append('location', form.location)
  if (form.color) fd.append('color', form.color)
  if (form.notes) fd.append('notes', form.notes)
  const file = Array.isArray(photoFile.value) ? photoFile.value[0] : photoFile.value
  if (file) fd.append('photo', file)

  emit('submit', fd)
}
</script>
