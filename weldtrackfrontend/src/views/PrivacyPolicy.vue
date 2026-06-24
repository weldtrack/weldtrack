<script setup lang="ts">
import PublicLayout from '../components/layout/PublicLayout.vue'
</script>

<template>
    <PublicLayout>
        <div class="mx-auto max-w-4xl p-6 text-slate-300">
            <h1 class="text-4xl font-bold text-white mb-6">Privacy Policy</h1>
            <p class="mb-4 text-sm text-slate-400">Last updated: June 24, 2026</p>
            
            <section class="mb-8">
                <h2 class="text-2xl font-semibold text-white mb-3">1. Introduction</h2>
                <p>Welcome to WeldTrack. We are committed to protecting your personal information and your right to privacy. This Privacy Policy explains how we collect, use, and safeguard the data you provide while using our welding management platform.</p>
            </section>

            <section class="mb-8">
                <h2 class="text-2xl font-semibold text-white mb-3">2. Information We Collect</h2>
                <p class="mb-2">We collect information to provide better services to all our users, including:</p>
                <ul class="list-disc pl-6 space-y-1">
                    <li>Account information: Name, email address, and company details.</li>
                    <li>Operational data: Welding task logs, project progress, and inventory metrics managed within the platform.</li>
                    <li>Technical data: Log data, IP address, and browser type for security and maintenance.</li>
                </ul>
            </section>

            <section class="mb-8">
                <h2 class="text-2xl font-semibold text-white mb-3">3. How We Use Your Data</h2>
                <p>We use the collected information to operate, maintain, and improve our services, manage user accounts, and provide customer support. We do not sell your personal data to third parties.</p>
            </section>

            <section>
                <h2 class="text-2xl font-semibold text-white mb-3">4. Security</h2>
                <p>We implement appropriate technical and organizational security measures to protect your data from unauthorized access, alteration, disclosure, or destruction.</p>
            </section>
        </div>
    </PublicLayout>
</template>
