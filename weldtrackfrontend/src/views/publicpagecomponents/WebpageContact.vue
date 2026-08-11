<script setup lang="ts">
import { Clock3, Mail, MapPin, Phone } from 'lucide-vue-next'
</script>

<template>
    <section id="contact" class="relative py-16 sm:py-24 border-t border-slate-800/60">
        <div class="mx-auto max-w-7xl px-6 sm:px-10">
            <div data-reveal class="reveal relative overflow-hidden rounded-xl border border-slate-800 bg-slate-900/90 p-6 sm:p-10 lg:p-14 shadow-xl">
                <div class="relative z-10 mx-auto max-w-4xl text-center">
                    <div class="mb-3 inline-flex items-center rounded-md border border-sky-500/30 bg-sky-500/10 px-3 py-1 text-xs font-semibold uppercase tracking-wider text-sky-400">
                        Contact Support
                    </div>
                    <h2 class="mb-4 text-3xl font-bold tracking-tight text-white sm:text-4xl">
                        Need help with a booking?
                    </h2>
                    <p class="mx-auto mb-10 max-w-xl text-base text-slate-300">
                        Reach out directly via phone, email, or visit our shop during business hours.
                    </p>
                    <div class="grid grid-cols-1 gap-4 sm:grid-cols-3">
                        <a href="tel:+639357705022" class="rounded-lg border border-slate-800 bg-slate-950/60 px-5 py-5 text-left transition hover:border-slate-700 hover:bg-slate-950">
                            <Phone class="mb-3 h-5 w-5 text-sky-400" />
                            <div class="text-xs font-semibold uppercase tracking-wider text-sky-400">Direct Line</div>
                            <div class="mt-1.5 text-base font-bold text-white">+63 935 770 5022</div>
                            <div class="mt-1 text-xs text-slate-400">Call for quick inquiries</div>
                        </a>
                        <a href="mailto:Goboleweldingshopadmin@gmail.com" class="rounded-lg border border-slate-800 bg-slate-950/60 px-5 py-5 text-left transition min-w-0 hover:border-slate-700 hover:bg-slate-950">
                            <Mail class="mb-3 h-5 w-5 text-sky-400" />
                            <div class="text-xs font-semibold uppercase tracking-wider text-sky-400">Email</div>
                            <div class="mt-1.5 text-sm font-bold text-white break-all">Goboleweldingshopadmin@gmail.com</div>
                            <div class="mt-1 text-xs text-slate-400">Send detailed requests</div>
                        </a>
                        <div class="rounded-lg border border-slate-800 bg-slate-950/60 px-5 py-5 text-left">
                            <MapPin class="mb-3 h-5 w-5 text-sky-400" />
                            <div class="text-xs font-semibold uppercase tracking-wider text-sky-400">Location</div>
                            <div class="mt-1.5 text-sm font-bold text-white">Sta. Remedios, Bulan Sorsogon</div>
                            <div class="mt-1 text-xs text-slate-400">Visit during shop hours</div>
                        </div>
                    </div>
                </div>
            </div>

            <div class="mt-10 flex justify-center">
                <div class="w-full max-w-md rounded-lg border border-slate-800 bg-slate-900/60 px-5 py-4 text-center">
                    <Clock3 class="mx-auto mb-2 h-4 w-4 text-sky-400" />
                    <div class="text-xs font-semibold uppercase tracking-wider text-slate-400">Operating Hours</div>
                    <div class="mt-1 text-sm font-semibold text-white">Monday — Saturday: 8:00 AM – 5:00 PM</div>
                </div>
            </div>
        </div>
    </section>
</template>
