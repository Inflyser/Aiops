<template>
  <div v-if="show" class="modal" @click.self="$emit('close')">
    <div class="modal-content" @click.stop>
      <span class="close" @click="$emit('close')">&times;</span>
      <h2>{{ editingEvent ? 'Редактировать задачу' : 'Новая задача' }}</h2>
      <form @submit.prevent="$emit('save')">
        <div class="form-group">
          <label for="eventTitle">Название задачи:</label>
          <input 
            type="text" 
            id="eventTitle" 
            v-model="formData.title" 
            required
            placeholder="Введите название задачи"
          >
        </div>
        <div class="form-group">
          <label for="eventDescription">Описание:</label>
          <textarea 
            id="eventDescription" 
            v-model="formData.description"
            placeholder="Добавьте описание задачи (необязательно)"
            rows="3"
          ></textarea>
        </div>
        <div class="form-group">
          <label for="eventDate">Дата:</label>
          <input 
            type="date" 
            id="eventDate" 
            v-model="formData.date" 
            required
          >
        </div>
        <div class="form-row">
          <div class="form-group">
            <label for="eventStartTime">Начало:</label>
            <input 
              type="time" 
              id="eventStartTime" 
              v-model="formData.startTime" 
              required
            >
          </div>
          <div class="form-group">
            <label for="eventEndTime">Конец:</label>
            <input 
              type="time" 
              id="eventEndTime" 
              v-model="formData.endTime" 
              required
            >
          </div>
        </div>
        <div class="form-group">
          <label for="eventLocation">Место (необязательно):</label>
          <input 
            type="text" 
            id="eventLocation" 
            v-model="formData.location"
            placeholder="Например: Школа, Библиотека"
          >
        </div>
        <div class="form-row">
          <div class="form-group">
            <label for="eventPriority">Приоритет:</label>
            <select id="eventPriority" v-model="formData.priority">
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
              v-model="formData.color"
            >
          </div>
        </div>
        <div class="form-actions">
          <button type="submit" class="btn btn-primary">Сохранить</button>
          <button 
            v-if="editingEvent"
            type="button" 
            class="btn btn-danger" 
            @click="$emit('delete')"
          >
            Удалить
          </button>
          <button 
            type="button" 
            class="btn btn-secondary" 
            @click="$emit('close')"
          >
            Отмена
          </button>
        </div>
      </form>
    </div>
  </div>
</template>

<script setup lang="ts">
import { computed } from 'vue'

interface EventFormData {
  title: string
  description: string
  date: string
  startTime: string
  endTime: string
  location: string
  priority: string
  color: string
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
}

const props = defineProps<{
  show: boolean
  editingEvent: CalendarEvent | null
  formData: EventFormData
}>()

defineEmits<{
  (e: 'close'): void
  (e: 'save'): void
  (e: 'delete'): void
}>()
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
