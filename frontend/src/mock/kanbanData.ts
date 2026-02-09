/**
 * Моковые данные для Kanban доски
 */

interface Task {
  id: string
  title: string
  description?: string
  completed: boolean
  due_date?: string
  priority: string
  tags?: string[]
  project_id?: string
  user_id: string
  created_at: string
  updated_at?: string
}

export const createMockKanbanData = () => {
  const tasks: Task[] = [
    {
      id: 'kanban-task-1',
      title: 'Спроектировать интерфейс',
      description: 'Создать прототипы основных экранов приложения',
      completed: false,
      due_date: new Date(Date.now() + 2 * 24 * 60 * 60 * 1000).toISOString(), // Через 2 дня
      priority: 'high',
      tags: ['design', 'ui'],
      project_id: 'project-1',
      user_id: 'user-123',
      created_at: new Date(Date.now() - 1 * 24 * 60 * 60 * 1000).toISOString(), // 1 день назад
      updated_at: new Date(Date.now() - 1 * 24 * 60 * 60 * 1000).toISOString()
    },
    {
      id: 'kanban-task-2',
      title: 'Разработать API',
      description: 'Создать REST API для управления задачами',
      completed: false,
      due_date: new Date(Date.now() + 5 * 24 * 60 * 60 * 1000).toISOString(), // Через 5 дней
      priority: 'medium',
      tags: ['backend', 'api'],
      project_id: 'project-1',
      user_id: 'user-123',
      created_at: new Date(Date.now() - 3 * 24 * 60 * 60 * 1000).toISOString(), // 3 дня назад
      updated_at: new Date(Date.now() - 1 * 24 * 60 * 60 * 1000).toISOString()
    },
    {
      id: 'kanban-task-3',
      title: 'Написать документацию',
      description: 'Подготовить техническую документацию для разработчиков',
      completed: true,
      due_date: new Date(Date.now() - 1 * 24 * 60 * 60 * 1000).toISOString(), // Вчера
      priority: 'low',
      tags: ['documentation'],
      project_id: 'project-1',
      user_id: 'user-123',
      created_at: new Date(Date.now() - 7 * 24 * 60 * 60 * 1000).toISOString(), // 7 дней назад
      updated_at: new Date(Date.now() - 1 * 24 * 60 * 60 * 1000).toISOString()
    },
    {
      id: 'kanban-task-4',
      title: 'Тестирование производительности',
      description: 'Провести нагрузочное тестирование системы',
      completed: false,
      due_date: new Date(Date.now() + 7 * 24 * 60 * 60 * 1000).toISOString(), // Через 7 дней
      priority: 'high',
      tags: ['testing', 'performance'],
      project_id: 'project-1',
      user_id: 'user-123',
      created_at: new Date(Date.now() - 2 * 24 * 60 * 60 * 1000).toISOString(), // 2 дня назад
      updated_at: new Date(Date.now() - 1 * 24 * 60 * 60 * 1000).toISOString()
    },
    {
      id: 'kanban-task-5',
      title: 'Интеграция с внешними сервисами',
      description: 'Подключить сторонние API для расширения функционала',
      completed: false,
      due_date: new Date(Date.now() + 10 * 24 * 60 * 60 * 1000).toISOString(), // Через 10 дней
      priority: 'medium',
      tags: ['integration', 'api'],
      project_id: 'project-1',
      user_id: 'user-123',
      created_at: new Date(Date.now() - 4 * 24 * 60 * 60 * 1000).toISOString(), // 4 дня назад
      updated_at: new Date(Date.now() - 2 * 24 * 60 * 60 * 1000).toISOString()
    }
  ]

  return { tasks }
}

export const { tasks: mockKanbanTasks } = createMockKanbanData()