<template>
	<div class="app-shell">
		<main class="app-main">
			<RouterView />
		</main>
		<GlobalModal />
	</div>
</template>

<script setup lang="ts">
import GlobalModal from './components/ui/GlobalModal.vue'
</script>
