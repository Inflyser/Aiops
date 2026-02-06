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
  user_id: string
  created_at: string
  updated_at?: string
}

export const useCalendarStore = defineStore('calendar', () => {
  const events = ref<CalendarEvent[]>([])
  const loading = ref(false)
  const error = ref<string | null>(null)

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

  return {
    events,
    loading,
    error,
    fetchEvents,
    createEvent,
    updateEvent,
    deleteEvent
  }
})

