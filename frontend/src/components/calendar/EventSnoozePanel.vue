<template>
  <div
    class="snooze-panel"
    :class="{ 'open': isOpen }"
    @dragover.prevent="onDragOver"
    @dragleave="onDragLeave"
    @drop="onDrop"
  >
    <div class="snooze-header">
      <h3 class="snooze-title">Отложенные</h3>
      <button class="close-btn" @click="$emit('close')">←</button>
    </div>

    <div class="snooze-content">
      <div v-if="snoozedEvents.length > 0 && !isDragOver" class="snooze-hint">
        Перетащите событие обратно в календарь
      </div>
      <div v-if="snoozedEvents.length === 0" class="empty-snooze">
        <span class="empty-icon">📦</span>
        <span>Пусто</span>
        <span class="empty-hint">Перетащите сюда событие из календаря</span>
      </div>

      <div
        v-for="ev in snoozedEvents"
        :key="ev.id"
        class="snooze-event"
        :class="{ 'drag-over': dragOverEventId === ev.id }"
        draggable="true"
        @dragstart="handleDragStart($event, ev)"
        @dragend="handleDragEnd"
      >
        <div class="snooze-event-indicator" :style="{ backgroundColor: ev.color || '#4a5568' }"></div>
        <div class="snooze-event-content">
          <div class="snooze-event-title">{{ ev.title }}</div>
          <div class="snooze-event-meta">
            <img src="@/assets/icon-clock.svg" alt="clock" class="snooze-event-clock" />
            {{ formatDate(ev.start) }} / {{ formatTime(ev.start) }}–{{ formatTime(ev.end) }}
          </div>
          <div v-if="ev.description" class="snooze-event-desc">{{ ev.description }}</div>
        </div>
        <button class="remove-btn" @click="removeFromSnooze(ev.id)" title="Удалить">✕</button>
      </div>
    </div>

    <div v-if="isDragOver" class="snooze-drop-zone">
      Бросьте сюда
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref } from 'vue'
import dayjs from 'dayjs'
import 'dayjs/locale/ru'
import type { SnoozedEvent } from '@/stores/eventSnooze'

dayjs.locale('ru')

defineProps<{
  isOpen: boolean
  snoozedEvents: SnoozedEvent[]
}>()

const emit = defineEmits<{
  (e: 'close'): void
  (e: 'snooze-event-drop', data: { event: SnoozedEvent; time: dayjs.Dayjs }): void
  (e: 'calendar-event-dropped', event: any): void
  (e: 'remove-snoozed', eventId: string): void
}>()

const isDragOver = ref(false)
const dragOverEventId = ref<string | null>(null)
let dragLeaveTimeout: ReturnType<typeof setTimeout> | null = null

const onDragOver = (e: DragEvent) => {
  e.preventDefault()
  if (e.dataTransfer) {
    e.dataTransfer.dropEffect = 'move'
  }
  isDragOver.value = true
  if (dragLeaveTimeout) {
    clearTimeout(dragLeaveTimeout)
    dragLeaveTimeout = null
  }
}

const onDragLeave = () => {
  dragLeaveTimeout = setTimeout(() => {
    isDragOver.value = false
  }, 150)
}

const onDrop = (e: DragEvent) => {
  e.preventDefault()
  isDragOver.value = false
  if (dragLeaveTimeout) {
    clearTimeout(dragLeaveTimeout)
    dragLeaveTimeout = null
  }

  try {
    const data = JSON.parse(e.dataTransfer?.getData('text/plain') || '{}')
    if (data._snoozed) return

    if (data.id && data.title) {
      emit('calendar-event-dropped', data)
    }
  } catch {
    // ignore
  }
}

const handleDragStart = (e: DragEvent, ev: SnoozedEvent) => {
  if (e.dataTransfer) {
    const data = { ...ev, _snoozed: true }
    e.dataTransfer.setData('text/plain', JSON.stringify(data))
    e.dataTransfer.effectAllowed = 'move'
  }
}

const handleDragEnd = () => {
  dragOverEventId.value = null
}

const removeFromSnooze = (eventId: string) => {
  emit('remove-snoozed', eventId)
}

const formatDate = (dateStr: string) => {
  return dayjs(dateStr).format('DD MMM')
}

const formatTime = (dateStr: string) => {
  return dayjs(dateStr).format('HH:mm')
}
</script>

<style scoped>
.snooze-panel {
  position: fixed;
  top: 0;
  right: -320px;
  width: 320px;
  height: 100vh;
  background: #050505;
  border-left: 1px solid #33333357;
  transition: right 0.3s ease;
  z-index: 1000;
  display: flex;
  flex-direction: column;
}

.snooze-panel.open {
  right: 0;
}

.snooze-header {
  padding: 20px;
  border-bottom: 1px solid #33333357;
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.snooze-title {
  margin: 0;
  color: #fff;
  font-size: 14px;
  font-weight: 600;
}

.close-btn {
  background: none;
  border: none;
  color: #888;
  font-size: 19px;
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

.snooze-content {
  flex: 1;
  overflow-y: auto;
  padding: 10px;
}

.empty-snooze {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: 50px 20px;
  color: #666;
  gap: 8px;
}

.empty-icon {
  font-size: 38px;
}

.empty-hint {
  font-size: 11px;
  color: #555;
}

.snooze-hint {
  text-align: center;
  padding: 8px;
  color: #555;
  font-size: 11px;
  border-bottom: 1px solid #33333357;
  margin-bottom: 8px;
}

.snooze-event {
  display: flex;
  padding: 10px;
  margin-bottom: 6px;
  border: 1px solid #33333357;
  border-radius: 8px;
  cursor: grab;
  transition: background 0.15s, border-color 0.15s;
  position: relative;
}

.snooze-event:hover {
  background: rgba(255, 255, 255, 0.03);
  border-color: #444;
}

.snooze-event:active {
  cursor: grabbing;
}

.snooze-event.drag-over {
  border-color: #4ade80;
  background: rgba(74, 222, 128, 0.05);
}

.snooze-event-indicator {
  width: 4px;
  border-radius: 4px;
  margin-right: 10px;
  flex-shrink: 0;
}

.snooze-event-content {
  flex: 1;
  overflow: hidden;
}

.snooze-event-title {
  color: #fff;
  font-weight: 600;
  font-size: 13px;
  margin-bottom: 4px;
}

.snooze-event-meta {
  color: #888;
  font-size: 11px;
  display: flex;
  align-items: center;
  gap: 4px;
}

.snooze-event-clock {
  width: 12px;
  height: 12px;
  filter: brightness(0.5);
}

.snooze-event-desc {
  color: #666;
  font-size: 11px;
  margin-top: 4px;
  line-height: 1.3;
}

.remove-btn {
  background: none;
  border: none;
  color: #555;
  cursor: pointer;
  padding: 4px;
  font-size: 12px;
  border-radius: 4px;
  transition: all 0.15s;
  flex-shrink: 0;
  align-self: flex-start;
  opacity: 0;
}

.snooze-event:hover .remove-btn {
  opacity: 1;
}

.remove-btn:hover {
  background: rgba(255, 60, 60, 0.15);
  color: #ff4444;
}

.snooze-drop-zone {
  position: absolute;
  bottom: 0;
  left: 0;
  right: 0;
  padding: 20px;
  text-align: center;
  color: #4ade80;
  font-weight: 600;
  font-size: 13px;
  background: rgba(74, 222, 128, 0.05);
  border-top: 2px dashed #4ade80;
}
</style>
