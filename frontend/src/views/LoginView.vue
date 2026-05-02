<template>
  <v-container class="d-flex align-center justify-center" style="min-height:100vh">
    <v-card width="380" :elevation="4" rounded="xl">
      <v-card-text class="pa-8">
        <div class="text-center mb-6">
          <v-icon icon="mdi-hanger" size="64" color="primary" />
          <div class="text-h4 font-weight-bold text-primary mt-2">Vesto</div>
          <div class="text-body-2 text-medium-emphasis">Il tuo guardaroba intelligente</div>
        </div>

        <v-alert
          v-if="authStore.error"
          type="error"
          variant="tonal"
          class="mb-4"
          closable
          @click:close="authStore.error = null"
        >
          {{ authStore.error }}
        </v-alert>

        <v-form @submit.prevent="login">
          <v-text-field
            v-model="username"
            label="Username"
            prepend-inner-icon="mdi-account"
            class="mb-2"
            :rules="[required]"
            autofocus
          />
          <v-text-field
            v-model="password"
            label="Password"
            prepend-inner-icon="mdi-lock"
            :type="showPassword ? 'text' : 'password'"
            :append-inner-icon="showPassword ? 'mdi-eye-off' : 'mdi-eye'"
            @click:append-inner="showPassword = !showPassword"
            :rules="[required]"
          />
          <v-btn
            type="submit"
            color="primary"
            block
            size="large"
            class="mt-4"
            :loading="authStore.loading"
          >
            Accedi
          </v-btn>
        </v-form>
      </v-card-text>
    </v-card>
  </v-container>
</template>

<script setup lang="ts">
import { ref } from 'vue'
import { useRouter } from 'vue-router'
import { useAuthStore } from '@/stores/auth'

const authStore = useAuthStore()
const router = useRouter()
const username = ref('')
const password = ref('')
const showPassword = ref(false)

const required = (v: string) => !!v || 'Campo obbligatorio'

async function login() {
  try {
    await authStore.login(username.value, password.value)
    router.push('/')
  } catch {
    // error handled in store
  }
}
</script>
