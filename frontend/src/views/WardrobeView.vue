<template>
  <div>
    <!-- Filtri -->
    <div class="pa-4 pb-2">
      <v-text-field
        v-model="search"
        placeholder="Cerca capi..."
        prepend-inner-icon="mdi-magnify"
        clearable
        hide-details
        density="compact"
        class="mb-3"
      />
      <div class="d-flex flex-wrap gap-2">
        <v-select
          v-model="filters.category"
          label="Categoria"
          :items="[{ title: 'Tutte', value: '' }, ...categoryItems]"
          density="compact"
          hide-details
          style="min-width:140px; max-width:160px"
          clearable
        />
        <v-select
          v-model="filters.season"
          label="Stagione"
          :items="[{ title: 'Tutte', value: '' }, ...seasonItems]"
          density="compact"
          hide-details
          style="min-width:130px; max-width:150px"
          clearable
        />
        <v-select
          v-model="filters.status"
          label="Stato"
          :items="[{ title: 'Tutti', value: '' }, ...statusItems]"
          density="compact"
          hide-details
          style="min-width:130px; max-width:150px"
          clearable
        />
      </div>
    </div>

    <div class="px-4 pb-2 text-caption text-medium-emphasis">
      {{ filteredItems.length }} capi
    </div>

    <!-- Loading -->
    <div v-if="loading" class="d-flex justify-center pa-8">
      <v-progress-circular indeterminate color="primary" />
    </div>

    <!-- Grid -->
    <v-row v-else dense class="pa-3">
      <v-col
        v-for="item in filteredItems"
        :key="item.id"
        cols="6"
        sm="4"
        md="3"
        lg="2"
      >
        <ItemCard :item="item" @click="selectedItem = item" />
      </v-col>
      <v-col v-if="!filteredItems.length" cols="12">
        <div class="text-center pa-8 text-medium-emphasis">
          <v-icon icon="mdi-wardrobe-outline" size="64" />
          <div class="mt-2">Nessun capo trovato</div>
        </div>
      </v-col>
    </v-row>

    <!-- FAB -->
    <v-btn
      icon="mdi-plus"
      color="secondary"
      size="large"
      position="fixed"
      style="bottom:80px; right:20px; z-index:100"
      :style="{ bottom: mobile ? '76px' : '24px' }"
      elevation="4"
      @click="openAddDialog"
    />

    <!-- Detail dialog -->
    <ItemDetail
      :item="selectedItem"
      @close="selectedItem = undefined"
      @edit="openEditDialog"
      @delete="deleteItem"
    />

    <!-- Add/Edit dialog -->
    <v-dialog v-model="formDialog" :fullscreen="mobile" max-width="560">
      <v-card>
        <v-toolbar color="primary" density="comfortable">
          <v-toolbar-title>{{ editingItem ? 'Modifica capo' : 'Aggiungi capo' }}</v-toolbar-title>
          <v-btn icon="mdi-close" @click="formDialog = false" />
        </v-toolbar>
        <v-card-text class="pa-4">
          <ItemForm
            :item="editingItem"
            :locations="locations"
            :loading="saving"
            @submit="saveItem"
            @cancel="formDialog = false"
          />
        </v-card-text>
      </v-card>
    </v-dialog>

    <v-snackbar v-model="snackbar" :color="snackColor" timeout="3000">
      {{ snackMessage }}
    </v-snackbar>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'
import { useDisplay } from 'vuetify'
import type { ClothingItem } from '@/types'
import ItemCard from '@/components/items/ItemCard.vue'
import ItemDetail from '@/components/items/ItemDetail.vue'
import ItemForm from '@/components/items/ItemForm.vue'
import { apiGetItems, apiCreateItem, apiUpdateItem, apiDeleteItem, apiUploadPhoto } from '@/api/items'
import { apiGetLocations } from '@/api/settings'
import { CATEGORY_LABELS, SEASON_LABELS, STATUS_LABELS, CATEGORIES, SEASONS, STATUSES } from '@/utils/constants'

const { mobile } = useDisplay()

const items = ref<ClothingItem[]>([])
const locations = ref<string[]>(['Casa'])
const loading = ref(false)
const saving = ref(false)
const selectedItem = ref<ClothingItem | undefined>()
const editingItem = ref<ClothingItem | undefined>()
const formDialog = ref(false)
const snackbar = ref(false)
const snackMessage = ref('')
const snackColor = ref('success')

const search = ref('')
const filters = ref({ category: '', season: '', status: '' })

const categoryItems = CATEGORIES.map(k => ({ title: CATEGORY_LABELS[k], value: k }))
const seasonItems = SEASONS.map(k => ({ title: SEASON_LABELS[k], value: k }))
const statusItems = STATUSES.map(k => ({ title: STATUS_LABELS[k], value: k }))

const filteredItems = computed(() => {
  let list = items.value
  if (search.value) {
    const q = search.value.toLowerCase()
    list = list.filter(i => i.name.toLowerCase().includes(q) || i.color?.toLowerCase().includes(q))
  }
  if (filters.value.category) list = list.filter(i => i.category === filters.value.category)
  if (filters.value.season) list = list.filter(i => i.seasons.includes(filters.value.season as any))
  if (filters.value.status) list = list.filter(i => i.status === filters.value.status)
  return list
})

async function loadData() {
  loading.value = true
  try {
    const [res, locs] = await Promise.all([apiGetItems(), apiGetLocations()])
    items.value = res.items
    locations.value = locs
  } finally {
    loading.value = false
  }
}

onMounted(loadData)

function openAddDialog() {
  editingItem.value = undefined
  formDialog.value = true
}

function openEditDialog(item: ClothingItem) {
  editingItem.value = item
  selectedItem.value = undefined
  formDialog.value = true
}

async function saveItem(formData: FormData) {
  saving.value = true
  try {
    if (editingItem.value) {
      const data: Record<string, any> = {}
      formData.forEach((v, k) => { data[k] = v })
      data.seasons = JSON.parse(data.seasons as string)
      data.age_years = parseFloat(data.age_years as string)
      data.like_score = parseInt(data.like_score as string)
      const updated = await apiUpdateItem(editingItem.value.id, data)
      const idx = items.value.findIndex(i => i.id === editingItem.value!.id)
      if (idx !== -1) items.value[idx] = updated

      const photoFile = formData.get('photo') as File | null
      if (photoFile && photoFile.size > 0) {
        const withPhoto = await apiUploadPhoto(updated.id, photoFile)
        if (idx !== -1) items.value[idx] = withPhoto
      }
    } else {
      const created = await apiCreateItem(formData)
      items.value.unshift(created)
    }
    formDialog.value = false
    showSnack('Capo salvato', 'success')
  } catch {
    showSnack('Errore nel salvataggio', 'error')
  } finally {
    saving.value = false
  }
}

async function deleteItem(id: string) {
  try {
    await apiDeleteItem(id)
    items.value = items.value.filter(i => i.id !== id)
    selectedItem.value = undefined
    showSnack('Capo eliminato', 'success')
  } catch {
    showSnack('Errore nell\'eliminazione', 'error')
  }
}

function showSnack(msg: string, color: string) {
  snackMessage.value = msg
  snackColor.value = color
  snackbar.value = true
}
</script>
