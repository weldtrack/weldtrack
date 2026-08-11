<script setup lang="ts">
import { reactive } from 'vue'
import { ChevronDown } from 'lucide-vue-next'

const faqs = reactive([
    {
        question: 'How do I track the progress of my project?',
        answer: 'Once you book a service, you will get access to a private Customer Portal. You can log in anytime to see the live status, whether it is pending approval, scheduled, or actively in-progress.',
        open: false
    },
    {
        question: 'When do I see the material costs?',
        answer: 'The initial booking will show you the estimated labor cost. Material costs are added by our staff once they assess or complete the project. You will see the final total in your portal.',
        open: false
    },
    {
        question: 'Can I cancel my booking if my plans change?',
        answer: 'Yes! As long as the booking is still in the "Pending" state, you can cancel it directly from your dashboard and provide a reason.',
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
    <section class="relative bg-public-bg py-16 sm:py-24">
        <div class="mx-auto max-w-3xl px-6 sm:px-12">
            <div data-reveal class="reveal mx-auto text-center mb-12">
                <h2 class="text-3xl font-bold tracking-tight text-[color:var(--public-text)] sm:text-4xl">Frequently asked questions</h2>
                <p class="mt-4 text-lg text-slate-500">Everything you need to know about booking with WeldTrack.</p>
            </div>

            <div class="space-y-4">
                <div v-for="(faq, index) in faqs" :key="index" data-reveal class="reveal rounded-2xl border border-slate-200/20 dark:border-white/10 bg-public-panel overflow-hidden backdrop-blur-xl transition-all">
                    <button 
                        @click="toggleFaq(index)" 
                        class="flex w-full items-center justify-between px-6 py-5 text-left font-semibold text-[color:var(--public-text)] hover:bg-slate-500/5 transition-colors"
                    >
                        {{ faq.question }}
                        <ChevronDown 
                            class="h-5 w-5 text-slate-400 transition-transform duration-300" 
                            :class="{ 'rotate-180': faq.open }" 
                        />
                    </button>
                    <div 
                        v-show="faq.open" 
                        class="px-6 pb-6 text-slate-500 dark:text-slate-400 leading-7"
                    >
                        {{ faq.answer }}
                    </div>
                </div>
            </div>
        </div>
    </section>
</template>
