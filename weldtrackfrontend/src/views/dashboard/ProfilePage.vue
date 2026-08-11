<template>
  <section class="mx-auto max-w-5xl space-y-7">
    <header class="flex flex-col gap-2 border-b border-slate-200 pb-6 dark:border-slate-800 sm:flex-row sm:items-end sm:justify-between">
      <div>
        <p class="text-xs font-semibold uppercase tracking-[0.16em] text-sky-600 dark:text-sky-400">Account settings</p>
        <h1 class="mt-2 text-2xl font-semibold tracking-tight text-gray-900 dark:text-slate-100">Profile and security</h1>
        <p class="mt-1 text-sm text-slate-500 dark:text-slate-400">Manage your contact details, profile photo, and password.</p>
      </div>
      <div class="inline-flex w-fit items-center gap-2 rounded-full border border-emerald-200 bg-emerald-50 px-3 py-1.5 text-xs font-semibold text-emerald-700 dark:border-emerald-900 dark:bg-emerald-950/40 dark:text-emerald-300">
        <ShieldCheck class="h-3.5 w-3.5" /> Account protected
      </div>
    </header>
    
    <div v-if="user" class="grid overflow-hidden rounded-2xl border border-slate-200 bg-white shadow-sm dark:border-slate-800 dark:bg-slate-900 lg:grid-cols-[18rem_1fr]">
      <aside class="flex flex-col items-center border-b border-slate-200 bg-slate-50/70 px-6 py-8 text-center dark:border-slate-800 dark:bg-slate-950/40 lg:border-r lg:border-b-0">
        <div class="relative group">
          <img v-if="user.profile_image" :src="getImageUrl(user.profile_image)" alt="Profile" class="h-28 w-28 rounded-2xl border border-slate-200 object-cover shadow-sm dark:border-slate-700">
          <div v-else class="flex h-28 w-28 items-center justify-center rounded-2xl border border-slate-200 bg-white text-3xl font-semibold text-slate-500 shadow-sm dark:border-slate-700 dark:bg-slate-800 dark:text-slate-300">{{ profileInitial }}</div>
          <label class="absolute -right-2 -bottom-2 flex h-9 w-9 cursor-pointer items-center justify-center rounded-xl border-2 border-slate-50 bg-sky-600 text-white shadow-md transition hover:bg-sky-700 dark:border-slate-950" title="Upload profile photo">
            <Camera class="h-4 w-4" />
            <input type="file" accept="image/*" class="hidden" @change="handleImageUpload">
          </label>
        </div>
        <p class="mt-5 max-w-full truncate text-base font-semibold text-slate-900 dark:text-slate-100">{{ user.email }}</p>
        <span class="mt-2 rounded-full border border-slate-200 bg-white px-3 py-1 text-[11px] font-semibold uppercase tracking-wider text-slate-500 dark:border-slate-700 dark:bg-slate-800 dark:text-slate-400">{{ roleLabel }}</span>
        <p class="mt-5 text-xs leading-5 text-slate-500 dark:text-slate-400">Use a clear photo so your account is easier to identify across WeldTrack.</p>
      </aside>

      <div class="p-6 sm:p-8">
        <div class="mb-6">
          <h2 class="text-base font-semibold text-slate-900 dark:text-slate-100">Personal information</h2>
          <p class="mt-1 text-sm text-slate-500 dark:text-slate-400">Valid changes are saved automatically.</p>
        </div>

        <div class="space-y-5">
          <div>
            <div class="mb-2 flex items-center justify-between gap-3">
              <label class="block text-sm font-medium text-slate-700 dark:text-slate-300" for="email">Email address</label>
              <span v-if="!canEditEmail" class="text-[11px] font-medium text-slate-400">Managed account</span>
            </div>
          <div :class="['flex overflow-hidden rounded-xl border border-slate-200 bg-slate-50 transition dark:border-slate-700 dark:bg-slate-800/60', !canEditEmail ? 'cursor-not-allowed opacity-70' : 'focus-within:border-sky-500 focus-within:ring-2 focus-within:ring-sky-200 dark:focus-within:ring-sky-900']">
            <input
              id="email"
              v-model="form.email"
              type="email"
              placeholder="newemail@example.com"
              :disabled="!canEditEmail"
              :class="['w-full bg-transparent px-4 py-3 outline-none text-slate-900 dark:text-slate-100', !canEditEmail ? 'cursor-not-allowed' : '']"
            />
            <span class="flex items-center border-l border-slate-200 px-4 text-slate-400 dark:border-slate-700">
              <Mail class="h-5 w-5" />
            </span>
          </div>
        </div>
        <div>
          <label class="mb-2 block text-sm font-medium text-slate-700 dark:text-slate-300">Password</label>
          <button
            @click="openPasswordModal"
            class="flex w-full items-center justify-between rounded-xl border border-slate-200 bg-slate-50 px-4 py-3 text-left text-slate-700 transition hover:border-slate-300 hover:bg-slate-100 dark:border-slate-700 dark:bg-slate-800/60 dark:text-slate-200 dark:hover:border-slate-600 dark:hover:bg-slate-800"
          >
            <span class="flex items-center gap-3"><Key class="h-4 w-4 text-slate-400" /><span><span class="block text-sm font-medium">Change password</span><span class="mt-0.5 block text-xs text-slate-500 dark:text-slate-400">Verify your email before setting a new password</span></span></span>
            <ChevronRight class="h-4 w-4 text-slate-400" />
          </button>
        </div>
        <div>
          <label class="mb-2 block text-sm font-medium text-slate-700 dark:text-slate-300" for="mobile_phone">Mobile phone</label>
          <div class="flex overflow-hidden rounded-xl border border-slate-200 bg-slate-50 transition focus-within:border-sky-500 focus-within:ring-2 focus-within:ring-sky-200 dark:border-slate-700 dark:bg-slate-800/60 dark:focus-within:ring-sky-900">
            <span class="inline-flex select-none items-center border-r border-slate-200 bg-slate-100 px-4 text-sm font-semibold text-slate-500 dark:border-slate-700 dark:bg-slate-800 dark:text-slate-400">
              +63
            </span>
            <input 
              id="mobile_phone" 
              v-model="form.mobile_phone" 
              type="tel" 
              maxlength="10"
              placeholder="9123456789"
              class="w-full bg-transparent px-4 py-3 text-slate-900 outline-none dark:text-slate-100"
            />
            <span class="flex items-center border-l border-slate-200 px-4 text-slate-400 dark:border-slate-700">
              <Phone class="h-5 w-5" />
            </span>
          </div>
          <p class="mt-2 text-xs text-slate-500 dark:text-slate-400">Enter a 10-digit Philippine mobile number starting with 9.</p>
        </div>
        </div>
      </div>
    </div>
    <div v-else class="rounded-2xl border border-slate-200 bg-white py-16 text-center text-slate-500 dark:border-slate-800 dark:bg-slate-900 dark:text-slate-400">Loading profile...</div>

    <ModalShell
      :show="showPasswordModal"
      title="Change Password"
      :subtitle="`Step ${resetStep} of 3`"
      tone="blue"
      size="md"
      @close="closePasswordModal"
    >
      <div class="space-y-4">
        <div v-if="resetError" class="p-3 rounded-lg bg-red-50 text-sm text-red-700 border border-red-200">
          {{ resetError }}
        </div>

        <!-- Step 1: Send Code -->
        <div v-if="resetStep === 1" class="space-y-4">
          <p class="text-sm text-gray-600">Enter your email to receive a verification code.</p>
          <input v-model="resetForm.email" type="email" class="w-full p-2 border rounded" placeholder="Email" readonly />
          <button @click="sendCode" :disabled="isSubmitting" class="w-full p-2 bg-blue-600 text-white rounded">Send Code</button>
        </div>

        <!-- Step 2: Verify Code -->
        <div v-if="resetStep === 2" class="space-y-4">
          <input v-model="resetForm.code" type="text" class="w-full p-2 border rounded" placeholder="Verification Code" />
          <button @click="verifyCode" :disabled="isSubmitting" class="w-full p-2 bg-blue-600 text-white rounded">Verify Code</button>
        </div>

        <!-- Step 3: New Password -->
        <div v-if="resetStep === 3" class="space-y-4">
          <div class="space-y-2">
            <label class="block text-sm font-medium text-gray-700">New Password</label>
            <div class="group relative">
              <input v-model="resetForm.newPassword" type="password" class="w-full p-2 border rounded pr-11" placeholder="New Password" />
              <div class="absolute inset-y-0 right-3 flex items-center">
                <div class="relative flex h-5 w-5 cursor-help items-center justify-center rounded-full border border-gray-300 bg-white text-[11px] font-black text-gray-500 shadow-sm transition">
                  !
                  <div class="pointer-events-none absolute right-0 top-full z-20 mt-2 w-52 rounded-xl border border-gray-200 bg-white px-3 py-2 text-left text-[11px] leading-snug text-gray-700 opacity-0 shadow-2xl transition group-hover:opacity-100">
                    Password must be 8+ characters and include 1 uppercase letter and 1 number.
                  </div>
                </div>
              </div>
            </div>
          </div>
          <input v-model="resetForm.confirmPassword" type="password" class="w-full p-2 border rounded" placeholder="Confirm Password" />
          <button @click="changePassword" :disabled="isSubmitting" class="w-full p-2 bg-blue-600 text-white rounded">Change Password</button>
        </div>
      </div>
    </ModalShell>
  </section>
</template>

<script setup lang="ts">
import { computed, ref, onMounted, watch } from 'vue';
import { Camera, ChevronRight, Mail, Key, Phone, ShieldCheck } from 'lucide-vue-next';
import { getProfile, updateProfile, uploadProfileImage } from '../../services/profile.service';
import type { UserRead } from '../../types/auth';
import { useAuthStore } from '../../stores/auth';
import ModalShell from '../../components/ui/ModalShell.vue';
import { getUserFriendlyApiError } from '../../services/errorMessage';

const authStore = useAuthStore();
const user = ref<UserRead | null>(null);
const form = ref({ mobile_phone: '', email: '' });
let debounceTimer: ReturnType<typeof setTimeout>;

// Password change modal state
const showPasswordModal = ref(false);
const resetStep = ref(1);
const resetForm = ref({ email: '', code: '', newPassword: '', confirmPassword: '' });
const resetError = ref('');
const isSubmitting = ref(false);
const canEditEmail = computed(() => ['staff', 'admin'].includes(authStore.role.trim().toLowerCase()));
const profileInitial = computed(() => user.value?.email?.charAt(0).toUpperCase() || 'U');
const roleLabel = computed(() => {
  const role = authStore.role.trim().toLowerCase();
  return role === 'admin' ? 'Administrator' : role === 'staff' ? 'Staff member' : 'Customer';
});

const openPasswordModal = () => {
    resetForm.value = { email: user.value?.email || '', code: '', newPassword: '', confirmPassword: '' };
    resetStep.value = 1;
    resetError.value = '';
    showPasswordModal.value = true;
};

const closePasswordModal = () => {
    showPasswordModal.value = false;
};

// Password change logic
const validatePassword = (password: string) => {
  if (password.length < 8) return 'Password must be 8 characters or longer.'
  if (!/\d/.test(password)) return 'Password must include one number.'
  if (!/[A-Z]/.test(password)) return 'Password must include one uppercase letter.'
  return ''
};

const sendCode = async () => {
    isSubmitting.value = true;
    try {
        await authStore.sendVerificationCode(resetForm.value.email);
        resetStep.value = 2;
    } catch (e) {
        resetError.value = getUserFriendlyApiError(e, 'Failed to send code');
    } finally {
        isSubmitting.value = false;
    }
};

const verifyCode = async () => {
    isSubmitting.value = true;
    try {
        await authStore.confirmVerificationCode({
            email: resetForm.value.email,
            code: resetForm.value.code,
            action: 'changepassword',
        });
        resetStep.value = 3;
    } catch (e) {
        resetError.value = getUserFriendlyApiError(e, 'Invalid code');
    } finally {
        isSubmitting.value = false;
    }
};

const changePassword = async () => {
    if (resetForm.value.newPassword !== resetForm.value.confirmPassword) {
        resetError.value = 'Passwords do not match';
        return;
    }
    const passError = validatePassword(resetForm.value.newPassword);
    if (passError) {
        resetError.value = passError;
        return;
    }
    isSubmitting.value = true;
    try {
        await authStore.resetPassword({
            email: resetForm.value.email,
            code: resetForm.value.code,
            password: resetForm.value.newPassword,
            password_confirmation: resetForm.value.confirmPassword,
        });
        closePasswordModal();
    } catch (e) {
        resetError.value = getUserFriendlyApiError(e, 'Failed to change password');
    } finally {
        isSubmitting.value = false;
    }
};

onMounted(async () => {
  user.value = await getProfile();
  authStore.user = user.value;
  
  // Strip +63 for input
  form.value.mobile_phone = (user.value.mobile_phone || '').replace('+63', '');
  form.value.email = user.value.email;
});

// Auto-save logic
watch(() => [form.value.mobile_phone, form.value.email], () => {
  clearTimeout(debounceTimer);
  debounceTimer = setTimeout(async () => {
    await autoSave();
  }, 1000);
});

const autoSave = async () => {
  const updateData: any = {};
  
  // Mobile phone validation
  const cleanPhone = form.value.mobile_phone.trim().replace(/\D/g, '');
  const phPhoneRegex = /^9\d{9}$/;
  if (cleanPhone && phPhoneRegex.test(cleanPhone)) {
    updateData.mobile_phone = `+63${cleanPhone}`;
  } else if (cleanPhone) {
    console.warn('Invalid phone format');
  }

  // Email validation
  if (form.value.email && form.value.email !== user.value?.email) {
    updateData.email = form.value.email;
  }

  if (Object.keys(updateData).length > 0 && user.value) {
    const updatedUser = await updateProfile(updateData);
    user.value = updatedUser;
    authStore.user = updatedUser;
  }
};
const handleImageUpload = async (event: any) => {
  const file = event.target.files[0];
  if (file && user.value) {
    try {
      const data = await uploadProfileImage(file);
      console.log('Image upload response:', data);
      user.value.profile_image = data.url;
      authStore.user = { ...user.value }; // Ensure reactivity
    } catch (error) {
      console.error('Image upload failed:', error);
    }
  }
};

const getImageUrl = (url?: string) => {
    if (!url) return '';
    // If it's a data URI, return as is
    if (url.startsWith('data:')) return url;
    // Otherwise, handle as API path
    const cleanUrl = url.replace('/api', '');
    return `${import.meta.env.VITE_API_BASE_URL}${cleanUrl}`;
};
</script>
