<template>
	<div class="app-shell">
		<main class="app-main">
			<RouterView />
		</main>
		<GlobalLoading />
		<GlobalModal />
	</div>
</template>

<script setup lang="ts">
import { onMounted } from 'vue'
import GlobalLoading from './components/ui/GlobalLoading.vue'
import GlobalModal from './components/ui/GlobalModal.vue'
import api from './services/api'
import { useAuthStore } from './stores/auth'
import { useRouter } from 'vue-router'

const authStore = useAuthStore()
const router = useRouter()

onMounted(async () => {
	if (authStore.isLoggedIn) {
		try {
			await api.get('/auth/me')
		} catch (error) {
			authStore.logout()
			router.push({ name: 'login' }).catch(() => {})
		}
	}
})
</script>
