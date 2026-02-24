import { defineStore } from 'pinia'
import { ref } from 'vue'
import axios from 'axios'

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
  tag_id?: string
  user_id: string
  created_at: string
  updated_at?: string
}

// Для Ctrl+Z (история действий)
interface HistoryAction {
  type: 'create' | 'update' | 'delete'
  eventId: string
  oldEvent?: CalendarEvent
  newEvent?: CalendarEvent
}

export const useCalendarStore = defineStore('calendar', () => {
  const events = ref<CalendarEvent[]>([])
  const loading = ref(false)
  const error = ref<string | null>(null)

  // Для Ctrl+C / Ctrl+V
  const copiedEvent = ref<CalendarEvent | null>(null)
  
  // Для Ctrl+Z (история действий)
  const undoStack = ref<HistoryAction[]>([])
  const maxUndoHistory = 20

  const api = axios.create({
    baseURL: '/api/v1/calendar',
    headers: {
      'Content-Type': 'application/json'
    }
  })

  const fetchEvents = async (start?: string, end?: string) => {
    loading.value = true
    error.value = null
    try {
      const params: any = {}
      if (start) params.start = start
      if (end) params.end = end
      
      const response = await api.get('/', { params })
      events.value = response.data
    } catch (err: any) {
      error.value = err.response?.data?.detail || 'Ошибка загрузки событий'
      console.error('Error fetching events:', err)
    } finally {
      loading.value = false
    }
  }

  const createEvent = async (eventData: Partial<CalendarEvent>) => {
    loading.value = true
    error.value = null
    try {
      const response = await api.post('/', eventData)
      events.value.push(response.data)
      return response.data
    } catch (err: any) {
      error.value = err.response?.data?.detail || 'Ошибка создания события'
      console.error('Error creating event:', err)
      throw err
    } finally {
      loading.value = false
    }
  }

  const updateEvent = async (eventId: string, eventData: Partial<CalendarEvent>) => {
    loading.value = true
    error.value = null
    try {
      const response = await api.put(`/${eventId}`, eventData)
      const index = events.value.findIndex(e => e.id === eventId)
      if (index !== -1) {
        events.value[index] = response.data
      }
      return response.data
    } catch (err: any) {
      error.value = err.response?.data?.detail || 'Ошибка обновления события'
      console.error('Error updating event:', err)
      throw err
    } finally {
      loading.value = false
    }
  }

  const deleteEvent = async (eventId: string) => {
    loading.value = true
    error.value = null
    try {
      await api.delete(`/${eventId}`)
      events.value = events.value.filter(e => e.id !== eventId)
    } catch (err: any) {
      error.value = err.response?.data?.detail || 'Ошибка удаления события'
      console.error('Error deleting event:', err)
      throw err
    } finally {
      loading.value = false
    }
  }

  // Добавить действие в историю
  const addToHistory = (action: HistoryAction) => {
    undoStack.value.push(action)
    // Ограничиваем историю
    if (undoStack.value.length > maxUndoHistory) {
      undoStack.value.shift()
    }
  }

  // Ctrl+C - копировать событие
  const copyEvent = (event: CalendarEvent) => {
    copiedEvent.value = { ...event }
    console.log('Event copied:', event.title)
  }

  // Ctrl+V - вставить событие
  const pasteEvent = async () => {
    if (!copiedEvent.value) return null
    
    const newEventData = {
      ...copiedEvent.value,
      id: undefined, // Создастся новое событие
      title: `${copiedEvent.value.title} (копия)`,
      created_at: undefined,
      updated_at: undefined
    }
    
    try {
      const newEvent = await createEvent(newEventData)
      // Добавляем в историю для отмены
      addToHistory({
        type: 'create',
        eventId: newEvent.id,
        newEvent
      })
      console.log('Event pasted:', newEvent.title)
      return newEvent
    } catch (err) {
      console.error('Failed to paste event:', err)
      return null
    }
  }

  // Ctrl+Z - отменить последнее действие
  const undo = async (): Promise<void> => {
    console.log('Undo called, stack length:', undoStack.value.length)
    
    if (undoStack.value.length === 0) {
      console.log('Нечего отменять!')
      return
    }
    
    const lastAction = undoStack.value.pop()
    if (!lastAction) return
    
    console.log('Undoing action:', lastAction.type, lastAction.eventId)
    
    try {
      switch (lastAction.type) {
        case 'create':
          // Отменяем создание - удаляем событие
          if (lastAction.newEvent) {
            await deleteEvent(lastAction.newEvent.id)
            console.log('Отменено: удалено событие', lastAction.newEvent.title)
          }
          break
        case 'update':
          // Отменяем обновление - восстанавливаем старое
          if (lastAction.oldEvent && lastAction.newEvent) {
            await updateEvent(lastAction.oldEvent.id, lastAction.oldEvent)
            console.log('Отменено: восстановлено событие', lastAction.oldEvent.title)
          }
          break
        case 'delete':
          // Отменяем удаление - восстанавливаем событие
          if (lastAction.oldEvent) {
            await createEvent(lastAction.oldEvent)
            console.log('Отменено: восстановлено событие', lastAction.oldEvent.title)
          }
          break
      }
    } catch (err) {
      console.error('Ошибка отмены:', err)
    }
  }

  // Проверка можно ли отменить
  const canUndo = () => {
    return undoStack.value.length > 0
  }

  // Проверка есть ли скопированное событие
  const hasCopiedEvent = () => {
    return copiedEvent.value !== null
  }

  return {
    events,
    loading,
    error,
    copiedEvent,
    canUndo,
    hasCopiedEvent,
    fetchEvents,
    createEvent,
    updateEvent,
    deleteEvent,
    copyEvent,
    pasteEvent,
    undo,
    addToHistory
  }
})
