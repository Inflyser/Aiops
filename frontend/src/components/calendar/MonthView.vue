<template>
  <div class="month-calendar">
    <div class="month-header">
      <div class="month-header2">
        <h1 class="month-year-title">{{ currentMonth.format('MMMM YYYY') }}</h1>
        <div class="month-nav">
          <button class="nav-btn1" @click="$emit('prev-month')"><</button>
          <button class="nav-btn1" @click="$emit('next-month')">></button>
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
          'weekend': day.isWeekend,
          'drag-over': dragOverDay === day.date
        }"
        @dragover="handleDragOver($event, day)"
        @dragleave="handleDragLeave"
        @drop="handleDrop($event, day)"
      >
        <div class="month-day-number" @click.stop="$emit('day-click', day)">{{ day.number }}</div>
        <div class="month-day-events">
          <div
            v-for="event in getVisibleEvents(day.date)"
            :key="event.id"
            class="month-event"
            :class="{ 'dragging': draggedEvent?.id === event.id }"
            :style="{ backgroundColor: event.color || '#4a5568' }"
            :data-event-id="event.id"
            draggable="true"
            @click.stop="handleEventClick(event)"
            @dragstart="handleDragStart($event, event)"
            @dragend="handleDragEnd"
            @dragover="handleTaskDragOver($event)"
            @drop="handleTaskDrop($event, day)"
          >
            <img
              v-if="event.tagIcon && getTagIconPath(event.tagIcon)"
              :src="getTagIconPath(event.tagIcon)"
              class="event-tag-icon"
            />
            {{ event.title }}
          </div>
          <div
            v-if="getExtraEventsCount(day.date) > 0"
            class="more-events"
            @click.stop="$emit('day-click', day)"
          >
            +{{ getExtraEventsCount(day.date) }} ещё
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { computed, ref } from 'vue'
import dayjs from 'dayjs'
import 'dayjs/locale/ru'

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

interface CalendarEvent {
  id: string | number
  title: string
  description?: string
  start: string
  end: string
  location?: string
  priority?: string
  color?: string
  tagIcon?: string
  task_count?: number
  completed_task_count?: number
  bouncing?: boolean
}

interface MonthDay {
  date: string
  number: number
  isToday: boolean
  isCurrentMonth: boolean
  isWeekend: boolean
  fullDate: dayjs.Dayjs
}

const props = defineProps<{
  currentMonth: dayjs.Dayjs
  events: CalendarEvent[]
}>()

const emit = defineEmits<{
  (e: 'prev-month'): void
  (e: 'next-month'): void
  (e: 'day-click', day: MonthDay): void
  (e: 'open-event', event: CalendarEvent): void
  (e: 'event-drop', data: { event: CalendarEvent; newDate: string; newStart: string; newEnd: string }): void
  (e: 'event-copy', data: { event: CalendarEvent; newDate: string; newStart: string; newEnd: string }): void
  (e: 'task-drop-to-event', data: { task: any; event: CalendarEvent }): void
  (e: 'task-drop-to-day', data: { task: any; time: dayjs.Dayjs }): void
  (e: 'category-drop-to-day', data: { categoryId: string; categoryTitle: string; time: dayjs.Dayjs }): void
}>()

const handleEventClick = (event: CalendarEvent) => {
  emit('open-event', event)
}

// Drag and drop state
const draggedEvent = ref<CalendarEvent | null>(null)
const dragOverDay = ref<string | null>(null)
const dragOverTimeout = ref<ReturnType<typeof setTimeout> | null>(null)

const isAltPressed = ref(false)

const handleDragStart = (event: DragEvent, calendarEvent: CalendarEvent) => {
  draggedEvent.value = calendarEvent
  isAltPressed.value = event.altKey

  if (event.dataTransfer) {
    event.dataTransfer.effectAllowed = event.altKey ? 'copy' : 'move'
    event.dataTransfer.setData('text/plain', JSON.stringify(calendarEvent))
    event.dataTransfer.setData('application/x-alt-drag', String(event.altKey))
  }
}

const handleDragEnd = () => {
  draggedEvent.value = null
  dragOverDay.value = null
  isAltPressed.value = false
  if (dragOverTimeout.value) clearTimeout(dragOverTimeout.value)
}

const handleDragOver = (event: DragEvent, day: MonthDay) => {
  event.preventDefault()
  if (event.dataTransfer) {
    event.dataTransfer.dropEffect = event.altKey ? 'copy' : 'move'
  }
  dragOverDay.value = day.date
  if (dragOverTimeout.value) clearTimeout(dragOverTimeout.value)
  dragOverTimeout.value = setTimeout(() => {
    dragOverDay.value = null
  }, 1000)
}

const handleDragLeave = () => {
  dragOverDay.value = null
  if (dragOverTimeout.value) clearTimeout(dragOverTimeout.value)
}

const handleDrop = (event: DragEvent, day: MonthDay) => {
  event.preventDefault()
  dragOverDay.value = null
  if (dragOverTimeout.value) clearTimeout(dragOverTimeout.value)

  try {
    const droppedData = JSON.parse(event.dataTransfer?.getData('text/plain') || '{}')

    if (draggedEvent.value) {
      const eventData = draggedEvent.value
      const isCopy = event.altKey || isAltPressed.value

      const originalStart = dayjs(eventData.start)
      const originalEnd = dayjs(eventData.end)
      const duration = originalEnd.diff(originalStart, 'minute')

      const newStart = day.fullDate
        .hour(originalStart.hour())
        .minute(originalStart.minute())
        .second(0)
      const newEnd = newStart.add(duration, 'minute')

      if (isCopy) {
        emit('event-copy', {
          event: eventData,
          newDate: day.date,
          newStart: newStart.toISOString(),
          newEnd: newEnd.toISOString()
        })
      } else {
        emit('event-drop', {
          event: eventData,
          newDate: day.date,
          newStart: newStart.toISOString(),
          newEnd: newEnd.toISOString()
        })
      }
    } else if (droppedData.type === 'category') {
      const dropTime = day.fullDate.hour(9).minute(0).second(0)

      emit('category-drop-to-day', {
        categoryId: droppedData.categoryId,
        categoryTitle: droppedData.categoryTitle,
        time: dropTime
      })
    } else if (droppedData.id && droppedData.title) {
      const dropTime = day.fullDate.hour(9).minute(0).second(0)

      emit('task-drop-to-day', {
        task: droppedData,
        time: dropTime
      })
    }
  } catch (error) {
    console.error('Error parsing drop data:', error)
  }

  draggedEvent.value = null
  isAltPressed.value = false
}

const handleTaskDragOver = (event: DragEvent) => {
  event.preventDefault()
  if (event.dataTransfer) {
    event.dataTransfer.dropEffect = 'move'
  }
}

const handleTaskDrop = (event: DragEvent, _day: MonthDay) => {
  event.preventDefault()

  // Если перетаскивается событие календаря — не останавливаем всплытие,
  // чтобы дроп ушёл в handleDrop на .month-day
  if (draggedEvent.value) return

  event.stopPropagation()

  try {
    const droppedData = JSON.parse(event.dataTransfer?.getData('text/plain') || '{}')

    if (droppedData.type === 'category' || (droppedData.id && droppedData.title)) {
      const targetElement = event.target as HTMLElement
      const eventBlock = targetElement.closest('.month-event')

      if (eventBlock) {
        const eventId = eventBlock.getAttribute('data-event-id')
        const targetEvent = props.events.find(e => String(e.id) === eventId)

        if (targetEvent) {
          emit('task-drop-to-event', { task: droppedData, event: targetEvent })
        }
      }
    }
  } catch (error) {
    console.error('Error parsing task data:', error)
  }
}

const dayNames = ['Пн', 'Вт', 'Ср', 'Чт', 'Пт', 'Сб', 'Вс']

const monthDays = computed(() => {
  const days: MonthDay[] = []
  const startOfMonth = props.currentMonth.startOf('month')
  const startDay = startOfMonth.startOf('week')
  
  let currentDay = startDay
  for (let i = 0; i < 42; i++) {
    days.push({
      date: currentDay.format('YYYY-MM-DD'),
      number: currentDay.date(),
      isToday: currentDay.isSame(dayjs(), 'day'),
      isCurrentMonth: currentDay.month() === props.currentMonth.month(),
      isWeekend: currentDay.day() === 6 || currentDay.day() === 0,
      fullDate: currentDay
    })
    currentDay = currentDay.add(1, 'day')
  }
  return days
})

const getAllEventsForDay = (date: string) => {
  return props.events.filter(event => {
    const eventDate = dayjs(event.start).format('YYYY-MM-DD')
    return eventDate === date
  })
}

const getVisibleEvents = (date: string) => {
  const all = getAllEventsForDay(date)
  const max = all.length > 4 ? 3 : 4
  return all.slice(0, max)
}

const getExtraEventsCount = (date: string) => {
  const allEvents = getAllEventsForDay(date)
  const visible = getVisibleEvents(date).length
  return Math.max(0, allEvents.length - visible)
}
</script>

<style scoped>
.month-calendar {
  padding: 20px 0;
}

.month-header {
  padding: 0 0 20px;
}

.month-header2 {
  display: flex;
  align-items: center;
  margin-bottom: 20px;
  padding: 0 20px;
}

.month-year-title {
  font-size: 42px;
  font-weight: bold;
  margin: 0;
  flex: 1;
  text-transform: capitalize;
}

.month-nav {
  display: flex;
  gap: 10px;
}

.nav-btn1 {
  background: transparent;
  border: none;
  color: #ffffff;
  font-size: 30px;
  cursor: pointer;
  font-weight: bold;
  padding: 0px 10px 15px 25px;
}

.days-header {
  display: grid;
  grid-template-columns: repeat(7, 1fr);
  gap: 1px;
}

.day-header {
  text-align: center;
}

.day-name {
  font-size: 19px;
  color: #888;
  margin-bottom: 5px;
  font-weight: 700;
}

.month-grid {
  display: grid;
  grid-template-columns: repeat(7, 1fr);
  border-left: 1px solid #333;
  border-top: 1px solid #333;
  border-top-left-radius: 12px;
  border-top-right-radius: 12px;
  overflow: hidden;
}

.month-day {
  min-height: 120px;
  border-right: 1px solid #333;
  border-bottom: 1px solid #333;
  padding: 8px;
  cursor: pointer;
  transition: background-color 0.2s;
}

.month-day:hover {
  background-color: #1a1a1a;
}

.month-day.today {
  background-color: rgba(85, 85, 85, 0.1);
}

.month-day.today .month-day-number {
  background-color: #555;
  color: white;
  width: 30px;
  height: 30px;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  margin: 0 auto 8px;
}

.month-day.other-month {
  opacity: 0.3;
  cursor: default;
}

.month-day.weekend {
  background-color: rgba(255, 255, 255, 0.05);
}

.month-day-number {
  font-size: 14px;
  font-weight: 500;
  margin-bottom: 5px;
  text-align: center;
}

.month-day-events {
  display: flex;
  flex-direction: column;
  gap: 2px;
}

.event-tag-icon {
  width: 13px;
  height: 13px;
  flex-shrink: 0;
}

.month-event {
  font-size: 12px;
  padding: 3px 6px;
  border-radius: 3px;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
  cursor: pointer;
  color: white;
  display: flex;
  align-items: center;
  gap: 4px;
}

.more-events {
  font-size: 9px;
  color: #888;
  padding: 2px 6px;
  cursor: pointer;
}

.more-events:hover {
  color: #aaa;
}

.month-day.drag-over {
  background-color: rgba(200, 200, 200, 0.15);
}

.month-event.dragging {
  opacity: 0.5;
}
</style>
