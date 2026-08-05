<script setup lang="ts">
import { useThemeMode } from '../../composables/useThemeMode'
import WebpageNavBar from '../../views/publicpagecomponents/WebpageNavbar.vue'
import WebpageFooter from '../../views/publicpagecomponents/WebpageFooter.vue'

const { isDarkMode } = useThemeMode()
</script>

<template>
    <div :class="['public-theme-page relative min-h-screen overflow-hidden', isDarkMode ? 'theme-dark' : 'theme-light']">
        <div class="pointer-events-none absolute inset-0 overflow-hidden">
            <div class="absolute -left-[10%] top-[-10%] h-[500px] w-[500px] rounded-full bg-cyan-500/10 blur-[120px]"></div>
            <div class="absolute -right-[5%] top-[20%] h-[600px] w-[600px] rounded-full bg-blue-600/10 blur-[140px]"></div>
            <div class="absolute bottom-[-10%] left-[20%] h-[400px] w-[400px] rounded-full bg-emerald-500/5 blur-[100px]"></div>
            <div class="absolute inset-0 bg-[url('https://grainy-gradients.vercel.app/noise.svg')] opacity-20 mix-blend-overlay"></div>
        </div>
        <WebpageNavBar />
        <main class="min-h-[60vh] pt-24">
            <slot />
        </main>
        <WebpageFooter />
    </div>
</template>
