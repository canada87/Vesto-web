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

        <!-- Step 1: credenziali -->
        <v-form v-if="!showOtp" @submit.prevent="submitCredentials">
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

        <!-- Step 2: codice OTP -->
        <div v-else>
          <div class="text-center mb-4">
            <v-icon icon="mdi-shield-key" size="48" color="primary" />
            <div class="text-body-1 font-weight-medium mt-2">Verifica identità</div>
            <div class="text-body-2 text-medium-emphasis mt-1">
              Inserisci il codice dall'app di autenticazione
            </div>
          </div>

          <v-form @submit.prevent="submitOtp">
            <v-text-field
              v-model="otpCode"
              label="Codice OTP"
              prepend-inner-icon="mdi-numeric"
              maxlength="6"
              :rules="[required]"
              autofocus
              inputmode="numeric"
            />
            <v-checkbox
              v-model="rememberDevice"
              label="Ricorda questo dispositivo"
              density="compact"
              hide-details
              class="mb-2"
            />
            <v-btn
              type="submit"
              color="primary"
              block
              size="large"
              class="mt-2"
              :loading="authStore.loading"
            >
              Verifica
            </v-btn>
            <v-btn
              variant="text"
              block
              class="mt-2"
              @click="showOtp = false; partialToken = ''"
            >
              Torna indietro
            </v-btn>
          </v-form>
        </div>
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
const showOtp = ref(false)
const otpCode = ref('')
const rememberDevice = ref(true)
const partialToken = ref('')

const required = (v: string) => !!v || 'Campo obbligatorio'

async function submitCredentials() {
  try {
    const result = await authStore.login(username.value, password.value)
    if (result.done) {
      router.push('/')
    } else {
      partialToken.value = result.partialToken
      showOtp.value = true
    }
  } catch {
    // error handled in store
  }
}

async function submitOtp() {
  try {
    await authStore.verify2FA(partialToken.value, otpCode.value, rememberDevice.value)
    router.push('/')
  } catch {
    // error handled in store
  }
}
</script>
