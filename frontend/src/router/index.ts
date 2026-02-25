import { createRouter, createWebHistory } from 'vue-router'
import WeeklyCalendar from '../views/WeeklyCalendar.vue'
import KanbanDesk from '../views/KanbanDesk.vue'
import Statistics from '../views/Statistics.vue'

const router = createRouter({
  history: createWebHistory(),
  routes: [
    {
      path: '/',
      name: 'weekly-calendar',
      component: WeeklyCalendar
    },
    {
      path: '/kanban',
      name: 'kanban-desk',
      component: KanbanDesk
    },
    {
      path: '/statistics',
      name: 'statistics',
      component: Statistics
    }
  ]
})

export default router

