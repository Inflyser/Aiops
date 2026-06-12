<template>
  <div v-if="show" class="modal" @click.self="$emit('close')">
    <div class="modal-content" @click.stop>
      <button class="close-btn" @click="$emit('close')">←</button>
      
      <div class="modal-header">
        <h2>Задачи события</h2>
      </div>
      
      <div v-if="event" class="event-info">
        <div class="event-title">{{ event.title }}</div>
        <div class="event-datetime">
          {{ formatEventDateTime(event) }}
        </div>
      </div>
      
      <!-- Задачи события -->
      <div v-if="eventTasks.length === 0" class="empty-tasks">
        Нет привязанных задач
      </div>
      <div v-else class="event-tasks-list">
        <div
          v-for="task in eventTasks"
          :key="task.id"
          class="event-task-item"
        >
          <div class="task-checkbox" @click="toggleTaskComplete(task)">
            <span v-if="task.completed" class="checked">✓</span>
          </div>
          <div class="task-content">
            <div class="task-title">{{ task.title }}</div>
            <div v-if="task.description" class="task-description">{{ task.description }}</div>
          </div>
          <button
            type="button"
            class="remove-task-btn"
            @click="removeTaskFromEvent(task)"
            title="Удалить задачу из события"
          >
            ✕
          </button>
        </div>
      </div>
      
      <!-- Прогресс бар -->
      <div v-if="eventTasks.length > 0" class="progress-section">
        <div class="progress-bar-container">
          <div class="progress-bar" :style="{ width: progressPercentage + '%' }"></div>
        </div>
        <div class="progress-label">{{ completedTasksCount }}/{{ eventTasks.length }} задач</div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, watch, computed } from 'vue'
import dayjs from 'dayjs'
import 'dayjs/locale/ru'
import axios from 'axios'

dayjs.locale('ru')

interface CalendarEvent {
  id: string | number
  title: string
  description?: string
  start: string
  end: string
  task_count?: number
  completed_task_count?: number
  task_ids?: string[]
}

interface Task {
  id: string
  title: string
  description?: string
  completed: boolean
}

const props = defineProps<{
  show: boolean
  event: CalendarEvent | null
}>()

const emit = defineEmits<{
  (e: 'close'): void
  (e: 'task-removed'): void
}>()

// Задачи события
const eventTasks = ref<Task[]>([])

// Количество выполненных задач
const completedTasksCount = computed(() => {
  return eventTasks.value.filter(task => task.completed).length
})

// Процент выполнения
const progressPercentage = computed(() => {
  if (eventTasks.value.length === 0) return 0
  return Math.round((completedTasksCount.value / eventTasks.value.length) * 100)
})

// API для работы с задачами событий
const eventTasksApi = axios.create({
  baseURL: '/api/v1/event-tasks',
  headers: {
    'Content-Type': 'application/json'
  }
})

// Форматирование даты и времени события
const formatEventDateTime = (event: CalendarEvent) => {
  const start = dayjs(event.start)
  const end = dayjs(event.end)
  
  const dateStr = start.format('D MMMM')
  const timeStr = `${start.format('HH:mm')} - ${end.format('HH:mm')}`
  
  return `${dateStr}, ${timeStr}`
}

// Загрузка задач события
const loadEventTasks = async (eventId: string | number) => {
  try {
    const response = await eventTasksApi.get(`/events/${eventId}/tasks`)
    eventTasks.value = response.data
  } catch (error) {
    console.error('Failed to load event tasks:', error)
    eventTasks.value = []
  }
}

// Переключение статуса задачи
const toggleTaskComplete = async (task: Task) => {
  try {
    await axios.put(`/api/v1/tasks/${task.id}`, {
      completed: !task.completed
    })
    task.completed = !task.completed
    // Emit event to refresh calendar events
    emit('task-removed')
  } catch (error) {
    console.error('Failed to toggle task:', error)
  }
}

// Удаление задачи из события
const removeTaskFromEvent = async (task: Task) => {
  try {
    const eventId = props.event?.id
    if (eventId) {
      await eventTasksApi.delete(`/${eventId}/tasks/${task.id}`)
      eventTasks.value = eventTasks.value.filter(t => t.id !== task.id)
      // Emit event to refresh calendar events
      emit('task-removed')
    }
  } catch (error) {
    console.error('Failed to remove task from event:', error)
  }
}

// Watch для загрузки задач при открытии модалки
watch(() => props.show, (isVisible) => {
  if (isVisible && props.event) {
    loadEventTasks(props.event.id)
  } else {
    eventTasks.value = []
  }
})
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
  from { opacity: 0; }
  to { opacity: 1; }
}

.modal-content {
  background-color: var(--bg-primary);
  padding: 20px;
  border-radius: 12px;
  width: 90%;
  max-width: 480px;
  max-height: 90vh;
  overflow-y: auto;
  position: relative;
  border: 1px solid var(--border-color);
  animation: slideUp 0.3s cubic-bezier(0.16, 1, 0.3, 1);
}

.modal-content::-webkit-scrollbar {
  width: 6px;
}

.modal-content::-webkit-scrollbar-thumb {
  background: var(--bg-elevated);
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

.close-btn {
  position: absolute;
  top: 16px;
  right: 16px;
  background: none;
  border: none;
  color: #888;
  font-size: 20px;
  cursor: pointer;
  width: 30px;
  height: 30px;
  display: flex;
  align-items: center;
  justify-content: center;
  border-radius: 4px;
  transition: background 0.2s;
}

.close-btn:hover {
  background: var(--bg-elevated);
  color: #fff;
}

.modal-header {
  margin-bottom: 20px;
}

.modal-header h2 {
  font-size: 18px;
  font-weight: 700;
  color: #fff;
  margin: 0;
}

.event-info {
  margin-bottom: 20px;
  padding: 12px;
  background: #080808;
  border-radius: 8px;
  border: 1px solid var(--border-color);
}

.event-title {
  font-size: 14px;
  font-weight: 600;
  color: #fff;
  margin-bottom: 4px;
}

.event-datetime {
  font-size: 11px;
  color: #888;
}

.empty-tasks {
  text-align: center;
  padding: 30px;
  color: #666;
  font-size: 13px;
}

.event-tasks-list {
  display: flex;
  flex-direction: column;
  gap: 6px;
  margin-bottom: 16px;
}

.event-task-item {
  display: flex;
  align-items: flex-start;
  padding: 10px 12px;
  background: #080808;
  border-radius: 8px;
  gap: 10px;
  border: 1px solid var(--border-color);
}

.task-checkbox {
  width: 18px;
  height: 18px;
  border: 1px solid #555;
  border-radius: 4px;
  flex-shrink: 0;
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: center;
  transition: border-color 0.2s, background 0.2s;
  margin-top: 1px;
}

.task-checkbox:hover {
  border-color: #888;
}

.task-checkbox .checked {
  color: #4ade80;
  font-size: 10px;
  font-weight: bold;
}

.task-content {
  flex: 1;
  min-width: 0;
}

.task-title {
  color: #fff;
  font-size: 12px;
  line-height: 1.3;
}

.task-description {
  color: #666;
  font-size: 10px;
  line-height: 1.4;
  margin-top: 2px;
}

.remove-task-btn {
  background: none;
  border: none;
  color: #555;
  font-size: 12px;
  cursor: pointer;
  padding: 2px;
  width: 22px;
  height: 22px;
  display: flex;
  align-items: center;
  justify-content: center;
  border-radius: 4px;
  transition: background 0.2s, color 0.2s;
  flex-shrink: 0;
}

.remove-task-btn:hover {
  background: var(--bg-elevated);
  color: #ff6b6b;
}

/* Progress bar */
.progress-section {
  border-top: 1px solid var(--border-color);
  padding-top: 16px;
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 8px;
}

.progress-bar-container {
  width: 100%;
  height: 6px;
  background: var(--bg-tertiary);
  border-radius: 3px;
  overflow: hidden;
}

.progress-bar {
  height: 100%;
  background: linear-gradient(90deg, #4a90e2, #4ade80);
  border-radius: 3px;
  transition: width 0.3s ease;
}

.progress-label {
  font-size: 11px;
  color: #888;
  font-weight: 500;
}
</style>
