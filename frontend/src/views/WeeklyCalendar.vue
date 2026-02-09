<template>
  <div class="weekly-calendar">
    <!-- Top Bar -->
    <div class="top-bar">
      <div class="time-display">{{ currentTime }}</div>
      <div class="menu-wrapper">
        <ThreeDotsMenu />
      </div>
      <button class="nav-btn" @click="nextWeek"> </button>
    </div>


    <div class="top-bar2">
      <div class="view-selector">
        <button 
          class="view-btn" 
          :class="{ active: currentView === 'day' }"
          @click="currentView = 'day'"
        >
          day
        </button>
        <button 
          class="view-btn active" 
          :class="{ active: currentView === 'week' }"
          @click="currentView = 'week'"
        >
          week
        </button>
        <button 
          class="view-btn" 
          :class="{ active: currentView === 'month' }"
          @click="currentView = 'month'"
        >
          month
        </button>
        <button 
          class="view-btn" 
          :class="{ active: currentView === 'year' }"
          @click="currentView = 'year'"
        >
          year
        </button>
      </div>
    </div>
      
    <!-- Week View (original unchanged) -->
    <div v-if="currentView === 'week'">
      <!-- Calendar Header -->
      <div class="calendar-header">
        <div class="calendar-header2">
          <h1 class="month-year">{{ monthYear }}</h1>
          <button class="nav-btn1" @click="lastWeek"><</button>
          <button class="nav-btn1" @click="nextWeek">></button>
        </div>
        <div class="days-header">
          <div 
            v-for="day in weekDays" 
            :key="day.date"
            class="day-header"
          >
            <div class="day-name">{{ day.shortName }}</div>
            <div class="day-number">{{ day.number }}</div>
          </div>
        </div>
      </div>



      <!-- Calendar Grid -->
      <div class="calendar-grid">
        <div class="time-column">
          <div 
            v-for="hour in hours" 
            :key="hour"
            class="time-slot"
          >
            {{ formatTime(hour) }}
          </div>
        </div>

        <div class="days-container">
          <div 
            v-for="day in weekDays" 
            :key="day.date"
            class="day-column"
            @click="handleDayClick($event, day)"
          >
            <div 
              v-for="hour in hours" 
              :key="hour"
              class="hour-slot"
            ></div>
            <div
              v-for="event in getEventsForDay(day.date)"
              :key="event.id"
              class="event-block"
              :style="getEventStyle(event, day.date)"
              @click.stop="openEventModal(event)"
            >
              <div class="event-indicator"></div>
              <div class="event-content">
                <div class="event-time">{{ formatEventTime(event) }}</div>
                <div class="event-title">{{ event.title }}</div>
                <div v-if="event.description" class="event-description">{{ event.description }}</div>
                <div v-if="event.location" class="event-location">📍 {{ event.location }}</div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- Year View (new) -->
    <div v-else-if="currentView === 'year'" class="year-calendar">
      <div class="year-header">
        <h1 class="year-title">{{ currentYear }}</h1>
        <div class="year-nav">
          <button class="nav-btn1" @click="prevYear"><</button>
          <button class="nav-btn1" @click="nextYear">></button>
        </div>
      </div>
      
      <div class="year-grid">
        <div 
          v-for="month in months" 
          :key="month.number"
          class="month-in-year"
        >
          <h3 class="month-name">{{ month.name }}</h3>
          <div class="mini-calendar">
            <div class="mini-day-names">
              <span v-for="dayName in miniDayNames" :key="dayName">{{ dayName }}</span>
            </div>
            <div class="mini-days">
              <div 
                v-for="day in month.days" 
                :key="day.date"
                class="mini-day"
                :class="{
                  'today': day.isToday,
                  'other-month': !day.isCurrentMonth
                }"
                @click="handleMiniDayClick(day)"
              >
                {{ day.number }}
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- Month View (simplified) -->
    <div v-else-if="currentView === 'month'" class="month-calendar">
      <div class="month-header">
        <div class="month-header2">
          <h1 class="month-year-title">{{ currentMonth.format('MMMM YYYY') }}</h1>
          <div class="month-nav">
            <button class="nav-btn1" @click="prevMonth"><</button>
            <button class="nav-btn1" @click="nextMonth">></button>
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
          @click="handleMonthDayClick(day)"
        >
          <div class="month-day-number">{{ day.number }}</div>
          <div class="month-day-events">
            <div 
              v-for="event in getEventsForDay(day.date)" 
              :key="event.id"
              class="month-event"
              :style="{ backgroundColor: event.color || '#4a5568' }"
              @click.stop="openEventModal(event)"
            >
              {{ event.title }}
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- Day View (Placeholder) -->
    <div v-else-if="currentView === 'day'" class="day-view">
      <h2>Day View - Under Development</h2>
    </div>

    <!-- Event Modal -->
    <div v-if="showModal" class="modal" @click.self="closeModal">
      <div class="modal-content" @click.stop>
        <span class="close" @click="closeModal">&times;</span>
        <h2>{{ editingEvent ? 'Редактировать задачу' : 'Новая задача' }}</h2>
        <form @submit.prevent="saveEvent">
          <div class="form-group">
            <label for="eventTitle">Название задачи:</label>
            <input 
              type="text" 
              id="eventTitle" 
              v-model="eventForm.title" 
              required
              placeholder="Введите название задачи"
            >
          </div>
          <div class="form-group">
            <label for="eventDescription">Описание:</label>
            <textarea 
              id="eventDescription" 
              v-model="eventForm.description"
              placeholder="Добавьте описание задачи (необязательно)"
              rows="3"
            ></textarea>
          </div>
          <div class="form-group">
            <label for="eventDate">Дата:</label>
            <input 
              type="date" 
              id="eventDate" 
              v-model="eventForm.date" 
              required
            >
          </div>
          <div class="form-row">
            <div class="form-group">
              <label for="eventStartTime">Начало:</label>
              <input 
                type="time" 
                id="eventStartTime" 
                v-model="eventForm.startTime" 
                required
              >
            </div>
            <div class="form-group">
              <label for="eventEndTime">Конец:</label>
              <input 
                type="time" 
                id="eventEndTime" 
                v-model="eventForm.endTime" 
                required
              >
            </div>
          </div>
          <div class="form-group">
            <label for="eventLocation">Место (необязательно):</label>
            <input 
              type="text" 
              id="eventLocation" 
              v-model="eventForm.location"
              placeholder="Например: Школа, Библиотека"
            >
          </div>
          <div class="form-row">
            <div class="form-group">
              <label for="eventPriority">Приоритет:</label>
              <select id="eventPriority" v-model="eventForm.priority">
                <option value="low">Низкий</option>
                <option value="medium">Средний</option>
                <option value="high">Высокий</option>
              </select>
            </div>
            <div class="form-group">
              <label for="eventColor">Цвет:</label>
              <input 
                type="color" 
                id="eventColor" 
                v-model="eventForm.color"
              >
            </div>
          </div>
          <div class="form-actions">
            <button type="submit" class="btn btn-primary">Сохранить</button>
            <button 
              v-if="editingEvent"
              type="button" 
              class="btn btn-danger" 
              @click="deleteEvent"
            >
              Удалить
            </button>
            <button 
              type="button" 
              class="btn btn-secondary" 
              @click="closeModal"
            >
              Отмена
            </button>
          </div>
        </form>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted, onUnmounted } from 'vue'
import dayjs from 'dayjs'
import 'dayjs/locale/ru'
import { useCalendarStore } from '../stores/calendar'
import ThreeDotsMenu from '../components/ThreeDotsMenu.vue'
import { mockWeeklyEvents } from '../mock/weeklyData'

dayjs.locale('ru')

const calendarStore = useCalendarStore()

const currentView = ref('week')
const currentTime = ref('')
const currentWeekStart = ref(dayjs().startOf('week'))
const currentMonth = ref(dayjs().startOf('month'))
const currentYear = ref(dayjs().year())
const showModal = ref(false)
const editingEvent = ref<any>(null)

const eventForm = ref({
  title: '',
  description: '',
  date: '',
  startTime: '',
  endTime: '',
  location: '',
  priority: 'medium',
  color: '#4a5568'
})

const hours = Array.from({ length: 24 }, (_, i) => i) // 0:00 to 23:00
const dayNames = ['Пн', 'Вт', 'Ср', 'Чт', 'Пт', 'Сб', 'Вс']
const miniDayNames = ['П', 'В', 'С', 'Ч', 'П', 'С', 'В']

const weekDays = computed(() => {
  const days = []
  for (let i = 0; i < 7; i++) {
    const date = currentWeekStart.value.add(i, 'day')
    days.push({
      date: date.format('YYYY-MM-DD'),
      shortName: date.format('ddd').toUpperCase().slice(0, 2),
      number: date.date(),
      fullDate: date
    })
  }
  return days
})

const monthYear = computed(() => {
  return currentWeekStart.value.format('MMMM YYYY')
})

// Month View data
const monthDays = computed(() => {
  const days = []
  const startOfMonth = currentMonth.value.startOf('month')
  const endOfMonth = currentMonth.value.endOf('month')
  const startDay = startOfMonth.startOf('week')
  
  let currentDay = startDay
  for (let i = 0; i < 42; i++) { // 6 weeks
    days.push({
      date: currentDay.format('YYYY-MM-DD'),
      number: currentDay.date(),
      isToday: currentDay.isSame(dayjs(), 'day'),
      isCurrentMonth: currentDay.month() === currentMonth.value.month(),
      isWeekend: currentDay.day() === 6 || currentDay.day() === 0,
      fullDate: currentDay
    })
    currentDay = currentDay.add(1, 'day')
  }
  return days
})

// Year View data
const months = computed(() => {
  const monthsArray = []
  const today = dayjs()
  
  for (let month = 0; month < 12; month++) {
    const monthDate = dayjs().year(currentYear.value).month(month).startOf('month')
    const days = []
    
    // Get days for this month's mini calendar
    const startDay = monthDate.startOf('week')
    for (let i = 0; i < 42; i++) {
      const day = startDay.add(i, 'day')
      days.push({
        date: day.format('YYYY-MM-DD'),
        number: day.date(),
        isToday: day.isSame(today, 'day'),
        isCurrentMonth: day.month() === month,
        isWeekend: day.day() === 6 || day.day() === 0,
        fullDate: day
      })
    }
    
    monthsArray.push({
      number: month,
      name: monthDate.format('MMMM'),
      days: days
    })
  }
  return monthsArray
})

const getEventsForDay = (date: string) => {
  // Используем моковые данные для демонстрации
  return mockWeeklyEvents.filter(event => {
    const eventDate = dayjs(event.start).format('YYYY-MM-DD')
    return eventDate === date
  })
}

const getEventStyle = (event: any, dayDate: string) => {
  const start = dayjs(event.start)
  const end = dayjs(event.end)
  const dayStart = dayjs(dayDate).startOf('day')
  
  const startMinutes = start.diff(dayStart, 'minute')
  const duration = end.diff(start, 'minute')
  
  // 120px per hour, так что умножаем на 120
  const top = (startMinutes / 60) * 120
  const height = Math.max((duration / 60) * 120, 30) // минимум 30px высоты
  
  // Проверяем, что событие не выходит за пределы 24 часов
  const maxTop = 24 * 120 // 24 часа * 120px
  const clampedTop = Math.min(top, maxTop)
  const clampedHeight = Math.min(height, maxTop - clampedTop)
  
  return {
    top: `${clampedTop}px`,
    height: `${clampedHeight}px`,
    backgroundColor: '#4a5568',
    position: 'absolute' as const,
    left: '2px',
    right: '2px',
    zIndex: 10
  }
}

const formatTime = (hour: number) => {
  return `${hour.toString().padStart(2, '0')}:00`
}

const formatEventTime = (event: any) => {
  const start = dayjs(event.start)
  const end = dayjs(event.end)
  return `${start.format('HH:mm')} - ${end.format('HH:mm')}`
}

const updateTime = () => {
  currentTime.value = dayjs().format('HH:mm DD MMMM')
}

const nextWeek = () => {
  currentWeekStart.value = currentWeekStart.value.add(1, 'week')
  loadEvents()
}

const lastWeek = () => {
  currentWeekStart.value = currentWeekStart.value.add(-1, 'week')
  loadEvents()
}

const nextMonth = () => {
  currentMonth.value = currentMonth.value.add(1, 'month')
}

const prevMonth = () => {
  currentMonth.value = currentMonth.value.add(-1, 'month')
}

const nextYear = () => {
  currentYear.value += 1
}

const prevYear = () => {
  currentYear.value -= 1
}

const handleDayClick = (event: MouseEvent, day: any) => {
  const rect = (event.currentTarget as HTMLElement).getBoundingClientRect()
  const clickY = event.clientY - rect.top
  const hour = Math.floor(clickY / 120)
  const minutes = Math.floor((clickY % 120) / 120 * 60)
  
  const startTime = dayjs(day.fullDate).hour(hour).minute(minutes)
  const endTime = startTime.add(1, 'hour')
  
  eventForm.value = {
    title: '',
    description: '',
    date: day.date,
    startTime: startTime.format('HH:mm'),
    endTime: endTime.format('HH:mm'),
    location: '',
    priority: 'medium',
    color: '#4a5568'
  }
  
  editingEvent.value = null
  showModal.value = true
}

const handleMonthDayClick = (day: any) => {
  eventForm.value = {
    title: '',
    description: '',
    date: day.date,
    startTime: '09:00',
    endTime: '10:00',
    location: '',
    priority: 'medium',
    color: '#4a5568'
  }
  
  editingEvent.value = null
  showModal.value = true
}

const handleMiniDayClick = (day: any) => {
  if (day.isCurrentMonth) {
    eventForm.value = {
      title: '',
      description: '',
      date: day.date,
      startTime: '09:00',
      endTime: '10:00',
      location: '',
      priority: 'medium',
      color: '#4a5568'
    }
    
    editingEvent.value = null
    showModal.value = true
  }
}

const openEventModal = (event: any) => {
  editingEvent.value = event
  const start = dayjs(event.start)
  const end = dayjs(event.end)
  
  eventForm.value = {
    title: event.title,
    description: event.description || '',
    date: start.format('YYYY-MM-DD'),
    startTime: start.format('HH:mm'),
    endTime: end.format('HH:mm'),
    location: event.location || '',
    priority: event.priority || 'medium',
    color: event.color || '#4a5568'
  }
  
  showModal.value = true
}

const closeModal = () => {
  showModal.value = false
  editingEvent.value = null
  eventForm.value = {
    title: '',
    description: '',
    date: '',
    startTime: '',
    endTime: '',
    location: '',
    priority: 'medium',
    color: '#4a5568'
  }
}

const saveEvent = async () => {
  const start = dayjs(`${eventForm.value.date} ${eventForm.value.startTime}`)
  const end = dayjs(`${eventForm.value.date} ${eventForm.value.endTime}`)
  
  const eventData = {
    title: eventForm.value.title,
    description: eventForm.value.description || undefined,
    start: start.toISOString(),
    end: end.toISOString(),
    location: eventForm.value.location || undefined,
    priority: eventForm.value.priority,
    color: getPriorityColor(eventForm.value.priority),
    all_day: false
  }
  
  if (editingEvent.value) {
    await calendarStore.updateEvent(editingEvent.value.id, eventData)
  } else {
    await calendarStore.createEvent(eventData)
  }
  
  closeModal()
  loadEvents()
}

const getPriorityColor = (priority: string) => {
  const colors: Record<string, string> = {
    low: '#3a403c',      // серый
    medium: '#47381f',   // коричневый (как на изображении)
    high: '#3a1d19'       // красный
  }
  return colors[priority] || '#4a5568'
}

const deleteEvent = async () => {
  if (editingEvent.value) {
    await calendarStore.deleteEvent(editingEvent.value.id)
    closeModal()
    loadEvents()
  }
}

const loadEvents = async () => {
  // Используем моковые данные вместо реального API
  console.log('Loading mock events')
}

let timeInterval: ReturnType<typeof setInterval>

onMounted(() => {
  updateTime()
  timeInterval = setInterval(updateTime, 1000)
  loadEvents()
})

onUnmounted(() => {
  if (timeInterval) {
    clearInterval(timeInterval)
  }
})
</script>

<style scoped>
.weekly-calendar {
  width: 100%;
  min-height: 100vh;
  background-color: #050505;
  color: #ffffff;
  overflow: hidden;
}

.top-bar {
  margin-top: 5px;
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 10px 20px;
}

.menu-wrapper {
  display: flex;
  align-items: center;
  justify-content: center;
}

.menu-icon {
  width: 24px;
  height: 24px;
  cursor: pointer;
  margin-right: 125px;
}

.top-bar2 {
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 30px 0px 0px 0px;
}

.time-display {
  font-size: 22px;
  color: #ffffff;
  font-weight: 500;
}

.view-selector {
  display: flex;
  gap: 25px;
  background-color: #0f0f0f;
  padding: 5px 25px 5px 25px;
  border-radius: 15px;
}

.view-btn {
  background: transparent;
  border: none;
  color: #888;
  padding: 5px 10px;
  cursor: pointer;
  font-size: 22px;
  transition: color 0.2s;
  font-weight: bold;
}

.view-btn.active {
  color: #ffffff;
  background: #333;
  padding: 10px 25px 10px 25px;
  border-radius: 15px;
}

.nav-links {
  display: flex;
  gap: 20px;
}

/* WEEK VIEW - ORIGINAL STYLES (unchanged) */
.calendar-grid {
  display: grid;
  grid-template-columns: 60px 1fr 1fr 1fr 1fr 1fr 1fr 1fr;
  height: calc(100vh - 250px);
  overflow: auto;
  position: relative;
  min-height: 800px;
}

.time-column {
  display: flex;
  flex-direction: column;
  border-right: 1px solid #333;
}

.time-slot {
  height: 120px;
  border-bottom: 1px solid #333;
  display: flex;
  align-items: flex-start;
  justify-content: center;
  padding-top: 5px;
  font-size: 14px;
  color: #aaa;
}

.days-container {
  display: grid;
  grid-template-columns: repeat(7, 1fr);
  position: relative;
  min-height: 2880px; /* 24 часа * 120px */
}

.day-column {
  position: relative;
  border-left: 1px solid #333;
  min-height: 2880px; /* 24 часа * 120px */
  height: fit-content;
}

.hour-slot {
  height: 120px;
  border-bottom: 1px solid #333;
  position: relative;
  min-height: 120px;
}

.event-block {
  position: absolute;
  left: 2px;
  right: 2px;
  border-radius: 4px;
  padding: 5px;
  font-size: 12px;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
  z-index: 10;
  cursor: pointer;
}

.event-time {
  font-weight: bold;
  font-size: 10px;
  margin-bottom: 2px;
}

.event-title {
  font-weight: 500;
  font-size: 11px;
}

.event-description {
  font-size: 9px;
  opacity: 0.8;
}

.event-location {
  font-size: 9px;
  margin-top: 2px;
}

.nav-link {
  color: #888;
  text-decoration: none;
  font-size: 14px;
  transition: color 0.2s;
}

.nav-link:hover,
.nav-link.router-link-active {
  color: #fff;
}

.nav-btn {
  background: transparent;
  border: none;
  color: #ffffff;
  font-size: 18px;
  cursor: pointer;
  padding: 5px 10px;
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

.calendar-header {
  padding: 20px;
  border-bottom: 1px solid #80808021;
}

.calendar-header2 {
  display: flex;
}

.month-year {
  font-size: 52px;
  font-weight: 300;
  margin-bottom: 20px;
  text-transform: capitalize;
  font-weight: bold;
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

.day-number {
  font-size: 22px;
  font-weight: 700;
}

.calendar-grid {
  overflow: hidden;
  display: flex;
  position: relative;
  height: calc(100vh - 200px);
  overflow-y: auto;
}

.time-column {
  width: 90px;
  padding: 20px 0 0 20px;
  margin-top: -145px;
  border-right: 1px solid #808080;
}

.time-slot {
  height: 60px;
  display: flex;
  align-items: flex-start;
  padding-top: 120px;
  font-size: 20px;
  color: #6b6b6b;
  font-weight: bold;
}

.days-container {
  overflow: hidden;
  display: grid;
  grid-template-columns: repeat(7, 1fr);
  flex: 1;
  position: relative;
}

.day-column {
  border-right: 1px solid #333;
  position: relative;
  min-height: 2880px;
}

.hour-slot {
  height: 120px;
  border-bottom: 1px solid #222;
}

.event-block {
  position: absolute;
  left: 2px;
  right: 2px;
  background-color: #4a5568;
  border-radius: 4px;
  padding: 5px 8px;
  cursor: pointer;
  overflow: hidden;
  z-index: 10;
  transition: opacity 0.2s;
  display: flex;
  height: 100%;
  min-height: 30px;
}

.event-block:hover {
  opacity: 0.9;
}

.event-indicator {
  width: 7px;
  border-radius: 6px;
  background-color: #ffffff;
  margin-right: 8px;
  flex-shrink: 0;
  opacity: 0.7;
}

.event-content {
  flex: 1;
  overflow: hidden;
}

.event-time {
  font-size: 20px;
  color: rgba(255, 255, 255, 0.8);
  margin-bottom: 2px;
  font-weight: 500;
}

.event-title {
  font-size: 22px;
  font-weight: 600;
  margin-bottom: 2px;
}

.event-description {
  font-size: 18px;
  color: rgba(255, 255, 255, 0.8);
  margin-top: 3px;
  line-height: 1.3;
}

.event-location {
  font-size: 14px;
  color: rgba(255, 255, 255, 0.7);
  margin-top: 2px;
}

/* YEAR VIEW STYLES */
.year-calendar {
  padding: 20px;
}

.year-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 20px;
  border-bottom: 1px solid #80808021;
}

.year-title {
  font-size: 52px;
  font-weight: bold;
  margin: 0;
}

.year-nav {
  display: flex;
  gap: 10px;
}

.year-grid {
  display: grid;
  grid-template-columns: repeat(4, 1fr);
  gap: 20px;
  padding: 20px;
}

.month-in-year {
  background: #0f0f0f;
  border-radius: 10px;
  padding: 15px;
  transition: transform 0.2s;
}

.month-in-year:hover {
  transform: translateY(-2px);
}

.month-name {
  font-size: 24px;
  margin: 0 0 15px 0;
  text-align: center;
  font-weight: 600;
}

.mini-calendar {
  background: #1a1a1a;
  border-radius: 8px;
  padding: 10px;
}

.mini-day-names {
  display: grid;
  grid-template-columns: repeat(7, 1fr);
  gap: 2px;
  margin-bottom: 5px;
  text-align: center;
}

.mini-day-names span {
  font-size: 12px;
  color: #888;
  font-weight: bold;
}

.mini-days {
  display: grid;
  grid-template-columns: repeat(7, 1fr);
  gap: 2px;
}

.mini-day {
  aspect-ratio: 1;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 14px;
  cursor: pointer;
  border-radius: 50%;
  transition: background-color 0.2s;
}

.mini-day:hover {
  background-color: #333;
}

.mini-day.today {
  background-color: #4a90e2;
  color: white;
  font-weight: bold;
  border: 2px solid #4a90e2;
}

.mini-day.other-month {
  opacity: 0.3;
  cursor: default;
}

.mini-day.other-month:hover {
  background-color: transparent;
}

/* MONTH VIEW STYLES */
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
}

.month-nav {
  display: flex;
  gap: 10px;
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

.month-day.other-month:hover {
  background-color: transparent;
}

.month-day.weekend {
  background-color: rgba(255, 255, 255, 0.05);
}

.month-day-number {
  font-size: 18px;
  font-weight: 500;
  margin-bottom: 5px;
}

.month-event {
  font-size: 12px;
  padding: 2px 6px;
  margin-bottom: 2px;
  border-radius: 3px;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
  cursor: pointer;
}

/* DAY VIEW STYLES */
.day-view {
  padding: 40px;
  text-align: center;
}

.day-view h2 {
  font-size: 36px;
  color: #888;
}

/* MODAL STYLES */
.modal {
  overflow: hidden;
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
  background-color: #1a1a1a;
  padding: 30px;
  border-radius: 8px;
  width: 90%;
  max-width: 500px;
  position: relative;
}

.close {
  position: absolute;
  top: 15px;
  right: 20px;
  font-size: 28px;
  cursor: pointer;
  color: #888;
}

.close:hover {
  color: #fff;
}

.modal-content h2 {
  margin-bottom: 20px;
  font-size: 24px;
}

.form-group {
  margin-bottom: 15px;
}

.form-group label {
  display: block;
  margin-bottom: 5px;
  font-size: 14px;
  color: #ccc;
}

.form-group input,
.form-group textarea,
.form-group select {
  width: 100%;
  padding: 10px;
  background-color: #2a2a2a;
  border: 1px solid #444;
  border-radius: 4px;
  color: #fff;
  font-size: 14px;
  font-family: inherit;
}

.form-group textarea {
  resize: vertical;
}

.form-group input[type="color"] {
  height: 40px;
  cursor: pointer;
}

.form-row {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 15px;
}

.form-actions {
  display: flex;
  gap: 10px;
  margin-top: 20px;
}

.btn {
  padding: 10px 20px;
  border: none;
  border-radius: 4px;
  cursor: pointer;
  font-size: 14px;
  transition: opacity 0.2s;
}

.btn:hover {
  opacity: 0.8;
}

.btn-primary {
  background-color: #4a5568;
  color: #fff;
}

.btn-secondary {
  background-color: #333;
  color: #fff;
}

.btn-danger {
  background-color: #dc3545;
  color: #fff;
}
</style>