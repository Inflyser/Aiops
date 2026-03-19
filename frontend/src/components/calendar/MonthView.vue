<template>
  <div class="month-calendar">
    <div class="month-header">
      <div class="month-header2">
        <h1 class="month-year-title">{{ currentMonth.format('MMMM YYYY') }}</h1>
        <div class="month-nav">
          <button class="nav-btn1" @click="$emit('prev-month')"><</button>
          <button class="nav-btn1" @click="$emit('next-month')">></button>
        </div>
      </div>
      <div class="days-header">
        <div v-for="dayName in dayNames" :key="dayName" class="day-header">
          <div class="day-name">{{ dayName }}</div>
        </div>
      </div>
    </div>
    
    <div class="month-grid">
      <div 
        v-for="day in monthDays" 
        :key="day.date"
        class="month-day"
        :class="{
          'today': day.isToday,
          'other-month': !day.isCurrentMonth,
          'weekend': day.isWeekend
        }"
        @click="$emit('day-click', day)"
      >
        <div class="month-day-number">{{ day.number }}</div>
        <div class="month-day-events">
          <div
            v-for="event in getEventsForDay(day.date)"
            :key="event.id"
            class="month-event"
            :style="{ backgroundColor: event.color || '#4a5568' }"
            @click.stop="handleEventClick(event)"
          >
            <img 
              v-if="event.tagIcon" 
              :src="getTagIconPath(event.tagIcon)" 
              class="event-tag-icon" 
            />
            {{ event.title }}
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

interface MonthDay {
  date: string
  number: number
  isToday: boolean
  isCurrentMonth: boolean
  isWeekend: boolean
  fullDate: dayjs.Dayjs
}

// Double click detection
const lastClickEvent = ref<{ event: CalendarEvent; time: number } | null>(null)
const clickTimeout = ref<ReturnType<typeof setTimeout> | null>(null)
const DOUBLE_CLICK_DELAY = 300 // ms

const props = defineProps<{
  currentMonth: dayjs.Dayjs
  events: CalendarEvent[]
}>()

const emit = defineEmits<{
  (e: 'prev-month'): void
  (e: 'next-month'): void
  (e: 'day-click', day: MonthDay): void
  (e: 'open-event', event: CalendarEvent): void
  (e: 'open-event-tasks', event: CalendarEvent): void
}>()

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

const dayNames = ['Пн', 'Вт', 'Ср', 'Чт', 'Пт', 'Сб', 'Вс']

const monthDays = computed(() => {
  const days: MonthDay[] = []
  const startOfMonth = props.currentMonth.startOf('month')
  const startDay = startOfMonth.startOf('week')
  
  let currentDay = startDay
  for (let i = 0; i < 42; i++) {
    days.push({
      date: currentDay.format('YYYY-MM-DD'),
      number: currentDay.date(),
      isToday: currentDay.isSame(dayjs(), 'day'),
      isCurrentMonth: currentDay.month() === props.currentMonth.month(),
      isWeekend: currentDay.day() === 6 || currentDay.day() === 0,
      fullDate: currentDay
    })
    currentDay = currentDay.add(1, 'day')
  }
  return days
})

const getEventsForDay = (date: string) => {
  return props.events.filter(event => {
    const eventDate = dayjs(event.start).format('YYYY-MM-DD')
    return eventDate === date
  })
}
</script>

<style scoped>
.month-calendar {
  padding: 20px;
}

.month-header {
  padding: 20px;
  border-bottom: 1px solid #80808021;
}

.month-header2 {
  display: flex;
  align-items: center;
  margin-bottom: 20px;
}

.month-year-title {
  font-size: 52px;
  font-weight: bold;
  margin: 0;
  flex: 1;
  text-transform: capitalize;
}

.month-nav {
  display: flex;
  gap: 10px;
}

.nav-btn1 {
  background: transparent;
  border: none;
  color: #ffffff;
  font-size: 38px;
  cursor: pointer;
  font-weight: bold;
  padding: 0px 10px 15px 25px;
}

.days-header {
  display: grid;
  grid-template-columns: repeat(7, 1fr);
  gap: 0px;
  margin-bottom: 10px;
  margin-left: 60px;
}

.day-header {
  text-align: center;
}

.day-name {
  font-size: 24px;
  color: #888;
  margin-bottom: 5px;
  font-weight: 700;
}

.month-grid {
  display: grid;
  grid-template-columns: repeat(7, 1fr);
  gap: 1px;
  margin-left: 60px;
  margin-right: 20px;
}

.month-day {
  min-height: 120px;
  border: 1px solid #333;
  padding: 8px;
  cursor: pointer;
  transition: background-color 0.2s;
}

.month-day:hover {
  background-color: #1a1a1a;
}

.month-day.today {
  border: 2px solid #4a90e2;
  background-color: rgba(74, 144, 226, 0.1);
}

.month-day.today .month-day-number {
  background-color: #4a90e2;
  color: white;
  width: 30px;
  height: 30px;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  margin-bottom: 8px;
}

.month-day.other-month {
  opacity: 0.3;
  cursor: default;
}

.month-day.weekend {
  background-color: rgba(255, 255, 255, 0.05);
}

.month-day-number {
  font-size: 18px;
  font-weight: 500;
  margin-bottom: 5px;
}

.month-day-events {
  display: flex;
  flex-direction: column;
  gap: 2px;
}

.event-tag-icon {
  width: 12px;
  height: 12px;
  flex-shrink: 0;
  filter: invert(1);
  margin-right: 3px;
}

.month-event {
  font-size: 12px;
  padding: 2px 6px;
  border-radius: 3px;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
  cursor: pointer;
  color: white;
}
</style>
