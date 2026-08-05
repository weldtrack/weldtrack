<template>
    <footer class="border-t border-white/5 bg-public-dark py-12">
        <div class="mx-auto max-w-7xl px-6 text-center sm:px-12">
            <div class="flex items-center justify-center gap-2.5 mb-8">
                <div class="flex h-8 w-8 items-center justify-center rounded-lg bg-white/5 text-lg">⚙️</div>
                <span class="text-lg font-bold tracking-tight">WeldTrack</span>
            </div>
            <p class="text-slate-500 text-sm">&copy; 2026 WeldTrack Management Systems. All rights reserved.</p>
            <div class="mt-4 flex justify-center gap-4 text-sm text-slate-500">
                <router-link to="/privacy" class="hover:text-white">Privacy Policy</router-link>
                <router-link to="/terms" class="hover:text-white">Terms of Service</router-link>
            </div>
        </div>
    </footer>
</template>