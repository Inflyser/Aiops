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
      
      <form @submit.prevent="$emit('save')">
        <!-- Название задачи -->
        <div class="form-group">
          
          <input 
            type="text" 
            id="eventTitle" 
            v-model="formData.title" 
            required
            placeholder="Введите название задачи"
          >
        </div>
        
        <!-- Описание -->
        <div class="form-group">
          <textarea 
            id="eventDescription" 
            v-model="formData.description"
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
            v-if="editingEvent"
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
            Отмена
          </button>
          <button type="submit" class="btn btn-primary">Сохранить</button>
        </div>
      </form>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, watch } from 'vue'
import dayjs from 'dayjs'
import 'dayjs/locale/ru'

interface Tag {
  id: string
  name: string
  color: string
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
}

const props = defineProps<{
  show: boolean
  editingEvent: CalendarEvent | null
  formData: EventFormData
  availableTags: Tag[]
}>()

const emit = defineEmits<{
  (e: 'close'): void
  (e: 'save'): void
  (e: 'delete'): void
}>()

const selectedTagId = ref<string | null>(null)
const calendarMonth = ref(dayjs())
const weekDays = ['Пн', 'Вт', 'Ср', 'Чт', 'Пт', 'Сб', 'Вс']

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
}

.modal-content {
  background-color: #121212;
  padding: 30px;
  border-radius: 35px;
  width: 90%;
  max-width: 500px;
  position: relative;
  border: 1px solid #444;
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
  font-size: 18px;
  text-align: center;
  display: flex;

  gap: 15px;
}

.header-icon {
  width: 24px;
  height: 24px;
}

.form-group {
  margin-bottom: 15px;
}

.form-group label {
  display: block;
  margin-bottom: 8px;
  font-size: 13px;
  color: #888;
  text-transform: uppercase;
  letter-spacing: 0.5px;
}

.form-group input,
.form-group textarea {
  width: 100%;
  padding: 12px;
  background-color: #2a2a2a;
  border: 1px solid #444;
  color: #fff;
  font-size: 14px;
  font-family: inherit;
  border-radius: 10px;
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

.divider {
  height: 1px;
  background-color: #333;
  margin: 20px -30px 20px -30px;
}

.month-navigator {
  display: flex;
  align-items: center;
  justify-content: space-between;
  margin-bottom: 10px;
}

.nav-btn {
  background: none;
  border: none;
  color: #888;
  font-size: 18px;
  cursor: pointer;
  padding: 5px 10px;
}

.nav-btn:hover {
  color: #fff;
}

.month-year {
  font-size: 18px;
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
  margin-bottom: 8px;
}

.weekdays span {
  font-size: 16px;
  color: #666;
  text-transform: uppercase;
}

.calendar-days {
  display: grid;
  grid-template-columns: repeat(7, 1fr);
  gap: 1px;
}

.calendar-day {
  aspect-ratio: 1;
  display: flex;
  align-items: center;
  justify-content: center;
  background: none;
  border: none;
  color: #ddd;
  font-size: 16px;
  cursor: pointer;
  border-radius: 12px;
  transition: all 0.2s;
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
  padding: 12px 12%;
  border: none;
  border-radius: 10px;
  cursor: pointer;
  font-size: 14px;
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
</style>
