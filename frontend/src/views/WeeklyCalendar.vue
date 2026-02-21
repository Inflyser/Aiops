<template>
  <div class="weekly-calendar">
    <!-- Top Bar -->
    <CalendarTopBar 
      :compact-mode="compactMode"
      :current-view="currentView"
      @toggle-compact="compactMode = $event"
    />

    <!-- View Selector -->
    <ViewSelector 
      :current-view="currentView"
      @update:model-value="currentView = $event"
    />
      
    <!-- Week View -->
    <div v-if="currentView === 'week'" class="week-view-container">
      <!-- Calendar Header -->
      <CalendarHeader 
        :current-week-start="currentWeekStart"
        @prev-week="lastWeek"
        @next-week="nextWeek"
      />

      <!-- Calendar Grid -->
      <WeekView 
        :week-days="weekDays"
        :events="events"
        :compact-mode="compactMode"
        @day-click="handleWeekDayClick"
        @open-event="openEventModal"
      />
    </div>

    <!-- Year View -->
    <div v-else-if="currentView === 'year'">
      <YearView 
        :current-year="currentYear"
        @prev-year="prevYear"
        @next-year="nextYear"
        @day-click="handleMiniDayClick"
      />
    </div>

    <!-- Month View -->
    <div v-else-if="currentView === 'month'">
      <MonthView 
        :current-month="currentMonth"
        :events="events"
        @prev-month="prevMonth"
        @next-month="nextMonth"
        @day-click="handleMonthDayClick"
        @open-event="openEventModal"
      />
    </div>

    <!-- Day View (Placeholder) -->
    <div v-else-if="currentView === 'day'" class="day-view">
      <h2>Day View - Under Development</h2>
    </div>

    <!-- Event Modal -->
    <EventModal 
      :show="showModal"
      :editing-event="editingEvent"
      :form-data="eventForm"
      @close="closeModal"
      @save="saveEvent"
      @delete="deleteEvent"
    />
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted, onUnmounted } from 'vue'
import dayjs from 'dayjs'
import 'dayjs/locale/ru'
import { useCalendarStore } from '../stores/calendar'
import { mockWeeklyEvents } from '../mock/weeklyData'

// Components
import CalendarTopBar from '../components/CalendarTopBar.vue'
import ViewSelector from '../components/ViewSelector.vue'
import CalendarHeader from '../components/CalendarHeader.vue'
import WeekView from '../components/WeekView.vue'
import MonthView from '../components/MonthView.vue'
import YearView from '../components/YearView.vue'
import EventModal from '../components/EventModal.vue'

dayjs.locale('ru')

const calendarStore = useCalendarStore()

// State
const currentView = ref('week')
const currentWeekStart = ref(dayjs().startOf('week'))
const currentMonth = ref(dayjs().startOf('month'))
const currentYear = ref(dayjs().year())
const showModal = ref(false)
const editingEvent = ref<any>(null)

// Переключатель режима: false = полный день (0-23), true = рабочий день (7-23)
const compactMode = ref(false)

// Events (mock data)
const events = computed(() => mockWeeklyEvents)

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

// Computed week days
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

// Navigation functions
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

// Event handlers
const handleWeekDayClick = (day: any, event: MouseEvent) => {
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
    low: '#3a403c',
    medium: '#47381f',
    high: '#3a1d19'
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
  console.log('Loading mock events')
}

onMounted(() => {
  loadEvents()
})
</script>

<style scoped>
.weekly-calendar {
  width: 100%;
  height: 100vh;
  background-color: #050505;
  color: #ffffff;
  display: flex;
  flex-direction: column;
}

/* Week View Container - with internal scrolling */
.week-view-container {
  flex: 1;
  display: flex;
  flex-direction: column;
  min-height: 0;
}

/* DAY VIEW */
.day-view {
  padding: 40px;
  text-align: center;
}

.day-view h2 {
  font-size: 36px;
  color: #888;
}
</style>
