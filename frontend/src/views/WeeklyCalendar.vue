<template>
  <div class="weekly-calendar" :class="{ 
    'inbox-open': showInboxPanel,
    'with-background': currentBackground
  }" :style="currentBackground ? { backgroundColor: `rgba(5, 5, 5, ${1 - backgroundOpacity})` } : {}">
    <!-- Top Bar -->
    <CalendarTopBar
      :current-view="currentView"
      :show-tags-panel="showTagsPanel"
      :show-inbox-panel="showInboxPanel"
      :show-important-panel="showImportantPanel"
      @toggle-tags="showTagsPanel = !showTagsPanel"
      @toggle-inbox="showInboxPanel = !showInboxPanel"
      @toggle-important="showImportantPanel = !showImportantPanel"
      @open-settings="showSettings = true"
    />

    <!-- Tags Panel -->
    <TagsPanel 
      v-if="showTagsPanel"
      :tags="tags"
      @close="showTagsPanel = false"
      @add-tag="addTag"
      @delete-tag="deleteTag"
    />

    <!-- Important Events Panel -->
    <ImportantEventsPanel 
      v-if="showImportantPanel"
      :important-events="importantEvents"
      @close="showImportantPanel = false"
      @open-event="openImportantEvent"
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
            :compact-mode="compactMode"
            @prev-week="lastWeek"
            @next-week="nextWeek"
            @toggle-compact="compactMode = $event"
          />
        </div>

        <!-- Calendar Grid -->
        <WeekView
          :week-days="weekDays"
          :events="events"
          :compact-mode="compactMode"
          :event-accent-mode="eventAccentMode"
          :inbox-panel-open="showInboxPanel"
          @day-click="handleWeekDayClick"
          @open-event="openEventModal"
          @open-event-tasks="openEventTasksModal"
          @event-drop="handleEventDrop"
          @event-copy="handleEventCopy"
          @event-move-to-next-week="handleMoveToNextWeek"
          @task-drop-to-event="handleTaskDropToEvent"
          @task-drop-to-day="handleTaskDropToDay"
          @category-drop-to-day="handleCategoryDropToDay"
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
          @hour-click="handleDayHourClick"
          @open-event="openEventModal"
          @open-event-tasks="openEventTasksModal"
          @event-move-to-next-week="handleMoveToNextWeekForDay"
          @event-drop="handleEventDropForDay"
          @event-copy="handleEventCopyForDay"
          @task-drop-to-event="handleTaskDropToEventForDay"
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
      @task-removed="handleTaskRemoved"
    />

    <!-- Inbox Panel -->
    <InboxPanel
      :is-open="showInboxPanel"
      @close="showInboxPanel = false"
      @category-dropped-to-event="handleCategoryDroppedToEvent"
    />

    <!-- Settings Modal -->
    <div v-if="showSettings" class="modal-overlay" @click.self="showSettings = false">
      <div class="settings-modal">
        <div class="modal-header">
          <h3>Настройки</h3>
          <button class="close-btn" @click="showSettings = false">&times;</button>
        </div>
        
        <div class="modal-body">
          <!-- Акцентный режим -->
          <div class="settings-section">
            <div class="settings-row">
              <div class="settings-info">
                <span class="settings-label">Акцент событий</span>
                <span class="settings-hint">Нейтральный фон + цветная полоска и иконка</span>
              </div>
              <label class="toggle-switch">
                <input type="checkbox" v-model="eventAccentMode" />
                <span class="toggle-slider"></span>
              </label>
            </div>
          </div>

          <div class="settings-divider"></div>

          <!-- Фон -->
          <div class="settings-section">
            <div class="settings-section-title">Фон календаря</div>
            
            <div class="current-background" v-if="currentBackground">
              <p>Текущий фон:</p>
              <img :src="currentBackground" class="preview-img" />
            </div>
            
            <div class="upload-section">
              <label class="upload-label">
                <input 
                  type="file" 
                  accept="image/*" 
                  @change="handleBackgroundUpload"
                  class="file-input"
                />
                <span>Загрузить картинку</span>
              </label>
            </div>
            
            <div class="opacity-section" v-if="currentBackground">
              <label>Прозрачность: {{ backgroundOpacity }}</label>
              <input 
                type="range" 
                min="0.1" 
                max="1" 
                step="0.1"
                v-model.number="backgroundOpacity"
                @input="updateBackgroundOpacity"
                class="opacity-slider"
              />
            </div>
            
            <button 
              v-if="currentBackground" 
              class="remove-bg-btn"
              @click="removeBackground"
            >
              Убрать фон
            </button>
          </div>
        </div>
      </div>
    </div>
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
import type { InboxCategory } from '../stores/kanban'
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
import ImportantEventsPanel from '../components/modals/ImportantEventsPanel.vue'
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

// Important panel state
const showImportantPanel = ref(false)

// Акцентный режим событий: true = нейтральный фон + цветная полоска/иконка
const eventAccentMode = ref(false)

// Background state
const showSettings = ref(false)
const currentBackground = ref<string | null>(null)
const backgroundOpacity = ref(0.5)

onMounted(() => {
  const saved = localStorage.getItem('app-background')
  if (saved) {
    const { url, opacity } = JSON.parse(saved)
    currentBackground.value = url
    backgroundOpacity.value = opacity
  }
})

const handleBackgroundUpload = (event: Event) => {
  const target = event.target as HTMLInputElement
  const file = target.files?.[0]
  if (file) {
    const reader = new FileReader()
    reader.onload = (e) => {
      const url = e.target?.result as string
      currentBackground.value = url
      localStorage.setItem('app-background', JSON.stringify({ url, opacity: backgroundOpacity.value }))
    }
    reader.readAsDataURL(file)
  }
}

const updateBackgroundOpacity = () => {
  if (currentBackground.value) {
    localStorage.setItem('app-background', JSON.stringify({ 
      url: currentBackground.value, 
      opacity: backgroundOpacity.value 
    }))
  }
}

const removeBackground = () => {
  currentBackground.value = null
  backgroundOpacity.value = 0.5
  localStorage.removeItem('app-background')
}

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

// Important events
const importantEvents = computed(() => {
  return calendarStore.events
    .filter(event => event.is_important)
    .sort((a, b) => new Date(a.start).getTime() - new Date(b.start).getTime())
})

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
  recurrenceEndDate: undefined as string | undefined,
  is_important: false
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
  loadEventsForMonth()
}

const prevMonth = () => {
  currentMonth.value = currentMonth.value.add(-1, 'month')
  loadEventsForMonth()
}

const loadEventsForMonth = async () => {
  const startOfMonth = currentMonth.value.startOf('month').format('YYYY-MM-DD')
  const endOfMonth = currentMonth.value.endOf('month').format('YYYY-MM-DD')
  await calendarStore.fetchEvents(startOfMonth, endOfMonth)
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
    recurrenceEndDate: undefined,
    is_important: false
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
    recurrenceEndDate: undefined,
    is_important: false
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
    recurrenceEndDate: undefined,
    is_important: false
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
      recurrenceEndDate: undefined,
      is_important: false
    }
    
    editingEvent.value = null
    showModal.value = true
  }
}

const openImportantEvent = (event: any) => {
  openEventModal(event)
  showImportantPanel.value = false
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
    recurrenceEndDate: event.recurrence_end_date ? dayjs(event.recurrence_end_date).format('YYYY-MM-DD') : undefined,
    is_important: event.is_important || false
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
    recurrenceEndDate: undefined,
    is_important: false
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

const handleTaskRemoved = async () => {
  // Перезагружаем события и задачи
  await loadEvents()
  await tasksStore.fetchTasks()
}

const handleCategoryDroppedToEvent = async (data: { event: any; category: InboxCategory }) => {
  const { event, category } = data
  
  try {
    // Получаем задачи категории
    const categoryTasks = tasksStore.tasks.filter((t: any) => t.column_id === category.id)
    
    console.log('DEBUG: categoryTasks:', categoryTasks)
    console.log('DEBUG: event:', event)
    console.log('DEBUG: category:', category)
    
    if (categoryTasks.length === 0) {
      console.log('No tasks in category:', category.title)
      return
    }
    
    // Добавляем все задачи категории к событию
    for (let i = 0; i < categoryTasks.length; i++) {
      const taskData = categoryTasks[i]
      
      // Проверяем, что task.id существует
      if (!taskData.id) {
        console.error(`DEBUG: Task ${i} has no id:`, taskData)
        continue
      }
      
      console.log(`DEBUG: Adding task ${i}:`, taskData)
      console.log(`DEBUG: event_id type: ${typeof event.id}, value: ${event.id}`)
      console.log(`DEBUG: task_id type: ${typeof taskData.id}, value: ${taskData.id}`)
      console.log(`DEBUG: order type: ${typeof i}, value: ${i}`)
      
      await eventTasksApi.post('/', {
        event_id: String(event.id),
        task_id: String(taskData.id),
        order: Number(i)
      })
    }
    
    // Обновляем события
    await loadEvents()
    
    console.log('Category tasks added to event:', category.title, '->', event.title)
  } catch (error) {
    console.error('Failed to add category tasks to event:', error)
  }
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
    tag_id: eventForm.value.tagId,
    is_important: eventForm.value.is_important === true
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

// Handle event drop for day view
const handleEventDropForDay = async (data: { event: any; newDate: string; newStart: string; newEnd: string }) => {
  const { event, newStart, newEnd } = data
  
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
  
  bouncingEvents.value.add(String(event.id))
  await calendarStore.updateEvent(event.id, eventData)
  
  calendarStore.addToHistory({
    type: 'update',
    eventId: event.id,
    oldEvent,
    newEvent: { ...event, ...eventData }
  })
  
  setTimeout(() => {
    const newSet = new Set(bouncingEvents.value)
    newSet.delete(String(event.id))
    bouncingEvents.value = newSet
  }, 500)
  
  // Reload events for day view
  await loadEventsForDay()
}

// Handle event copy for day view
const handleEventCopyForDay = async (data: { event: any; newDate: string; newStart: string; newEnd: string }) => {
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
  
  const newEvent = await calendarStore.createEvent(eventData)
  
  calendarStore.addToHistory({
    type: 'create',
    eventId: newEvent.id,
    newEvent
  })
  
  loadEventsForDay()
  
  console.log('Event copied:', event.title, 'to', newStart)
}

// Handle task drop to event for day view
const handleTaskDropToEventForDay = async (data: { task: any; event: any }) => {
  const { task, event } = data
  
  try {
    if (task.type === 'category') {
      const categoryTasks = tasksStore.tasks.filter((t: any) => t.column_id === task.categoryId)
      
      if (categoryTasks.length === 0) {
        console.log('No tasks in category:', task.categoryTitle)
        return
      }
      
      for (let i = 0; i < categoryTasks.length; i++) {
        const taskData = categoryTasks[i]
        
        if (!taskData.id) {
          console.error(`Task ${i} has no id:`, taskData)
          continue
        }
        
        await eventTasksApi.post('/', {
          event_id: String(event.id),
          task_id: String(taskData.id),
          order: Number(i)
        })
      }
      
      await loadEventsForDay()
      
      console.log('Category tasks added to event:', task.categoryTitle, '->', event.title)
    } else {
      if (!task.id) {
        console.error('Task.id is undefined or null')
        return
      }
      
      await eventTasksApi.post('/', {
        event_id: String(event.id),
        task_id: String(task.id),
        order: Number(0)
      })
    
      await loadEventsForDay()
      
      console.log('Task added to event:', task.title, '->', event.title)
    }
  } catch (error) {
    console.error('Failed to add task to event:', error)
  }
}

// Handle move event to next week for day view
const handleMoveToNextWeekForDay = async (event: any) => {
  const originalStart = dayjs(event.start)
  const originalEnd = dayjs(event.end)
  
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
  
  await calendarStore.updateEvent(event.id, eventData)
  
  console.log('Event moved to next week:', event.title, 'to', newStart.format('YYYY-MM-DD HH:mm'))
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
    // Проверяем, это категория или задача
    if (task.type === 'category') {
      // Получаем задачи категории
      const categoryTasks = tasksStore.tasks.filter((t: any) => t.column_id === task.categoryId)
      
      if (categoryTasks.length === 0) {
        console.log('No tasks in category:', task.categoryTitle)
        return
      }
      
      // Добавляем все задачи категории к событию
      for (let i = 0; i < categoryTasks.length; i++) {
        const taskData = categoryTasks[i]
        
        // Проверяем, что taskData.id существует
        if (!taskData.id) {
          console.error(`Task ${i} has no id:`, taskData)
          continue
        }
        
        await eventTasksApi.post('/', {
          event_id: String(event.id),
          task_id: String(taskData.id),
          order: Number(i)
        })
      }
      
      // Обновляем события
      await loadEvents()
      
      console.log('Category tasks added to event:', task.categoryTitle, '->', event.title)
    } else {
      // Проверяем, что task.id существует
      if (!task.id) {
        console.error('Task.id is undefined or null')
        return
      }
      
      // Добавляем задачу к событию через API
      await eventTasksApi.post('/', {
        event_id: String(event.id),
        task_id: String(task.id),
        order: Number(0)
      })
    
      // Обновляем события, чтобы отобразить количество задач
      await loadEvents()
      
      console.log('Task added to event:', task.title, '->', event.title)
    }
  } catch (error) {
    console.error('Failed to add task to event:', error)
  }
}

// Handle task drop to day
const handleTaskDropToDay = async (_data: { task: any; time: dayjs.Dayjs }) => {
  // Не создаем новые события при перетаскивании на пустое место
  // Задачи должны прикрепляться только к существующим событиям
  console.log('Task dropped on empty day. Please drop task on an existing event.')
  
  // Можно показать уведомление пользователю
  alert('Перетащите задачу на существующее событие календаря')
}

// Handle category drop to day
const handleCategoryDropToDay = async (_data: { categoryId: string; categoryTitle: string; time: dayjs.Dayjs }) => {
  // Не создаем новые события при перетаскивании на пустое место
  // Задачи должны прикрепляться только к существующим событиям
  console.log('Category dropped on empty day. Please drop category on an existing event.')
  
  // Можно показать уведомление пользователю
  alert('Перетащите категорию на существующее событие календаря')
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
  } else if (newView === 'month') {
    // Load events for current month
    loadEventsForMonth()
  }
})

onMounted(() => {
  // Load events for current week by default (so we have data for all views)
  loadEvents()
  tagsStore.fetchTags()
  // Load tasks and inbox categories for Inbox panel
tasksStore.fetchTasks()
  kanbanStore.fetchInboxCategories()
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
  background-color: rgba(5, 5, 5, 0.95);
  color: #ffffff;
  display: flex;
  flex-direction: column;
  overflow: hidden;
  transition: padding-right 0.3s ease, background-color 0.3s;
  padding-right: 0;
}

.weekly-calendar.with-background {
  background-color: rgba(5, 5, 5, 0.6);
}

.weekly-calendar.inbox-open {
  padding-right: 320px;
}

/* Week View Container - with internal scrolling */
.week-view-container {
  flex: 1;
  display: flex;
  flex-direction: column;
  min-height: 0;
  width: 100%;
}

/* Calendar Header */
.calendar-header-with-inbox {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 10px 0;
  border-bottom: 1px solid #333;
  width: 100%;
  box-sizing: border-box;
}

/* DAY VIEW */
.day-view {
  padding: 40px;
  text-align: center;
}

.day-view h2 {
  font-size: 29px;
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

/* Background Settings Modal */
.modal-overlay {
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
  from { opacity: 0; }
  to { opacity: 1; }
}

.settings-modal {
  background-color: #121212;
  border: 1px solid #444;
  border-radius: 25px;
  padding: 20px;
  width: 90%;
  max-width: 400px;
  animation: slideUp 0.3s cubic-bezier(0.16, 1, 0.3, 1);
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

.settings-modal .modal-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 20px;
}

.settings-modal .modal-header h3 {
  margin: 0;
  font-size: 16px;
  color: #fff;
}

.settings-modal .close-btn {
  background: none;
  border: none;
  color: #888;
  font-size: 22px;
  cursor: pointer;
  padding: 0;
  line-height: 1;
}

.settings-modal .close-btn:hover {
  color: #fff;
}

.settings-modal .modal-body {
  display: flex;
  flex-direction: column;
  gap: 16px;
}

.settings-section {
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.settings-section-title {
  font-size: 12px;
  color: #888;
  font-weight: 600;
  text-transform: uppercase;
  letter-spacing: 0.5px;
}

.settings-row {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 12px;
}

.settings-info {
  display: flex;
  flex-direction: column;
  gap: 2px;
}

.settings-label {
  font-size: 13px;
  color: #fff;
  font-weight: 500;
}

.settings-hint {
  font-size: 10px;
  color: #888;
}

.settings-divider {
  height: 1px;
  background: #333;
  margin: 4px 0;
}

/* Toggle Switch */
.toggle-switch {
  position: relative;
  width: 40px;
  height: 22px;
  flex-shrink: 0;
}

.toggle-switch input {
  display: none;
}

.toggle-slider {
  position: absolute;
  top: 0; left: 0; right: 0; bottom: 0;
  background: #333;
  border-radius: 11px;
  cursor: pointer;
  transition: background 0.2s;
}

.toggle-slider::before {
  content: '';
  position: absolute;
  top: 2px; left: 2px;
  width: 18px;
  height: 18px;
  background: #888;
  border-radius: 50%;
  transition: all 0.2s;
}

.toggle-switch input:checked + .toggle-slider {
  background: #8b5cf6;
}

.toggle-switch input:checked + .toggle-slider::before {
  background: #fff;
  transform: translateX(18px);
}

.current-background {
  text-align: center;
}

.current-background p {
  color: #888;
  font-size: 11px;
  margin: 0 0 10px 0;
}

.preview-img {
  max-width: 100%;
  max-height: 150px;
  border-radius: 10px;
  border: 1px solid #444;
}

.upload-label {
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 12px;
  background: #2a2a2a;
  border: 1px dashed #444;
  border-radius: 10px;
  cursor: pointer;
  color: #aaa;
  font-size: 11px;
  transition: all 0.2s;
}

.upload-label:hover {
  background: #333;
  border-color: #666;
  color: #fff;
}

.file-input {
  display: none;
}

.opacity-section {
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.opacity-section label {
  color: #888;
  font-size: 10px;
}

.opacity-slider {
  width: 100%;
  height: 6px;
  background: #333;
  border-radius: 3px;
  outline: none;
  cursor: pointer;
  -webkit-appearance: none;
}

.opacity-slider::-webkit-slider-thumb {
  -webkit-appearance: none;
  width: 16px;
  height: 16px;
  background: #1c3496;
  border-radius: 50%;
  cursor: pointer;
}

.remove-bg-btn {
  padding: 10px;
  background: #333;
  border: none;
  border-radius: 8px;
  color: #fff;
  font-size: 11px;
  cursor: pointer;
  transition: background 0.2s;
}

.remove-bg-btn:hover {
  background: #444;
}
</style>
