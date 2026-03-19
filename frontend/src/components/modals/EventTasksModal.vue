<template>
  <div v-if="show" class="modal" @click.self="$emit('close')">
    <div class="modal-content" @click.stop>
      <span class="close" @click="$emit('close')">&times;</span>
      
      <!-- Заголовок -->
      <h2>
        <img src="@/assets/icon-clock.svg" alt="clock" class="header-icon" />
        Задачи события
      </h2>

      <div class="divider"></div>
      
      <!-- Информация о событии -->
      <div v-if="event" class="event-info">
        <div class="event-title">{{ event.title }}</div>
        <div class="event-datetime">
          {{ formatEventDateTime(event) }}
        </div>
      </div>
      
      <div class="divider"></div>
      
      <!-- Задачи события -->
      <div class="form-group">
        <label class="form-label">Задачи ({{ eventTasks.length }})</label>
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
      </div>
      
      <div class="divider"></div>
      
      <!-- Кнопки -->
      <div class="form-actions">
        <button
          type="button"
          class="btn btn-secondary"
          @click="$emit('close')"
        >
          Закрыть
        </button>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, watch } from 'vue'
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

.divider {
  height: 1px;
  background-color: #333;
  margin: 15px 0;
}

.event-info {
  padding: 10px 0;
}

.event-title {
  font-size: 18px;
  font-weight: 600;
  color: #fff;
  margin-bottom: 5px;
}

.event-datetime {
  font-size: 14px;
  color: #888;
}

.form-group {
  margin-bottom: 10px;
}

.form-group label {
  display: block;
  margin-bottom: 8px;
  font-size: 11px;
  color: #888;
  text-transform: uppercase;
  letter-spacing: 0.5px;
}

.empty-tasks {
  text-align: center;
  padding: 30px;
  color: #666;
  font-size: 14px;
}

.event-tasks-list {
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.event-task-item {
  display: flex;
  align-items: flex-start;
  padding: 12px;
  background-color: #2a2a2a;
  border-radius: 8px;
  gap: 12px;
}

.task-checkbox {
  width: 20px;
  height: 20px;
  border: 2px solid #666;
  border-radius: 4px;
  flex-shrink: 0;
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: center;
  transition: border-color 0.2s, background 0.2s;
}

.task-checkbox:hover {
  border-color: #888;
}

.task-checkbox .checked {
  color: #4ade80;
  font-size: 14px;
  font-weight: bold;
}

.task-content {
  flex: 1;
  min-width: 0;
}

.task-title {
  color: #fff;
  font-size: 14px;
  margin-bottom: 4px;
}

.task-description {
  color: #888;
  font-size: 12px;
  line-height: 1.4;
}

.remove-task-btn {
  background: none;
  border: none;
  color: #666;
  font-size: 16px;
  cursor: pointer;
  padding: 4px;
  width: 24px;
  height: 24px;
  display: flex;
  align-items: center;
  justify-content: center;
  border-radius: 4px;
  transition: background 0.2s, color 0.2s;
  flex-shrink: 0;
}

.remove-task-btn:hover {
  background: #333;
  color: #ff6b6b;
}

.form-actions {
  display: flex;
  justify-content: flex-end;
  gap: 10px;
  margin-top: 15px;
}

.btn {
  padding: 10px 20px;
  border-radius: 8px;
  font-size: 14px;
  font-weight: 500;
  cursor: pointer;
  transition: all 0.2s;
  border: none;
}

.btn-secondary {
  background-color: #333;
  color: #fff;
}

.btn-secondary:hover {
  background-color: #444;
}

.btn-primary {
  background-color: #1c3496;
  color: #fff;
}

.btn-primary:hover {
  background-color: #2a4bb8;
}
</style>
