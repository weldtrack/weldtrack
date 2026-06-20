<script setup lang="ts">
import { computed, onBeforeUnmount, reactive, ref } from 'vue'
import { onBeforeRouteLeave, useRouter } from 'vue-router'
import { useAuthStore } from '../../stores/auth'
import { useModalStore } from '../../stores/modal'
import { getUserFriendlyApiError } from '../../services/errorMessage'
import ThemeToggle from '../../components/ui/ThemeToggle.vue'
import { useThemeMode } from '../../composables/useThemeMode'

const authStore = useAuthStore()
const router = useRouter()
const modalStore = useModalStore()
const { isDarkMode } = useThemeMode()

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
const pendingRoute = ref<string | null>(null)
const allowRouteLeave = ref(false)

function validatePassword(password: string) {
  if (password.length < 8) {
    return 'Password must be 8 characters or longer.'
  }

  if (!/\d/.test(password)) {
    return 'Password must include one number.'
  }

  if (!/[A-Z]/.test(password)) {
    return 'Password must include one uppercase letter.'
  }

  return ''
}

async function submitLogin() {
  if (!loginForm.email || !loginForm.password) {
    loginError.value = 'Email and password are required.'
    return
  }

  loginError.value = ''
  isSubmittingLogin.value = true

  try {
    authStore.logout()
    
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
    loginError.value = getUserFriendlyApiError(error, 'Unable to sign in. Please try again.')
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
    resetError.value = getUserFriendlyApiError(error, 'Unable to send reset code.')
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
    resetError.value = getUserFriendlyApiError(error, 'Unable to verify reset code.')
  } finally {
    isVerifyingResetCode.value = false
  }
}

async function submitNewPassword() {
  if (!resetForm.newPassword || !resetForm.confirmPassword) {
    resetError.value = 'Enter and confirm your new password.'
    return
  }

  const passwordError = validatePassword(resetForm.newPassword)
  if (passwordError) {
    resetError.value = passwordError
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
    resetError.value = getUserFriendlyApiError(error, 'Unable to reset password.')
  } finally {
    isSavingNewPassword.value = false
  }
}

onBeforeRouteLeave((to) => {
  if (allowRouteLeave.value || !isResetActive.value) return true

  pendingRoute.value = to.fullPath

  modalStore.open({
    title: 'Leave this page?',
    message: leaveWarningMessage,
    variant: 'warning',
    confirmLabel: 'Leave',
    cancelLabel: 'Stay',
    onConfirm: () => {
      allowRouteLeave.value = true
      if (pendingRoute.value) {
        void router.push(pendingRoute.value)
      }
    },
  })

  return false
})

onBeforeUnmount(() => {
  if (codeTimer.value !== null) {
    window.clearInterval(codeTimer.value)
  }
})
</script>

<template>
  <div :class="['public-theme-page relative min-h-screen overflow-hidden bg-[#020617] p-4 text-slate-50 sm:p-6 lg:p-10', isDarkMode ? 'theme-dark' : 'theme-light']">
    <!-- Background Elements -->
    <div class="pointer-events-none absolute inset-0">
      <div class="absolute -left-20 top-16 h-72 w-72 rounded-full bg-cyan-500/10 blur-[100px]"></div>
      <div class="absolute right-0 top-24 h-96 w-96 rounded-full bg-blue-600/10 blur-[120px]"></div>
      <div class="absolute bottom-0 left-1/2 h-80 w-80 rounded-full bg-emerald-500/5 blur-[80px]"></div>
      <div class="absolute inset-0 bg-[url('https://grainy-gradients.vercel.app/noise.svg')] opacity-20 mix-blend-overlay"></div>
    </div>

    <div class="relative mx-auto flex min-h-[calc(100vh-2rem)] w-full max-w-6xl items-center justify-center sm:min-h-[calc(100vh-3rem)] lg:min-h-[calc(100vh-5rem)]">
      <div class="relative grid w-full overflow-hidden rounded-[2.5rem] border border-white/10 bg-[#0f172a]/40 shadow-2xl backdrop-blur-2xl xl:grid-cols-[1.1fr_0.9fr]">
        <ThemeToggle class="absolute right-4 top-4 z-20 sm:right-6 sm:top-6" />
        <!-- Left Side: Visual/Branding -->
        <div class="relative isolate hidden min-h-[38rem] overflow-hidden bg-slate-950 xl:flex">
          <img
            src="https://images.pexels.com/photos/15888227/pexels-photo-15888227.jpeg?cs=srgb&dl=pexels-hoang-nc-483165236-15888227.jpg&fm=jpg"
            alt="Welder creating sparks"
            class="absolute inset-0 h-full w-full object-cover"
          />
          <div class="absolute inset-0 bg-[linear-gradient(135deg,rgba(2,6,23,0.98)_0%,rgba(15,23,42,0.88)_48%,rgba(8,47,73,0.72)_100%)]"></div>
          <div class="absolute inset-0 bg-slate-950/30 mix-blend-multiply"></div>
          <div class="relative z-10 flex h-full w-full flex-col justify-between p-10 text-white">
            <div>
              <div class="mb-8 flex h-14 w-14 items-center justify-center rounded-2xl border border-white/15 bg-white/10 shadow-[inset_0_1px_0_rgba(255,255,255,0.08),0_8px_30px_rgba(0,0,0,0.22)] backdrop-blur-xl">
              <svg class="h-8 w-8 !text-cyan-300" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M13 10V3L4 14h7v7l9-11h-7z" />
              </svg>
              </div>
              <div class="mb-4 inline-block rounded-full border border-cyan-400/20 bg-cyan-500/15 px-4 py-1 text-[10px] font-bold tracking-[0.2em] !text-cyan-200 uppercase backdrop-blur-md">Customer Access</div>
              <h1 class="max-w-md text-4xl font-black leading-tight tracking-tight !text-white">
                Access your <br> booking account.
              </h1>
              <p class="mt-6 max-w-sm text-lg leading-relaxed !text-slate-200">
                Sign in to view your bookings, update your details, and continue your service requests.
              </p>
            </div>

            <div class="grid grid-cols-3 gap-6">
              <div class="rounded-2xl border border-white/15 bg-white/10 p-4 backdrop-blur-xl shadow-[0_10px_30px_rgba(0,0,0,0.2)]">
              <div class="text-xl font-black !text-white">Fast</div>
              <div class="mt-1 text-xs font-bold !text-slate-300 uppercase tracking-widest">Login</div>
              </div>
              <div class="rounded-2xl border border-white/15 bg-white/10 p-4 backdrop-blur-xl shadow-[0_10px_30px_rgba(0,0,0,0.2)]">
              <div class="text-xl font-black !text-white">Safe</div>
              <div class="mt-1 text-xs font-bold !text-slate-300 uppercase tracking-widest">Encrypted</div>
              </div>
              <div class="rounded-2xl border border-white/15 bg-white/10 p-4 backdrop-blur-xl shadow-[0_10px_30px_rgba(0,0,0,0.2)]">
              <div class="text-xl font-black !text-white">Live</div>
              <div class="mt-1 text-xs font-bold !text-slate-300 uppercase tracking-widest">Synced</div>
              </div>
            </div>
          </div>
        </div>

        <!-- Right Side: Form -->
        <div class="flex items-center justify-center p-8 sm:p-12 xl:p-16">
          <div class="w-full max-w-sm">
            <div class="mb-10 text-center xl:text-left">
                <div class="mb-6 inline-flex h-12 w-12 items-center justify-center rounded-xl bg-linear-to-br from-cyan-400 to-blue-600 p-0.5 xl:hidden">
                    <div class="flex h-full w-full items-center justify-center rounded-[10px] bg-[#020617] text-xl">⚙️</div>
                </div>
                <h2 class="text-3xl font-black tracking-tight text-white">{{ forgotPassword ? 'Reset Password' : 'Welcome Back' }}</h2>
                <p class="mt-2 text-slate-400">Please enter your details to continue.</p>
            </div>

            <form v-if="!forgotPassword" class="space-y-6" @submit.prevent="submitLogin">
              <div v-if="loginError" class="rounded-2xl border border-red-500/20 bg-red-500/10 px-4 py-3 text-sm font-medium text-red-400">
                {{ loginError }}
              </div>

              <div class="space-y-2">
                <label class="text-xs font-bold uppercase tracking-widest text-slate-500" for="email">Email Address</label>
                <input
                  id="email"
                  v-model="loginForm.email"
                  type="email"
                  placeholder="name@company.com"
                  class="h-12 w-full rounded-xl border border-white/10 bg-white/5 px-4 text-white outline-none transition-all focus:border-cyan-500/50 focus:ring-4 focus:ring-cyan-500/10"
                />
              </div>

              <div class="space-y-2">
                <div class="flex justify-between items-center">
                    <label class="text-xs font-bold uppercase tracking-widest text-slate-500" for="password">Password</label>
                    <button type="button" class="text-xs font-bold text-cyan-400 hover:text-cyan-300 transition-colors" @click="openForgotPassword">
                      Forgot?
                    </button>
                </div>
                <input
                  id="password"
                  v-model="loginForm.password"
                  type="password"
                  placeholder="••••••••"
                  class="h-12 w-full rounded-xl border border-white/10 bg-white/5 px-4 text-white outline-none transition-all focus:border-cyan-500/50 focus:ring-4 focus:ring-cyan-500/10"
                />
              </div>

              <button
                type="submit"
                class="group relative h-12 w-full overflow-hidden rounded-xl border border-white/10 !bg-slate-900 font-bold !text-white shadow-lg shadow-slate-950/20 transition-all hover:!bg-slate-800 hover:shadow-xl hover:shadow-slate-950/25 active:scale-95 disabled:opacity-70 disabled:active:scale-100"
                :disabled="isSubmittingLogin"
              >
                {{ isSubmittingLogin ? 'Signing in...' : 'Sign In' }}
              </button>
            </form>

            <div v-else class="space-y-8">
              <div class="flex items-center gap-4 justify-between mb-2">
                <div v-for="i in 3" :key="i" class="flex-1">
                    <div :class="['h-1.5 rounded-full transition-all duration-500', resetStep >= i ? 'bg-cyan-500' : 'bg-white/10']"></div>
                </div>
              </div>

              <div v-if="resetStep === 1" class="space-y-6">
                <div v-if="resetError" class="rounded-2xl border border-red-500/20 bg-red-500/10 px-4 py-3 text-sm text-red-400">
                  {{ resetError }}
                </div>
                <div class="space-y-2">
                  <label class="text-xs font-bold uppercase tracking-widest text-slate-500" for="reset-email">Recovery Email</label>
                  <input
                    id="reset-email"
                    v-model="resetForm.email"
                    type="email"
                    placeholder="Enter your email"
                    class="h-12 w-full rounded-xl border border-white/10 bg-white/5 px-4 text-white outline-none transition-all focus:border-cyan-500/50 focus:ring-4 focus:ring-cyan-500/10"
                  />
                </div>
                <button
                  type="button"
                  class="h-12 w-full rounded-xl border border-white/10 !bg-slate-900 font-bold !text-white shadow-lg shadow-slate-950/20 transition-all hover:!bg-slate-800 active:scale-95 disabled:opacity-70"
                  :disabled="isSendingResetEmail"
                  @click="verifyEmail"
                >
                  {{ isSendingResetEmail ? 'Sending Code...' : 'Get Reset Code' }}
                </button>
              </div>

              <div v-else-if="resetStep === 2" class="space-y-6">
                <div v-if="resetError" class="rounded-2xl border border-red-500/20 bg-red-500/10 px-4 py-3 text-sm text-red-400">
                  {{ resetError }}
                </div>
                <div class="rounded-2xl bg-cyan-500/10 border border-cyan-500/20 p-4 text-sm text-cyan-50/80">
                  We sent a code to <span class="font-bold text-white">{{ resetForm.email }}</span>.
                </div>
                <div class="space-y-2">
                  <label class="text-xs font-bold uppercase tracking-widest text-slate-500" for="reset-code">Verification Code</label>
                  <input
                    id="reset-code"
                    v-model="resetForm.code"
                    type="text"
                    placeholder="Enter 6-digit code"
                    class="h-12 w-full rounded-xl border border-white/10 bg-white/5 px-4 text-white outline-none transition-all focus:border-cyan-500/50 focus:ring-4 focus:ring-cyan-500/10"
                  />
                </div>
                <button
                  type="button"
                  class="h-12 w-full rounded-xl border border-white/10 !bg-slate-900 font-bold !text-white shadow-lg shadow-slate-950/20 transition-all hover:!bg-slate-800 active:scale-95 disabled:opacity-70"
                  :disabled="isVerifyingResetCode"
                  @click="verifyCode"
                >
                  {{ isVerifyingResetCode ? 'Verifying...' : 'Verify Code' }}
                </button>
                <button
                  type="button"
                  class="w-full text-sm font-bold text-slate-500 hover:text-white transition-colors"
                  :disabled="codeTimer !== null || isSendingResetEmail"
                  @click="verifyEmail"
                >
                  <span v-if="codeTimer === null">Resend Code</span>
                  <span v-else>Resend in {{ countdown }}s</span>
                </button>
              </div>

              <div v-else class="space-y-6">
                <div v-if="resetError" class="rounded-2xl border border-red-500/20 bg-red-500/10 px-4 py-3 text-sm text-red-400">
                  {{ resetError }}
                </div>
                <div class="space-y-4">
                    <div class="space-y-2">
                      <label class="text-xs font-bold uppercase tracking-widest text-slate-500" for="new-password">New Password</label>
                      <div class="group relative">
                        <input
                          id="new-password"
                          v-model="resetForm.newPassword"
                          type="password"
                          class="h-12 w-full rounded-xl border border-white/10 bg-white/5 px-4 pr-11 text-white outline-none transition-all focus:border-cyan-500/50 focus:ring-4 focus:ring-cyan-500/10"
                        />
                        <div class="absolute inset-y-0 right-3 flex items-center">
                          <div class="relative flex h-5 w-5 cursor-help items-center justify-center rounded-full border border-white/20 bg-white/5 text-[11px] font-black text-slate-300 shadow-sm transition group-hover:border-cyan-400/60 group-hover:text-cyan-200 group-focus-within:border-cyan-400/60 group-focus-within:text-cyan-200">
                            !
                            <div class="pointer-events-none absolute right-0 top-full z-20 mt-2 w-52 rounded-xl border border-white/10 bg-slate-950 px-3 py-2 text-left text-[11px] leading-snug text-slate-200 opacity-0 shadow-2xl transition group-hover:opacity-100 group-focus-within:opacity-100">
                              Password must be 8+ characters and include 1 uppercase letter and 1 number.
                            </div>
                          </div>
                        </div>
                      </div>
                    </div>
                    <div class="space-y-2">
                      <label class="text-xs font-bold uppercase tracking-widest text-slate-500" for="confirm-password">Confirm Password</label>
                      <input
                        id="confirm-password"
                        v-model="resetForm.confirmPassword"
                        type="password"
                        class="h-12 w-full rounded-xl border border-white/10 bg-white/5 px-4 text-white outline-none transition-all focus:border-cyan-500/50 focus:ring-4 focus:ring-cyan-500/10"
                      />
                    </div>
                </div>
                <button
                  type="button"
                  class="h-12 w-full rounded-xl border border-white/10 !bg-slate-900 font-bold !text-white shadow-lg shadow-slate-950/20 transition-all hover:!bg-slate-800 active:scale-95"
                  :disabled="isSavingNewPassword"
                  @click="submitNewPassword"
                >
                  {{ isSavingNewPassword ? 'Updating...' : 'Update Password' }}
                </button>
              </div>

              <button type="button" class="w-full text-center text-sm font-bold text-slate-500 hover:text-white transition-colors" @click="closeForgotPassword">
                Return to Login
              </button>
            </div>

            <div v-if="!forgotPassword" class="mt-10 pt-8 border-t border-white/5 text-center">
                <p class="text-slate-500 text-sm font-medium">
                    Don't have an account? 
                    <RouterLink replace to="/signup" class="ml-1 text-cyan-400 font-bold hover:text-cyan-300 transition-colors">Create one</RouterLink>
                </p>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>
