import { createRouter, createWebHistory } from 'vue-router'

const router = createRouter({
  history: createWebHistory(),
  routes: [
    {
      path: '/',
      name: 'weekly-calendar',
      component: () => import('../views/WeeklyCalendar.vue')
    },
    {
      path: '/kanban',
      name: 'kanban-desk',
      component: () => import('../views/KanbanDesk.vue')
    },
    {
      path: '/statistics',
      name: 'statistics',
      component: () => import('../views/Statistics.vue')
    }
  ]
})

export default router
