<template>
  <div class="pa-4">
    <div class="d-flex align-center justify-space-between mb-4">
      <div class="text-h6 font-weight-bold">Gestione utenti</div>
      <v-btn color="primary" @click="openCreate">
        <v-icon start>mdi-account-plus</v-icon>
        Nuovo utente
      </v-btn>
    </div>

    <v-card :elevation="1" rounded="xl">
      <v-list>
        <v-list-item
          v-for="user in users"
          :key="user.id"
          :subtitle="user.role === 'admin' ? 'Amministratore' : 'Utente'"
        >
          <template #prepend>
            <v-avatar :color="user.role === 'admin' ? 'primary' : 'secondary'" size="40">
              <v-icon :icon="user.role === 'admin' ? 'mdi-shield-account' : 'mdi-account'" color="white" />
            </v-avatar>
          </template>
          <template #title>
            <span class="text-body-1 font-weight-medium">{{ user.username }}</span>
            <v-chip
              v-if="!user.is_active"
              size="x-small"
              color="error"
              variant="flat"
              class="ml-2"
            >Disabilitato</v-chip>
            <v-chip
              v-if="user.id === authStore.user?.id"
              size="x-small"
              variant="tonal"
              class="ml-2"
            >Tu</v-chip>
          </template>
          <template #append>
            <div class="d-flex gap-1">
              <v-btn icon="mdi-pencil" size="small" variant="text" @click="openEdit(user)" />
              <v-btn
                v-if="user.id !== authStore.user?.id"
                :icon="user.is_active ? 'mdi-account-off' : 'mdi-account-check'"
                size="small"
                variant="text"
                :color="user.is_active ? 'warning' : 'success'"
                @click="toggleActive(user)"
              />
              <v-btn
                v-if="user.id !== authStore.user?.id"
                icon="mdi-delete-outline"
                size="small"
                variant="text"
                color="error"
                @click="confirmDeleteUser = user"
              />
            </div>
          </template>
        </v-list-item>
      </v-list>
    </v-card>

    <!-- Create / Edit dialog -->
    <v-dialog v-model="formDialog" max-width="400">
      <v-card>
        <v-toolbar color="primary" density="compact">
          <v-toolbar-title>{{ editingUser ? 'Modifica utente' : 'Nuovo utente' }}</v-toolbar-title>
          <v-btn icon="mdi-close" @click="formDialog = false" />
        </v-toolbar>
        <v-card-text class="pa-4">
          <v-form @submit.prevent="saveUser">
            <v-text-field
              v-if="!editingUser"
              v-model="form.username"
              label="Username *"
              class="mb-2"
            />
            <v-text-field
              v-model="form.password"
              :label="editingUser ? 'Nuova password (lascia vuoto per non cambiare)' : 'Password *'"
              :type="showPwd ? 'text' : 'password'"
              :append-inner-icon="showPwd ? 'mdi-eye-off' : 'mdi-eye'"
              @click:append-inner="showPwd = !showPwd"
              class="mb-2"
            />
            <v-select
              v-model="form.role"
              label="Ruolo"
              :items="[{ title: 'Utente', value: 'user' }, { title: 'Amministratore', value: 'admin' }]"
            />
            <div class="d-flex gap-3 mt-3">
              <v-spacer />
              <v-btn variant="text" @click="formDialog = false">Annulla</v-btn>
              <v-btn color="primary" type="submit" :loading="saving">Salva</v-btn>
            </div>
          </v-form>
        </v-card-text>
      </v-card>
    </v-dialog>

    <!-- Delete confirm -->
    <v-dialog v-model="!!confirmDeleteUser" max-width="360">
      <v-card>
        <v-card-title>Elimina utente</v-card-title>
        <v-card-text>
          Eliminare l'utente <strong>{{ confirmDeleteUser?.username }}</strong>? Tutti i suoi dati verranno persi.
        </v-card-text>
        <v-card-actions>
          <v-spacer />
          <v-btn variant="text" @click="confirmDeleteUser = null">Annulla</v-btn>
          <v-btn color="error" variant="flat" @click="doDeleteUser">Elimina</v-btn>
        </v-card-actions>
      </v-card>
    </v-dialog>

    <v-snackbar v-model="snackbar" :color="snackColor" timeout="3000">{{ snackMessage }}</v-snackbar>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, onMounted } from 'vue'
import { useAuthStore } from '@/stores/auth'
import type { User } from '@/types'
import { apiGetUsers, apiCreateUser, apiUpdateUser, apiDeleteUser } from '@/api/auth'

const authStore = useAuthStore()
const users = ref<User[]>([])
const formDialog = ref(false)
const saving = ref(false)
const editingUser = ref<User | null>(null)
const confirmDeleteUser = ref<User | null>(null)
const showPwd = ref(false)
const snackbar = ref(false)
const snackMessage = ref('')
const snackColor = ref('success')

const form = reactive({ username: '', password: '', role: 'user' })

onMounted(async () => { users.value = await apiGetUsers() })

function openCreate() {
  editingUser.value = null
  Object.assign(form, { username: '', password: '', role: 'user' })
  formDialog.value = true
}

function openEdit(user: User) {
  editingUser.value = user
  Object.assign(form, { username: user.username, password: '', role: user.role })
  formDialog.value = true
}

async function saveUser() {
  saving.value = true
  try {
    if (editingUser.value) {
      const payload: Record<string, any> = { role: form.role }
      if (form.password) payload.password = form.password
      const updated = await apiUpdateUser(editingUser.value.id, payload)
      const idx = users.value.findIndex(u => u.id === editingUser.value!.id)
      if (idx !== -1) users.value[idx] = updated
    } else {
      const created = await apiCreateUser({ username: form.username, password: form.password, role: form.role })
      users.value.push(created)
    }
    formDialog.value = false
    showSnack('Utente salvato', 'success')
  } catch (e: any) {
    showSnack(e.response?.data?.detail || 'Errore', 'error')
  } finally {
    saving.value = false
  }
}

async function toggleActive(user: User) {
  const updated = await apiUpdateUser(user.id, { is_active: !user.is_active })
  const idx = users.value.findIndex(u => u.id === user.id)
  if (idx !== -1) users.value[idx] = updated
}

async function doDeleteUser() {
  if (!confirmDeleteUser.value) return
  await apiDeleteUser(confirmDeleteUser.value.id)
  users.value = users.value.filter(u => u.id !== confirmDeleteUser.value!.id)
  confirmDeleteUser.value = null
  showSnack('Utente eliminato', 'success')
}

function showSnack(msg: string, color: string) {
  snackMessage.value = msg
  snackColor.value = color
  snackbar.value = true
}
</script>
