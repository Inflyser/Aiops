<template>
  <div v-if="show" class="modal" @click.self="$emit('close')">
    <div class="modal-content" @click.stop>
      <span class="close" @click="$emit('close')">&times;</span>
      
      <!-- Заголовок с датой и временем -->
      <h2 v-if="editingEvent">
        <img src="@/assets/icon-clock.svg" alt="clock" class="header-icon" />
        Редактировать задачу
      </h2>
      <h2 v-else>
        <img src="@/assets/icon-clock.svg" alt="clock" class="header-icon" />
        {{ headerDateTime }}
      </h2>

      <div class="divider"></div>
      
      <form @submit.prevent="viewMode !== 'view' ? $emit('save') : null">
        <!-- Название задачи -->
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
        
        <!-- Тег -->
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
        
        <!-- Время начало - конец -->
        <div class="form-group">
         
          <div class="time-range">
            <input 
              type="time" 
              v-model="formData.startTime" 
              required
            >
            <span class="time-separator">—</span>
            <input 
              type="time" 
              v-model="formData.endTime" 
              required
            >
          </div>
        </div>
        
        <!-- Повторение -->
        <div class="form-group">
          <label class="form-label">Повторение</label>
          <div class="recurrence-options">
            <select v-model="formData.recurrenceType" class="recurrence-select">
              <option :value="undefined">Не повторяется</option>
              <option value="weekly">Еженедельно</option>
            </select>
          </div>
          
          <!-- Выбор дней недели -->
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
          
          <!-- Дата окончания повторения -->
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
        
        <!-- Выбор даты -->
        <div class="form-group">
          
          <!-- Навигация по месяцам -->
          <div class="month-navigator">
            <button type="button" class="nav-btn" @click="prevMonth">←</button>
            <span class="month-year">{{ monthYearDisplay }}</span>
            <button type="button" class="nav-btn" @click="nextMonth">→</button>
          </div>

          <div class="divider"></div>
          
          <!-- Мини календарь -->
          <div class="mini-calendar">
            <div class="weekdays">
              <span v-for="day in weekDays" :key="day">{{ day }}</span>
            </div>
            <div class="calendar-days">
              <button 
                v-for="(day, index) in calendarDays" 
                :key="index"
                type="button"
                class="calendar-day"
                :class="{ 
                  'other-month': !day.isCurrentMonth,
                  'selected': day.date === formData.date,
                  'today': day.isToday
                }"
                @click="selectDate(day.date)"
              >
                {{ day.dayNumber }}
              </button>
            </div>
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
const calendarMonth = ref(dayjs())
const weekDays = ['Пн', 'Вт', 'Ср', 'Чт', 'Пт', 'Сб', 'Вс']
const weekDaysFull = ['Пн', 'Вт', 'Ср', 'Чт', 'Пт', 'Сб', 'Вс']

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

const monthYearDisplay = computed(() => {
  return calendarMonth.value.format('MMMM YYYY')
})

const calendarDays = computed(() => {
  const days: Array<{dayNumber: number, date: string, isCurrentMonth: boolean, isToday: boolean}> = []
  const startOfMonth = calendarMonth.value.startOf('month')
  const endOfMonth = calendarMonth.value.endOf('month')
  const startDay = startOfMonth.day() || 7
  const today = dayjs().format('YYYY-MM-DD')
  
  const prevMonth = calendarMonth.value.subtract(1, 'month')
  const prevMonthDays = prevMonth.daysInMonth()
  for (let i = startDay - 1; i > 0; i--) {
    const dayNum = prevMonthDays - i + 1
    days.push({
      dayNumber: dayNum,
      date: prevMonth.format(`YYYY-MM-${String(dayNum).padStart(2, '0')}`),
      isCurrentMonth: false,
      isToday: false
    })
  }
  
  for (let i = 1; i <= endOfMonth.date(); i++) {
    const dateStr = calendarMonth.value.format(`YYYY-MM-${String(i).padStart(2, '0')}`)
    days.push({
      dayNumber: i,
      date: dateStr,
      isCurrentMonth: true,
      isToday: dateStr === today
    })
  }
  
  const remainingDays = 42 - days.length
  for (let i = 1; i <= remainingDays; i++) {
    const nextMonth = calendarMonth.value.add(1, 'month')
    days.push({
      dayNumber: i,
      date: nextMonth.format(`YYYY-MM-${String(i).padStart(2, '0')}`),
      isCurrentMonth: false,
      isToday: false
    })
  }
  
  return days
})

const prevMonth = () => {
  calendarMonth.value = calendarMonth.value.subtract(1, 'month')
}

const nextMonth = () => {
  calendarMonth.value = calendarMonth.value.add(1, 'month')
}

const selectDate = (date: string) => {
  const fData = props.formData as any
  fData.date = date
}

watch(() => props.formData, (newFormData) => {
  selectedTagId.value = newFormData.tagId || null
  if (newFormData.date) {
    calendarMonth.value = dayjs(newFormData.date)
  }
}, { immediate: true })

watch(() => props.show, (isVisible) => {
  if (isVisible && props.editingEvent) {
    selectedTagId.value = props.editingEvent.tagId || null
  } else if (isVisible && props.formData.date) {
    calendarMonth.value = dayjs(props.formData.date)
  }
})

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
  background-color: #121212;
  padding: 20px;
  border-radius: 25px;
  width: 90%;
  max-width: 500px;
  max-height: 90vh;
  overflow-y: auto;
  position: relative;
  border: 1px solid #444;
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

.close {
  position: absolute;
  top: 18px;
  right: 40px;
  font-size: 32px;
  cursor: pointer;
  color: #888;
}

.close:hover {
  color: #fff;
}

.modal-content h2 {
  font-size: 16px;
  text-align: center;
  display: flex;
  color: #ffffffd8;
  gap: 10px;
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
  background-color: #2a2a2a;
  border: 1px solid #444;
  color: #fff;
  font-size: 13px;
  font-family: inherit;
  border-radius: 8px;
}

.form-group textarea {
  resize: vertical;
}

.form-group input:focus,
.form-group textarea:focus {
  outline: none;
  border-color: #1c3496;
}

.time-range {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 10px;
}

.time-range input {
  width: 100px;
  text-align: center;
}

.time-separator {
  color: #666;
  font-size: 16px;
}

.recurrence-options {
  margin-bottom: 10px;
}

.recurrence-select {
  width: 100%;
  padding: 10px;
  background-color: #2a2a2a;
  border: 1px solid #444;
  color: #fff;
  font-size: 14px;
  border-radius: 8px;
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
  border: 1px solid #444;
  border-radius: 4px;
  background: #2a2a2a;
  color: #888;
  font-size: 11px;
  cursor: pointer;
  transition: all 0.2s;
}

.day-btn:hover {
  background: #333;
  color: #fff;
}

.day-btn.selected {
  background: #3B82F6;
  border-color: #3B82F6;
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
  background-color: #333;
  margin: 12px -20px 12px -20px;
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
  background-color: #333;
}

.calendar-day.other-month {
  color: #444;
}

.calendar-day.today {
  border: 1px solid #1c3496;
}

.calendar-day.selected {
  background-color: #1c3496;
  color: #fff;
}

.form-actions {
  display: flex;
  gap: 10px;
  justify-content: center;
}

.btn {
  padding: 10px 12%;
  border: none;
  border-radius: 8px;
  cursor: pointer;
  font-size: 13px;
  transition: opacity 0.2s;
}

.btn:hover {
  opacity: 0.8;
}

.btn-primary {
  background-color: #1c3496;
  color: #fff;
}

.btn-secondary {
  background-color: #333;
  color: #fff;
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
  background-color: #2a2a2a;
  border: 1px solid #444;
  border-radius: 10px;
}

.tag-option {
  display: flex;
  align-items: center;
  gap: 6px;
  padding: 6px 12px;
  border-radius: 16px;
  background-color: #333;
  cursor: pointer;
  transition: all 0.2s;
  border: 2px solid transparent;
}

.tag-option:hover {
  background-color: #444;
}

.tag-option.selected {
  border-color: #fff;
  background-color: #4a5568;
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
  background: #1a1a1a;
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
