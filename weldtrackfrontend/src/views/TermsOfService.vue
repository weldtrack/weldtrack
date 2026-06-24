<script setup lang="ts">
import PublicLayout from '../components/layout/PublicLayout.vue'
</script>

<template>
    <PublicLayout>
        <div class="mx-auto max-w-4xl p-6 text-slate-300">
            <h1 class="text-4xl font-bold text-white mb-6">Terms of Service</h1>
            <p class="mb-4 text-sm text-slate-400">Last updated: June 24, 2026</p>
            
            <section class="mb-8">
                <h2 class="text-2xl font-semibold text-white mb-3">1. Acceptance of Terms</h2>
                <p>By accessing or using WeldTrack, you agree to be bound by these Terms of Service. If you do not agree to these terms, please do not use our services.</p>
            </section>

            <section class="mb-8">
                <h2 class="text-2xl font-semibold text-white mb-3">2. Service Description</h2>
                <p>WeldTrack provides a digital management platform for welding operations, including task tracking, inventory management, and reporting. We reserve the right to modify, suspend, or discontinue any aspect of the service at any time.</p>
            </section>

            <section class="mb-8">
                <h2 class="text-2xl font-semibold text-white mb-3">3. User Obligations</h2>
                <p class="mb-2">As a user, you agree to:</p>
                <ul class="list-disc pl-6 space-y-1">
                    <li>Provide accurate and complete information during registration.</li>
                    <li>Maintain the security of your account credentials.</li>
                    <li>Use the platform solely for its intended professional purposes.</li>
                </ul>
            </section>

            <section>
                <h2 class="text-2xl font-semibold text-white mb-3">4. Limitation of Liability</h2>
                <p>WeldTrack is provided "as is." We are not liable for any damages arising out of the use or inability to use our platform, including data loss or operational disruptions.</p>
            </section>
        </div>
    </PublicLayout>
</template>
