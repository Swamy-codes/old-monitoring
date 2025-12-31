import { createApp } from 'vue'
import { createPinia } from 'pinia';
import router from './router/router.js'
import './tailwind.css'
import App from './App.vue'
import jQuery from 'jquery';
import $ from 'jquery';
import './components/Charts/jQueryCharts/waterBubble.js'

// createApp(App).mount('#app')

window.$ = $ 
// window.jQuery = jQuery;

const pinia = createPinia()
const app = createApp(App)
app.use(router)
app.use(pinia)
app.mount('#app')