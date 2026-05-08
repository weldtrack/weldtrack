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
import GlobalLoading from './components/ui/GlobalLoading.vue'
import GlobalModal from './components/ui/GlobalModal.vue'
</script>
