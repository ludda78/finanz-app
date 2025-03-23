import { createRouter, createWebHistory } from "vue-router";
import MonatsUebersicht from "./components/MonatsUebersicht.vue";
import FesteKonfiguration from './components/FesteKonfiguration.vue';

const routes = [
{
  path: "/",
  name: "CurrentMonthView",
  component: MonatsUebersicht,
  props: (route) => {
    const today = new Date();
    return { 
      monat: today.getMonth() + 1, // JavaScript months are 0-indexed
      jahr: today.getFullYear()
    };
  }
},
{
    path: "/monatsuebersicht/:monat/:jahr",
    name: "MonatsUebersicht",
    component: MonatsUebersicht,
    props: true,
  },
  {
    path: '/konfiguration',
    name: 'Konfiguration',
    component: FesteKonfiguration
  }
];

const router = createRouter({
  history: createWebHistory(),
  routes
});

export default router;
