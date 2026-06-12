<template>
  <div class="task-list">
    <div class="task-header">
      <div class="header-left">
        <router-link to="/" class="back-link">← Календарь</router-link>
        <h2>Задачи</h2>
      </div>
      <button class="btn-add" @click="showModal = true">+ Добавить задачу</button>
    </div>

    <div v-if="loading" class="loading">Загрузка...</div>
    <div v-if="error" class="error">{{ error }}</div>

    <div class="tasks-container">
      <div 
        v-for="task in tasks" 
        :key="task.id" 
        class="task-item"
        :class="{ completed: task.completed }"
      >
        <div class="task-content">
          <input 
            type="checkbox" 
            :checked="task.completed"
            @change="toggleTask(task.id)"
            class="task-checkbox"
          >
          <div class="task-info">
            <h3 class="task-title">{{ task.title }}</h3>
            <p v-if="task.description" class="task-description">{{ task.description }}</p>
            <div class="task-meta">
              <span v-if="task.due_date" class="task-date">
                📅 {{ formatDate(task.due_date) }}
              </span>
              <span class="task-priority" :class="`priority-${task.priority}`">
                {{ getPriorityLabel(task.priority) }}
              </span>
            </div>
          </div>
        </div>
        <div class="task-actions">
          <button @click="editTask(task)" class="btn-edit">✏️</button>
          <button @click="deleteTask(task.id)" class="btn-delete">🗑️</button>
        </div>
      </div>
      <div v-if="tasks.length === 0 && !loading" class="empty-state">
        Нет задач. Создайте первую задачу!
      </div>
    </div>

    <!-- Task Modal -->
    <div v-if="showModal" class="modal" @click.self="closeModal">
      <div class="modal-content" @click.stop>
        <span class="close" @click="closeModal">&times;</span>
        <h2>{{ editingTask ? 'Редактировать задачу' : 'Новая задача' }}</h2>
        <form @submit.prevent="saveTask">
          <div class="form-group">
            <label for="taskTitle">Название:</label>
            <input 
              type="text" 
              id="taskTitle" 
              v-model="taskForm.title" 
              required
              placeholder="Введите название задачи"
            >
          </div>
          <div class="form-group">
            <label for="taskDescription">Описание:</label>
            <textarea 
              id="taskDescription" 
              v-model="taskForm.description"
              placeholder="Введите описание задачи"
              rows="3"
            ></textarea>
          </div>
          <div class="form-row">
            <div class="form-group">
              <label for="taskDueDate">Срок выполнения:</label>
              <input 
                type="date" 
                id="taskDueDate" 
                v-model="taskForm.due_date"
              >
            </div>
            <div class="form-group">
              <label for="taskPriority">Приоритет:</label>
              <select id="taskPriority" v-model="taskForm.priority">
                <option value="low">Низкий</option>
                <option value="medium">Средний</option>
                <option value="high">Высокий</option>
              </select>
            </div>
          </div>
          <div class="form-actions">
            <button type="submit" class="btn btn-primary">Сохранить</button>
            <button 
              v-if="editingTask"
              type="button" 
              class="btn btn-danger" 
              @click="deleteTask(editingTask.id)"
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
import { ref, onMounted } from 'vue'
import { useTasksStore } from '../../stores/tasks'
import dayjs from 'dayjs'

const tasksStore = useTasksStore()
const { tasks, loading, error } = tasksStore

const showModal = ref(false)
const editingTask = ref<any>(null)

const taskForm = ref({
  title: '',
  description: '',
  due_date: '',
  priority: 'medium'
})

const formatDate = (date: string) => {
  return dayjs(date).format('DD.MM.YYYY')
}

const getPriorityLabel = (priority: string) => {
  const labels: Record<string, string> = {
    low: 'Низкий',
    medium: 'Средний',
    high: 'Высокий'
  }
  return labels[priority] || priority
}

const toggleTask = async (taskId: string) => {
  await tasksStore.toggleTask(taskId)
}

const editTask = (task: any) => {
  editingTask.value = task
  taskForm.value = {
    title: task.title,
    description: task.description || '',
    due_date: task.due_date ? dayjs(task.due_date).format('YYYY-MM-DD') : '',
    priority: task.priority || 'medium'
  }
  showModal.value = true
}

const deleteTask = async (taskId: string) => {
  if (confirm('Вы уверены, что хотите удалить эту задачу?')) {
    await tasksStore.deleteTask(taskId)
    if (editingTask.value?.id === taskId) {
      closeModal()
    }
  }
}

const saveTask = async () => {
  const taskData: any = {
    title: taskForm.value.title,
    description: taskForm.value.description || null,
    priority: taskForm.value.priority
  }
  
  if (taskForm.value.due_date) {
    taskData.due_date = dayjs(taskForm.value.due_date).toISOString()
  }
  
  if (editingTask.value) {
    await tasksStore.updateTask(editingTask.value.id, taskData)
  } else {
    await tasksStore.createTask(taskData)
  }
  
  closeModal()
}

const closeModal = () => {
  showModal.value = false
  editingTask.value = null
  taskForm.value = {
    title: '',
    description: '',
    due_date: '',
    priority: 'medium'
  }
}

onMounted(() => {
  tasksStore.fetchTasks()
})
</script>

<style scoped>
.task-list {
  padding: 20px;
  background-color: #0a0a0a;
  min-height: 100vh;
}

.task-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 30px;
}

.header-left {
  display: flex;
  align-items: center;
  gap: 20px;
}

.back-link {
  color: #888;
  text-decoration: none;
  font-size: 11px;
  transition: color 0.2s;
}

.back-link:hover {
  color: #fff;
}

.task-header h2 {
  font-size: 22px;
  font-weight: 300;
}

.btn-add {
  background-color: #4a5568;
  color: #fff;
  border: none;
  padding: 10px 20px;
  border-radius: 6px;
  cursor: pointer;
  font-size: 11px;
  transition: background-color 0.2s;
}

.btn-add:hover {
  background-color: #5a6578;
}

.loading, .error {
  padding: 20px;
  text-align: center;
  color: #888;
}

.error {
  color: #dc3545;
}

.tasks-container {
  display: flex;
  flex-direction: column;
  gap: 15px;
}

.task-item {
  background-color: var(--bg-tertiary);
  border: 1px solid var(--border-color);
  border-radius: 8px;
  padding: 20px;
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  transition: all 0.2s;
}

.task-item:hover {
  border-color: #444;
}

.task-item.completed {
  opacity: 0.6;
}

.task-content {
  display: flex;
  gap: 15px;
  flex: 1;
}

.task-checkbox {
  width: 20px;
  height: 20px;
  cursor: pointer;
  margin-top: 2px;
}

.task-info {
  flex: 1;
}

.task-title {
  font-size: 14px;
  font-weight: 500;
  margin-bottom: 8px;
  color: #fff;
}

.task-item.completed .task-title {
  text-decoration: line-through;
  color: #888;
}

.task-description {
  color: #aaa;
  font-size: 11px;
  margin-bottom: 10px;
  line-height: 1.5;
}

.task-meta {
  display: flex;
  gap: 15px;
  font-size: 10px;
  color: #888;
}

.task-priority {
  padding: 4px 8px;
  border-radius: 4px;
  font-size: 9px;
}

.priority-low {
  background-color: #2d5016;
  color: #7cb342;
}

.priority-medium {
  background-color: #5d4037;
  color: #ff9800;
}

.priority-high {
  background-color: #b71c1c;
  color: #f44336;
}

.task-actions {
  display: flex;
  gap: 10px;
}

.btn-edit, .btn-delete {
  background: transparent;
  border: none;
  font-size: 14px;
  cursor: pointer;
  padding: 5px;
  opacity: 0.7;
  transition: opacity 0.2s;
}

.btn-edit:hover, .btn-delete:hover {
  opacity: 1;
}

.empty-state {
  text-align: center;
  padding: 60px 20px;
  color: #666;
  font-size: 13px;
}

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
  background-color: var(--bg-tertiary);
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
  font-size: 22px;
  cursor: pointer;
  color: #888;
}

.close:hover {
  color: #fff;
}

.modal-content h2 {
  margin-bottom: 20px;
  font-size: 19px;
}

.form-group {
  margin-bottom: 15px;
}

.form-group label {
  display: block;
  margin-bottom: 5px;
  font-size: 11px;
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
  font-size: 11px;
  font-family: inherit;
}

.form-group textarea {
  resize: vertical;
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
  font-size: 11px;
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
  background-color: var(--bg-elevated);
  color: #fff;
}

.btn-danger {
  background-color: #dc3545;
  color: #fff;
}
</style>

