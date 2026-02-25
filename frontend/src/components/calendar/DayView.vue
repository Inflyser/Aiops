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
          @click="$emit('hour-click', { hour, date: currentDay })"
        >
          <div class="hour-label">{{ hour }}:00</div>
          <div class="hour-events">
            <div 
              v-for="event in getEventsForHour(hour)" 
              :key="event.id"
              class="day-event"
              :style="{ 
                backgroundColor: event.color || '#4a5568',
                height: getEventHeight(event)
              }"
              @click.stop="$emit('open-event', event)"
            >
              <div class="event-time">{{ formatEventTime(event) }}</div>
              <div class="event-title">{{ event.title }}</div>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
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

const props = defineProps<{
  currentDay: dayjs.Dayjs
  events: CalendarEvent[]
}>()

defineEmits<{
  (e: 'prev-day'): void
  (e: 'next-day'): void
  (e: 'go-today'): void
  (e: 'hour-click', data: { hour: number; date: dayjs.Dayjs }): void
  (e: 'open-event', event: CalendarEvent): void
}>()

const hours = Array.from({ length: 24 }, (_, i) => i)

const getEventsForHour = (hour: number) => {
  return props.events.filter(event => {
    const eventStart = dayjs(event.start)
    return eventStart.hour() === hour
  })
}

const getEventHeight = (event: CalendarEvent) => {
  const start = dayjs(event.start)
  const end = dayjs(event.end)
  const durationHours = end.diff(start, 'hour')
  return `${Math.max(durationHours * 60, 30)}px`
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
}

.day-hour-row {
  display: flex;
  min-height: 60px;
  border-bottom: 1px solid #1a1a1a;
  cursor: pointer;
  transition: background-color 0.2s;
}

.day-hour-row:hover {
  background-color: rgba(255, 255, 255, 0.03);
}

.hour-label {
  width: 80px;
  padding: 10px;
  font-size: 14px;
  color: #666;
  flex-shrink: 0;
  border-right: 1px solid #1a1a1a;
}

.hour-events {
  flex: 1;
  padding: 5px;
  display: flex;
  flex-direction: column;
  gap: 2px;
}

.day-event {
  padding: 8px 12px;
  border-radius: 4px;
  cursor: pointer;
  color: white;
  overflow: hidden;
  transition: transform 0.1s;
}

.day-event:hover {
  transform: scale(1.02);
}

.event-time {
  font-size: 12px;
  opacity: 0.8;
}

.event-title {
  font-size: 14px;
  font-weight: 500;
}
</style>
