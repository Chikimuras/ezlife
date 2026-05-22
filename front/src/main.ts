import { createApp } from 'vue'
import { createPinia } from 'pinia'
import { i18n } from './lib/i18n'
import './assets/styles/main.css'
import App from './App.vue'
import router from './router'

const app = createApp(App)

app.use(createPinia())
app.use(router)
app.use(i18n)

app.mount('#app')
