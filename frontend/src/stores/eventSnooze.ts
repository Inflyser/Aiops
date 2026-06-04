import { defineStore } from 'pinia'
import { ref, watch } from 'vue'

export interface SnoozedEvent {
  id: string
  title: string
  description?: string
  start: string
  end: string
  color: string
  location?: string
  priority?: string
  is_important?: boolean
  tag_id?: string
  tagIcon?: string
  task_ids?: string[]
  task_count?: number
  completed_task_count?: number
  snoozed_at: string
}

const STORAGE_KEY = 'snoozed-events'

export const useEventSnoozeStore = defineStore('eventSnooze', () => {
  const snoozedEvents = ref<SnoozedEvent[]>([])

  const loadFromStorage = () => {
    try {
      const raw = localStorage.getItem(STORAGE_KEY)
      if (raw) {
        snoozedEvents.value = JSON.parse(raw)
      }
    } catch {
      snoozedEvents.value = []
    }
  }

  const saveToStorage = () => {
    try {
      localStorage.setItem(STORAGE_KEY, JSON.stringify(snoozedEvents.value))
    } catch {
      console.error('Failed to save snoozed events')
    }
  }

  watch(snoozedEvents, saveToStorage, { deep: true })

  loadFromStorage()

  const addEvent = (event: SnoozedEvent) => {
    if (!snoozedEvents.value.find(e => e.id === event.id)) {
      snoozedEvents.value.push({
        ...event,
        snoozed_at: new Date().toISOString()
      })
    }
  }

  const removeEvent = (eventId: string) => {
    const idx = snoozedEvents.value.findIndex(e => e.id === eventId)
    if (idx !== -1) {
      const event = snoozedEvents.value[idx]
      snoozedEvents.value.splice(idx, 1)
      return event
    }
    return null
  }

  const clearAll = () => {
    snoozedEvents.value = []
  }

  return {
    snoozedEvents,
    addEvent,
    removeEvent,
    clearAll
  }
})
