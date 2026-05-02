<template>
  <v-dialog :model-value="!!item" @update:model-value="$emit('close')" :fullscreen="mobile" max-width="600">
    <v-card v-if="item">
      <v-toolbar color="primary" density="comfortable">
        <v-toolbar-title class="text-h6">{{ item.name }}</v-toolbar-title>
        <v-spacer />
        <v-btn icon="mdi-pencil" @click="$emit('edit', item)" />
        <v-btn icon="mdi-delete" @click="confirmDelete = true" color="error" />
        <v-btn icon="mdi-close" @click="$emit('close')" />
      </v-toolbar>

      <v-img
        v-if="item.photo_url"
        :src="item.photo_url"
        max-height="280"
        cover
        class="bg-grey-lighten-3"
      />
      <div v-else class="d-flex align-center justify-center bg-grey-lighten-3" style="height:180px">
        <v-icon :icon="categoryIcon" size="72" color="grey-lighten-1" />
      </div>

      <v-card-text>
        <v-row dense>
          <v-col cols="6">
            <div class="text-caption text-medium-emphasis">Categoria</div>
            <div class="text-body-2">{{ CATEGORY_LABELS[item.category] }}</div>
          </v-col>
          <v-col cols="6">
            <div class="text-caption text-medium-emphasis">Stato</div>
            <v-chip :color="STATUS_COLORS[item.status]" size="small" variant="flat">
              {{ STATUS_LABELS[item.status] }}
            </v-chip>
          </v-col>

          <v-col cols="6">
            <div class="text-caption text-medium-emphasis">Utilizzo</div>
            <div class="text-body-2">{{ USAGE_TYPE_LABELS[item.usage_type] }}</div>
          </v-col>
          <v-col cols="6">
            <div class="text-caption text-medium-emphasis">Posizione</div>
            <div class="text-body-2">{{ item.location }}</div>
          </v-col>

          <v-col cols="6">
            <div class="text-caption text-medium-emphasis">Peso</div>
            <div class="text-body-2">{{ WEIGHT_LABELS[item.weight] }}</div>
          </v-col>
          <v-col cols="6">
            <div class="text-caption text-medium-emphasis">Condizioni</div>
            <div class="text-body-2">{{ CONDITION_LABELS[item.condition] }}</div>
          </v-col>

          <v-col cols="6" v-if="item.color">
            <div class="text-caption text-medium-emphasis">Colore</div>
            <div class="text-body-2">{{ item.color }}</div>
          </v-col>
          <v-col cols="6">
            <div class="text-caption text-medium-emphasis">Anni possesso</div>
            <div class="text-body-2">{{ item.age_years }}</div>
          </v-col>

          <v-col cols="12">
            <div class="text-caption text-medium-emphasis mb-1">Preferenza</div>
            <div class="d-flex align-center gap-1">
              <v-icon
                v-for="n in 5" :key="n"
                :icon="n <= item.like_score ? 'mdi-star' : 'mdi-star-outline'"
                size="20"
                :color="n <= item.like_score ? 'warning' : 'grey'"
              />
              <span class="text-body-2 ml-1">{{ item.like_score }}/5</span>
            </div>
          </v-col>

          <v-col cols="12">
            <div class="text-caption text-medium-emphasis mb-1">Stagioni</div>
            <div class="d-flex flex-wrap gap-1">
              <v-chip
                v-for="s in item.seasons" :key="s"
                size="small" variant="tonal" color="primary"
              >
                <v-icon :icon="SEASON_ICONS[s]" start size="14" />
                {{ SEASON_LABELS[s] }}
              </v-chip>
              <span v-if="!item.seasons.length" class="text-body-2 text-medium-emphasis">Tutte le stagioni</span>
            </div>
          </v-col>

          <v-col cols="12" v-if="item.notes">
            <div class="text-caption text-medium-emphasis">Note</div>
            <div class="text-body-2">{{ item.notes }}</div>
          </v-col>
        </v-row>
      </v-card-text>
    </v-card>

    <v-dialog v-model="confirmDelete" max-width="360">
      <v-card>
        <v-card-title>Elimina capo</v-card-title>
        <v-card-text>Sei sicuro di voler eliminare "{{ item?.name }}"? L'operazione non è reversibile.</v-card-text>
        <v-card-actions>
          <v-spacer />
          <v-btn variant="text" @click="confirmDelete = false">Annulla</v-btn>
          <v-btn color="error" variant="flat" @click="doDelete">Elimina</v-btn>
        </v-card-actions>
      </v-card>
    </v-dialog>
  </v-dialog>
</template>

<script setup lang="ts">
import { ref } from 'vue'
import { useDisplay } from 'vuetify'
import type { ClothingItem } from '@/types'
import {
  CATEGORY_LABELS, CATEGORY_ICONS, STATUS_LABELS, STATUS_COLORS,
  WEIGHT_LABELS, CONDITION_LABELS, USAGE_TYPE_LABELS, SEASON_LABELS, SEASON_ICONS,
} from '@/utils/constants'
import { computed } from 'vue'

const props = defineProps<{ item?: ClothingItem }>()
const emit = defineEmits<{ close: []; edit: [item: ClothingItem]; delete: [id: string] }>()
const { mobile } = useDisplay()
const confirmDelete = ref(false)

const categoryIcon = computed(() => CATEGORY_ICONS[props.item?.category ?? ''] ?? 'mdi-hanger')

function doDelete() {
  if (props.item) emit('delete', props.item.id)
  confirmDelete.value = false
}
</script>
