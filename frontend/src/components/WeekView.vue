<template>
  <div class="week-view">
    <!-- Calendar Grid -->
    <div class="calendar-grid">
      <div class="time-column">
        <div 
          v-for="hour in hours" 
          :key="hour"
          class="time-slot"
        >
          {{ formatTime(hour) }}
        </div>
      </div>

      <div class="days-container" :style="{ minHeight: calendarHeight + 'px' }">
        <div 
          v-for="day in weekDays" 
          :key="day.date"
          class="day-column"
          :class="{ 'current-day': isCurrentDay(day) }"
          :style="{ minHeight: calendarHeight + 'px' }"
          @click="handleDayClick($event, day)"
        >
          <div 
            v-for="hour in hours" 
            :key="hour"
            class="hour-slot"
          ></div>
          <div
            v-for="event in getEventsForDay(day.date)"
            :key="event.id"
            class="event-block"
            :style="getEventStyle(event, day.date)"
            @click.stop="$emit('open-event', event)"
          >
            <div class="event-indicator"></div>
            <div class="event-content">
              <div class="event-time">{{ formatEventTime(event) }}</div>
              <div class="event-title">{{ event.title }}</div>
              <div v-if="event.description" class="event-description">{{ event.description }}</div>
              <div v-if="event.location" class="event-location">📍 {{ event.location }}</div>
            </div>
          </div>
          
          <!-- Current Time Line (only for today) -->
          <div 
            v-if="isCurrentDay(day)"
            class="current-time-line"
            :style="currentTimeLineStyle"
          >
            <div class="current-time-dot"></div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { computed, ref, onMounted, onUnmounted } from 'vue'
import dayjs from 'dayjs'
import 'dayjs/locale/ru'

dayjs.locale('ru')

interface CalendarEvent {
  id: string | number
  title: string
  description?: string
  start: string
  end: string
  location?: string
  priority?: string
  color?: string
}

interface WeekDay {
  date: string
  shortName: string
  number: number
  fullDate: dayjs.Dayjs
}

const props = defineProps<{
  weekDays: WeekDay[]
  events: CalendarEvent[]
  compactMode: boolean
}>()

const emit = defineEmits<{
  (e: 'day-click', day: WeekDay, event: MouseEvent): void
  (e: 'open-event', event: CalendarEvent): void
}>()

// Current time for the red line
const currentTime = ref(dayjs())
let timeInterval: ReturnType<typeof setInterval> | null = null

onMounted(() => {
  // Update time every minute
  timeInterval = setInterval(() => {
    currentTime.value = dayjs()
  }, 60000)
})

onUnmounted(() => {
  if (timeInterval) {
    clearInterval(timeInterval)
  }
})

// Calculate the position of the current time line
const currentTimeLineStyle = computed(() => {
  const hours = currentTime.value.hour()
  const minutes = currentTime.value.minute()
  
  // Calculate total minutes from start of day (or 7:00 for compact mode)
  const startHour = props.compactMode ? 7 : 0
  const totalMinutes = (hours - startHour) * 60 + minutes
  
  // Convert to pixels (120px per hour)
  const top = (totalMinutes / 60) * 120
  
  return {
    top: `${top}px`
  }
})

// Check if current day is today
const isCurrentDay = (day: WeekDay) => {
  return dayjs(day.date).isSame(dayjs(), 'day')
}

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

const getEventsForDay = (date: string) => {
  return props.events.filter(event => {
    const eventDate = dayjs(event.start).format('YYYY-MM-DD')
    return eventDate === date
  })
}

const getEventStyle = (event: CalendarEvent, dayDate: string) => {
  const start = dayjs(event.start)
  const end = dayjs(event.end)
  const dayStart = dayjs(dayDate).startOf('day')

  const startMinutes = start.diff(dayStart, 'minute')
  const duration = end.diff(start, 'minute')

  const offsetMinutes = props.compactMode ? 7 * 60 : 0

  const top = ((startMinutes - offsetMinutes) / 60) * 120
  const height = Math.max((duration / 60) * 120, 30)

  const totalHours = props.compactMode ? 17 : 24
  const maxTop = totalHours * 120
  const clampedTop = Math.max(0, Math.min(top, maxTop))
  const clampedHeight = Math.min(height, maxTop - clampedTop)

  if (clampedTop >= maxTop || clampedHeight <= 0) {
    return { display: 'none' }
  }

  return {
    top: `${clampedTop}px`,
    height: `${clampedHeight}px`,
    backgroundColor: '#4a5568',
    position: 'absolute' as const,
    left: '2px',
    right: '2px',
    zIndex: 10
  }
}

const formatTime = (hour: number) => {
  return `${hour.toString().padStart(2, '0')}:00`
}

const formatEventTime = (event: CalendarEvent) => {
  const start = dayjs(event.start)
  const end = dayjs(event.end)
  return `${start.format('HH:mm')} - ${end.format('HH:mm')}`
}

const handleDayClick = (event: MouseEvent, day: WeekDay) => {
  emit('day-click', day, event)
}
</script>

<style scoped>
.week-view {
  flex: 1;
  display: flex;
  flex-direction: column;
  min-height: 0;
}

.calendar-grid {
  flex: 1;
  display: flex;
  position: relative;
  min-height: 0;
  overflow-y: auto;
  overflow-x: hidden;
}

.time-column {
  width: 90px;
  border-right: 1px solid #808080;
  flex-shrink: 0;
  display: flex;
  flex-direction: column;
  position: sticky;
  left: 0;
  background-color: #050505;
  z-index: 5;
}

.time-slot {
  height: 120px;
  display: flex;
  align-items: flex-start;
  justify-content: center;
  padding-top: 5px;
  font-size: 20px;
  color: #6b6b6b;
  font-weight: bold;
  border-bottom: 1px solid #333;
  box-sizing: border-box;
  flex-shrink: 0;
}

.days-container {
  display: grid;
  grid-template-columns: repeat(7, 1fr);
  flex: 1;
  position: relative;
}

.day-column {
  border-right: 1px solid #333;
  position: relative;
  display: flex;
  flex-direction: column;
}

.hour-slot {
  height: 120px;
  border-bottom: 1px solid #222;
  min-height: 120px;
}

.event-block {
  position: absolute;
  left: 2px;
  right: 2px;
  background-color: #4a5568;
  border-radius: 4px;
  padding: 5px 8px;
  cursor: pointer;
  overflow: hidden;
  z-index: 10;
  transition: opacity 0.2s;
  display: flex;
  min-height: 30px;
}

.event-block:hover {
  opacity: 0.9;
}

.event-indicator {
  width: 7px;
  border-radius: 6px;
  background-color: #ffffff;
  margin-right: 8px;
  flex-shrink: 0;
  opacity: 0.7;
}

.event-content {
  flex: 1;
  overflow: hidden;
}

.event-time {
  font-size: 20px;
  color: rgba(255, 255, 255, 0.8);
  margin-bottom: 2px;
  font-weight: 500;
}

.event-title {
  font-size: 22px;
  font-weight: 600;
  margin-bottom: 2px;
}

.event-description {
  font-size: 18px;
  color: rgba(255, 255, 255, 0.8);
  margin-top: 3px;
  line-height: 1.3;
}

.event-location {
  font-size: 14px;
  color: rgba(255, 255, 255, 0.7);
  margin-top: 2px;
}

/* Current Time Line */
.current-time-line {
  position: absolute;
  left: 0;
  right: 0;
  height: 2px;
  background-color: #ff4444;
  z-index: 20;
  pointer-events: none;
}

.current-time-dot {
  position: absolute;
  left: -5px;
  top: 50%;
  transform: translateY(-50%);
  width: 10px;
  height: 10px;
  background-color: #ff4444;
  border-radius: 50%;
}
</style>
