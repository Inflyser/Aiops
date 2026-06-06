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
        :style="snoozeEventStyle(ev)"
        :class="{ 'drag-over': dragOverEventId === ev.id }"
        draggable="true"
        @dragstart="handleDragStart($event, ev)"
        @dragend="handleDragEnd"
      >
        <div class="event-indicator"></div>
        <div class="event-content">
          <div class="event-title-row">
            <img v-if="ev.tagIcon && getTagIconPath(ev.tagIcon)" :src="getTagIconPath(ev.tagIcon)" class="event-tag-icon" />
            <span class="event-title-text">{{ ev.title }}</span>
          </div>
          <div class="event-time">
            <img src="@/assets/icon-clock.svg" class="event-time-icon" />
            {{ formatDate(ev.start) }} / {{ formatTime(ev.start) }}–{{ formatTime(ev.end) }}
          </div>
          <div v-if="ev.description" class="event-description">{{ ev.description }}</div>
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
import { getContrastColors } from '@/utils/color'

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

const snoozeEventStyle = (ev: SnoozedEvent) => {
  const bg = ev.color || '#4a5568'
  const colors = getContrastColors(bg)
  return {
    backgroundColor: bg,
    '--event-text-color': colors.text,
    '--event-text-muted': colors.textMuted,
    '--event-icon-filter': colors.iconFilter
  } as any
}

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
  padding: 8px 10px;
  margin-bottom: 6px;
  border-radius: 8px;
  cursor: grab;
  transition: opacity 0.15s;
  position: relative;
  color: var(--event-text-color, #fff);
  min-height: 30px;
}

.snooze-event:hover {
  opacity: 0.9;
}

.snooze-event:active {
  cursor: grabbing;
}

.snooze-event.drag-over {
  outline: 2px solid #4ade80;
  outline-offset: 2px;
}

.event-indicator {
  width: 5px;
  border-radius: 10px;
  background: var(--event-text-muted, rgba(255,255,255,0.7));
  margin: 2px 8px 2px 0;
  flex-shrink: 0;
  opacity: 0.9;
}

.event-content {
  flex: 1;
  overflow: hidden;
  min-width: 0;
}

.event-title-row {
  display: flex;
  align-items: center;
  gap: 6px;
  margin-bottom: 2px;
}

.event-tag-icon {
  width: 18px;
  height: 18px;
  flex-shrink: 0;
  filter: var(--event-icon-filter, none);
}

.event-title-text {
  font-size: 15px;
  font-weight: 600;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.event-time {
  font-size: 12px;
  color: var(--event-text-muted, rgba(255,255,255,0.7));
  font-weight: 500;
  display: flex;
  align-items: center;
  gap: 4px;
}

.event-time-icon {
  width: 14px;
  height: 14px;
  filter: var(--event-icon-filter, none);
}

.event-description {
  font-size: 12px;
  color: var(--event-text-muted, rgba(255,255,255,0.7));
  margin-top: 3px;
  line-height: 1.3;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.remove-btn {
  background: none;
  border: none;
  color: var(--event-text-muted, rgba(255,255,255,0.5));
  cursor: pointer;
  padding: 2px 4px;
  font-size: 14px;
  border-radius: 4px;
  transition: all 0.15s;
  flex-shrink: 0;
  align-self: flex-start;
  opacity: 0;
  line-height: 1;
}

.snooze-event:hover .remove-btn {
  opacity: 1;
}

.remove-btn:hover {
  background: rgba(255, 60, 60, 0.2);
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
