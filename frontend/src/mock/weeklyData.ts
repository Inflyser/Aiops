/**
 * Моковые данные для недельного представления
 */
import dayjs from 'dayjs'

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

interface CalendarEvent {
  id: string
  title: string
  description?: string
  start: string
  end: string
  all_day: boolean
  color: string
  location?: string
  priority?: string
  user_id: string
  created_at: string
  updated_at?: string
}

export const createMockWeeklyData = (startDate?: Date) => {
  const start = startDate || dayjs().startOf('week').toDate()
  
  const tasks: Task[] = [
    {
      id: 'task-1',
      title: 'Задача на неделю',
      description: 'Моковая задача для демонстрации на 7 дней',
      completed: false,
      due_date: dayjs(start).add(4, 'day').toISOString(),
      priority: 'high',
      tags: ['mock', 'weekly'],
      project_id: undefined,
      user_id: 'user-123',
      created_at: dayjs(start).toISOString(),
      updated_at: dayjs(start).toISOString()
    }
  ]

  const events: CalendarEvent[] = []
  for (let i = 0; i < 7; i++) {
    const day = dayjs(start).add(i, 'day').toDate()
    const nextDay = dayjs(start).add(i + 1, 'day').toDate()
    
    events.push({
      id: `event-${i + 1}`,
      title: `Событие дня ${i + 1}`,
      description: `Описание события для дня ${i + 1} недели`,
      start: day.toISOString(),
      end: nextDay.toISOString(),
      all_day: false,
      color: ['#47381F', '#3A403C', '#3A1D19', '#47381F', '#3A403C', '#3A1D19', '#3A1D19'][i],
      location: 'Офис',
      priority: 'medium',
      user_id: 'user-123',
      created_at: dayjs(start).toISOString(),
      updated_at: dayjs(start).toISOString()
    })
  }

  // Добавляем событие на 22 февраля 2026 с 9:00 до 13:00
  events.push({
    id: 'event-8',
    title: 'Рабочая встреча',
    description: 'Совещание с командой',
    start: dayjs('2026-02-22 09:00:00').toISOString(),
    end: dayjs('2026-02-22 13:00:00').toISOString(),
    all_day: false,
    color: '#38a14a',
    location: 'Переговорная',
    priority: 'medium',
    user_id: 'user-123',
    created_at: dayjs().toISOString(),
    updated_at: dayjs().toISOString()
  })

  return { tasks, events }
}

// По умолчанию используем текущую неделю
export const { tasks: mockWeeklyTasks, events: mockWeeklyEvents } = createMockWeeklyData()