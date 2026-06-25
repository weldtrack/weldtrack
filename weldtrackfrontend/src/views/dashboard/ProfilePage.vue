<template>
  <div class="max-w-2xl mx-auto p-6">
    <div class="flex items-center gap-3 mb-8">
      <div class="flex h-12 w-12 items-center justify-center rounded-lg bg-linear-to-br from-sky-50 to-white ring-1 ring-sky-100">
        <User class="h-6 w-6 text-sky-600" />
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
          </div>
          <p class="text-xs text-slate-500 mt-2">Enter a 10-digit number starting with 9 (e.g., 9123456789).</p>
        </div>
      </div>
    </div>
    <div v-else class="text-center py-12 text-slate-500">Loading profile...</div>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted, watch } from 'vue';
import { User } from 'lucide-vue-next';
import { getProfile, updateProfile, uploadProfileImage } from '../../services/profile.service';
import type { UserRead } from '../../types/auth';
import { useAuthStore } from '../../stores/auth';

const authStore = useAuthStore();
const user = ref<UserRead | null>(null);
const form = ref({ mobile_phone: '' });
let debounceTimer: ReturnType<typeof setTimeout>;

onMounted(async () => {
  user.value = await getProfile();
  authStore.user = user.value;
  
  // Strip +63 for input
  form.value.mobile_phone = (user.value.mobile_phone || '').replace('+63', '');
});

// Auto-save logic
watch(() => form.value.mobile_phone, () => {
  clearTimeout(debounceTimer);
  debounceTimer = setTimeout(async () => {
    await autoSave();
  }, 1000);
});

const autoSave = async () => {
  // Validate 10-digit number starting with 9
  const cleanPhone = form.value.mobile_phone.trim().replace(/\D/g, '');
  const phPhoneRegex = /^9\d{9}$/;
  
  if (cleanPhone && !phPhoneRegex.test(cleanPhone)) {
    console.warn('Invalid phone format');
    return;
  }
  
  if (user.value) {
    const updatedUser = await updateProfile({ mobile_phone: `+63${cleanPhone}` });
    user.value = updatedUser;
    authStore.user = updatedUser;
  }
};

const handleImageUpload = async (event: any) => {
  const file = event.target.files[0];
  if (file) {
    const data = await uploadProfileImage(file);
    if (user.value) {
      user.value.profile_image = data.url;
      authStore.user = user.value;
    }
  }
};

const getImageUrl = (url?: string) => {
    if (!url) return 'https://via.placeholder.com/150';
    const cleanUrl = url.replace('/api', '');
    return `${import.meta.env.VITE_API_BASE_URL}${cleanUrl}`;
};
</script>
