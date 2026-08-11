<script setup lang="ts">
import { computed, onBeforeUnmount, reactive, ref } from 'vue'
import { useAuthStore } from '../../stores/auth'
import { onBeforeRouteLeave, useRouter } from 'vue-router'
import { useModalStore } from '../../stores/modal'
import { getUserFriendlyApiError } from '../../services/errorMessage'
import ThemeToggle from '../../components/ui/ThemeToggle.vue'
import { useThemeMode } from '../../composables/useThemeMode'

const authStore = useAuthStore()
const router = useRouter()
const modalStore = useModalStore()
const { isDarkMode } = useThemeMode()

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
const pendingRoute = ref<string | null>(null)
const allowRouteLeave = ref(false)

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
    signupError.value = getUserFriendlyApiError(error, 'Unable to resend verification code.')
  } finally {
    isSubmittingSignup.value = false
  }
}

async function submitSignup() {
  if (!form.email || !form.password || !form.confirm) {
    signupError.value = 'Email, password, and confirmation are required.'
    return
  }

  const passwordError = validatePassword(form.password)
  if (passwordError) {
    signupError.value = passwordError
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

    step.value = 2
    startCodeTimer()
  } catch (error) {
    signupError.value = getUserFriendlyApiError(error, 'Unable to create account.')
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
    
    if (response.user || response.access_token || response.token) {
      authStore.setSession({
        email: response.user?.email || form.email,
        role: response.user?.role || 'customer',
        user: response.user,
      })
      allowRouteLeave.value = true
      await router.replace('/dashboard')
    } else {
      throw new Error('Request failed.')
    }
  } catch (error) {
    signupError.value = getUserFriendlyApiError(error, 'Unable to verify signup code.')
  } finally {
    isVerifyingCode.value = false
  }
}

function handleFormSubmit() {
  if (step.value === 1) {
    return submitSignup()
  }

  return submitCode()
}

onBeforeRouteLeave((to) => {
  if (allowRouteLeave.value || !isProgressActive.value) return true

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
  <div :class="['public-theme-page relative min-h-screen overflow-hidden p-4 sm:p-6 lg:p-10', isDarkMode ? 'theme-dark' : 'theme-light']">
    <!-- Background Elements -->
    <div class="pointer-events-none absolute inset-0">
      <div class="absolute -left-20 top-16 h-72 w-72 rounded-full bg-cyan-500/10 blur-[100px]"></div>
      <div class="absolute right-0 top-24 h-96 w-96 rounded-full bg-blue-600/10 blur-[120px]"></div>
      <div class="absolute bottom-0 left-1/2 h-80 w-80 rounded-full bg-emerald-500/5 blur-[80px]"></div>
      <div class="absolute inset-0 bg-[url('https://grainy-gradients.vercel.app/noise.svg')] opacity-20 mix-blend-overlay"></div>
    </div>

    <div class="relative mx-auto flex min-h-[calc(100vh-2rem)] w-full max-w-6xl items-center justify-center sm:min-h-[calc(100vh-3rem)] lg:min-h-[calc(100vh-5rem)]">
      <div class="auth-shell-card relative grid w-full overflow-hidden rounded-[2.5rem] border border-white/10 bg-public-panel xl:grid-cols-[0.95fr_1.05fr] shadow-2xl backdrop-blur-2xl">
        <ThemeToggle class="absolute right-4 top-4 z-20 sm:right-6 sm:top-6" />
        <!-- Left Side: Visual/Branding -->
        <div class="auth-visual relative isolate hidden min-h-[38rem] overflow-hidden bg-slate-950 xl:flex">
          <img
            src="https://images.unsplash.com/photo-1504328345606-18bbc8c9d7d1?q=80&w=1600&auto=format&fit=crop"
            alt="Fabrication workshop"
            class="absolute inset-0 h-full w-full object-cover"
          />
          <div class="absolute inset-0 bg-[linear-gradient(135deg,rgba(2,6,23,0.98)_0%,rgba(15,23,42,0.88)_48%,rgba(8,47,73,0.72)_100%)]"></div>
          <div class="absolute inset-0 bg-slate-950/30 mix-blend-multiply"></div>
          <div class="relative z-10 flex h-full w-full flex-col justify-between p-10 text-white">
            <div>
              <RouterLink to="/" class="mb-8 block transition hover:opacity-80">
                <img src="/weldtrack.png" alt="WeldTrack Logo" class="h-20 w-auto object-contain" />
              </RouterLink>
              <div class="mb-4 inline-block rounded-full border border-cyan-400/20 bg-cyan-500/15 px-4 py-1 text-[10px] font-bold tracking-[0.2em] !text-cyan-200 uppercase backdrop-blur-md">Create Your Account</div>
              <h1 class="max-w-md text-4xl font-black leading-tight tracking-tight !text-white">
                Book welding services <br> without the hassle.
              </h1>
              <p class="mt-6 max-w-sm text-lg leading-relaxed !text-slate-200">
                Create your customer account in just two steps, then book welding services and keep track of your requests in one place.
              </p>
            </div>

            <div class="grid grid-cols-3 gap-6 text-sm">
              <div class="flex flex-col gap-2 rounded-2xl border border-white/15 bg-white/10 p-4 backdrop-blur-xl shadow-[0_10px_30px_rgba(0,0,0,0.2)]">
                <div :class="['h-1 rounded-full', step >= 1 ? 'bg-cyan-400' : 'bg-white/10']"></div>
                <div class="font-bold !text-white">Step 1</div>
                <div class="text-[10px] font-bold !text-slate-300 uppercase tracking-widest">Details</div>
              </div>
              <div class="flex flex-col gap-2 rounded-2xl border border-white/15 bg-white/10 p-4 backdrop-blur-xl shadow-[0_10px_30px_rgba(0,0,0,0.2)]">
                <div :class="['h-1 rounded-full', step >= 2 ? 'bg-cyan-400' : 'bg-white/10']"></div>
                <div class="font-bold !text-white">Step 2</div>
                <div class="text-[10px] font-bold !text-slate-300 uppercase tracking-widest">Verify</div>
              </div>
              <div class="flex flex-col gap-2 rounded-2xl border border-white/15 bg-white/10 p-4 backdrop-blur-xl shadow-[0_10px_30px_rgba(0,0,0,0.2)]">
                <div class="h-1 rounded-full bg-white/10"></div>
                <div class="font-bold !text-slate-200">Ready</div>
                <div class="text-[10px] font-bold !text-slate-300 uppercase tracking-widest">Access</div>
              </div>
            </div>
          </div>
        </div>

        <!-- Right Side: Form -->
        <div class="auth-form-panel flex items-center justify-center p-8 sm:p-12 xl:p-16">
          <div class="w-full max-w-sm">
                <div class="mb-10 text-center xl:text-left">
                        <RouterLink to="/" class="mb-6 inline-block xl:hidden transition hover:opacity-80">
                          <img src="/weldtrack.png" alt="WeldTrack Logo" class="h-16 w-auto object-contain" />
                        </RouterLink>
                <h2 class="text-3xl font-black tracking-tight text-white">Create Account</h2>
                <p class="mt-2 text-slate-400">Create your customer account to book welding services.</p>
                </div>

            <form class="space-y-6" @submit.prevent="handleFormSubmit">
              <div v-if="signupError" class="rounded-2xl border border-red-500/20 bg-red-500/10 px-4 py-3 text-sm font-medium text-red-400">
                {{ signupError }}
              </div>

              <div v-if="step === 1" class="space-y-5">
                <div class="space-y-2">
                  <label class="text-xs font-bold uppercase tracking-widest text-slate-500" for="email">Email Address</label>
                  <input
                    id="email"
                    v-model="form.email"
                    type="email"
                    placeholder="you@example.com"
                    class="h-12 w-full rounded-xl border border-white/10 bg-white/5 px-4 text-white outline-none transition-all focus:border-cyan-500/50 focus:ring-4 focus:ring-cyan-500/10"
                  />
                </div>

                <div class="space-y-2">
                  <label class="text-xs font-bold uppercase tracking-widest text-slate-500" for="password">Create Password</label>
                  <div class="group relative">
                    <input
                      id="password"
                      v-model="form.password"
                      type="password"
                      placeholder="••••••••"
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
                  <label class="text-xs font-bold uppercase tracking-widest text-slate-500" for="confirm">Confirm Password</label>
                  <input
                    id="confirm"
                    v-model="form.confirm"
                    type="password"
                    placeholder="••••••••"
                    class="h-12 w-full rounded-xl border border-white/10 bg-white/5 px-4 text-white outline-none transition-all focus:border-cyan-500/50 focus:ring-4 focus:ring-cyan-500/10"
                  />
                </div>

                <button
                  type="submit"
                  class="h-12 w-full rounded-xl border border-white/10 !bg-slate-900 font-bold !text-white shadow-lg shadow-slate-950/20 transition-all hover:!bg-slate-800 active:scale-95 disabled:opacity-70"
                  :disabled="isSubmittingSignup"
                >
                  {{ isSubmittingSignup ? 'Creating...' : 'Continue' }}
                </button>
              </div>

              <div v-else class="space-y-6">
                <div class="rounded-2xl bg-cyan-500/10 border border-cyan-500/20 p-4 text-sm text-cyan-50/80 text-center">
                    Verification code sent to <br> <span class="font-bold text-white">{{ form.email }}</span>
                </div>

                <div class="space-y-2">
                  <label class="text-xs font-bold uppercase tracking-widest text-slate-500" for="code">Verification Code</label>
                  <input
                    id="code"
                    v-model="form.code"
                    type="text"
                    placeholder="Enter 6-digit code"
                    class="h-12 w-full rounded-xl border border-white/10 bg-white/5 px-4 text-white outline-none transition-all focus:border-cyan-500/50 focus:ring-4 focus:ring-cyan-500/10 text-center tracking-[0.5em] font-black"
                  />
                </div>

                <button
                  type="button"
                  class="h-12 w-full rounded-xl border border-white/10 !bg-slate-900 font-bold !text-white shadow-lg shadow-slate-950/20 transition-all hover:!bg-slate-800 active:scale-95 disabled:opacity-70"
                  :disabled="isVerifyingCode"
                  @click="submitCode"
                >
                  {{ isVerifyingCode ? 'Verifying...' : 'Verify & Create Account' }}
                </button>

                <button
                  type="button"
                  class="w-full text-sm font-bold text-slate-500 hover:text-white transition-colors"
                  :disabled="codeTimer !== null || isSubmittingSignup"
                  @click="resendCode"
                >
                  <span v-if="codeTimer === null">Resend Code</span>
                  <span v-else>Resend in {{ countdown }}s</span>
                </button>
              </div>
            </form>

            <div v-if="step === 1" class="mt-10 pt-8 border-t border-white/5 text-center">
                <p class="text-slate-500 text-sm font-medium">
                    Already have an account? 
                    <RouterLink replace to="/login" class="ml-1 text-cyan-400 font-bold hover:text-cyan-300 transition-colors">Sign in</RouterLink>
                </p>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<style>
@import './login-theme.css';
</style>
