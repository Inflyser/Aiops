<template>
  <div class="weekly-calendar" :class="{ 
    'inbox-open': showInboxPanel,
    'filter-open': showFilterPanel,
    'snooze-open': showSnoozePanel,
    'tags-open': showTagsPanel,
    'with-background': currentBackground
  }" :style="currentBackground ? { backgroundColor: `rgba(5, 5, 5, ${1 - backgroundOpacity})` } : {}">
    <!-- Top Bar -->
    <CalendarTopBar
      :current-view="currentView"
      :show-inbox-panel="showInboxPanel"
      :show-important-panel="showImportantPanel"
      :show-snooze-panel="showSnoozePanel"
      @toggle-inbox="showInboxPanel = !showInboxPanel"
      @toggle-important="showImportantPanel = !showImportantPanel"
      @toggle-snooze="showSnoozePanel = !showSnoozePanel"
      @open-settings="showSettings = true"
    />

    <!-- Tags Panel -->
    <TagsPanel 
      :is-open="showTagsPanel"
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

    <!-- Left Controls: Tags + Filter + View Selector -->
    <div class="left-controls-row">
      <div class="left-toggle-buttons">
        <button
          class="left-toggle-btn"
          :class="{ active: showTagsPanel }"
          @click="showTagsPanel = !showTagsPanel"
          title="Теги"
        >
          <img src="@/assets/icon-tags.svg" width="18" height="18" />
        </button>
        <button
          class="left-toggle-btn"
          :class="{ active: showFilterPanel }"
          @click="showFilterPanel = !showFilterPanel"
          title="Фильтр"
        >
          <img src="@/assets/icon/checklist_24dp_B1B3B2_FILL0_wght400_GRAD0_opsz24.svg" width="18" height="18" />
        </button>
      </div>
      <ViewSelector 
        :current-view="currentView"
        @update:model-value="currentView = $event"
      />
    </div>
      
    <!-- Week View -->
    <Transition name="slide-fade" mode="out-in">
      <div v-if="currentView === 'week'" key="week" class="week-view-container">
        <!-- Calendar Header -->
        <div class="calendar-header-with-inbox">
          <CalendarHeader
            :current-week-start="currentWeekStart"
            :sleep-mode="sleepMode"
            @prev-week="lastWeek"
            @next-week="nextWeek"
            @toggle-sleep="sleepMode = $event"
          />
        </div>

        <!-- Calendar Grid -->
        <WeekView
          :week-days="weekDays"
          :events="filteredEvents"
          :day-start-hour="0"
          :day-end-hour="24"
          :event-accent-mode="eventAccentMode"
          :inbox-panel-open="showInboxPanel"
          :hour-height="weekHourHeight"
          :sleep-mode="sleepMode"
          :sleep-start-hour="sleepStartHour"
          :sleep-end-hour="sleepEndHour"
          @day-click="handleWeekDayClick"
          @open-event="openEventModal"
          @open-event-tasks="openEventTasksModal"
          @event-drop="handleEventDrop"
          @event-copy="handleEventCopy"
          @event-move-to-next-week="handleMoveToNextWeek"
          @event-toggle-important="handleToggleImportant"
          @task-drop-to-event="handleTaskDropToEvent"
          @tag-drop-to-event="handleTagDropToEvent"
          @task-drop-to-day="handleTaskDropToDay"
          @category-drop-to-day="handleCategoryDropToDay"
          @create-event="handleCreateEvent"
          @event-update="handleEventUpdate"
          @add-task-to-event="handleAddTaskToEvent"
          @toggle-tags-panel="showTagsPanel = !showTagsPanel"
        />
      </div>

      <!-- Month View -->
      <div v-else-if="currentView === 'month'" key="month">
        <MonthView
          :current-month="currentMonth"
          :events="filteredEvents"
          @prev-month="prevMonth"
          @next-month="nextMonth"
          @day-click="handleMonthDayClick"
          @open-event="openEventModal"
          @event-drop="handleEventDrop"
          @event-copy="handleEventCopy"
          @task-drop-to-event="handleTaskDropToEvent"
          @tag-drop-to-event="handleTagDropToEvent"
          @task-drop-to-day="handleTaskDropToDay"
          @category-drop-to-day="handleCategoryDropToDay"
        />
      </div>

      <!-- Day View -->
      <div v-else-if="currentView === 'day'" key="day" class="day-view-container" style="flex: 1; display: flex; flex-direction: column; min-height: 0;">
        <DayView
          :current-day="currentDay"
          :events="dayEvents"
          :day-start-hour="0"
          :day-end-hour="24"
          :event-accent-mode="eventAccentMode"
          :hour-height="dayHourHeight"
          :sleep-mode="sleepMode"
          :sleep-start-hour="sleepStartHour"
          :sleep-end-hour="sleepEndHour"
          @prev-day="prevDay"
          @next-day="nextDay"
          @go-today="goToToday"
          @hour-click="handleDayHourClick"
          @open-event="openEventModal"
          @open-event-tasks="openEventTasksModal"
          @event-move-to-next-week="handleMoveToNextWeekForDay"
          @event-toggle-important="handleToggleImportant"
          @event-drop="handleEventDropForDay"
          @event-copy="handleEventCopyForDay"
          @task-drop-to-event="handleTaskDropToEventForDay"
          @tag-drop-to-event="handleTagDropToEvent"
          @task-drop-to-day="handleTaskDropToDay"
          @category-drop-to-day="handleCategoryDropToDay"
          @create-event="handleCreateEvent"
          @event-update="handleEventUpdate"
          @add-task-to-event="handleAddTaskToEvent"
          @toggle-tags-panel="showTagsPanel = !showTagsPanel"
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

    <!-- Filter Panel -->
    <FilterPanel
      :is-open="showFilterPanel"
      :tags="tags"
      :active-tags="activeFilterTags"
      :show-important="filterShowImportant"
      @close="showFilterPanel = false"
      @update:active-tags="activeFilterTags = $event"
      @update:show-important="filterShowImportant = $event"
    />

    <!-- Event Snooze Panel -->
    <EventSnoozePanel
      :is-open="showSnoozePanel"
      :snoozed-events="snoozeStore.snoozedEvents"
      @close="showSnoozePanel = false"
      @calendar-event-dropped="handleCalendarEventDroppedOnSnooze"
      @remove-snoozed="handleRemoveSnoozed"
    />

    <!-- Zoom Handle -->
    <div
      v-if="currentView === 'week' || currentView === 'day'"
      class="zoom-handle"
      @mousedown="startZoom"
      title="Изменить масштаб (перетащите вверх/вниз)"
    >
      <svg width="16" height="16" viewBox="0 0 16 16" fill="none">
        <path d="M16 0v6l-2-2-6 6-3-3-5 5 1 1 5-5 3 3 6-6 2 2V0z" fill="currentColor"/>
      </svg>
      <span class="zoom-label">{{ Math.round(hourHeight / 120 * 100) }}%</span>
    </div>

    <!-- Settings Modal -->
    <SettingsModal
      :show="showSettings"
      :event-accent-mode="eventAccentMode"
      :sleep-mode="sleepMode"
      :sleep-start-hour="sleepStartHour"
      :sleep-end-hour="sleepEndHour"
      @close="showSettings = false"
      @update:event-accent-mode="eventAccentMode = $event"
      @update:sleep-mode="sleepMode = $event"
      @update:sleep-start-hour="sleepStartHour = $event"
      @update:sleep-end-hour="sleepEndHour = $event"
      @background-changed="handleBackgroundChanged"
      @background-removed="handleBackgroundRemoved"
    />

    <!-- Trash Drop Zone -->
    <div
      class="trash-zone"
      :class="{ visible: isDragging, 'drag-over': isOverTrash }"
      @dragover.prevent="onTrashDragOver"
      @dragleave="onTrashDragLeave"
      @drop.prevent="onTrashDrop"
    >
      <svg class="trash-icon" xmlns="http://www.w3.org/2000/svg" height="24px" viewBox="0 -960 960 960" width="24px" fill="currentColor"><path d="M280-120q-33 0-56.5-23.5T200-200v-520h-40v-80h200v-40h240v40h200v80h-40v520q0 33-23.5 56.5T680-120H280Zm400-600H280v520h400v-520ZM360-280h80v-360h-80v360Zm160 0h80v-360h-80v360ZM280-720v520-520Z"/></svg>
      <span class="trash-label">Удалить</span>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted, onUnmounted, watch, inject } from 'vue'
import type { Ref } from 'vue'
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
import DayView from '../components/calendar/DayView.vue'
import EventModal from '../components/modals/EventModal.vue'
import EventTasksModal from '../components/modals/EventTasksModal.vue'
import TagsPanel from '../components/modals/TagsPanel.vue'
import ImportantEventsPanel from '../components/modals/ImportantEventsPanel.vue'
import SettingsModal from '../components/modals/SettingsModal.vue'
import InboxPanel from '../components/calendar/InboxPanel.vue'
import FilterPanel from '../components/calendar/FilterPanel.vue'
import EventSnoozePanel from '../components/calendar/EventSnoozePanel.vue'
import { useEventSnoozeStore } from '../stores/eventSnooze'

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
const showModal = ref(false)
const editingEvent = ref<any>(null)
const viewMode = ref<'view' | 'edit' | null>(null)
const showEventTasksModal = ref(false)
const selectedEventForTasks = ref<any>(null)

// Zoom state
const MIN_HOUR_HEIGHT = 60
const MAX_HOUR_HEIGHT = 300

const savedWeekZoom = localStorage.getItem('calendarWeekHourHeight')
const weekHourHeight = ref(savedWeekZoom ? parseInt(savedWeekZoom) : 120)

const savedDayZoom = localStorage.getItem('calendarDayHourHeight')
const dayHourHeight = ref(savedDayZoom ? parseInt(savedDayZoom) : 120)

let isZooming = false
let zoomStartY = 0
let zoomStartHeight = 0

const hourHeight = computed(() => {
  return currentView.value === 'day' ? dayHourHeight.value : weekHourHeight.value
})

const startZoom = (e: MouseEvent) => {
  e.preventDefault()
  isZooming = true
  zoomStartY = e.clientY
  zoomStartHeight = hourHeight.value

  const onMove = (me: MouseEvent) => {
    if (!isZooming) return
    const deltaY = me.clientY - zoomStartY
    const newVal = Math.max(MIN_HOUR_HEIGHT, Math.min(MAX_HOUR_HEIGHT, zoomStartHeight + deltaY))
    if (currentView.value === 'day') {
      dayHourHeight.value = newVal
    } else {
      weekHourHeight.value = newVal
    }
  }

  const onUp = () => {
    isZooming = false
    localStorage.setItem('calendarWeekHourHeight', String(weekHourHeight.value))
    localStorage.setItem('calendarDayHourHeight', String(dayHourHeight.value))
    document.removeEventListener('mousemove', onMove)
    document.removeEventListener('mouseup', onUp)
    document.body.style.cursor = ''
    document.body.style.userSelect = ''
  }

  document.body.style.cursor = 'nwse-resize'
  document.body.style.userSelect = 'none'
  document.addEventListener('mousemove', onMove)
  document.addEventListener('mouseup', onUp)
}

// Локальное состояние для bounce анимации
const bouncingEvents = ref<Set<string>>(new Set())

const savedSleepMode = localStorage.getItem('sleep-mode')
const savedSleepStart = localStorage.getItem('sleep-start-hour')
const savedSleepEnd = localStorage.getItem('sleep-end-hour')

const sleepMode = ref(savedSleepMode ? savedSleepMode === 'true' : false)
const sleepStartHour = ref(savedSleepStart ? parseFloat(savedSleepStart) : 0)
const sleepEndHour = ref(savedSleepEnd ? parseFloat(savedSleepEnd) : 0)

watch([sleepMode, sleepStartHour, sleepEndHour], () => {
  localStorage.setItem('sleep-mode', String(sleepMode.value))
  localStorage.setItem('sleep-start-hour', String(sleepStartHour.value))
  localStorage.setItem('sleep-end-hour', String(sleepEndHour.value))
})

// Tags state
const showTagsPanel = ref(false)

// Inbox state
const showInboxPanel = ref(false)

// Important panel state
const showImportantPanel = ref(false)

// Filter panel state
const showFilterPanel = ref(false)
const activeFilterTags = ref<string[]>([])
const filterShowImportant = ref(false)

// Snooze panel state
const showSnoozePanel = ref(false)
const snoozeStore = useEventSnoozeStore()

// Trash drop zone state
const isDragging = ref(false)
const isOverTrash = ref(false)
let dragCounter = 0

const onGlobalDragEnter = () => {
  dragCounter++
  isDragging.value = true
}

const onGlobalDragEnd = () => {
  dragCounter = 0
  isDragging.value = false
  isOverTrash.value = false
}

const onTrashDragOver = (e: DragEvent) => {
  e.dataTransfer!.dropEffect = 'move'
  isOverTrash.value = true
}

const onTrashDragLeave = () => {
  isOverTrash.value = false
}

const onTrashDrop = async (e: DragEvent) => {
  isOverTrash.value = false
  isDragging.value = false
  dragCounter = 0

  try {
    const data = JSON.parse(e.dataTransfer?.getData('text/plain') || '{}')
    if (data.id && data.title && !data._tag && data.type !== 'category' && !data._snoozed) {
      if (!confirm(`Удалить событие "${data.title}"?`)) return
      await calendarStore.deleteEvent(data.id)
      loadEvents()
    }
  } catch {
    // ignore
  }
}

onMounted(() => {
  document.addEventListener('dragenter', onGlobalDragEnter)
  document.addEventListener('dragend', onGlobalDragEnd)
})

onUnmounted(() => {
  document.removeEventListener('dragenter', onGlobalDragEnter)
  document.removeEventListener('dragend', onGlobalDragEnd)
})

// Акцентный режим событий: true = нейтральный фон + цветная полоска/иконка
const eventAccentMode = ref(false)

// Background state (provided from App.vue)
const showSettings = ref(false)
const currentBackground = inject<Ref<string | null>>('backgroundUrl')!
const backgroundOpacity = inject<Ref<number>>('backgroundOpacity')!
const setBackground = inject<(url: string, opacity: number) => void>('setBackground')!
const clearBackground = inject<() => void>('clearBackground')!

const handleBackgroundChanged = (data: { url: string; opacity: number }) => {
  setBackground(data.url, data.opacity)
}

const handleBackgroundRemoved = () => {
  clearBackground()
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

interface EventTask {
  id: string
  title: string
  description?: string
  completed: boolean
}

// Events from calendar store (с уже установленными цветами от тегов)
const events = computed(() => {
  return calendarStore.events.map(event => {
    const taskIds = event.task_ids || []
    const eventTaskList: EventTask[] = taskIds
      .map((id: string) => tasksStore.tasks.find(t => t.id === id))
      .filter((t): t is NonNullable<typeof t> => t != null)

    return {
      ...event,
      color: event.color || getTagColor(event.tag_id),
      tagIcon: getTagIcon(event.tag_id),
      bouncing: bouncingEvents.value.has(String(event.id)),
      eventTasks: eventTaskList,
    }
  })
})

// Фильтрованные события (по тегам и важности)
const filteredEvents = computed(() => {
  return events.value.filter(event => {
    if (activeFilterTags.value.length > 0) {
      if (!event.tag_id || !activeFilterTags.value.includes(event.tag_id)) {
        return false
      }
    }
    if (filterShowImportant.value && !event.is_important) {
      return false
    }
    return true
  })
})

// Фильтрованные события для дневного вида
const dayEvents = computed(() => {
  const currentDayStr = currentDay.value.format('YYYY-MM-DD')
  return filteredEvents.value.filter(event => {
    const eventDate = dayjs(event.start).format('YYYY-MM-DD')
    return eventDate === currentDayStr
  })
})

const defaultEventForm = () => ({
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

const eventForm = ref(defaultEventForm())

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
    ...defaultEventForm(),
    date: date.format('YYYY-MM-DD'),
    startTime: startTime.format('HH:mm'),
    endTime: endTime.format('HH:mm'),
  }
  
  editingEvent.value = null
  showModal.value = true
}

// Event handlers
const handleWeekDayClick = (data: { day: any; dateTime: dayjs.Dayjs }) => {
  const { day, dateTime } = data
  const endTime = dateTime.add(1, 'hour')
  
  eventForm.value = {
    ...defaultEventForm(),
    date: day.date,
    startTime: dateTime.format('HH:mm'),
    endTime: endTime.format('HH:mm'),
  }
  
  editingEvent.value = null
  showModal.value = true
}

const handleMonthDayClick = (day: any) => {
  currentWeekStart.value = dayjs(day.fullDate).startOf('week')
  currentView.value = 'week'
}

const handleCreateEvent = async (data: { date: string; startTime: string; endTime: string; title: string }) => {
  const start = dayjs(`${data.date} ${data.startTime}`)
  const end = dayjs(`${data.date} ${data.endTime}`)
  
  const eventData = {
    title: data.title,
    start: start.toISOString(),
    end: end.toISOString(),
    color: '#4a5568',
    all_day: false
  }
  
  await calendarStore.createEvent(eventData)
  if (currentView.value === 'day') {
    await loadEventsForDay()
  } else {
    await loadEvents()
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
    ...defaultEventForm(),
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
  eventForm.value = defaultEventForm()
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
    if (!confirm(`Удалить событие "${editingEvent.value.title}"?`)) return
    // Сохраняем старое событие для отмены
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
  if (currentView.value === 'month') {
    await loadEventsForMonth()
  } else if (currentView.value === 'day') {
    await loadEventsForDay()
  } else {
    const startOfWeek = currentWeekStart.value.format('YYYY-MM-DD')
    const endOfWeek = currentWeekStart.value.add(6, 'day').format('YYYY-MM-DD')
    await calendarStore.fetchEvents(startOfWeek, endOfWeek)
  }
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

// Shared task-to-event logic
const handleTaskDropToEventShared = async (data: { task: any; event: any }, onSuccess: () => Promise<void>) => {
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
      
      await onSuccess()
      
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
    
      await onSuccess()
      
      console.log('Task added to event:', task.title, '->', event.title)
    }
  } catch (error) {
    console.error('Failed to add task to event:', error)
  }
}

// Handle task drop to event for day view
const handleTaskDropToEventForDay = async (data: { task: any; event: any }) => {
  await handleTaskDropToEventShared(data, async () => {
    await loadEventsForDay()
    await tasksStore.fetchTasks()
  })
}

// Handle tag drop to event
const handleTagDropToEvent = async (data: { tag: any; event: any }) => {
  await calendarStore.updateEvent(data.event.id, { tag_id: data.tag.id, color: data.tag.color })
  if (currentView.value === 'day') {
    await loadEventsForDay()
  } else {
    await loadEvents()
  }
}

// Handle move event to next week for day view
const handleEventUpdate = async (data: { event: any; changes: Partial<any> }) => {
  await calendarStore.updateEvent(data.event.id, data.changes)
  if (currentView.value === 'day') {
    await loadEventsForDay()
  } else {
    await loadEvents()
  }
}

const handleCalendarEventDroppedOnSnooze = async (eventData: any) => {
  try {
    await calendarStore.deleteEvent(eventData.id)
    snoozeStore.addEvent({
      id: eventData.id,
      title: eventData.title,
      description: eventData.description,
      start: eventData.start,
      end: eventData.end,
      color: eventData.color || '#4a5568',
      location: eventData.location,
      priority: eventData.priority,
      is_important: eventData.is_important,
      tag_id: eventData.tag_id || eventData.tagId,
      tagIcon: eventData.tagIcon,
      task_ids: eventData.task_ids,
      task_count: eventData.task_count,
      completed_task_count: eventData.completed_task_count,
      snoozed_at: new Date().toISOString()
    })
    if (currentView.value === 'day') {
      await loadEventsForDay()
    } else {
      await loadEvents()
    }
  } catch (err) {
    console.error('Failed to snooze event:', err)
  }
}

const handleRemoveSnoozed = (eventId: string) => {
  snoozeStore.removeEvent(eventId)
}

const handleToggleImportant = async (event: any) => {
  await calendarStore.updateEvent(event.id, { is_important: !event.is_important })
  console.log('Event importance toggled:', event.title, '->', !event.is_important)

  if (currentView.value === 'day') {
    await loadEventsForDay()
  } else {
    await loadEvents()
  }
}

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
  await handleTaskDropToEventShared(data, async () => {
    await loadEvents()
    await tasksStore.fetchTasks()
  })
}

// Handle inline add task to event
const handleAddTaskToEvent = async (data: { event: any; title: string }) => {
  try {
    const newTask = await tasksStore.createTask({ title: data.title })
    if (newTask && newTask.id) {
      await eventTasksApi.post('/', {
        event_id: String(data.event.id),
        task_id: String(newTask.id),
        order: 0
      })
    }
    await loadEvents()
    if (currentView.value === 'day') await loadEventsForDay()
    await tasksStore.fetchTasks()
  } catch (error) {
    console.error('Failed to add task to event:', error)
  }
}

// Handle task drop to day
const handleTaskDropToDay = async (data: { task: any; time: dayjs.Dayjs }) => {
  const task = data.task
  if (task._snoozed) {
    const origStart = dayjs(task.start)
    const origEnd = dayjs(task.end)
    const duration = origEnd.diff(origStart, 'minute')
    const eventData = {
      title: task.title,
      description: task.description || undefined,
      start: data.time.toISOString(),
      end: data.time.add(Math.max(duration, 30), 'minute').toISOString(),
      location: task.location || undefined,
      priority: task.priority || 'medium',
      color: task.color || '#4a5568',
      all_day: false,
      tag_id: task.tag_id || undefined,
      is_important: task.is_important === true
    }
    try {
      await calendarStore.createEvent(eventData)
      snoozeStore.removeEvent(task.id)
      if (currentView.value === 'day') {
        await loadEventsForDay()
      } else {
        await loadEvents()
      }
    } catch (err) {
      console.error('Failed to restore snoozed event:', err)
    }
    return
  }

  console.log('Task dropped on empty day. Please drop task on an existing event.')
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
        if (!confirm('Удалить выбранное событие?')) return
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
    await loadEventsForDay()
  } else if (newView === 'week') {
    await loadEvents()
  } else if (newView === 'month') {
    await loadEventsForMonth()
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
  color: var(--text-primary);
  display: flex;
  flex-direction: column;
  overflow: hidden;
  position: relative;
  transition: padding-left 0.3s ease, padding-right 0.3s ease, background-color 0.3s;
}

.left-controls-row {
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 12px 0 0;
  flex-shrink: 0;
  position: relative;
  z-index: 10;
}

.left-toggle-buttons {
  position: absolute;
  left: 12px;
  display: flex;
  gap: 6px;
}

.left-toggle-btn {
  width: 34px;
  height: 34px;
  border: 1px solid rgba(255, 255, 255, 0.15);
  border-radius: 50%;
  background: rgba(200, 200, 200, 0.12);
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: center;
  transition: all 0.25s;
  flex-shrink: 0;
}

.left-toggle-btn:hover {
  background: rgba(200, 200, 200, 0.22);
  border-color: rgba(255, 255, 255, 0.3);
}

.left-toggle-btn.active {
  background: rgba(200, 200, 200, 0.25);
  border-color: rgba(200, 200, 200, 0.4);
}

.weekly-calendar.with-background {
  background-color: rgba(5, 5, 5, 0.6);
}

.weekly-calendar.inbox-open {
  padding-right: 320px;
}

.weekly-calendar.tags-open {
  padding-left: 320px;
}

.weekly-calendar.filter-open {
  padding-left: 320px;
}

.weekly-calendar.snooze-open {
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
  border-bottom: 1px solid var(--border-color);
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

/* Zoom Handle */
.zoom-handle {
  position: absolute;
  bottom: 12px;
  right: 12px;
  width: 36px;
  height: 36px;
  display: flex;
  align-items: center;
  justify-content: center;
  border-radius: 8px;
  background: rgba(30, 30, 30, 0.85);
  border: 1px solid rgba(255, 255, 255, 0.1);
  color: #888;
  cursor: nwse-resize;
  z-index: 50;
  transition: background 0.2s, color 0.2s;
  user-select: none;
}

.zoom-handle:hover {
  background: rgba(60, 60, 60, 0.9);
  color: #fff;
}

.zoom-label {
  display: none;
  position: absolute;
  right: calc(100% + 8px);
  top: 50%;
  transform: translateY(-50%);
  font-size: 12px;
  color: #ccc;
  background: rgba(30, 30, 30, 0.85);
  padding: 2px 8px;
  border-radius: 4px;
  white-space: nowrap;
  pointer-events: none;
}

.zoom-handle:hover .zoom-label {
  display: block;
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

/* Trash Drop Zone */
.trash-zone {
  position: fixed;
  bottom: 0;
  left: 50%;
  transform: translateX(-50%) translateY(100%);
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 12px 24px;
  background: rgba(30, 30, 30, 0.9);
  border: 2px dashed rgba(255, 255, 255, 0.15);
  border-radius: 12px;
  color: #888;
  font-size: 13px;
  font-weight: 500;
  z-index: 10000;
  transition: transform 0.3s cubic-bezier(0.4, 0, 0.2, 1), background 0.2s, border-color 0.2s, color 0.2s;
  pointer-events: none;
  backdrop-filter: blur(8px);
}

.trash-zone.visible {
  transform: translateX(-50%) translateY(-20px);
  pointer-events: auto;
}

.trash-zone.drag-over {
  background: rgba(220, 50, 50, 0.2);
  border-color: #ef4444;
  color: #ef4444;
}

.trash-icon {
  flex-shrink: 0;
}

.trash-label {
  white-space: nowrap;
}

</style>
