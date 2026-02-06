import { createRouter, createWebHistory } from 'vue-router'
import WeeklyCalendar from '../views/WeeklyCalendar.vue'

const router = createRouter({
  history: createWebHistory(),
  routes: [
    {
      path: '/',
      name: 'weekly-calendar',
      component: WeeklyCalendar
    }
  ]
})

export default router

