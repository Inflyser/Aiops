<template>
  <div class="important-panel">
    <div class="important-panel-header">
      <h3>Важные события</h3>
      <button class="close-btn" @click="$emit('close')">←</button>
    </div>
    
    <div class="important-events-list">
      <div 
        v-for="event in sortedEvents" 
        :key="event.id" 
        class="important-event-item"
        :class="{ 'is-past': dayjs(event.end).isBefore(dayjs()) }"
        @click="$emit('open-event', event)"
      >
        <div class="event-color" :style="{ backgroundColor: event.color || '#4A90E2' }"></div>
        <div class="event-info">
          <div class="event-title">{{ event.title }}</div>
          <div class="event-deadline">{{ formatDeadline(event) }}</div>
          <div class="event-date">{{ formatEventDate(event) }}</div>
        </div>
        <div class="event-star">★</div>
      </div>
      
      <div v-if="importantEvents.length === 0" class="no-events">
        Нет важных событий
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { computed } from 'vue'
import dayjs from 'dayjs'

interface CalendarEvent {
  id: string
  title: string
  start: string
  end: string
  all_day: boolean
  color?: string
}

const props = defineProps<{
  importantEvents: CalendarEvent[]
}>()

defineEmits<{
  (e: 'close'): void
  (e: 'open-event', event: CalendarEvent): void
}>()

const sortedEvents = computed(() => {
  const now = dayjs()
  const active = [...props.importantEvents].filter(e => dayjs(e.end).isAfter(now))
  const past = [...props.importantEvents].filter(e => dayjs(e.end).isBefore(now))
  active.sort((a, b) => dayjs(a.start).diff(dayjs(b.start)))
  past.sort((a, b) => dayjs(b.start).diff(dayjs(a.start)))
  return [...active, ...past]
})

const formatEventDate = (event: CalendarEvent) => {
  if (event.all_day) {
    return dayjs(event.start).format('DD MMMM YYYY')
  }
  return dayjs(event.start).format('DD MMMM YYYY, HH:mm')
}

const formatDeadline = (event: CalendarEvent) => {
  const now = dayjs()
  const start = dayjs(event.start)
  const end = dayjs(event.end)

  if (end.isBefore(now)) {
    const hours = now.diff(end, 'hour')
    if (hours < 1) return 'только что завершилось'
    if (hours < 24) return `завершилось ${hours}ч назад`
    return `завершилось ${now.diff(end, 'day')}д назад`
  }

  if (start.isBefore(now) && end.isAfter(now)) {
    const left = end.diff(now, 'minute')
    if (left < 60) return `осталось ${left} мин`
    return `осталось ${end.diff(now, 'hour')}ч`
  }

  const diffMin = start.diff(now, 'minute')
  if (diffMin < 60) return `через ${diffMin} мин`

  const diffHours = start.diff(now, 'hour')
  if (diffHours < 24) return `через ${diffHours}ч`

  const diffDays = start.diff(now, 'day')
  if (diffDays === 0) return 'сегодня'
  if (diffDays === 1) return 'завтра'
  if (diffDays < 7) return `через ${diffDays} дн`

  return start.format('D MMM')
}
</script>

<style scoped>
.important-panel {
  position: fixed;
  top: 70px;
  right: 20px;
  width: 320px;
  max-height: calc(100vh - 100px);
  background: #050505;
  border-radius: 12px;
  border: 1px solid #333;
  z-index: 1000;
  display: flex;
  flex-direction: column;
  box-shadow: 0 8px 32px rgba(0, 0, 0, 0.4);
}

.important-panel-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 16px 20px;
  border-bottom: 1px solid #333;
}

.important-panel-header h3 {
  margin: 0;
  color: #fff;
  font-size: 14px;
  font-weight: 600;
}

.close-btn {
  background: none;
  border: none;
  color: #888;
  font-size: 20px;
  cursor: pointer;
  padding: 0;
  width: 30px;
  height: 30px;
  display: flex;
  align-items: center;
  justify-content: center;
  border-radius: 4px;
  transition: background 0.2s;
}

.close-btn:hover {
  background: #333;
  color: #fff;
}

.important-events-list {
  flex: 1;
  overflow-y: auto;
  padding: 8px;
}

.important-events-list::-webkit-scrollbar {
  width: 4px;
}

.important-events-list::-webkit-scrollbar-thumb {
  background: #333;
  border-radius: 2px;
}

.important-event-item {
  display: flex;
  align-items: center;
  padding: 12px;
  border-radius: 8px;
  cursor: pointer;
  transition: background 0.2s, opacity 0.3s;
  margin-bottom: 4px;
  border: 1px solid transparent;
}

.important-event-item:hover {
  background: #080808;
  border-color: #333;
}

.important-event-item.is-past {
  opacity: 0.4;
}

.important-event-item.is-past:hover {
  opacity: 0.6;
}

.event-color {
  width: 4px;
  height: 36px;
  border-radius: 2px;
  margin-right: 12px;
  flex-shrink: 0;
}

.event-info {
  flex: 1;
  min-width: 0;
}

.event-title {
  color: #fff;
  font-size: 12px;
  font-weight: 600;
  margin-bottom: 2px;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}

.event-deadline {
  font-size: 10px;
  color: #888;
  font-weight: 500;
  margin-bottom: 1px;
}

.important-event-item.is-past .event-deadline {
  color: #555;
}

.event-date {
  color: #666;
  font-size: 10px;
}

.event-star {
  color: #FFD700;
  font-size: 14px;
  margin-left: 8px;
  flex-shrink: 0;
}

.no-events {
  text-align: center;
  color: #666;
  padding: 40px 20px;
  font-size: 13px;
}
</style>