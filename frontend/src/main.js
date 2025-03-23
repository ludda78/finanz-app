import { createApp } from 'vue'
import App from './App.vue'
import router from "./router"; // Router importieren


const app = createApp(App);

app.use(router); // 🔥 Router in die App einbinden
console.log("✅ Router wurde geladen:", router.getRoutes());
app.mount("#app");

//createApp(App).use(router).mount("#app");
