import { createApp } from 'vue'
import App from './App.vue'

import 'lib-flexible/flexible.js'

const app = createApp(App)
for (const [key, component] of Object.entries(ElementPlusIconsVue)) {
  app.component(key, component)
}

app.mount('#app')
