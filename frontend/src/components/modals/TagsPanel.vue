<template>
  <div class="tags-panel">
    <div class="tags-panel-header">
      <h3>Теги</h3>
      <button class="close-btn" @click="$emit('close')">×</button>
    </div>
    
    <div class="tags-list">
      <div 
        v-for="tag in tags" 
        :key="tag.id" 
        class="tag-item"
      >
        <span class="tag-color" :style="{ backgroundColor: tag.color }"></span>
        <span class="tag-name">{{ tag.name }}</span>
        <button class="delete-tag-btn" @click="$emit('delete-tag', tag.id)">×</button>
      </div>
      
      <div v-if="tags.length === 0" class="no-tags">
        Нет тегов. Добавьте новый тег.
      </div>
    </div>
    
    <div class="add-tag-form">
      <input 
        v-model="newTagName" 
        type="text" 
        placeholder="Название тега"
        class="tag-input"
      />
      <input 
        v-model="newTagColor" 
        type="color" 
        class="color-input"
        title="Выберите цвет"
      />
      <button 
        class="add-tag-btn" 
        @click="handleAddTag"
        :disabled="!newTagName.trim()"
      >
        +
      </button>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref } from 'vue'

interface Tag {
  id: string
  name: string
  color: string
}

defineProps<{
  tags: Tag[]
}>()

const emit = defineEmits<{
  (e: 'close'): void
  (e: 'add-tag', tag: { name: string; color: string }): void
  (e: 'delete-tag', tagId: string): void
}>()

const newTagName = ref('')
const newTagColor = ref('#3B82F6')

const handleAddTag = () => {
  if (newTagName.value.trim()) {
    emit('add-tag', { 
      name: newTagName.value.trim(), 
      color: newTagColor.value 
    })
    newTagName.value = ''
    newTagColor.value = '#3B82F6'
  }
}
</script>

<style scoped>
.tags-panel {
  position: absolute;
  top: 60px;
  right: 20px;
  width: 280px;
  background: #1a1a1a;
  border: 1px solid #333;
  border-radius: 12px;
  padding: 16px;
  z-index: 100;
  box-shadow: 0 4px 20px rgba(0, 0, 0, 0.5);
}

.tags-panel-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 16px;
  padding-bottom: 12px;
  border-bottom: 1px solid #333;
}

.tags-panel-header h3 {
  margin: 0;
  font-size: 16px;
  font-weight: 600;
  color: #fff;
}

.close-btn {
  background: none;
  border: none;
  color: #888;
  font-size: 24px;
  cursor: pointer;
  padding: 0;
  line-height: 1;
}

.close-btn:hover {
  color: #fff;
}

.tags-list {
  max-height: 240px;
  overflow-y: auto;
  margin-bottom: 16px;
}

.tag-item {
  display: flex;
  align-items: center;
  padding: 8px;
  border-radius: 6px;
  margin-bottom: 4px;
  background: #252525;
  transition: background 0.2s;
}

.tag-item:hover {
  background: #2a2a2a;
}

.tag-color {
  width: 16px;
  height: 16px;
  border-radius: 4px;
  margin-right: 10px;
  flex-shrink: 0;
}

.tag-name {
  flex: 1;
  color: #ddd;
  font-size: 14px;
}

.delete-tag-btn {
  background: none;
  border: none;
  color: #666;
  font-size: 18px;
  cursor: pointer;
  padding: 0 4px;
}

.delete-tag-btn:hover {
  color: #ef4444;
}

.no-tags {
  text-align: center;
  color: #666;
  padding: 20px;
  font-size: 14px;
}

.add-tag-form {
  display: flex;
  gap: 8px;
  align-items: center;
}

.tag-input {
  flex: 1;
  background: #252525;
  border: 1px solid #333;
  border-radius: 6px;
  padding: 8px 12px;
  color: #fff;
  font-size: 14px;
}

.tag-input:focus {
  outline: none;
  border-color: #3B82F6;
}

.tag-input::placeholder {
  color: #666;
}

.color-input {
  width: 36px;
  height: 36px;
  border: none;
  border-radius: 6px;
  cursor: pointer;
  background: none;
  padding: 0;
}

.color-input::-webkit-color-swatch-wrapper {
  padding: 0;
}

.color-input::-webkit-color-swatch {
  border: 1px solid #333;
  border-radius: 6px;
}

.add-tag-btn {
  width: 36px;
  height: 36px;
  background: #3B82F6;
  border: none;
  border-radius: 6px;
  color: #fff;
  font-size: 20px;
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: center;
  transition: background 0.2s;
}

.add-tag-btn:hover:not(:disabled) {
  background: #2563eb;
}

.add-tag-btn:disabled {
  background: #333;
  cursor: not-allowed;
}
</style>
