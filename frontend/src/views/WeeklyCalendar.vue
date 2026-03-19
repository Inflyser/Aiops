<template>
  <div class="weekly-calendar">
    <!-- Top Bar -->
    <CalendarTopBar
      :compact-mode="compactMode"
      :current-view="currentView"
      :show-tags-panel="showTagsPanel"
      :show-inbox-panel="showInboxPanel"
      @toggle-compact="compactMode = $event"
      @toggle-tags="showTagsPanel = !showTagsPanel"
      @toggle-inbox="showInboxPanel = !showInboxPanel"
    />

    <!-- Tags Panel -->
    <TagsPanel 
      v-if="showTagsPanel"
      :tags="tags"
      @close="showTagsPanel = false"
      @add-tag="addTag"
      @delete-tag="deleteTag"
    />

    <!-- View Selector -->
    <ViewSelector 
      :current-view="currentView"
      @update:model-value="currentView = $event"
    />
      
    <!-- Week View -->
    <Transition name="slide-fade" mode="out-in">
      <div v-if="currentView === 'week'" key="week" class="week-view-container">
        <!-- Calendar Header -->
        <div class="calendar-header-with-inbox">
          <CalendarHeader
            :current-week-start="currentWeekStart"
            :inbox-panel-open="showInboxPanel"
            @prev-week="lastWeek"
            @next-week="nextWeek"
          />
        </div>

        <!-- Calendar Grid -->
        <WeekView
          :week-days="weekDays"
          :events="events"
          :compact-mode="compactMode"
          :inbox-panel-open="showInboxPanel"
          @day-click="handleWeekDayClick"
          @open-event="openEventModal"
          @open-event-tasks="openEventTasksModal"
          @event-drop="handleEventDrop"
          @event-copy="handleEventCopy"
          @event-move-to-next-week="handleMoveToNextWeek"
          @task-drop-to-event="handleTaskDropToEvent"
        />
      </div>

      <!-- Year View -->
      <div v-else-if="currentView === 'year'" key="year">
        <YearView 
          :current-year="currentYear"
          @prev-year="prevYear"
          @next-year="nextYear"
          @day-click="handleMiniDayClick"
        />
      </div>

      <!-- Month View -->
      <div v-else-if="currentView === 'month'" key="month">
        <MonthView
          :current-month="currentMonth"
          :events="events"
          @prev-month="prevMonth"
          @next-month="nextMonth"
          @day-click="handleMonthDayClick"
          @open-event="openEventModal"
          @open-event-tasks="openEventTasksModal"
        />
      </div>

      <!-- Day View -->
      <div v-else-if="currentView === 'day'" key="day" class="day-view-container" style="flex: 1; display: flex; flex-direction: column; min-height: 0;">
        <DayView
          :current-day="currentDay"
          :events="dayEvents"
          :compact-mode="compactMode"
          @prev-day="prevDay"
          @next-day="nextDay"
          @go-today="goToToday"
          @toggle-compact="toggleCompactMode"
          @hour-click="handleDayHourClick"
          @open-event="openEventModal"
          @open-event-tasks="openEventTasksModal"
        />
      </div>
    </Transition>

    <!-- Event Modal -->
    <EventModal
      :show="showModal"
      :editing-event="editingEvent"
      :form-data="eventForm"
      :available-tags="tags"
      :view-mode="viewMode"
      @close="closeModal"
      @save="saveEvent"
      @delete="deleteEvent"
    />

    <!-- Event Tasks Modal -->
    <EventTasksModal
      :show="showEventTasksModal"
      :event="selectedEventForTasks"
      @close="closeEventTasksModal"
      @task-removed="loadEvents"
    />

    <!-- Inbox Panel -->
    <InboxPanel
      :is-open="showInboxPanel"
      @close="showInboxPanel = false"
    />
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted, onUnmounted, watch } from 'vue'
import dayjs from 'dayjs'
import 'dayjs/locale/ru'
import { useCalendarStore } from '../stores/calendar'
import { useTagsStore } from '../stores/tags'
import { useTasksStore } from '../stores/tasks'
import { useKanbanStore } from '../stores/kanban'
import axios from 'axios'

// Components
import CalendarTopBar from '../components/calendar/CalendarTopBar.vue'
import ViewSelector from '../components/ui/ViewSelector.vue'
import CalendarHeader from '../components/calendar/CalendarHeader.vue'
import WeekView from '../components/calendar/WeekView.vue'
import MonthView from '../components/calendar/MonthView.vue'
import YearView from '../components/calendar/YearView.vue'
import DayView from '../components/calendar/DayView.vue'
import EventModal from '../components/modals/EventModal.vue'
import EventTasksModal from '../components/modals/EventTasksModal.vue'
import TagsPanel from '../components/modals/TagsPanel.vue'
import InboxPanel from '../components/calendar/InboxPanel.vue'

dayjs.locale('ru')

const calendarStore = useCalendarStore()
const tagsStore = useTagsStore()
const tasksStore = useTasksStore()
const kanbanStore = useKanbanStore()

// API для связи задач с событиями
const eventTasksApi = axios.create({
  baseURL: '/api/v1/event-tasks',
  headers: {
    'Content-Type': 'application/json'
  }
})

// Выбранное событие (для копирования)
const selectedEventId = ref<string | null>(null)

// State
const currentView = ref('day')
const currentDay = ref(dayjs())
const currentWeekStart = ref(dayjs().startOf('week'))
const currentMonth = ref(dayjs().startOf('month'))
const currentYear = ref(dayjs().year())
const showModal = ref(false)
const editingEvent = ref<any>(null)
const viewMode = ref<'view' | 'edit' | null>(null)
const showEventTasksModal = ref(false)
const selectedEventForTasks = ref<any>(null)

// Локальное состояние для bounce анимации
const bouncingEvents = ref<Set<string>>(new Set())

// Переключатель режима: true = рабочий день (7-23), false = полный день (0-23)
// По умолчанию рабочий день (7-24)
const compactMode = ref(true)

// Tags state
const showTagsPanel = ref(false)

// Inbox state
const showInboxPanel = ref(false)

// Tags methods
const addTag = async (tag: { name: string; color: string; icon?: string }) => {
  try {
    await tagsStore.createTag(tag)
  } catch (error) {
    console.error('Failed to add tag:', error)
  }
}

const deleteTag = async (tagId: string) => {
  try {
    await tagsStore.deleteTag(tagId)
  } catch (error) {
    console.error('Failed to delete tag:', error)
  }
}

// Computed for tags from store
const tags = computed(() => tagsStore.tags)

// Функция для получения цвета тега по ID
const getTagColor = (tagId: string | undefined): string => {
  if (!tagId) return '#4a5568'
  const tag = tags.value.find(t => t.id === tagId)
  return tag?.color || '#4a5568'
}

// Функция для получения иконки тега по ID
const getTagIcon = (tagId: string | undefined): string | undefined => {
  if (!tagId) return undefined
  const tag = tags.value.find(t => t.id === tagId)
  return tag?.icon
}

// Events from calendar store (с уже установленными цветами от тегов)
const events = computed(() => {
  return calendarStore.events.map(event => ({
    ...event,
    // Используем цвет события или цвет тега, если он есть
    color: event.color || getTagColor(event.tag_id),
    // Иконка тега
    tagIcon: getTagIcon(event.tag_id),
    // Используем локальное состояние для bounce анимации
    bouncing: bouncingEvents.value.has(String(event.id))
  }))
})

// Фильтрованные события для дневного вида
const dayEvents = computed(() => {
  const currentDayStr = currentDay.value.format('YYYY-MM-DD')
  return events.value.filter(event => {
    const eventDate = dayjs(event.start).format('YYYY-MM-DD')
    return eventDate === currentDayStr
  })
})

const eventForm = ref({
  title: '',
  description: '',
  date: '',
  startTime: '',
  endTime: '',
  location: '',
  priority: 'medium',
  color: '#4a5568',
  tagId: undefined as string | undefined,
  recurrenceType: undefined as string | undefined,
  recurrenceDays: undefined as string | undefined,
  recurrenceEndDate: undefined as string | undefined
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

// Day navigation
const prevDay = () => {
  currentDay.value = currentDay.value.subtract(1, 'day')
  loadEventsForDay()
}

const nextDay = () => {
  currentDay.value = currentDay.value.add(1, 'day')
  loadEventsForDay()
}

const goToToday = () => {
  currentDay.value = dayjs()
  loadEventsForDay()
}

const toggleCompactMode = () => {
  compactMode.value = !compactMode.value
}

const loadEventsForDay = async () => {
  // Загружаем всю неделю чтобы данные были доступны для фильтрации
  const startOfWeek = currentDay.value.startOf('week').format('YYYY-MM-DD')
  const endOfWeek = currentDay.value.startOf('week').add(6, 'day').format('YYYY-MM-DD')
  await calendarStore.fetchEvents(startOfWeek, endOfWeek)
}

const handleDayHourClick = (data: { hour: number; date: dayjs.Dayjs }) => {
  const { hour, date } = data
  const startTime = date.hour(hour)
  const endTime = startTime.add(1, 'hour')
  
  eventForm.value = {
    title: '',
    description: '',
    date: date.format('YYYY-MM-DD'),
    startTime: startTime.format('HH:mm'),
    endTime: endTime.format('HH:mm'),
    location: '',
    priority: 'medium',
    color: '#4a5568',
    tagId: undefined,
    recurrenceType: undefined,
    recurrenceDays: undefined,
    recurrenceEndDate: undefined
  }
  
  editingEvent.value = null
  showModal.value = true
}

// Event handlers
const handleWeekDayClick = (data: { day: any; dateTime: dayjs.Dayjs }) => {
  const { day, dateTime } = data
  const endTime = dateTime.add(1, 'hour')
  
  eventForm.value = {
    title: '',
    description: '',
    date: day.date,
    startTime: dateTime.format('HH:mm'),
    endTime: endTime.format('HH:mm'),
    location: '',
    priority: 'medium',
    color: '#4a5568',
    tagId: undefined,
    recurrenceType: undefined,
    recurrenceDays: undefined,
    recurrenceEndDate: undefined
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
    color: '#4a5568',
    tagId: undefined,
    recurrenceType: undefined,
    recurrenceDays: undefined,
    recurrenceEndDate: undefined
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
      color: '#4a5568',
      tagId: undefined,
      recurrenceType: undefined,
      recurrenceDays: undefined,
      recurrenceEndDate: undefined
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
    color: event.color || '#4a5568',
    tagId: event.tag_id || event.tagId || undefined,
    recurrenceType: event.recurrence_type || undefined,
    recurrenceDays: event.recurrence_days || undefined,
    recurrenceEndDate: event.recurrence_end_date ? dayjs(event.recurrence_end_date).format('YYYY-MM-DD') : undefined
  }
  
  showModal.value = true
}

const closeModal = () => {
  showModal.value = false
  editingEvent.value = null
  viewMode.value = null
  eventForm.value = {
    title: '',
    description: '',
    date: '',
    startTime: '',
    endTime: '',
    location: '',
    priority: 'medium',
    color: '#4a5568',
    tagId: undefined,
    recurrenceType: undefined,
    recurrenceDays: undefined,
    recurrenceEndDate: undefined
  }
}

const openEventTasksModal = (event: any) => {
  selectedEventForTasks.value = event
  showEventTasksModal.value = true
}

const closeEventTasksModal = () => {
  showEventTasksModal.value = false
  selectedEventForTasks.value = null
}

const saveEvent = async () => {
  const start = dayjs(`${eventForm.value.date} ${eventForm.value.startTime}`)
  const end = dayjs(`${eventForm.value.date} ${eventForm.value.endTime}`)
  
  // Если выбран тег, используем его цвет, иначе дефолтный
  const eventColor = eventForm.value.tagId 
    ? getTagColor(eventForm.value.tagId)
    : '#4a5568'
  
  const eventData: any = {
    title: eventForm.value.title,
    description: eventForm.value.description || undefined,
    start: start.toISOString(),
    end: end.toISOString(),
    location: eventForm.value.location || undefined,
    priority: eventForm.value.priority,
    color: eventColor,
    all_day: false,
    tag_id: eventForm.value.tagId
  }
  
  // Добавляем данные о повторении
  if (eventForm.value.recurrenceType) {
    eventData.recurrence_type = eventForm.value.recurrenceType
    eventData.recurrence_days = eventForm.value.recurrenceDays
    if (eventForm.value.recurrenceEndDate) {
      eventData.recurrence_end_date = dayjs(eventForm.value.recurrenceEndDate).toISOString()
    }
  }
  
  if (editingEvent.value) {
    // Сохраняем старое событие для отмены
    const oldEvent = { ...editingEvent.value }
    // Используем original_id если есть (для повторяющихся событий)
    const eventIdToUpdate = editingEvent.value.original_id || editingEvent.value.id
    await calendarStore.updateEvent(eventIdToUpdate, eventData)
    // Добавляем в историю
    calendarStore.addToHistory({
      type: 'update',
      eventId: eventIdToUpdate,
      oldEvent,
      newEvent: { ...editingEvent.value, ...eventData }
    })
  } else {
    const newEvent = await calendarStore.createEvent(eventData)
    // Добавляем в историю
    calendarStore.addToHistory({
      type: 'create',
      eventId: newEvent.id,
      newEvent
    })
  }
  
  closeModal()
  loadEvents()
}

const deleteEvent = async () => {
  if (editingEvent.value) {
    // Сохраняем событие для отмены
    const deletedEvent = { ...editingEvent.value }
    // Используем original_id если есть (для повторяющихся событий)
    const eventIdToDelete = editingEvent.value.original_id || editingEvent.value.id
    await calendarStore.deleteEvent(eventIdToDelete)
    // Добавляем в историю
    calendarStore.addToHistory({
      type: 'delete',
      eventId: eventIdToDelete,
      oldEvent: deletedEvent
    })
    closeModal()
    loadEvents()
  }
}

const loadEvents = async () => {
  // Load events from backend for current week
  const startOfWeek = currentWeekStart.value.format('YYYY-MM-DD')
  const endOfWeek = currentWeekStart.value.add(6, 'day').format('YYYY-MM-DD')
  await calendarStore.fetchEvents(startOfWeek, endOfWeek)
}

// Handle drag and drop event
const handleEventDrop = async (data: { event: any; newDate: string; newStart: string; newEnd: string }) => {
  const { event, newStart, newEnd } = data
  
  // Сохраняем старое событие для отмены
  const oldEvent = { ...event }
  
  const eventData = {
    title: event.title,
    description: event.description || undefined,
    start: newStart,
    end: newEnd,
    location: event.location || undefined,
    priority: event.priority || 'medium',
    color: event.color || '#4a5568',
    all_day: false,
    tag_id: event.tag_id || event.tagId || undefined
  }
  
  // Включаем bounce анимацию
  bouncingEvents.value.add(String(event.id))
  
  // Update the event in the store/backend
  await calendarStore.updateEvent(event.id, eventData)
  
  // Добавляем в историю
  calendarStore.addToHistory({
    type: 'update',
    eventId: event.id,
    oldEvent,
    newEvent: { ...event, ...eventData }
  })
  
  console.log('Event moved:', event.title, 'to', newStart)
  
  // Remove bounce effect after animation completes
  setTimeout(() => {
    const newSet = new Set(bouncingEvents.value)
    newSet.delete(String(event.id))
    bouncingEvents.value = newSet
  }, 500)
}

// Handle move event to next week (+7 days)
const handleMoveToNextWeek = async (event: any) => {
  const originalStart = dayjs(event.start)
  const originalEnd = dayjs(event.end)
  
  // Add 7 days to the event
  const newStart = originalStart.add(7, 'day')
  const newEnd = originalEnd.add(7, 'day')
  
  const eventData = {
    title: event.title,
    description: event.description || undefined,
    start: newStart.toISOString(),
    end: newEnd.toISOString(),
    location: event.location || undefined,
    priority: event.priority || 'medium',
    color: event.color || '#4a5568',
    all_day: false,
    tag_id: event.tag_id || event.tagId || undefined
  }
  
  // Update the event in the store/backend
  await calendarStore.updateEvent(event.id, eventData)
  
  console.log('Event moved to next week:', event.title, 'to', newStart.format('YYYY-MM-DD HH:mm'))
}

// Handle task drop to event
const handleTaskDropToEvent = async (data: { task: any; event: any }) => {
  const { task, event } = data
  
  try {
    // Добавляем задачу к событию через API
    await eventTasksApi.post('/', {
      event_id: event.id,
      task_id: task.id,
      order: 0
    })
    
    // Обновляем события, чтобы отобразить количество задач
    await loadEvents()
    
    console.log('Task added to event:', task.title, '->', event.title)
  } catch (error) {
    console.error('Failed to add task to event:', error)
  }
}

// Handle Alt+drag copy event
const handleEventCopy = async (data: { event: any; newDate: string; newStart: string; newEnd: string }) => {
  const { event, newStart, newEnd } = data
  
  const eventData = {
    title: event.title,
    description: event.description || undefined,
    start: newStart,
    end: newEnd,
    location: event.location || undefined,
    priority: event.priority || 'medium',
    color: event.color || '#4a5568',
    all_day: false,
    tag_id: event.tag_id || event.tagId || undefined
  }
  
  // Create a new event (copy)
  const newEvent = await calendarStore.createEvent(eventData)
  
  // Добавляем в историю
  calendarStore.addToHistory({
    type: 'create',
    eventId: newEvent.id,
    newEvent
  })
  
  loadEvents()
  
  console.log('Event copied:', event.title, 'to', newStart)
}

// Keyboard navigation handler
const handleKeydown = (event: KeyboardEvent) => {
  // Ignore if modal is open or input is focused
  if (showModal.value) return
  
  const target = event.target as HTMLElement
  if (target.tagName === 'INPUT' || target.tagName === 'TEXTAREA' || target.tagName === 'SELECT') {
    return
  }
  
  // Ctrl+Z или Ctrl+Я (русская раскладка) - отменить действие
  if (event.ctrlKey && (event.key === 'z' || event.key === 'я')) {
    event.preventDefault()
    console.log('Ctrl+Z pressed, calling undo...')
    calendarStore.undo().then(() => {
      loadEvents()
    })
    return
  }
  
  // Ctrl+C - копировать событие
  if (event.ctrlKey && event.key === 'c' && selectedEventId.value) {
    const eventToCopy = calendarStore.events.find(e => e.id === selectedEventId.value)
    if (eventToCopy) {
      calendarStore.copyEvent(eventToCopy)
    }
    return
  }
  
  // Ctrl+V - вставить событие
  if (event.ctrlKey && event.key === 'v') {
    if (calendarStore.hasCopiedEvent()) {
      calendarStore.pasteEvent().then(() => {
        loadEvents()
      })
    }
    return
  }
  
  switch (event.key) {
    case 'ArrowLeft':
      // Previous
      if (currentView.value === 'week') {
        lastWeek()
      } else if (currentView.value === 'month') {
        prevMonth()
      } else if (currentView.value === 'year') {
        prevYear()
      } else if (currentView.value === 'day') {
        prevDay()
      }
      break
    case 'ArrowRight':
      // Next
      if (currentView.value === 'week') {
        nextWeek()
      } else if (currentView.value === 'month') {
        nextMonth()
      } else if (currentView.value === 'year') {
        nextYear()
      } else if (currentView.value === 'day') {
        nextDay()
      }
      break
    case 'ArrowUp':
      // Previous month view
      if (currentView.value === 'month') {
        prevMonth()
      }
      break
    case 'ArrowDown':
      // Next month view
      if (currentView.value === 'month') {
        nextMonth()
      }
      break
    case 'Delete':
    case 'Backspace':
      // Удалить выбранное событие
      if (selectedEventId.value) {
        calendarStore.deleteEvent(selectedEventId.value)
        selectedEventId.value = null
        loadEvents()
      }
      break
    case 'Escape':
      // Снять выделение
      selectedEventId.value = null
      break
  }
}

// Watch for view changes to reload events for the current view
watch(currentView, async (newView) => {
  if (newView === 'day') {
    // For day view, also load a wider range (week) to have data available
    loadEvents()
  }
})

onMounted(() => {
  // Load events for current week by default (so we have data for all views)
  loadEvents()
  tagsStore.fetchTags()
  // Load tasks and kanban columns for Inbox panel
  tasksStore.fetchTasks()
  kanbanStore.fetchColumns()
  window.addEventListener('keydown', handleKeydown)
})

onUnmounted(() => {
  window.removeEventListener('keydown', handleKeydown)
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

/* Calendar Header */
.calendar-header-with-inbox {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 10px 20px;
  border-bottom: 1px solid #333;
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

/* View Transition Animations - Slide effect */
.slide-fade-enter-active,
.slide-fade-leave-active {
  transition: all 0.35s cubic-bezier(0.4, 0, 0.2, 1);
}

.slide-fade-enter-from {
  opacity: 0;
  transform: translateX(40px) scale(0.95);
}

.slide-fade-leave-to {
  opacity: 0;
  transform: translateX(-40px) scale(0.95);
}
</style>
