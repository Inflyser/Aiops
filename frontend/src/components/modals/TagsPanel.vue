<template>
  <div class="tags-panel" :class="{ 'open': isOpen }">
    <div class="tags-panel-header">
      <h3 class="tags-title">Теги</h3>
      <button class="close-btn" @click="$emit('close')">→</button>
    </div>

    <div class="tags-list">
      <div
        v-for="tag in tags"
        :key="tag.id"
        class="tag-item"
        draggable="true"
        @dragstart="handleDragStart($event, tag)"
      >
        <img
          v-if="tag.icon"
          :src="getIconPath(tag.icon)"
          class="tag-icon"
        />
        <span v-else class="tag-icon-placeholder"></span>
        <span class="tag-color" :style="{ backgroundColor: tag.color }"></span>
        <span class="tag-name">{{ tag.name }}</span>
        <button class="delete-tag-btn" @click="$emit('delete-tag', tag.id)">✕</button>
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

      <div class="form-row">
        <label class="form-label">Цвет</label>
        <div class="color-picker-wrap">
          <input
            v-model="newTagColor"
            type="color"
            class="color-input"
            title="Выберите цвет"
          />
          <span class="color-hex">{{ newTagColor }}</span>
        </div>
      </div>

      <div class="form-row">
        <label class="form-label">Иконка</label>
        <div class="icon-selector">
          <button
            type="button"
            class="icon-btn"
            :class="{ selected: !newTagIcon }"
            @click="selectIcon(undefined)"
            title="Без иконки"
          >
            —
          </button>
          <button
            v-for="icon in iconFiles"
            :key="icon.name"
            type="button"
            class="icon-btn"
            :class="{ selected: newTagIcon === icon.name }"
            @click="selectIcon(icon.name)"
          >
            <img :src="icon.path" />
          </button>
        </div>
      </div>

      <button
        class="add-tag-btn"
        @click="handleAddTag"
        :disabled="!newTagName.trim()"
      >
        Добавить тег
      </button>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed } from 'vue'

interface Tag {
  id: string
  name: string
  color: string
  icon?: string
}

defineProps<{
  isOpen: boolean
  tags: Tag[]
}>()

const emit = defineEmits<{
  (e: 'close'): void
  (e: 'add-tag', tag: { name: string; color: string; icon?: string }): void
  (e: 'delete-tag', tagId: string): void
}>()

const newTagName = ref('')
const newTagColor = ref('#3B82F6')
const newTagIcon = ref<string | undefined>(undefined)

const iconModules = import.meta.glob<{ default: string }>('../../assets/icon/*.svg', { query: '?url', import: 'default', eager: true })

const iconFiles = computed(() => {
  return Object.entries(iconModules).map(([path, url]) => {
    const name = path.split('/').pop()?.replace('.svg', '') || ''
    return { name, path: (url as unknown as string) }
  })
})

const selectIcon = (iconName: string | undefined) => {
  newTagIcon.value = iconName
}

const handleAddTag = () => {
  if (newTagName.value.trim()) {
    emit('add-tag', {
      name: newTagName.value.trim(),
      color: newTagColor.value,
      icon: newTagIcon.value
    })
    newTagName.value = ''
    newTagColor.value = '#3B82F6'
    newTagIcon.value = undefined
  }
}

const getIconPath = (iconName: string): string | undefined => {
  const icon = iconFiles.value.find(i => i.name === iconName)
  return icon?.path
}

const handleDragStart = (e: DragEvent, tag: Tag) => {
  if (e.dataTransfer) {
    e.dataTransfer.setData('text/plain', JSON.stringify({
      _tag: true,
      id: tag.id,
      name: tag.name,
      color: tag.color,
      icon: tag.icon
    }))
    e.dataTransfer.effectAllowed = 'all'
  }
}
</script>

<style scoped>
.tags-panel {
  position: fixed;
  top: 0;
  left: -320px;
  width: 320px;
  height: 100vh;
  background: #050505;
  border-right: 1px solid #33333357;
  transition: left 0.3s ease;
  z-index: 1000;
  display: flex;
  flex-direction: column;
}

.tags-panel.open {
  left: 0;
}

.tags-panel-header {
  padding: 20px;
  border-bottom: 1px solid #33333357;
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.tags-title {
  margin: 0;
  color: #fff;
  font-size: 14px;
  font-weight: 600;
}

.close-btn {
  background: none;
  border: none;
  color: #888;
  font-size: 19px;
  cursor: pointer;
  padding: 0;
  width: 30px;
  height: 30px;
  display: flex;
  align-items: center;
  justify-content: center;
  border-radius: 4px;
  transition: background 0.2s;
}

.close-btn:hover {
  background: #333;
  color: #fff;
}

.tags-list {
  flex: 1;
  overflow-y: auto;
  padding: 10px;
}

.tag-item {
  display: flex;
  align-items: center;
  padding: 8px;
  border-radius: 6px;
  margin-bottom: 4px;
  background: #0d0d0d;
  transition: background 0.2s;
}

.tag-item:hover {
  background: #151515;
}

.tag-item:active {
  cursor: grabbing;
}

.tag-color {
  width: 16px;
  height: 16px;
  border-radius: 4px;
  margin-right: 10px;
  flex-shrink: 0;
}

.tag-icon {
  width: 16px;
  height: 16px;
  margin-right: 6px;
  flex-shrink: 0;
}

.tag-icon-placeholder {
  width: 16px;
  height: 16px;
  margin-right: 6px;
  flex-shrink: 0;
}

.tag-name {
  flex: 1;
  color: #ddd;
  font-size: 11px;
}

.delete-tag-btn {
  background: none;
  border: none;
  color: #666;
  font-size: 14px;
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
  font-size: 11px;
}

.add-tag-form {
  display: flex;
  flex-direction: column;
  gap: 12px;
  padding: 16px 20px 20px;
  border-top: 1px solid #33333357;
}

.tag-input {
  width: 100%;
  background: #0d0d0d;
  border: 1px solid #33333357;
  border-radius: 6px;
  padding: 10px 12px;
  color: #fff;
  font-size: 11px;
  box-sizing: border-box;
}

.tag-input:focus {
  outline: none;
  border-color: #3B82F6;
  background: #101010;
}

.tag-input::placeholder {
  color: #666;
}

.form-row {
  display: flex;
  flex-direction: column;
  gap: 6px;
}

.form-label {
  font-size: 10px;
  color: #888;
  text-transform: uppercase;
  letter-spacing: 0.5px;
}

.color-picker-wrap {
  display: flex;
  align-items: center;
  gap: 10px;
}

.color-input {
  width: 40px;
  height: 40px;
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

.color-hex {
  font-size: 10px;
  color: #888;
  font-family: monospace;
}

.icon-selector {
  display: flex;
  flex-wrap: wrap;
  gap: 6px;
  max-height: 120px;
  overflow-y: auto;
  padding: 4px;
}

.icon-selector::-webkit-scrollbar {
  width: 6px;
}

.icon-selector::-webkit-scrollbar-track {
  background: #1a1a1a;
  border-radius: 3px;
}

.icon-selector::-webkit-scrollbar-thumb {
  background: #444;
  border-radius: 3px;
}

.icon-selector::-webkit-scrollbar-thumb:hover {
  background: #555;
}

.icon-btn {
  width: 32px;
  height: 32px;
  border: 1px solid #33333357;
  border-radius: 6px;
  background: #0d0d0d;
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 6px;
  transition: all 0.2s;
}

.icon-btn:hover {
  background: #151515;
}

.icon-btn.selected {
  border-color: #3B82F6;
  background: #3B82F620;
}

.icon-btn img {
  width: 100%;
  height: 100%;
  object-fit: contain;
}

.add-tag-btn {
  width: 100%;
  padding: 12px;
  background: #3B82F6;
  border: none;
  border-radius: 8px;
  color: #fff;
  font-size: 11px;
  font-weight: 600;
  cursor: pointer;
  transition: background 0.2s;
}

.add-tag-btn:hover:not(:disabled) {
  background: #2563eb;
  transform: scale(1.02);
}

.add-tag-btn:disabled {
  background: #33333357;
  cursor: not-allowed;
}
</style>
