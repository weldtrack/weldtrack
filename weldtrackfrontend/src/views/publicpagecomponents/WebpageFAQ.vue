<script setup lang="ts">
import { reactive } from 'vue'
import { ChevronDown } from 'lucide-vue-next'

const faqs = reactive([
    {
        question: 'How do I track the progress of my project?',
        answer: 'Sign in to your customer account and open Booking History. Each request shows whether it is pending review, approved, scheduled, in progress, or completed.',
        open: false
    },
    {
        question: 'When do I see the material costs?',
        answer: 'The initial booking will show you the estimated labor cost. Material costs are added by our staff once they assess or complete the project. You will see the final total in your portal.',
        open: false
    },
    {
        question: 'Can I cancel my booking if my plans change?',
        answer: 'Yes. If the booking is still pending, you can cancel it from your dashboard and provide a reason.',
        open: false
    },
    {
        question: 'Do I need to be home for the welding service?',
        answer: 'It is highly recommended that you or a representative is present during the scheduled time to ensure the staff can access the project area and confirm details with you.',
        open: false
    }
])

const toggleFaq = (index: number) => {
    faqs[index].open = !faqs[index].open
}
</script>

<template>
    <section class="relative bg-public-bg py-16 sm:py-24 border-t border-slate-800/60">
        <div class="mx-auto max-w-3xl px-6 sm:px-10">
            <div data-reveal class="reveal mx-auto text-center mb-10">
                <h2 class="text-3xl font-bold tracking-tight text-[color:var(--public-text)] sm:text-4xl">Frequently asked questions</h2>
                <p class="mt-3 text-base text-slate-400">Everything you need to know about booking with WeldTrack.</p>
            </div>

            <div class="space-y-3">
                <div v-for="(faq, index) in faqs" :key="index" data-reveal class="reveal rounded-xl border border-slate-800 bg-slate-900/60 overflow-hidden transition-all">
                    <button 
                        @click="toggleFaq(index)"
                        :aria-expanded="faq.open"
                        class="flex w-full items-center justify-between px-5 py-4 text-left text-sm font-semibold text-[color:var(--public-text)] hover:bg-slate-800/50 transition-colors"
                    >
                        {{ faq.question }}
                        <ChevronDown 
                            class="h-4 w-4 text-slate-400 transition-transform duration-200" 
                            :class="{ 'rotate-180': faq.open }" 
                        />
                    </button>
                    <div 
                        v-show="faq.open" 
                        class="px-5 pb-5 text-sm text-slate-300 leading-6 border-t border-slate-800/40 pt-3"
                    >
                        {{ faq.answer }}
                    </div>
                </div>
            </div>
        </div>
    </section>
</template>
