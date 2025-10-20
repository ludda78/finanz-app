import { createRouter, createWebHistory } from "vue-router";
import MonatsUebersicht from "./components/MonatsUebersicht.vue";
import FesteKonfiguration from './components/FesteKonfiguration.vue';
import JahresUebersicht from './components/JahresUebersicht.vue'; 
import InfoPage from './components/InfoPage.vue';


const routes = [
  {
    path: "/",
    name: "CurrentMonthView",
    component: MonatsUebersicht, // Ensure correct component name here
    props: () => {
      const today = new Date();
      return { 
        monat: today.getMonth() + 1,
        jahr: today.getFullYear()
      };
    }
  },
  {
    path: "/monatsuebersicht/:monat/:jahr",
    name: "MonatsUebersicht",
    component: MonatsUebersicht, // Ensure correct component name here
    props: true,
  },
  {
    path: "/monatsuebersicht",
    name: "DefaultMonatsUebersicht",
    redirect: () => {
      const today = new Date();
      return {
        name: "MonatsUebersicht",
        params: {
          monat: today.getMonth() + 1,
          jahr: today.getFullYear()
        }
      };
    }
  },
  {
    path: '/konfiguration',
    name: 'Konfiguration',
    component: FesteKonfiguration
  },
  {
    path: '/jahresuebersicht/:jahr?',
    name: 'Jahresuebersicht',
    component: JahresUebersicht,
    props: (route) => ({
      jahr: route.params.jahr ? parseInt(route.params.jahr) : new Date().getFullYear()
    })
  },
   { path: '/info', name: 'Info', component: InfoPage },
];

const router = createRouter({
  history: createWebHistory(),
  routes
});

export default router;