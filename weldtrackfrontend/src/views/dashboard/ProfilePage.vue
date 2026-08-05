<template>
  <div class="max-w-2xl mx-auto p-6">
    <div class="flex items-center gap-3 mb-8">
      <div class="flex h-12 w-12 items-center justify-center rounded-lg bg-linear-to-br from-sky-50 to-white ring-1 ring-sky-100">
        <User class="dashboard-view-icon h-6 w-6 text-sky-600 dark:text-sky-400" />
      </div>
      <h1 class="text-2xl font-semibold text-gray-900">User Profile</h1>
    </div>
    
    <div v-if="user" class="bg-white border border-slate-200 shadow-sm rounded-2xl p-8">
      <div class="flex flex-col items-center mb-8">
        <div class="relative group">
          <img :src="getImageUrl(user.profile_image)" alt="Profile" class="w-32 h-32 rounded-full object-cover border-4 border-slate-100 shadow-md">
          <label class="absolute bottom-0 right-0 bg-blue-600 p-2 rounded-full cursor-pointer shadow-lg hover:bg-blue-700 transition">
            <svg class="h-5 w-5 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M3 9a2 2 0 012-2h.93a2 2 0 001.66-.9l.82-1.23A2 2 0 0110.93 4h2.14a2 2 0 011.66.9l.82 1.23A2 2 0 0018.07 7H19a2 2 0 012 2v9a2 2 0 01-2 2H5a2 2 0 01-2-2V9z"/><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15 13a3 3 0 11-6 0 3 3 0 016 0z"/></svg>
            <input type="file" @change="handleImageUpload" accept="image/*" class="hidden">
          </label>
        </div>
        <p class="mt-4 text-xl font-semibold text-slate-900">{{ user.email }}</p>
      </div>

      <div class="space-y-6">
        <div>
          <label class="block text-sm font-medium text-slate-700 mb-2" for="email">Email</label>
          <div :class="['flex rounded-xl border border-slate-200 bg-slate-50 shadow-sm overflow-hidden transition', !['staff', 'admin'].includes(authStore.role.trim().toLowerCase()) ? 'opacity-70 cursor-not-allowed' : 'focus-within:border-blue-500 focus-within:ring-2 focus-within:ring-blue-200']">
            <input
              id="email"
              v-model="form.email"
              type="email"
              placeholder="newemail@example.com"
              :disabled="!['staff', 'admin'].includes(authStore.role.trim().toLowerCase())"
              :class="['w-full bg-transparent px-4 py-3 outline-none text-slate-900', !['staff', 'admin'].includes(authStore.role.trim().toLowerCase()) ? 'cursor-not-allowed' : '']"
            />
            <button type="button" class="px-4 bg-slate-100 text-slate-500 hover:text-blue-600 transition" :disabled="!['staff', 'admin'].includes(authStore.role.trim().toLowerCase())">
              <Mail class="h-5 w-5" />
            </button>
          </div>
        </div>
        <div>
          <label class="block text-sm font-medium text-slate-700 mb-2">Password</label>
          <button
            @click="openPasswordModal"
            class="w-full flex items-center justify-center gap-2 rounded-xl border border-slate-200 bg-slate-50 px-4 py-3 text-slate-700 hover:bg-slate-100 transition"
          >
            <Key class="h-4 w-4" />
            Change Password
          </button>
        </div>
        <div>
          <label class="block text-sm font-medium text-slate-700 mb-2" for="mobile_phone">Mobile Phone</label>
          <div class="flex rounded-xl border border-slate-200 bg-slate-50 shadow-sm overflow-hidden focus-within:border-blue-500 focus-within:ring-2 focus-within:ring-blue-200 transition">
            <span class="inline-flex items-center px-4 bg-slate-100 text-slate-500 font-semibold text-sm border-r border-slate-200 select-none">
              +63
            </span>
            <input 
              id="mobile_phone" 
              v-model="form.mobile_phone" 
              type="tel" 
              maxlength="10"
              placeholder="9123456789"
              class="w-full bg-transparent px-4 py-3 outline-none text-slate-900" 
            />
            <button type="button" class="px-4 bg-slate-100 text-slate-500 hover:text-blue-600 transition border-l border-slate-200">
              <Phone class="h-5 w-5" />
            </button>
          </div>
          <p class="text-xs text-slate-500 mt-2">Enter a 10-digit number starting with 9 (e.g., 9123456789).</p>
        </div>
      </div>
    </div>
    <div v-else class="text-center py-12 text-slate-500">Loading profile...</div>

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
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted, watch } from 'vue';
import { User, Mail, Key, Phone } from 'lucide-vue-next';
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
    if (!url) return 'https://via.placeholder.com/150';
    // If it's a data URI, return as is
    if (url.startsWith('data:')) return url;
    // Otherwise, handle as API path
    const cleanUrl = url.replace('/api', '');
    return `${import.meta.env.VITE_API_BASE_URL}${cleanUrl}`;
};
</script>
