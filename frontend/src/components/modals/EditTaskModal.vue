<template>
  <div class="modal-overlay" @click="closeModal">
    <div class="modal-content" @click.stop @keyup.esc="closeModal">
      <div class="modal-header">
        <h3>Редактировать задачу</h3>
        <button class="close-btn" @click="closeModal">✕</button>
      </div>
      <div class="modal-body">
        <form @submit.prevent="saveTask">
          <div class="form-group">
            <label for="taskTitle">Заголовок</label>
            <input
              id="taskTitle"
              v-model="localTask.title"
              type="text"
              class="form-control"
              required
            />
          </div>
          <div class="form-group">
            <label for="taskDescription">Описание</label>
            <textarea
              id="taskDescription"
              v-model="localTask.description"
              class="form-control"
              rows="3"
            ></textarea>
          </div>
          <div class="form-group">
            <label for="taskPriority">Приоритет</label>
            <select
              id="taskPriority"
              v-model="localTask.priority"
              class="form-control"
            >
              <option :value="undefined">Нет</option>
              <option value="low">Низкий</option>
              <option value="medium">Средний</option>
              <option value="high">Высокий</option>
            </select>
          </div>
          <div class="form-group">
            <label for="taskDueDate">Срок выполнения</label>
            <input
              id="taskDueDate"
              v-model="localTask.due_date"
              type="date"
              class="form-control"
            />
          </div>
          <div class="form-actions">
            <button type="button" class="btn-cancel" @click="closeModal">Отмена</button>
            <button type="submit" class="btn-save">Сохранить</button>
          </div>
        </form>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, watch } from 'vue'

interface Task {
  id: string
  title: string
  description?: string
  priority?: string
  due_date?: string
  completed: boolean
}

interface Props {
  task: Task
  visible: boolean
}

const props = defineProps<Props>()
const emit = defineEmits(['update:visible', 'save'])

const localTask = ref<Task>({
  id: '',
  title: '',
  description: '',
  priority: undefined,
  due_date: '',
  completed: false
})

watch(
  () => props.task,
  (newTask) => {
    localTask.value = { ...newTask }
  },
  { deep: true, immediate: true }
)

const closeModal = () => {
  emit('update:visible', false)
}

const saveTask = () => {
  emit('save', localTask.value)
  closeModal()
}
</script>

<style scoped>
.modal-overlay {
  position: fixed;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  background: rgba(0, 0, 0, 0.7);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 1000;
  animation: fadeIn 0.2s ease-out;
}

@keyframes fadeIn {
  from { opacity: 0; }
  to { opacity: 1; }
}

.modal-content {
  background: #1a1a1a;
  border: 1px solid #333;
  border-radius: 15px;
  width: 90%;
  max-width: 500px;
  max-height: 90vh;
  overflow-y: auto;
  box-shadow: 0 4px 20px rgba(0, 0, 0, 0.5);
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

.modal-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 16px 20px;
  border-bottom: 1px solid #333;
}

.modal-header h3 {
  margin: 0;
  color: #e2e8f0;
}

.close-btn {
  background: #333;
  border: none;
  color: white;
  width: 28px;
  height: 28px;
  border-radius: 4px;
  cursor: pointer;
  font-size: 13px;
}

.close-btn:hover {
  background: #333;
}

.modal-body {
  padding: 20px;
}

.form-group {
  margin-bottom: 16px;
}

.form-group label {
  display: block;
  margin-bottom: 6px;
  color: #cbd5e0;
  font-weight: 500;
}

.form-control {
  width: 100%;
  padding: 10px 12px;
  border: 1px solid #333;
  border-radius: 4px;
  background: #333;
  color: #d1d1d1;
  font-size: 11px;
}

.form-control:focus {
  outline: none;
  border-color: #4a90e2;
}

.form-actions {
  display: flex;
  gap: 12px;
  justify-content: flex-end;
  margin-top: 20px;
}

.btn-cancel,
.btn-save {
  padding: 10px 20px;
  border: none;
  border-radius: 4px;
  cursor: pointer;
  font-size: 11px;
}

.btn-cancel {
  background: #333;
  color: white;
}

.btn-cancel:hover {
  background: #333333;
}

.btn-save {
  background: #4767a3;
  color: white;
}

.btn-save:hover {
  background: #4767a3;
}
</style>