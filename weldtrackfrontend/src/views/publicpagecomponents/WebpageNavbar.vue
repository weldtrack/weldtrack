<script setup lang="ts">
import { ref } from 'vue'
import { Menu, X } from 'lucide-vue-next'
import ThemeToggle from '../../components/ui/ThemeToggle.vue'

const isMobileMenuOpen = ref(false)
</script>

<template>
    <nav class="public-nav fixed top-0 left-0 w-full z-50 border-b border-slate-800/60 public-nav-bg px-6 py-3 backdrop-blur-md transition-all sm:px-10">
        <div class="mx-auto flex max-w-7xl items-center justify-between">
            <RouterLink to="/" class="flex items-center gap-3" aria-label="WeldTrack home">
                <img src="/weldtrack.png" alt="WeldTrack Logo" class="h-9 w-auto object-contain" />
            </RouterLink>

            <div class="hidden items-center gap-8 lg:flex">
                <RouterLink to="/#home" class="text-sm font-medium text-slate-300 transition-colors hover:text-white">Home</RouterLink>
                <RouterLink to="/#about" class="text-sm font-medium text-slate-300 transition-colors hover:text-white">How it works</RouterLink>
                <RouterLink to="/services" class="text-sm font-medium text-slate-300 transition-colors hover:text-white">Services</RouterLink>
                <RouterLink to="/#contact" class="text-sm font-medium text-slate-300 transition-colors hover:text-white">Contact</RouterLink>
            </div>

            <div class="hidden items-center gap-3 lg:flex">
                <ThemeToggle />
                <RouterLink to="/login" class="px-3.5 py-1.5 text-sm font-semibold text-slate-300 transition-colors hover:text-white">Sign In</RouterLink>
                <RouterLink to="/signup" class="rounded-lg bg-sky-600 px-4 py-2 text-sm font-semibold text-white transition-all hover:bg-sky-500 active:scale-95 shadow-sm">Request a job</RouterLink>
            </div>

            <button type="button" class="flex h-10 w-10 items-center justify-center rounded-xl border border-white/10 bg-white/5 text-white transition hover:bg-white/10 lg:hidden" :aria-label="isMobileMenuOpen ? 'Close navigation' : 'Open navigation'" :aria-expanded="isMobileMenuOpen" aria-controls="public-mobile-menu" @click="isMobileMenuOpen = !isMobileMenuOpen">
                <Menu v-if="!isMobileMenuOpen" class="h-5 w-5" />
                <X v-else class="h-5 w-5" />
            </button>
        </div>

        <div v-if="isMobileMenuOpen" id="public-mobile-menu" class="public-mobile-menu absolute left-0 top-full w-full space-y-6 border-b border-white/5 bg-public-dark px-6 py-8 shadow-2xl lg:hidden">
            <div class="flex justify-end">
                <ThemeToggle />
            </div>
            <div class="flex flex-col gap-6">
                <RouterLink to="/#home" class="text-lg font-medium text-slate-400 transition-colors hover:text-[color:var(--public-text)]" @click="isMobileMenuOpen = false">Home</RouterLink>
                <RouterLink to="/#about" class="text-lg font-medium text-slate-400 transition-colors hover:text-[color:var(--public-text)]" @click="isMobileMenuOpen = false">How it works</RouterLink>
                <RouterLink to="/services" class="text-lg font-medium text-slate-400 transition-colors hover:text-[color:var(--public-text)]" @click="isMobileMenuOpen = false">Services</RouterLink>
                <RouterLink to="/#contact" class="text-lg font-medium text-slate-400 transition-colors hover:text-[color:var(--public-text)]" @click="isMobileMenuOpen = false">Contact</RouterLink>
            </div>
            <div class="flex flex-col gap-4 pt-4 border-t border-white/5">
                <RouterLink to="/login" class="flex h-12 items-center justify-center font-semibold text-slate-400 transition-colors hover:text-[color:var(--public-text)]" @click="isMobileMenuOpen = false">Sign In</RouterLink>
                <RouterLink to="/signup" class="flex h-12 items-center justify-center rounded-lg bg-[color:var(--public-text)] font-bold text-[color:var(--public-bg)]" @click="isMobileMenuOpen = false">Request a job</RouterLink>
            </div>
        </div>
    </nav>
</template>
