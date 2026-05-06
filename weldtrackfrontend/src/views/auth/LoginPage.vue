<script setup lang="ts">
import { computed, onBeforeUnmount, onMounted, reactive, ref } from 'vue'
import { onBeforeRouteLeave, useRouter } from 'vue-router'
import { useAuthStore } from '../../stores/auth'

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

const loginForm = reactive({ email: '', password: '' })
const forgotPassword = ref(false)
const resetStep = ref(1)
const resetForm = reactive({ email: '', code: '', newPassword: '', confirmPassword: '' })
const countdown = ref(60)
const codeTimer = ref<number | null>(null)
const cooldownSeconds = 60
const loginError = ref('')
const resetError = ref('')
const isSubmittingLogin = ref(false)
const isSendingResetEmail = ref(false)
const isVerifyingResetCode = ref(false)
const isSavingNewPassword = ref(false)

const isResetActive = computed(() => forgotPassword.value && resetStep.value >= 2)
const leaveWarningMessage = 'Progress data will be deleted if you go back. Leave this page?'

const resetStepClass = computed(() => ({
  one: resetStep.value >= 1 ? 'bg-green-500 text-white border-green-500' : 'bg-white text-gray-700 border-gray-300',
  two: resetStep.value >= 2 ? 'bg-green-500 text-white border-green-500' : 'bg-white text-gray-700 border-gray-300',
  three: resetStep.value >= 3 ? 'bg-green-500 text-white border-green-500' : 'bg-white text-gray-700 border-gray-300',
}))

async function submitLogin() {
  if (!loginForm.email || !loginForm.password) {
    loginError.value = 'Email and password are required.'
    return
  }

  loginError.value = ''
  isSubmittingLogin.value = true

  try {
    await authStore.login({
      email: loginForm.email,
      password: loginForm.password,
    })

    if (authStore.role === 'admin') {
      router.replace('/dashboard/admin')
    } else if (authStore.role === 'staff') {
      router.replace('/dashboard/staff')
    } else {
      router.replace('/dashboard')
    }
  } catch (error) {
    loginError.value = getApiErrorMessage(error, 'Unable to sign in. Please try again.')
  } finally {
    isSubmittingLogin.value = false
  }
}

function openForgotPassword() {
  forgotPassword.value = true
  resetStep.value = 1
  resetForm.email = loginForm.email
  resetForm.code = ''
  resetForm.newPassword = ''
  resetForm.confirmPassword = ''
  resetError.value = ''
}

function closeForgotPassword() {
  forgotPassword.value = false
  resetStep.value = 1
  resetForm.code = ''
  resetForm.newPassword = ''
  resetForm.confirmPassword = ''
  resetError.value = ''
  if (codeTimer.value !== null) {
    window.clearInterval(codeTimer.value)
    codeTimer.value = null
  }
}

function startResetTimer() {
  if (codeTimer.value !== null) return

  countdown.value = cooldownSeconds
  resetStep.value = 2

  codeTimer.value = window.setInterval(() => {
    countdown.value -= 1
    if (countdown.value <= 0 && codeTimer.value !== null) {
      window.clearInterval(codeTimer.value)
      codeTimer.value = null
    }
  }, 1000)
}

async function verifyEmail() {
  if (!resetForm.email) {
    resetError.value = 'Email is required.'
    return
  }

  resetError.value = ''
  isSendingResetEmail.value = true

  try {
    const response = await authStore.sendVerificationCode(resetForm.email)
    if (response.success !== true) {
      throw new Error('Request failed.')
    }
    startResetTimer()
  } catch (error) {
    resetError.value = getApiErrorMessage(error, 'Unable to send reset code.')
  } finally {
    isSendingResetEmail.value = false
  }
}

async function verifyCode() {
  if (!resetForm.email || !resetForm.code) {
    resetError.value = 'Email and verification code are required.'
    return
  }

  resetError.value = ''
  isVerifyingResetCode.value = true

  try {
    const response = await authStore.confirmVerificationCode({
      email: resetForm.email,
      code: resetForm.code,
      action: 'changepassword',
    })
    if (response.success !== true) {
      throw new Error('Request failed.')
    }
    resetStep.value = 3
  } catch (error) {
    resetError.value = getApiErrorMessage(error, 'Unable to verify reset code.')
  } finally {
    isVerifyingResetCode.value = false
  }
}

async function submitNewPassword() {
  if (!resetForm.newPassword || !resetForm.confirmPassword) {
    resetError.value = 'Enter and confirm your new password.'
    return
  }

  if (resetForm.newPassword !== resetForm.confirmPassword) {
    resetError.value = 'Passwords do not match.'
    return
  }

  resetError.value = ''
  isSavingNewPassword.value = true

  try {
    const response = await authStore.resetPassword({
      email: resetForm.email,
      code: resetForm.code,
      password: resetForm.newPassword,
      password_confirmation: resetForm.confirmPassword,
    })
    if (response.success !== true) {
      throw new Error('Request failed.')
    }
    loginForm.email = resetForm.email
    closeForgotPassword()
  } catch (error) {
    resetError.value = getApiErrorMessage(error, 'Unable to reset password.')
  } finally {
    isSavingNewPassword.value = false
  }
}

onBeforeUnmount(() => {
  if (codeTimer.value !== null) {
    window.clearInterval(codeTimer.value)
  }
})

function handleBeforeUnload(event: BeforeUnloadEvent) {
  if (!isResetActive.value) return

  event.preventDefault()
  event.returnValue = leaveWarningMessage
}

onBeforeRouteLeave(() => {
  if (!isResetActive.value) return true

  return window.confirm(leaveWarningMessage)
})

onMounted(() => {
  window.addEventListener('beforeunload', handleBeforeUnload)
})

onBeforeUnmount(() => {
  window.removeEventListener('beforeunload', handleBeforeUnload)
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

        <form v-if="!forgotPassword" class="space-y-6" @submit.prevent="submitLogin">
          <div v-if="loginError" class="rounded-xl border border-red-200 bg-red-50 px-4 py-3 text-sm text-red-700">
            {{ loginError }}
          </div>

          <div>
            <label class="mb-1 block text-sm font-semibold text-gray-700" for="email">Email</label>
            <input
              id="email"
              v-model="loginForm.email"
              type="text"
              placeholder="Enter any email"
              class="mt-1 w-full rounded-xl border border-gray-300 bg-gray-50 px-4 py-3 outline-none transition focus:border-blue-500 focus:ring-2 focus:ring-blue-200"
            />
          </div>

          <div>
            <label class="mb-1 block text-sm font-semibold text-gray-700" for="password">Password</label>
            <input
              id="password"
              v-model="loginForm.password"
              type="password"
              placeholder="Enter password"
              class="mt-1 w-full rounded-xl border border-gray-300 bg-gray-50 px-4 py-3 outline-none transition focus:border-blue-500 focus:ring-2 focus:ring-blue-200"
            />
            <div class="mt-2 text-right">
              <button type="button" class="text-sm font-medium text-blue-600 hover:underline" @click="openForgotPassword">
                Forgot password?
              </button>
            </div>
          </div>

          <button
            type="submit"
            class="h-12 w-full rounded-xl bg-blue-600 font-semibold text-white transition-colors hover:bg-blue-700 disabled:cursor-not-allowed disabled:bg-blue-400"
            :disabled="isSubmittingLogin"
          >
            {{ isSubmittingLogin ? 'Logging in...' : 'Login' }}
          </button>
        </form>

        <div v-else class="space-y-6">
          <div class="mb-6">
            <div class="flex items-start">
              <div class="flex flex-1 justify-center">
                <div class="flex flex-col items-center text-center">
                  <div :class="['flex h-9 w-9 items-center justify-center rounded-full border-2 text-sm font-semibold', resetStepClass.one]">1</div>
                  <div class="mt-2 text-xs text-gray-600">Email</div>
                </div>
              </div>

              <div class="mt-4.5 flex flex-1 items-center">
                <div class="h-1 w-full rounded-full bg-gray-200">
                  <div class="h-1 rounded-full bg-green-500" :style="{ width: resetStep >= 2 ? '100%' : '50%' }"></div>
                </div>
              </div>

              <div class="flex flex-1 justify-center">
                <div class="flex flex-col items-center text-center">
                  <div :class="['flex h-9 w-9 items-center justify-center rounded-full border-2 text-sm font-semibold', resetStepClass.two]">2</div>
                  <div class="mt-2 text-xs text-gray-600">Verify</div>
                </div>
              </div>

              <div class="mt-4.5 flex flex-1 items-center">
                <div class="h-1 w-full rounded-full bg-gray-200">
                  <div class="h-1 rounded-full bg-green-500" :style="{ width: resetStep >= 3 ? '100%' : '0%' }"></div>
                </div>
              </div>

              <div class="flex flex-1 justify-center">
                <div class="flex flex-col items-center text-center">
                  <div :class="['flex h-9 w-9 items-center justify-center rounded-full border-2 text-sm font-semibold', resetStepClass.three]">3</div>
                  <div class="mt-2 text-xs text-gray-600">New Password</div>
                </div>
              </div>
            </div>
          </div>

          <div v-if="resetStep === 1" class="space-y-4">
          <div v-if="resetError" class="rounded-xl border border-red-200 bg-red-50 px-4 py-3 text-sm text-red-700">
            {{ resetError }}
          </div>

            <div>
              <label class="mb-1 block text-sm font-semibold text-gray-700" for="reset-email">Email</label>
              <input
                id="reset-email"
                v-model="resetForm.email"
                type="email"
                placeholder="Enter email"
                class="mt-1 w-full rounded-xl border border-gray-300 bg-gray-50 px-4 py-3 outline-none transition focus:border-blue-500 focus:ring-2 focus:ring-blue-200"
              />
            </div>

            <button
              type="button"
              class="h-12 w-full rounded-xl bg-blue-600 font-semibold text-white transition-colors hover:bg-blue-700 disabled:cursor-not-allowed disabled:bg-blue-400"
              :disabled="isSendingResetEmail"
              @click="verifyEmail"
            >
              {{ isSendingResetEmail ? 'Sending Code...' : 'Get Code' }}
            </button>
          </div>

          <div v-else-if="resetStep === 2" class="space-y-4">
            <div v-if="resetError" class="rounded-xl border border-red-200 bg-red-50 px-4 py-3 text-sm text-red-700">
              {{ resetError }}
            </div>

            <div class="rounded-xl bg-blue-50 p-4 text-sm text-gray-700">
              <p class="font-medium text-gray-900">Email: {{ resetForm.email || 'you@example.com' }}</p>
              <p class="mt-1">We sent a reset code to your email. Enter it below.</p>
              <p v-if="codeTimer !== null" class="mt-2 font-medium text-blue-700">You can request a new code in {{ countdown }}s</p>
            </div>

            <div>
              <label class="mb-1 block text-sm font-semibold text-gray-700" for="reset-code">Verification Code</label>
              <input
                id="reset-code"
                v-model="resetForm.code"
                type="text"
                placeholder="Enter code"
                class="mt-1 w-full rounded-xl border border-gray-300 bg-gray-50 px-4 py-3 outline-none transition focus:border-blue-500 focus:ring-2 focus:ring-blue-200"
              />
            </div>

            <button
              type="button"
              class="h-12 w-full rounded-xl bg-blue-600 font-semibold text-white transition-colors hover:bg-blue-700 disabled:cursor-not-allowed disabled:bg-blue-400"
              :disabled="isVerifyingResetCode"
              @click="verifyCode"
            >
              {{ isVerifyingResetCode ? 'Verifying...' : 'Verify Code' }}
            </button>

            <button
              type="button"
              class="h-12 w-full rounded-xl border border-blue-600 font-semibold text-blue-600 transition-colors hover:bg-blue-50 disabled:cursor-not-allowed disabled:border-blue-300 disabled:text-blue-300"
              :disabled="codeTimer !== null || isSendingResetEmail"
              @click="verifyEmail"
            >
              <span v-if="codeTimer === null">Resend Code</span>
              <span v-else>Resend in {{ countdown }}s</span>
            </button>

            <button type="button" class="text-sm font-medium text-gray-600 hover:underline" @click="closeForgotPassword">
              Back to login
            </button>
          </div>

          <div v-else class="space-y-4">
            <div v-if="resetError" class="rounded-xl border border-red-200 bg-red-50 px-4 py-3 text-sm text-red-700">
              {{ resetError }}
            </div>

            <div class="rounded-xl bg-blue-50 p-4 text-sm text-gray-700">
              <p class="font-medium text-gray-900">Email: {{ resetForm.email || 'you@example.com' }}</p>
              <p class="mt-1">Set your new password below.</p>
            </div>

            <div>
              <label class="mb-1 block text-sm font-semibold text-gray-700" for="new-password">New Password</label>
              <input
                id="new-password"
                v-model="resetForm.newPassword"
                type="password"
                placeholder="Enter new password"
                class="mt-1 w-full rounded-xl border border-gray-300 bg-gray-50 px-4 py-3 outline-none transition focus:border-blue-500 focus:ring-2 focus:ring-blue-200"
              />
            </div>

            <div>
              <label class="mb-1 block text-sm font-semibold text-gray-700" for="confirm-password">Confirm Password</label>
              <input
                id="confirm-password"
                v-model="resetForm.confirmPassword"
                type="password"
                placeholder="Confirm new password"
                class="mt-1 w-full rounded-xl border border-gray-300 bg-gray-50 px-4 py-3 outline-none transition focus:border-blue-500 focus:ring-2 focus:ring-blue-200"
              />
            </div>

            <button
              type="button"
              class="h-12 w-full rounded-xl bg-blue-600 font-semibold text-white transition-colors hover:bg-blue-700 disabled:cursor-not-allowed disabled:bg-blue-400"
              :disabled="isSavingNewPassword"
              @click="submitNewPassword"
            >
              {{ isSavingNewPassword ? 'Saving...' : 'Save New Password' }}
            </button>
          </div>
        </div>

        <div v-if="!forgotPassword" class="mt-8 border-t border-gray-200 pt-6">
          <div class="flex flex-col items-center justify-center gap-2 text-center sm:flex-row sm:whitespace-nowrap">
            <p class="m-0 text-gray-600">Don't have an account?</p>
            <RouterLink replace to="/signup" class="whitespace-nowrap font-semibold text-green-600 hover:underline">Sign up</RouterLink>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>
