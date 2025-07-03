import { createApp } from 'vue'
import App from './App.vue'
import router from './router'
import './assets/styles/main.css'
import './assets/styles/global-gradient.css' // 引入全局渐变背景样式

const app = createApp(App)
app.use(router)
app.mount('#app')