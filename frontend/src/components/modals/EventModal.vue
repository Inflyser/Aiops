<template>
  <div v-if="show" class="modal" @click.self="$emit('close')">
    <div class="modal-content" @click.stop>
      <div class="modal-header">
        <h2 v-if="editingEvent">
          <img src="@/assets/icon-clock.svg" alt="clock" class="header-icon" />
          Редактировать задачу
        </h2>
        <h2 v-else>
          <img src="@/assets/icon-clock.svg" alt="clock" class="header-icon" />
          {{ headerDateTime }}
        </h2>
        <button
          type="button"
          class="star-btn"
          :class="{ 'is-important': formData.is_important }"
          @click="toggleImportant"
          :title="formData.is_important ? 'Убрать важность' : 'Отметить как важное'"
        >
          {{ formData.is_important ? '★' : '☆' }}
        </button>
      </div>

      <div class="divider"></div>
      
<form @submit.prevent="viewMode !== 'view' ? $emit('save') : null">
        <!-- Название -->
        <div class="form-group">
          <input
            type="text"
            id="eventTitle"
            v-model="formData.title"
            :disabled="viewMode === 'view'"
            required
            placeholder="Введите название задачи"
          >
        </div>


<!-- Описание -->
        <div class="form-group">
          <textarea
            id="eventDescription"
            v-model="formData.description"
            :disabled="viewMode === 'view'"
            placeholder="Добавьте описание задачи"
            rows="2"
          ></textarea>
        </div>

        <!-- Теги -->
        <div class="form-group">
          <div class="tags-selector">
            <div
              v-for="tag in availableTags"
              :key="tag.id"
              class="tag-option"
              :class="{ selected: selectedTagId === tag.id }"
              @click="selectTag(tag)"
            >
              <img
                v-if="tag.icon && getIconPath(tag.icon)"
                :src="getIconPath(tag.icon)"
                class="tag-icon"
              />
              <span class="tag-color" :style="{ backgroundColor: tag.color }"></span>
              <span class="tag-name">{{ tag.name }}</span>
            </div>
            <div v-if="availableTags.length === 0" class="no-tags-message">
              Нет тегов
            </div>
          </div>
        </div>

        <div class="divider"></div>

        <!-- Время -->
        <div class="form-group">
          <div class="time-slider-group">
            <div class="slider-labels">
              <span class="time-display">Начало: {{ formData.startTime }}</span>
              <span class="time-display">Конец: {{ formData.endTime }}</span>
            </div>
            <div class="dual-slider">
              <div class="track">
                <div class="track-fill" :style="rangeStyle"></div>
              </div>
              <input
                type="range"
                class="range-input range-min"
                min="0"
                max="1439"
                step="10"
                :value="timeToMinutes(formData.startTime)"
                @input="updateStartTime($event)"
              >
              <input
                type="range"
                class="range-input range-max"
                min="0"
                max="1439"
                step="10"
                :value="timeToMinutes(formData.endTime)"
                @input="updateEndTime($event)"
              >
            </div>
            <div class="slider-ticks">
              <span>00:00</span>
              <span>06:00</span>
              <span>12:00</span>
              <span>18:00</span>
              <span>23:59</span>
            </div>
          </div>
        </div>

        <div class="divider"></div>

        <!-- Дата -->
        <div class="form-group">
          <label class="form-label">Дата</label>
          <div class="date-selector">
            <button
              v-for="day in upcomingDays"
              :key="day.date"
              type="button"
              class="date-btn"
              :class="{
                'selected': day.date === formData.date,
                'is-today': day.isToday
              }"
              @click="selectDate(day.date)"
            >
              <span class="date-day-name">{{ day.dayName }}</span>
              <span class="date-day-num">{{ day.dayNum }}</span>
              <span class="date-month">{{ day.month }}</span>
            </button>
          </div>
        </div>

        <div class="divider"></div>

        <!-- Повторение -->
        <div class="form-group">
          <label class="form-label">Повторение</label>
          <div class="recurrence-options">
            <select v-model="formData.recurrenceType" class="recurrence-select">
              <option :value="undefined">Не повторяется</option>
              <option value="weekly">Еженедельно</option>
            </select>
          </div>

          <div v-if="formData.recurrenceType === 'weekly'" class="recurrence-days">
            <button
              v-for="(day, index) in weekDaysFull"
              :key="index"
              type="button"
              class="day-btn"
              :class="{ selected: isDaySelected(index) }"
              @click="toggleDay(index)"
            >
              {{ day }}
            </button>
          </div>

          <div v-if="formData.recurrenceType === 'weekly'" class="recurrence-end">
            <label class="small-label">Повторять до:</label>
            <input
              type="date"
              v-model="formData.recurrenceEndDate"
              class="recurrence-end-input"
            >
          </div>
        </div>

        <!-- Разделитель -->
        <div class="divider"></div>
        
        <!-- Кнопки -->
        <div class="form-actions">
          
          <button
            v-if="editingEvent && viewMode !== 'view'"
            type="button"
            class="btn-icon delete-btn"
            @click="$emit('delete')"
            title="Удалить"
          >
            <img src="@/assets/icon-delete.svg" alt="Удалить" />
          </button>
          
          <button
            type="button"
            class="btn btn-secondary"
            @click="$emit('close')"
          >
            {{ viewMode === 'view' ? 'Закрыть' : 'Отмена' }}
          </button>
          <button
            v-if="viewMode !== 'view'"
            type="submit"
            class="btn btn-primary"
          >
            Сохранить
          </button>
        </div>
      </form>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, watch } from 'vue'
import dayjs from 'dayjs'
import 'dayjs/locale/ru'

const iconModules = import.meta.glob<{ default: string }>('../../assets/icon/*.svg', { query: '?url', import: 'default', eager: true })

const iconFiles = computed(() => {
  return Object.entries(iconModules).map(([path, url]) => {
    const name = path.split('/').pop()?.replace('.svg', '') || ''
    return { name, path: (url as unknown as string) }
  })
})

const getIconPath = (iconName: string) => {
  const icon = iconFiles.value.find(i => i.name === iconName)
  return icon?.path || ''
}

interface Tag {
  id: string
  name: string
  color: string
  icon?: string
}

interface EventFormData {
  title: string
  description: string
  date: string
  startTime: string
  endTime: string
  priority: string
  is_important?: boolean
  color: string
  tagId?: string
  recurrenceType?: string
  recurrenceDays?: string
  recurrenceEndDate?: string
}

interface CalendarEvent {
  id: string | number
  title: string
  description?: string
  start: string
  end: string
  priority?: string
  is_important?: boolean
  color?: string
  tagId?: string
  recurrence_type?: string
  recurrence_days?: string
  recurrence_end_date?: string
}

const props = defineProps<{
  show: boolean
  editingEvent: CalendarEvent | null
  formData: EventFormData
  availableTags: Tag[]
  viewMode?: 'view' | 'edit' | null
}>()

defineEmits<{
  (e: 'close'): void
  (e: 'save'): void
  (e: 'delete'): void
}>()

const selectedTagId = ref<string | null>(null)
const weekDaysFull = ['Пн', 'Вт', 'Ср', 'Чт', 'Пт', 'Сб', 'Вс']
const shortDayNames = ['Вс', 'Пн', 'Вт', 'Ср', 'Чт', 'Пт', 'Сб']

const upcomingDays = computed(() => {
  const days = []
  const targetDate = props.formData.date ? dayjs(props.formData.date) : dayjs()
  const weekStart = targetDate.startOf('week')
  for (let i = 0; i < 7; i++) {
    const d = weekStart.add(i, 'day')
    days.push({
      date: d.format('YYYY-MM-DD'),
      dayName: shortDayNames[d.day()],
      dayNum: d.format('D'),
      month: d.format('MMMM'),
      isToday: d.isSame(dayjs(), 'day')
    })
  }
  return days
})

// Задачи события
const selectedDays = ref<number[]>([])

const isDaySelected = (dayIndex: number) => {
  return selectedDays.value.includes(dayIndex)
}

const toggleDay = (dayIndex: number) => {
  const index = selectedDays.value.indexOf(dayIndex)
  if (index === -1) {
    selectedDays.value.push(dayIndex)
  } else {
    selectedDays.value.splice(index, 1)
  }
  // Обновляем formData.recurrenceDays
  props.formData.recurrenceDays = selectedDays.value.join(',')
}

// Watch для обновления selectedDays при изменении formData
watch(() => props.formData.recurrenceDays, (newVal) => {
  if (newVal) {
    selectedDays.value = newVal.split(',').map(d => parseInt(d)).filter(d => !isNaN(d))
  } else {
    selectedDays.value = []
  }
})

// Header date/time display: "22 февраля, 09:00"
const headerDateTime = computed(() => {
  if (!props.formData.date) return 'Новая задача'
  const dateStr = dayjs(props.formData.date).format('D MMMM')
  const timeStr = props.formData.startTime || ''
  return timeStr ? `${dateStr}, ${timeStr}` : dateStr
})

const selectDate = (date: string) => {
  const fData = props.formData as any
  fData.date = date
}

watch(() => props.formData, (newFormData) => {
  selectedTagId.value = newFormData.tagId || null
}, { immediate: true })

watch(() => props.show, (isVisible) => {
  if (isVisible && props.editingEvent) {
    selectedTagId.value = props.editingEvent.tagId || null
  }
})

const timeToMinutes = (time: string): number => {
  if (!time) return 0
  const [hours, minutes] = time.split(':').map(Number)
  return hours * 60 + (minutes || 0)
}

const minutesToTime = (mins: number): string => {
  const rounded = Math.round(mins / 10) * 10
  const h = Math.floor(rounded / 60)
  const m = rounded % 60
  return `${String(h).padStart(2, '0')}:${String(m).padStart(2, '0')}`
}

const updateStartTime = (event: Event) => {
  const mins = Math.round(parseInt((event.target as HTMLInputElement).value) / 10) * 10
  const fData = props.formData as any
  fData.startTime = minutesToTime(mins)
  if (timeToMinutes(fData.endTime) - mins < 60) {
    fData.endTime = minutesToTime(Math.min(mins + 60, 1430))
  }
}

const updateEndTime = (event: Event) => {
  const mins = Math.round(parseInt((event.target as HTMLInputElement).value) / 10) * 10
  const fData = props.formData as any
  if (mins - timeToMinutes(fData.startTime) < 60) {
    fData.endTime = minutesToTime(Math.min(timeToMinutes(fData.startTime) + 60, 1430))
  } else {
    fData.endTime = minutesToTime(mins)
  }
}

const rangeStyle = computed(() => {
  const start = timeToMinutes(props.formData.startTime)
  const end = timeToMinutes(props.formData.endTime)
  const left = (start / 1439) * 100
  const width = ((end - start) / 1439) * 100
  return { left: `${left}%`, width: `${width}%` }
})

const toggleImportant = () => {
  const fData = props.formData as any
  fData.is_important = !fData.is_important
}

const selectTag = (tag: Tag) => {
  const fData = props.formData as any
  
  if (selectedTagId.value === tag.id) {
    selectedTagId.value = null
    fData.color = '#4a5568'
    fData.tagId = undefined
  } else {
    selectedTagId.value = tag.id
    fData.color = tag.color
    fData.tagId = tag.id
  }
}
</script>

<style scoped>
.modal {
  position: fixed;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  background-color: rgba(0, 0, 0, 0.8);
  display: flex;
  justify-content: center;
  align-items: center;
  z-index: 1000;
  animation: fadeIn 0.2s ease-out;
}

@keyframes fadeIn {
  from {
    opacity: 0;
  }
  to {
    opacity: 1;
  }
}

.modal-content {
  background-color: #0a0a0a;
  padding: 20px;
  border-radius: 12px;
  width: 90%;
  max-width: 500px;
  max-height: 90vh;
  overflow-y: auto;
  position: relative;
  border: 1px solid var(--border-subtle);
  box-shadow: 0 4px 20px rgba(0, 0, 0, 0.5);
  animation: slideUp 0.3s cubic-bezier(0.16, 1, 0.3, 1);
}

.modal-content::-webkit-scrollbar {
  width: 6px;
}

.modal-content::-webkit-scrollbar-track {
  background: transparent;
}

.modal-content::-webkit-scrollbar-thumb {
  background: #444;
  border-radius: 3px;
}

@keyframes slideUp {
  from {
    opacity: 0;
    transform: translateY(20px) scale(0.95);
  }
  to {
    opacity: 1;
    transform: translateY(0) scale(1);
  }
}

.modal-header {
  display: flex;
  align-items: center;
  gap: 10px;
}

.modal-header h2 {
  flex: 1;
  font-size: 16px;
  display: flex;
  align-items: center;
  color: var(--text-secondary);
  gap: 10px;
  margin: 0;
}

.star-btn {
  background: none;
  border: none;
  font-size: 22px;
  cursor: pointer;
  color: #555;
  padding: 0 4px;
  line-height: 1;
  margin-left: auto;
  transition: color 0.2s, transform 0.2s;
}

.star-btn:hover {
  color: #f59e0b;
  transform: scale(1.15);
}

.star-btn.is-important {
  color: #f59e0b;
}

.header-icon {
  width: 24px;
  height: 24px;
  padding: 0 0 4px 0;
}

.form-group {
  margin-bottom: 10px;
}

.form-group label {
  display: block;
  margin-bottom: 4px;
  font-size: 11px;
  color: #888;
  text-transform: uppercase;
  letter-spacing: 0.5px;
}

.form-group input,
.form-group textarea {
  width: 100%;
  padding: 8px 10px;
  background-color: #0d0d0d;
  border: 1px solid var(--border-subtle);
  color: #fff;
  font-size: 13px;
  font-family: inherit;
  border-radius: 6px;
}

.form-group textarea {
  resize: vertical;
}

.form-group input:focus,
.form-group textarea:focus {
  outline: none;
  border-color: #666;
}

.dual-slider {
  position: relative;
  height: 24px;
  margin: 12px 0 8px;
}

.track {
  position: absolute;
  top: 8px;
  left: 0;
  right: 0;
  height: 6px;
  background: var(--bg-elevated);
  border-radius: 999px;
  pointer-events: none;
  z-index: 1;
}

.track-fill {
  position: absolute;
  height: 100%;
  background: #555;
  border-radius: 999px;
}

.range-input {
  position: absolute;
  width: 100%;
  height: 24px;
  -webkit-appearance: none;
  background: transparent;
  pointer-events: auto;
  top: 0;
  margin: 0;
  z-index: 1;
}

.range-min {
  z-index: 3;
}

.range-max {
  z-index: 2;
}

.range-input:hover,
.range-input:active,
.range-input:focus {
  z-index: 5;
}

.range-input::-webkit-slider-thumb {
  -webkit-appearance: none;
  width: 20px;
  height: 20px;
  border-radius: 50%;
  cursor: pointer;
  pointer-events: auto;
  border: 2.5px solid #fff;
  box-shadow: 0 2px 6px rgba(0,0,0,0.5);
  z-index: 1;
}

.range-min::-webkit-slider-thumb,
.range-max::-webkit-slider-thumb {
  background: #888;
}

.range-input::-webkit-slider-runnable-track {
  height: 0;
}

.slider-labels {
  display: flex;
  justify-content: space-between;
  margin-bottom: 6px;
}

.time-display {
  font-size: 12px;
  color: #aaa;
  background: #0d0d0d;
  padding: 4px 8px;
  border-radius: 4px;
}

.slider-ticks {
  display: flex;
  justify-content: space-between;
  font-size: 10px;
  color: #666;
  margin-top: 4px;
}

.recurrence-options {
  margin-bottom: 10px;
}

.recurrence-select {
  width: 100%;
  padding: 10px;
  background-color: #0d0d0d;
  border: 1px solid var(--border-subtle);
  color: #fff;
  font-size: 14px;
  border-radius: 6px;
  cursor: pointer;
}

.recurrence-days {
  display: flex;
  gap: 4px;
  margin-bottom: 8px;
}

.day-btn {
  width: 32px;
  height: 28px;
  border: 1px solid var(--border-subtle);
  border-radius: 4px;
  background: #0d0d0d;
  color: #888;
  font-size: 11px;
  cursor: pointer;
  transition: all 0.2s;
}

.day-btn:hover {
  background: #151515;
  color: #fff;
}

.day-btn.selected {
  background: #444;
  border-color: #666;
  color: #fff;
}

.recurrence-end {
  display: flex;
  align-items: center;
  gap: 10px;
}

.small-label {
  font-size: 12px;
  color: #888;
  text-transform: none;
  letter-spacing: normal;
}

.recurrence-end-input {
  padding: 8px;
  background-color: #2a2a2a;
  border: 1px solid #444;
  color: #fff;
  font-size: 13px;
  border-radius: 6px;
}

.form-label {
  display: block;
  margin-bottom: 8px;
  font-size: 13px;
  color: #888;
  text-transform: uppercase;
  letter-spacing: 0.5px;
}

.divider {
  height: 1px;
  background-color: var(--bg-elevated);
  margin: 12px -20px 12px -20px;
}

.date-selector {
  display: flex;
  gap: 6px;
  justify-content: center;
}

.date-btn {
  display: flex;
  flex-direction: column;
  align-items: center;
  padding: 8px 10px;
  background: #111;
  border: 1px solid #2a2a2a;
  border-radius: 10px;
  cursor: pointer;
  transition: all 0.2s;
  min-width: 52px;
  flex: 1;
}

.date-btn:hover {
  background: var(--bg-tertiary);
  border-color: #555;
}

.date-btn.selected {
  background: #2a2a2a;
  border-color: #666;
}

.date-btn.is-today {
  border-color: #444;
}

.date-btn.selected.is-today {
  border-color: #888;
}

.date-day-name {
  font-size: 10px;
  color: #666;
  text-transform: uppercase;
  font-weight: 500;
}

.date-btn.selected .date-day-name {
  color: #ccc;
}

.date-day-num {
  font-size: 16px;
  color: #fff;
  font-weight: 600;
  margin: 2px 0;
}

.date-month {
  font-size: 9px;
  color: #555;
}

.date-btn.selected .date-month {
  color: #999;
}

.month-navigator {
  display: flex;
  align-items: center;
  justify-content: space-between;
  margin-bottom: 6px;
}

.nav-btn {
  background: none;
  border: none;
  color: #888;
  font-size: 14px;
  cursor: pointer;
  padding: 4px 8px;
}

.nav-btn:hover {
  color: #fff;
}

.month-year {
  font-size: 14px;
  color: #fff;
  text-transform: capitalize;
}

.mini-calendar {
  background-color: #121212;
  border-radius: 10px;
  padding: 1px;
}

.weekdays {
  display: grid;
  grid-template-columns: repeat(7, 1fr);
  text-align: center;
  margin-bottom: 4px;
}

.weekdays span {
  font-size: 11px;
  color: #666;
  text-transform: uppercase;
}

.calendar-days {
  display: grid;
  grid-template-columns: repeat(7, 1fr);
  gap: 2px;
}

.calendar-day {
  aspect-ratio: 1;
  display: flex;
  align-items: center;
  justify-content: center;
  background: none;
  border: none;
  color: #ddd;
  font-size: 12px;
  cursor: pointer;
  border-radius: 6px;
  transition: all 0.2s;
  padding: 2px;
}

.calendar-day:hover {
  background-color: var(--bg-elevated);
  color: #fff;
}

.btn-secondary {
  background-color: #151515;
  color: #aaa;
}

.btn-icon {
  background: transparent;
  border: none;
  cursor: pointer;
  padding: 4px;
  display: flex;
  align-items: center;
  justify-content: center;
  transition: opacity 0.2s;
}

.btn-icon:hover {
  opacity: 0.8;
}

.btn-icon img {
  width: 24px;
  height: 24px;
}

.delete-btn {
  margin-left: auto;
}

.tags-selector {
  display: flex;
  flex-wrap: wrap;
  gap: 8px;
  padding: 10px;
  background-color: #0d0d0d;
  border: 1px solid var(--border-subtle);
  border-radius: 10px;
  max-height: 100px;
  overflow-y: auto;
  scrollbar-width: none;
}

.tags-selector::-webkit-scrollbar {
  display: none;
}

.tag-option {
  display: flex;
  align-items: center;
  gap: 6px;
  padding: 6px 12px;
  border-radius: 16px;
  background-color: var(--bg-tertiary);
  cursor: pointer;
  transition: all 0.2s;
  border: 2px solid transparent;
}

.tag-option:hover {
  background-color: #2a2a2a;
}

.tag-option.selected {
  border-color: #888;
  background-color: #2a2a2a;
}

.tag-color {
  width: 12px;
  height: 12px;
  border-radius: 50%;
  flex-shrink: 0;
}

.tag-icon {
  width: 14px;
  height: 14px;
  object-fit: contain;
  filter: invert(1);
}

.tag-name {
  font-size: 13px;
  color: #ddd;
}



.no-tags-message {
  color: #666;
  font-size: 13px;
  padding: 10px;
  text-align: center;
  width: 100%;
}

/* Event Tasks Styles */
.event-tasks-list {
  display: flex;
  flex-direction: column;
  gap: 8px;
  max-height: 200px;
  overflow-y: auto;
}

.event-task-item {
  display: flex;
  align-items: flex-start;
  padding: 10px;
  background: var(--bg-tertiary);
  border-radius: 6px;
  gap: 10px;
}

.task-checkbox {
  width: 18px;
  height: 18px;
  border: 2px solid #666;
  border-radius: 4px;
  flex-shrink: 0;
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: center;
  transition: border-color 0.2s;
}

.task-checkbox:hover {
  border-color: #4A90E2;
}

.task-checkbox .checked {
  color: #4A90E2;
  font-size: 12px;
  font-weight: bold;
}

.task-content {
  flex: 1;
  min-width: 0;
}

.task-title {
  color: #fff;
  font-size: 14px;
  word-break: break-word;
}

.task-description {
  color: #888;
  font-size: 12px;
  margin-top: 4px;
  word-break: break-word;
}

.remove-task-btn {
  background: none;
  border: none;
  color: #666;
  font-size: 16px;
  cursor: pointer;
  padding: 4px;
  border-radius: 4px;
  transition: color 0.2s, background 0.2s;
  flex-shrink: 0;
}

.remove-task-btn:hover {
  color: #ff4444;
  background: rgba(255, 68, 68, 0.1);
}
</style>
