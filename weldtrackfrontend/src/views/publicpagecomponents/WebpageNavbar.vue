<script setup lang="ts">
import { ref } from 'vue'
import ThemeToggle from '../../components/ui/ThemeToggle.vue'

const isMobileMenuOpen = ref(false)
</script>

<template>
    <nav class="public-nav sticky top-0 z-50 border-b border-white/5 bg-[#020617]/80 px-6 py-4 backdrop-blur-md transition-all sm:px-12">
        <div class="mx-auto flex max-w-7xl items-center justify-between">
            <div class="flex items-center gap-2.5">
                <div class="flex h-9 w-9 items-center justify-center rounded-xl bg-linear-to-br from-cyan-400 to-blue-600 p-0.5 shadow-lg shadow-cyan-500/20">
                    <div class="flex h-full w-full items-center justify-center rounded-[10px] bg-[#020617] text-lg">⚙️</div>
                </div>
                <span class="text-xl font-bold tracking-tight">WeldTrack</span>
            </div>

            <div class="hidden items-center gap-10 lg:flex">
                <RouterLink to="/#home" class="text-[15px] font-medium text-slate-400 transition-colors hover:text-white">Home</RouterLink>
                <RouterLink to="/#about" class="text-[15px] font-medium text-slate-400 transition-colors hover:text-white">Why WeldTrack</RouterLink>
                <RouterLink to="/#services" class="text-[15px] font-medium text-slate-400 transition-colors hover:text-white">Services</RouterLink>
                <RouterLink to="/#contact" class="text-[15px] font-medium text-slate-400 transition-colors hover:text-white">Contact</RouterLink>
            </div>

            <div class="hidden items-center gap-4 lg:flex">
                <ThemeToggle />
                <RouterLink to="/login" class="text-[15px] font-semibold text-slate-300 transition-colors hover:text-white">Sign In</RouterLink>
                <RouterLink to="/signup" class="rounded-full bg-slate-50 px-6 py-2 text-[15px] font-bold text-[#020617] transition-all hover:bg-white hover:shadow-xl hover:shadow-white/10 active:scale-95">Get Started</RouterLink>
            </div>

            <button type="button" class="flex h-10 w-10 items-center justify-center rounded-lg bg-white/5 text-white lg:hidden" @click="isMobileMenuOpen = !isMobileMenuOpen">
                <svg v-if="!isMobileMenuOpen" class="h-6 w-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 6h16M4 12h16M4 18h16" />
                </svg>
                <svg v-else class="h-6 w-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12" />
                </svg>
            </button>
        </div>

        <div v-if="isMobileMenuOpen" class="absolute left-0 top-full w-full border-b border-white/5 bg-[#020617] px-6 py-8 space-y-6 lg:hidden">
            <div class="flex justify-end">
                <ThemeToggle />
            </div>
            <div class="flex flex-col gap-6">
                <RouterLink to="/#home" class="text-lg font-medium text-slate-300" @click="isMobileMenuOpen = false">Home</RouterLink>
                <RouterLink to="/#about" class="text-lg font-medium text-slate-300" @click="isMobileMenuOpen = false">Why WeldTrack</RouterLink>
                <RouterLink to="/#services" class="text-lg font-medium text-slate-300" @click="isMobileMenuOpen = false">Services</RouterLink>
                <RouterLink to="/#contact" class="text-lg font-medium text-slate-300" @click="isMobileMenuOpen = false">Contact</RouterLink>
            </div>
            <div class="flex flex-col gap-4 pt-4 border-t border-white/5">
                <RouterLink to="/login" class="flex h-12 items-center justify-center font-semibold text-white" @click="isMobileMenuOpen = false">Sign In</RouterLink>
                <RouterLink to="/signup" class="flex h-12 items-center justify-center rounded-xl bg-slate-50 font-bold text-[#020617]" @click="isMobileMenuOpen = false">Get Started</RouterLink>
            </div>
        </div>
    </nav>
</template>