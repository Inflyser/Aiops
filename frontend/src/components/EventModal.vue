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
          <label>Тег:</label>
          <div class="tags-selector">
            <div 
              v-for="tag in availableTags" 
              :key="tag.id"
              class="tag-option"
              :class="{ selected: selectedTagId === tag.id }"
              @click="selectTag(tag)"
            >
              <span class="tag-color" :style="{ backgroundColor: tag.color }"></span>
              <span class="tag-name">{{ tag.name }}</span>
            </div>
            <div v-if="availableTags.length === 0" class="no-tags-message">
              Нет доступных тегов. Создайте теги в панели тегов.
            </div>
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
import { ref, computed, watch } from 'vue'

interface Tag {
  id: string
  name: string
  color: string
}

interface EventFormData {
  title: string
  description: string
  date: string
  startTime: string
  endTime: string
  priority: string
  color: string
  tagId?: string
}

interface CalendarEvent {
  id: string | number
  title: string
  description?: string
  start: string
  end: string
  priority?: string
  color?: string
  tagId?: string
}

const props = defineProps<{
  show: boolean
  editingEvent: CalendarEvent | null
  formData: EventFormData
  availableTags: Tag[]
}>()

const emit = defineEmits<{
  (e: 'close'): void
  (e: 'save'): void
  (e: 'delete'): void
}>()

const selectedTagId = ref<string | null>(null)

// Sync selectedTagId with formData when editing
watch(() => props.formData, (newFormData) => {
  selectedTagId.value = newFormData.tagId || null
}, { immediate: true })

// Also watch for when the modal opens with editing event
watch(() => props.show, (isVisible) => {
  if (isVisible && props.editingEvent) {
    selectedTagId.value = props.editingEvent.tagId || null
  }
})

const selectTag = (tag: Tag) => {
  if (selectedTagId.value === tag.id) {
    // Deselect if clicking on already selected tag
    selectedTagId.value = null
    props.formData.color = '#4a5568'
    props.formData.tagId = undefined
  } else {
    selectedTagId.value = tag.id
    props.formData.color = tag.color
    props.formData.tagId = tag.id
  }
}
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
  border-radius: 35px;
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

/* Tags Selector Styles */
.tags-selector {
  display: flex;
  flex-wrap: wrap;
  gap: 8px;
  padding: 10px;
  background-color: #2a2a2a;
  border: 1px solid #444;
  border-radius: 4px;
}

.tag-option {
  display: flex;
  align-items: center;
  gap: 6px;
  padding: 6px 12px;
  border-radius: 16px;
  background-color: #333;
  cursor: pointer;
  transition: all 0.2s;
  border: 2px solid transparent;
}

.tag-option:hover {
  background-color: #444;
}

.tag-option.selected {
  border-color: #fff;
  background-color: #4a5568;
}

.tag-color {
  width: 12px;
  height: 12px;
  border-radius: 50%;
  flex-shrink: 0;
}

.tag-name {
  font-size: 13px;
  color: #ddd;
}

.no-tags-message {
  color: #666;
  font-size: 13px;
  padding: 10px;
  text-align: center;
  width: 100%;
}
</style>
