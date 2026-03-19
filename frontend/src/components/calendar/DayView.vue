<template>
  <div class="day-calendar">
    <div class="day-header">
      <div class="day-header-content">
        <div class="day-info">
          <h1 class="day-weekday">{{ currentDay.format('dddd') }}</h1>
          <h2 class="day-date">{{ currentDay.format('D MMMM YYYY') }}</h2>
        </div>
        <div class="day-nav">
          <button class="nav-btn1" @click="$emit('prev-day')"><</button>
          <button class="today-btn" @click="$emit('go-today')">Сегодня</button>
          <button class="nav-btn1" @click="$emit('next-day')">></button>
        </div>
      </div>
    </div>
    
    <div class="day-scroll-container">
      <div class="day-grid">
        <div 
          v-for="hour in hours" 
          :key="hour"
          class="day-hour-row"
        >
          <div class="hour-label">{{ hour.toString().padStart(2, '0') }}:00</div>
          <div class="hour-events" @click="handleRowClick(hour)"></div>
        </div>
        
        <div class="events-container" :style="{ minHeight: calendarHeight + 'px' }">
          <div
            v-for="event in events"
            :key="event.id"
            class="day-event"
            :style="getEventStyle(event)"
            @click.stop="handleEventClick(event)"
          >
            <div class="event-time">{{ formatEventTime(event) }}</div>
            <img 
              v-if="event.tagIcon" 
              :src="getTagIconPath(event.tagIcon)" 
              class="event-tag-icon" 
            />
            <div class="event-title">{{ event.title }}</div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { computed, ref } from 'vue'
import dayjs from 'dayjs'
import 'dayjs/locale/ru'

dayjs.locale('ru')

const iconFiles: Record<string, string> = import.meta.glob('@/assets/icon/*.svg', { query: '?url', import: 'default', eager: true }) as any

const getTagIconPath = (iconName: string): string => {
  for (const [path, url] of Object.entries(iconFiles)) {
    if (path.includes(`/${iconName}.svg`) || path.includes(`/${iconName}`)) {
      return url
    }
  }
  return ''
}

interface CalendarEvent {
  id: string | number
  title: string
  description?: string
  start: string
  end: string
  location?: string
  priority?: string
  color?: string
  tagIcon?: string
  task_count?: number
}

const props = defineProps<{
  currentDay: dayjs.Dayjs
  events: CalendarEvent[]
  compactMode: boolean
}>()

const emit = defineEmits<{
  (e: 'prev-day'): void
  (e: 'next-day'): void
  (e: 'go-today'): void
  (e: 'hour-click', data: { hour: number; date: dayjs.Dayjs }): void
  (e: 'open-event', event: CalendarEvent): void
  (e: 'open-event-tasks', event: CalendarEvent): void
}>()

// Double click detection
const lastClickEvent = ref<{ event: CalendarEvent; time: number } | null>(null)
const clickTimeout = ref<ReturnType<typeof setTimeout> | null>(null)
const DOUBLE_CLICK_DELAY = 300 // ms

const hours = computed(() => {
  if (props.compactMode) {
    return Array.from({ length: 17 }, (_, i) => i + 7) // 7:00 to 23:00
  }
  return Array.from({ length: 24 }, (_, i) => i) // 0:00 to 23:00
})

const calendarHeight = computed(() => {
  const totalHours = props.compactMode ? 17 : 24
  return totalHours * 120
})

const handleRowClick = (hour: number) => {
  emit('hour-click', { hour, date: props.currentDay })
}

// Handle event click with double click detection
const handleEventClick = (event: CalendarEvent) => {
  const now = Date.now()
  
  // Clear previous timeout if exists
  if (clickTimeout.value) {
    clearTimeout(clickTimeout.value)
    clickTimeout.value = null
  }
  
  // Check if this is a double click
  if (lastClickEvent.value &&
      lastClickEvent.value.event.id === event.id &&
      now - lastClickEvent.value.time < DOUBLE_CLICK_DELAY) {
    // Double click detected - open event modal for editing
    emit('open-event', event)
    lastClickEvent.value = null
  } else {
    // Store click info and wait to see if it's a single or double click
    lastClickEvent.value = { event, time: now }
    
    // Set timeout to handle single click
    clickTimeout.value = setTimeout(() => {
      // Single click - check if event has tasks
      if (event.task_count && event.task_count > 0) {
        emit('open-event-tasks', event)
      }
      lastClickEvent.value = null
      clickTimeout.value = null
    }, DOUBLE_CLICK_DELAY)
  }
}

const getEventStyle = (event: CalendarEvent) => {
  const start = dayjs(event.start)
  const end = dayjs(event.end)
  const dayStart = props.currentDay.startOf('day')
  
  let startMinutes = start.diff(dayStart, 'minute')
  const duration = end.diff(start, 'minute')
  
  const eventColor = event.color || '#4a5568'
  
  if (props.compactMode) {
    if (startMinutes < 7 * 60) {
      startMinutes = 7 * 60
    } else if (startMinutes >= 24 * 60) {
      return { display: 'none' }
    }
    
    const offsetMinutes = 7 * 60
    const top = ((startMinutes - offsetMinutes) / 60) * 120
    const height = Math.max((duration / 60) * 120, 30)
    
    const maxTop = 17 * 120
    const clampedTop = Math.max(0, Math.min(top, maxTop))
    const clampedHeight = Math.min(height, maxTop - clampedTop)
    
    if (clampedTop >= maxTop || clampedHeight <= 0) {
      return { display: 'none' }
    }
    
    return {
      top: `${clampedTop}px`,
      height: `${clampedHeight}px`,
      backgroundColor: eventColor,
      position: 'absolute' as const,
      left: '2px',
      right: '2px',
      zIndex: 10
    }
  }
  
  const top = (startMinutes / 60) * 120
  const height = Math.max((duration / 60) * 120, 30)
  
  const maxTop = 24 * 120
  const clampedTop = Math.max(0, Math.min(top, maxTop))
  const clampedHeight = Math.min(height, maxTop - clampedTop)
  
  if (clampedTop >= maxTop || clampedHeight <= 0) {
    return { display: 'none' }
  }
  
  return {
    top: `${clampedTop}px`,
    height: `${clampedHeight}px`,
    backgroundColor: eventColor,
    position: 'absolute' as const,
    left: '2px',
    right: '2px',
    zIndex: 10
  }
}

const formatEventTime = (event: CalendarEvent) => {
  const start = dayjs(event.start)
  const end = dayjs(event.end)
  return `${start.format('HH:mm')} - ${end.format('HH:mm')}`
}
</script>

<style scoped>
.day-calendar {
  display: flex;
  flex-direction: column;
  height: 100%;
  overflow: hidden;
}

.day-header {
  padding: 20px;
  border-bottom: 1px solid #80808021;
  flex-shrink: 0;
  background-color: #050505;
  z-index: 10;
}

.day-scroll-container {
  flex: 1;
  overflow-y: auto;
  overflow-x: hidden;
}

.day-header-content {
  display: flex;
  align-items: center;
  justify-content: space-between;
}

.day-info {
  display: flex;
  flex-direction: column;
}

.day-weekday {
  font-size: 48px;
  font-weight: bold;
  margin: 0;
  text-transform: capitalize;
}

.day-date {
  font-size: 24px;
  color: #888;
  margin: 5px 0 0;
  font-weight: 400;
}

.day-nav {
  display: flex;
  align-items: center;
  gap: 10px;
}

.nav-btn1 {
  background: transparent;
  border: none;
  color: #ffffff;
  font-size: 28px;
  cursor: pointer;
  font-weight: bold;
  padding: 5px 15px;
}

.today-btn {
  background: #1a1a1a;
  border: 1px solid #333;
  color: #fff;
  font-size: 14px;
  cursor: pointer;
  padding: 8px 16px;
  border-radius: 6px;
  transition: background 0.2s;
}

.today-btn:hover {
  background: #2a2a2a;
}

.day-grid {
  display: flex;
  flex-direction: column;
  position: relative;
}

.day-hour-row {
  display: flex;
  min-height: 120px;
  border-bottom: 1px solid #1a1a1a;
}

.hour-label {
  width: 80px;
  padding: 10px;
  font-size: 18px;
  color: #666;
  flex-shrink: 0;
  border-right: 1px solid #1a1a1a;
}

.hour-events {
  flex: 1;
  cursor: pointer;
}

.hour-events:hover {
  background-color: rgba(255, 255, 255, 0.03);
}

.events-container {
  position: absolute;
  top: 0;
  left: 80px;
  right: 0;
  pointer-events: none;
}

.day-event {
  position: absolute;
  left: 2px;
  right: 2px;
  padding: 8px 12px;
  border-radius: 4px;
  cursor: pointer;
  color: white;
  overflow: hidden;
  pointer-events: auto;
  transition: transform 0.1s;
}

.day-event:hover {
  transform: scale(1.02);
}

.event-time {
  font-size: 12px;
  opacity: 0.8;
}

.event-tag-icon {
  width: 14px;
  height: 14px;
  flex-shrink: 0;
  filter: invert(1);
  margin-right: 4px;
}

.event-title {
  font-size: 14px;
  font-weight: 500;
}
</style>
