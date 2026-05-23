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
            v-for="event in getVisibleEvents(day.date)"
            :key="event.id"
            class="month-event"
            :style="{ backgroundColor: event.color || '#4a5568' }"
            @click.stop="handleEventClick(event)"
          >
            <img
              v-if="event.tagIcon && getTagIconPath(event.tagIcon)"
              :src="getTagIconPath(event.tagIcon)"
              class="event-tag-icon"
            />
            {{ event.title }}
          </div>
          <div
            v-if="getExtraEventsCount(day.date) > 0"
            class="more-events"
            @click.stop="$emit('day-click', day)"
          >
            +{{ getExtraEventsCount(day.date) }} ещё
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

const iconModules = import.meta.glob<{ default: string }>('../../assets/icon/*.svg', { query: '?url', import: 'default', eager: true })

const getTagIconPath = (iconName: string): string => {
  for (const [path, url] of Object.entries(iconModules)) {
    if (path.includes(`/${iconName}.svg`) || path.includes(`/${iconName}`)) {
      return (url as unknown as string)
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
  completed_task_count?: number
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

const MAX_VISIBLE_EVENTS = 3

const getAllEventsForDay = (date: string) => {
  return props.events.filter(event => {
    const eventDate = dayjs(event.start).format('YYYY-MM-DD')
    return eventDate === date
  })
}

const getVisibleEvents = (date: string) => {
  return getAllEventsForDay(date).slice(0, MAX_VISIBLE_EVENTS)
}

const getExtraEventsCount = (date: string) => {
  const allEvents = getAllEventsForDay(date)
  return Math.max(0, allEvents.length - MAX_VISIBLE_EVENTS)
}
</script>

<style scoped>
.month-calendar {
  padding: 20px 0;
}

.month-header {
  padding: 20px 0;
}

.month-header2 {
  display: flex;
  align-items: center;
  margin-bottom: 20px;
  padding: 0 20px;
}

.month-year-title {
  font-size: 42px;
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
  font-size: 30px;
  cursor: pointer;
  font-weight: bold;
  padding: 0px 10px 15px 25px;
}

.days-header {
  display: grid;
  grid-template-columns: repeat(7, 1fr);
  gap: 1px;
}

.day-header {
  text-align: center;
}

.day-name {
  font-size: 19px;
  color: #888;
  margin-bottom: 5px;
  font-weight: 700;
}

.month-grid {
  display: grid;
  grid-template-columns: repeat(7, 1fr);
  border-left: 1px solid #333;
  border-top: 1px solid #333;
  border-top-left-radius: 12px;
  border-top-right-radius: 12px;
  overflow: hidden;
}

.month-day {
  min-height: 120px;
  border-right: 1px solid #333;
  border-bottom: 1px solid #333;
  padding: 8px;
  cursor: pointer;
  transition: background-color 0.2s;
}

.month-day:hover {
  background-color: #1a1a1a;
}

.month-day.today {
  background-color: rgba(85, 85, 85, 0.1);
}

.month-day.today .month-day-number {
  background-color: #555;
  color: white;
  width: 30px;
  height: 30px;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  margin: 0 auto 8px;
}

.month-day.other-month {
  opacity: 0.3;
  cursor: default;
}

.month-day.weekend {
  background-color: rgba(255, 255, 255, 0.05);
}

.month-day-number {
  font-size: 14px;
  font-weight: 500;
  margin-bottom: 5px;
  text-align: center;
}

.month-day-events {
  display: flex;
  flex-direction: column;
  gap: 2px;
}

.event-tag-icon {
  width: 13px;
  height: 13px;
  flex-shrink: 0;
}

.month-event {
  font-size: 12px;
  padding: 3px 6px;
  border-radius: 3px;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
  cursor: pointer;
  color: white;
  display: flex;
  align-items: center;
  gap: 4px;
}

.more-events {
  font-size: 9px;
  color: #888;
  padding: 2px 6px;
  cursor: pointer;
}

.more-events:hover {
  color: #aaa;
}
</style>
