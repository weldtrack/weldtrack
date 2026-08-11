<script setup lang="ts">
import { onBeforeUnmount, onMounted, ref, provide } from 'vue'
import { useThemeMode } from '../composables/useThemeMode'
import WebpageNavBar from './publicpagecomponents/WebpageNavbar.vue'
import WebpageHero from './publicpagecomponents/WebpageHero.vue'
import WebpageAbout from './publicpagecomponents/WebpageAbout.vue'
import WebpageServices from './publicpagecomponents/WebpageServices.vue'
import WebpageContact from './publicpagecomponents/WebpageContact.vue'
import WebpageTestimonials from './publicpagecomponents/WebpageTestimonials.vue'
import WebpageFAQ from './publicpagecomponents/WebpageFAQ.vue'
import WebpageCTA from './publicpagecomponents/WebpageCTA.vue'
import WebpageFooter from './publicpagecomponents/WebpageFooter.vue'

const { isDarkMode } = useThemeMode()
const observerRef = ref<IntersectionObserver | null>(null)
provide('observer', observerRef)

onMounted(() => {
    observerRef.value = new IntersectionObserver(
        (entries) => {
            entries.forEach((entry) => {
                if (entry.isIntersecting) {
                    entry.target.classList.add('is-visible')
                    observerRef.value?.unobserve(entry.target)
                }
            })
        },
        { threshold: 0.1, rootMargin: '0px 0px -50px 0px' },
    )
    document.querySelectorAll<HTMLElement>('[data-reveal]').forEach((el) => {
        observerRef.value?.observe(el)
    })
})

onBeforeUnmount(() => {
    observerRef.value?.disconnect()
    observerRef.value = null
})
</script>

<template>
    <div :class="['public-theme-page relative min-h-screen overflow-x-hidden', isDarkMode ? 'theme-dark' : 'theme-light']">
        <div class="pointer-events-none absolute inset-0 overflow-hidden">
            <div class="landing-grid absolute inset-x-0 top-0 h-[40rem] opacity-15"></div>
        </div>
        <WebpageNavBar />
        <WebpageHero />
        <WebpageAbout />
        <WebpageServices />
        <WebpageTestimonials />
        <WebpageFAQ />
        <WebpageContact />
        <WebpageCTA />
        <WebpageFooter />
    </div>
</template>

<style>
html { scroll-behavior: smooth; }

.reveal {
    opacity: 0;
    transform: translateY(30px);
    transition: opacity 800ms cubic-bezier(0.2, 1, 0.3, 1), transform 800ms cubic-bezier(0.2, 1, 0.3, 1);
}
.reveal.is-visible {
    opacity: 1;
    transform: translateY(0);
}
.fade-enter-active, .fade-leave-active { transition: opacity 500ms ease; }
.fade-enter-from, .fade-leave-to { opacity: 0; }
::selection { background: rgba(34, 211, 238, 0.3); color: var(--public-text); }
::-webkit-scrollbar { width: 8px; }
::-webkit-scrollbar-track { background: var(--public-bg); }
::-webkit-scrollbar-thumb { background: var(--scroll-thumb); border-radius: 10px; }
::-webkit-scrollbar-thumb:hover { background: var(--scroll-thumb-hover); }
.landing-grid {
    background-image:
        linear-gradient(rgb(148 163 184 / 0.045) 1px, transparent 1px),
        linear-gradient(90deg, rgb(148 163 184 / 0.045) 1px, transparent 1px);
    background-size: 48px 48px;
    mask-image: linear-gradient(to bottom, black, transparent 86%);
}


</style>
