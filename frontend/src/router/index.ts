import { createRouter, createWebHistory } from 'vue-router'

const router = createRouter({
  history: createWebHistory(),
  routes: [
    {
      path: '/',
      name: 'landing',
      component: () => import('../views/LandingPage.vue')
    },
    {
      path: '/calendar',
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
    },
    {
      path: '/goals',
      name: 'goals',
      component: () => import('../views/Goals.vue')
    },
    {
      path: '/goals/new',
      name: 'goal-new',
      component: () => import('../views/GoalEdit.vue')
    },
    {
      path: '/goals/:id',
      name: 'goal-edit',
      component: () => import('../views/GoalEdit.vue')
    }
  ]
})

export default router
