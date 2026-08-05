<script setup lang="ts">
import { useThemeMode } from '../composables/useThemeMode'

const { isDarkMode } = useThemeMode()
</script>

<template>
    <div :class="['public-theme-page relative min-h-screen flex items-center justify-center overflow-hidden', isDarkMode ? 'theme-dark' : 'theme-light']">
        <!-- Background Decorations -->
        <div class="pointer-events-none absolute inset-0 overflow-hidden">
            <div class="absolute -left-[10%] top-[-10%] h-[500px] w-[500px] rounded-full bg-cyan-500/10 blur-[120px] animate-pulse"></div>
            <div class="absolute -right-[5%] top-[20%] h-[600px] w-[600px] rounded-full bg-blue-600/10 blur-[140px]"></div>
            <div class="absolute inset-0 bg-[url('https://grainy-gradients.vercel.app/noise.svg')] opacity-20 mix-blend-overlay"></div>
        </div>
        
        <!-- Main Content -->
        <div class="relative z-10 text-center p-8 max-w-lg">
            <div class="mb-8 inline-block p-4 rounded-2xl bg-white/5 backdrop-blur-md border border-white/10 shadow-xl">
                <span class="text-6xl">🔍</span>
            </div>
            
            <h1 class="text-9xl font-extrabold tracking-tighter text-transparent bg-clip-text bg-gradient-to-b from-white to-slate-500 drop-shadow-2xl animate-fade-in">
                404
            </h1>
            
            <p class="mt-6 text-2xl font-light text-slate-300">
                Oops! The page you're looking for doesn't exist or has been moved.
            </p>
            
            <router-link to="/" class="mt-10 inline-flex items-center gap-2 rounded-full bg-cyan-600 px-8 py-4 font-semibold text-white hover:bg-cyan-500 hover:scale-105 transition-all duration-300 shadow-[0_0_20px_rgba(8,145,178,0.4)]">
                <span>←</span> Take me home
            </router-link>
        </div>
    </div>
</template>

<style scoped>
@keyframes fade-in {
    from { opacity: 0; transform: translateY(20px); }
    to { opacity: 1; transform: translateY(0); }
}
.animate-fade-in {
    animation: fade-in 0.8s ease-out forwards;
}
</style>

<style>
@import './auth/login-theme.css';
/* selection color for public pages */
::selection { background: rgba(34, 211, 238, 0.3); color: var(--public-text); }
</style>
