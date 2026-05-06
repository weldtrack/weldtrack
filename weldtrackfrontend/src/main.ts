import { createApp } from 'vue'
import './style.css'
import App from './App.vue'
import { createPinia } from 'pinia'
import { createRouter } from './router'

const app = createApp(App)

app.use(createPinia())
app.use(createRouter())

app.mount('#app')
