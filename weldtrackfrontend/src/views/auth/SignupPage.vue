<script setup lang="ts">
import { computed, onBeforeUnmount, onMounted, reactive, ref } from 'vue'
import { useAuthStore } from '../../stores/auth'
import { onBeforeRouteLeave, useRouter } from 'vue-router'

const authStore = useAuthStore()
const router = useRouter()

function getApiErrorMessage(error: unknown, fallback: string) {
  const maybeAxiosError = error as {
    response?: { data?: { message?: string }; statusText?: string }
  }

  if (maybeAxiosError?.response) {
    return maybeAxiosError.response.data?.message || maybeAxiosError.response.statusText || fallback
  }

  if (error instanceof Error) {
    return error.message
  }

  return fallback
}

const form = reactive({ email: '', password: '', confirm: '', code: '' })
const step = ref(1)
const countdown = ref(60)
const codeTimer = ref<number | null>(null)
const cooldownSeconds = 60
const signupError = ref('')
const isSubmittingSignup = ref(false)
const isVerifyingCode = ref(false)
const isProgressActive = computed(() => step.value >= 2)
const leaveWarningMessage = 'Progress data will be deleted if you go back. Leave this page?'

const stepClass = computed(() => ({
  one: step.value >= 1 ? 'bg-green-500 text-white border-green-500' : 'bg-white text-gray-700 border-gray-300',
  two: step.value >= 2 ? 'bg-green-500 text-white border-green-500' : 'bg-white text-gray-700 border-gray-300',
}))

function startCodeTimer() {
  if (codeTimer.value !== null) return

  countdown.value = cooldownSeconds
  step.value = 2

  codeTimer.value = window.setInterval(() => {
    countdown.value -= 1
    if (countdown.value <= 0 && codeTimer.value !== null) {
      window.clearInterval(codeTimer.value)
      codeTimer.value = null
    }
  }, 1000)
}

async function resendCode() {
  signupError.value = ''
  isSubmittingSignup.value = true

  try {
    const response = await authStore.signup({
      email: form.email,
      password: form.password,
    })
    if (response.success !== true) {
      throw new Error('Request failed.')
    }
    startCodeTimer()
  } catch (error) {
    signupError.value = getApiErrorMessage(error, 'Unable to resend verification code.')
  } finally {
    isSubmittingSignup.value = false
  }
}

async function submitSignup() {
  if (!form.email || !form.password || !form.confirm) {
    signupError.value = 'Email, password, and confirmation are required.'
    return
  }

  if (form.password !== form.confirm) {
    signupError.value = 'Passwords do not match.'
    return
  }

  signupError.value = ''
  isSubmittingSignup.value = true

  try {
    const response = await authStore.signup({
      email: form.email,
      password: form.password,
    })
    if (response.success !== true) {
      throw new Error('Request failed.')
    }
    
    // Code sent successfully, move to verification step
    step.value = 2
    startCodeTimer()
  } catch (error) {
    signupError.value = getApiErrorMessage(error, 'Unable to create account.')
  } finally {
    isSubmittingSignup.value = false
  }
}

async function submitCode() {
  if (!form.code) {
    signupError.value = 'Verification code is required.'
    return
  }

  signupError.value = ''
  isVerifyingCode.value = true

  try {
    const response = await authStore.confirmVerificationCode({
      email: form.email,
      code: form.code,
      password: form.password,
      action: 'createaccount',
    })
    
    // If response has user data, it means account was created and we're logged in
    if (response.user || response.access_token) {
      authStore.setSession({
        token: response.access_token || '',
        email: response.user?.email || form.email,
        role: response.user?.role || 'customer',
      })
      router.replace('/dashboard')
    } else if (response.success) {
      throw new Error('Request failed.')
    }
  } catch (error) {
    signupError.value = getApiErrorMessage(error, 'Unable to verify signup code.')
  } finally {
    isVerifyingCode.value = false
  }
}

function handleBeforeUnload(event: BeforeUnloadEvent) {
  if (!isProgressActive.value) return

  event.preventDefault()
  event.returnValue = leaveWarningMessage
}

onBeforeRouteLeave(() => {
  if (!isProgressActive.value) return true

  return window.confirm(leaveWarningMessage)
})

onMounted(() => {
  window.addEventListener('beforeunload', handleBeforeUnload)
})

onBeforeUnmount(() => {
  window.removeEventListener('beforeunload', handleBeforeUnload)

  if (codeTimer.value !== null) {
    window.clearInterval(codeTimer.value)
  }
})
</script>

<template>
  <div class="min-h-screen bg-linear-to-br from-slate-900 via-blue-900 to-slate-800 p-4 text-slate-900 sm:p-6">
    <div class="mx-auto flex min-h-[calc(100vh-2rem)] w-full max-w-xl items-center justify-center sm:min-h-[calc(100vh-3rem)]">
      <div class="w-full rounded-3xl border border-white/10 bg-white p-6 shadow-2xl shadow-slate-950/40 sm:p-8">
        <div class="mb-8 text-center">
          <div class="mb-4 inline-flex h-16 w-16 items-center justify-center rounded-2xl bg-blue-600 shadow-lg shadow-blue-900/30">
            <svg class="h-9 w-9 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path
                stroke-linecap="round"
                stroke-linejoin="round"
                stroke-width="2"
                d="M13 10V3L4 14h7v7l9-11h-7z"
              />
            </svg>
          </div>

          <h1 class="mb-1 text-3xl font-extrabold tracking-tight text-gray-900">WeldTrack</h1>
          <p class="text-sm text-gray-500 sm:text-base">Inventory Management System</p>
        </div>

        <div class="mb-7">
          <div class="flex items-start">
            <div class="flex flex-1 justify-center">
              <div class="flex flex-col items-center text-center">
                <div :class="['flex h-9 w-9 items-center justify-center rounded-full border-2 text-sm font-semibold', stepClass.one]">1</div>
                <div class="mt-2 text-xs text-gray-600">Account</div>
              </div>
            </div>

            <div class="mt-4.5 flex flex-1 items-center">
              <div class="h-1 w-full rounded-full bg-gray-200">
                <div class="h-1 rounded-full bg-green-500" :style="{ width: step >= 2 ? '100%' : '50%' }"></div>
              </div>
            </div>

            <div class="flex flex-1 justify-center">
              <div class="flex flex-col items-center text-center">
                <div :class="['flex h-9 w-9 items-center justify-center rounded-full border-2 text-sm font-semibold', stepClass.two]">2</div>
                <div class="mt-2 text-xs text-gray-600">Verify</div>
              </div>
            </div>
          </div>
        </div>

        <form class="space-y-6" @submit.prevent="submitSignup">
          <div v-if="signupError" class="rounded-xl border border-red-200 bg-red-50 px-4 py-3 text-sm text-red-700">
            {{ signupError }}
          </div>

          <div v-if="step === 1">
            <label class="mb-1 block text-sm font-semibold text-gray-700" for="email">Email</label>
            <input
              id="email"
              v-model="form.email"
              type="email"
              placeholder="you@example.com"
              class="mt-1 w-full rounded-xl border border-gray-300 bg-gray-50 px-4 py-3 outline-none transition focus:border-blue-500 focus:ring-2 focus:ring-blue-200"
            />
          </div>

          <div v-if="step === 1">
            <label class="mb-1 block text-sm font-semibold text-gray-700" for="password">Password</label>
            <input
              id="password"
              v-model="form.password"
              type="password"
              placeholder="Create password"
              class="mt-1 w-full rounded-xl border border-gray-300 bg-gray-50 px-4 py-3 outline-none transition focus:border-blue-500 focus:ring-2 focus:ring-blue-200"
            />
          </div>

          <div v-if="step === 1">
            <label class="mb-1 block text-sm font-semibold text-gray-700" for="confirm">Confirm Password</label>
            <input
              id="confirm"
              v-model="form.confirm"
              type="password"
              placeholder="Confirm password"
              class="mt-1 w-full rounded-xl border border-gray-300 bg-gray-50 px-4 py-3 outline-none transition focus:border-blue-500 focus:ring-2 focus:ring-blue-200"
            />
          </div>

          <button
            v-if="step === 1"
            type="submit"
            class="h-12 w-full rounded-xl bg-blue-600 font-semibold text-white transition-colors hover:bg-blue-700 disabled:cursor-not-allowed disabled:bg-blue-400"
            :disabled="isSubmittingSignup"
          >
            {{ isSubmittingSignup ? 'Creating Account...' : 'Create Account' }}
          </button>

          <div v-else class="space-y-4">
            <div class="rounded-xl bg-blue-50 p-4 text-sm text-gray-700">
              <p class="font-medium text-gray-900">Email: {{ form.email || 'you@example.com' }}</p>
              <p class="mt-1">We sent a code to your email. Enter it below.</p>
              <p v-if="codeTimer !== null" class="mt-2 font-medium text-blue-700">You can request a new code in {{ countdown }}s</p>
            </div>

            <div>
              <label class="mb-1 block text-sm font-semibold text-gray-700" for="code">Verification Code</label>
              <input
                id="code"
                v-model="form.code"
                type="text"
                placeholder="Enter code"
                class="mt-1 w-full rounded-xl border border-gray-300 bg-gray-50 px-4 py-3 outline-none transition focus:border-blue-500 focus:ring-2 focus:ring-blue-200"
              />
            </div>

            <button
              type="button"
              class="h-12 w-full rounded-xl bg-blue-600 font-semibold text-white transition-colors hover:bg-blue-700 disabled:cursor-not-allowed disabled:bg-blue-400"
              :disabled="isVerifyingCode"
              @click="submitCode"
            >
              {{ isVerifyingCode ? 'Verifying...' : 'Verify Email' }}
            </button>

            <button
              type="button"
              class="h-12 w-full rounded-xl border border-blue-600 font-semibold text-blue-600 transition-colors hover:bg-blue-50 disabled:cursor-not-allowed disabled:border-blue-300 disabled:text-blue-300"
              :disabled="codeTimer !== null || isSubmittingSignup"
              @click="resendCode"
            >
              <span v-if="codeTimer === null">Resend Code</span>
              <span v-else>Resend in {{ countdown }}s</span>
            </button>
          </div>
        </form>

        <div v-if="step === 1" class="mt-8 border-t border-gray-200 pt-6">
          <div class="flex flex-col items-center justify-center gap-2 text-center sm:flex-row sm:whitespace-nowrap">
            <p class="m-0 text-gray-600">Already have an account?</p>
            <RouterLink replace to="/login" class="whitespace-nowrap font-semibold text-green-600 hover:underline">Login</RouterLink>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>
