<template>
  <div class="important-panel">
    <div class="important-panel-header">
      <h3>Важные события</h3>
      <button class="close-btn" @click="$emit('close')">×</button>
    </div>
    
    <div class="important-events-list">
      <div 
        v-for="event in importantEvents" 
        :key="event.id" 
        class="important-event-item"
        @click="$emit('open-event', event)"
      >
        <div class="event-color" :style="{ backgroundColor: event.color || '#4A90E2' }"></div>
        <div class="event-info">
          <div class="event-title">{{ event.title }}</div>
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
import dayjs from 'dayjs'

interface CalendarEvent {
  id: string
  title: string
  start: string
  end: string
  all_day: boolean
  color?: string
}

defineProps<{
  importantEvents: CalendarEvent[]
}>()

defineEmits<{
  (e: 'close'): void
  (e: 'open-event', event: CalendarEvent): void
}>()

const formatEventDate = (event: CalendarEvent) => {
  if (event.all_day) {
    return dayjs(event.start).format('DD MMMM YYYY')
  }
  return dayjs(event.start).format('DD MMMM YYYY, HH:mm')
}
</script>

<style scoped>
.important-panel {
  position: fixed;
  top: 70px;
  right: 20px;
  width: 320px;
  max-height: calc(100vh - 100px);
  background: #1e1e1e;
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
  font-size: 13px;
  font-weight: 500;
}

.close-btn {
  background: none;
  border: none;
  color: #888;
  font-size: 19px;
  cursor: pointer;
  padding: 0;
  line-height: 1;
}

.close-btn:hover {
  color: #fff;
}

.important-events-list {
  flex: 1;
  overflow-y: auto;
  padding: 8px;
}

.important-event-item {
  display: flex;
  align-items: center;
  padding: 12px;
  border-radius: 8px;
  cursor: pointer;
  transition: background 0.2s;
  margin-bottom: 4px;
}

.important-event-item:hover {
  background: #2a2a2a;
}

.event-color {
  width: 4px;
  height: 36px;
  border-radius: 2px;
  margin-right: 12px;
}

.event-info {
  flex: 1;
}

.event-title {
  color: #fff;
  font-size: 11px;
  font-weight: 500;
  margin-bottom: 4px;
}

.event-date {
  color: #888;
  font-size: 10px;
}

.event-star {
  color: #FFD700;
  font-size: 14px;
}

.no-events {
  text-align: center;
  color: #666;
  padding: 40px 20px;
  font-size: 11px;
}
</style>