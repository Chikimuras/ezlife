<script setup lang="ts">
import { useRouter } from 'vue-router'
import { GoogleLogin } from 'vue3-google-login'
import type { CallbackTypes } from 'vue3-google-login'
import { useAuthStore } from '@/stores/auth'

const router = useRouter()
const authStore = useAuthStore()

const callback: CallbackTypes.CredentialCallback = async (response) => {
  if (response.credential) {
    try {
      await authStore.loginWithGoogle(response.credential)
      await router.push('/')
    } catch (error) {
      console.error('Login failed', error)
      // Handle error (show notification, etc.)
    }
  }
}
</script>

<template>
  <div class="flex min-h-screen items-center justify-center bg-gray-50 px-4 py-12 sm:px-6 lg:px-8">
    <div class="w-full max-w-md space-y-8">
      <div>
        <h2 class="mt-6 text-center text-3xl font-bold tracking-tight text-gray-900">
          Sign in to your account
        </h2>
      </div>
      <div class="flex justify-center">
        <GoogleLogin :callback="callback" />
      </div>
    </div>
  </div>
</template>
