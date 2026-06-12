<template>
  <div class="filter-panel" :class="{ 'open': isOpen }">
    <div class="filter-header">
      <h3 class="filter-title">Фильтр</h3>
      <button class="close-btn" @click="$emit('close')">←</button>
    </div>

    <div class="filter-content">
      <div class="filter-section">
        <div class="filter-section-title">По тегам</div>
        <div v-if="tags.length === 0" class="empty-filter">Нет тегов</div>
        <div
          v-for="tag in tags"
          :key="tag.id"
          class="filter-option"
          @click="toggleTag(tag.id)"
        >
          <span class="filter-checkbox" :class="{ checked: activeTags.includes(tag.id) }">
            <span v-if="activeTags.includes(tag.id)">✓</span>
          </span>
          <span class="filter-dot" :style="{ background: tag.color }"></span>
          <span class="filter-label">{{ tag.name }}</span>
        </div>
      </div>

      <div class="filter-section">
        <div class="filter-section-title">По важности</div>
        <div class="filter-option" @click="showImportant = !showImportant">
          <span class="filter-checkbox" :class="{ checked: showImportant }">
            <span v-if="showImportant">✓</span>
          </span>
          <span class="filter-label">Только важные</span>
        </div>
      </div>

      <button class="clear-btn" @click="clearFilters">Сбросить фильтры</button>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, watch } from 'vue'

interface Tag {
  id: string
  name: string
  color: string
  icon?: string
}

const props = defineProps<{
  isOpen: boolean
  tags: Tag[]
  activeTags: string[]
  showImportant: boolean
}>()

const emit = defineEmits<{
  (e: 'close'): void
  (e: 'update:activeTags', tags: string[]): void
  (e: 'update:showImportant', val: boolean): void
}>()

const activeTags = ref<string[]>([...props.activeTags])
const showImportant = ref(props.showImportant)

watch(() => props.isOpen, (val) => {
  if (val) {
    activeTags.value = [...props.activeTags]
    showImportant.value = props.showImportant
  }
})

watch(activeTags, () => {
  emit('update:activeTags', activeTags.value)
}, { deep: true })

watch(showImportant, (val) => {
  emit('update:showImportant', val)
})

const toggleTag = (tagId: string) => {
  const idx = activeTags.value.indexOf(tagId)
  if (idx === -1) {
    activeTags.value.push(tagId)
  } else {
    activeTags.value.splice(idx, 1)
  }
}

const clearFilters = () => {
  activeTags.value = props.tags.map(t => t.id)
  showImportant.value = false
}
</script>

<style scoped>
.filter-panel {
  position: fixed;
  top: 0;
  left: -320px;
  width: 320px;
  height: 100vh;
  background: var(--bg-primary);
  border-right: 1px solid var(--border-subtle);
  transition: left 0.3s ease;
  z-index: 999;
  display: flex;
  flex-direction: column;
}

.filter-panel.open {
  left: 0;
}

.filter-header {
  padding: 20px;
  border-bottom: 1px solid var(--border-subtle);
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.filter-title {
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
  background: var(--bg-elevated);
  color: #fff;
}

.filter-content {
  flex: 1;
  overflow-y: auto;
  padding: 10px;
}

.filter-section {
  margin-bottom: 20px;
}

.filter-section-title {
  color: #888;
  font-size: 10px;
  text-transform: uppercase;
  letter-spacing: 1px;
  margin-bottom: 10px;
  padding: 0 4px;
}

.empty-filter {
  color: #666;
  padding: 10px 4px;
  font-size: 13px;
}

.filter-option {
  display: flex;
  align-items: center;
  padding: 8px;
  cursor: pointer;
  border-radius: 6px;
  transition: background 0.15s;
  gap: 8px;
}

.filter-option:hover {
  background: rgba(255, 255, 255, 0.05);
}

.filter-checkbox {
  width: 18px;
  height: 18px;
  border: 1px solid #444;
  border-radius: 4px;
  display: flex;
  align-items: center;
  justify-content: center;
  flex-shrink: 0;
  font-size: 11px;
  color: #4ade80;
  transition: all 0.15s;
}

.filter-checkbox.checked {
  border-color: #4ade80;
  background: rgba(74, 222, 128, 0.1);
}

.filter-dot {
  width: 10px;
  height: 10px;
  border-radius: 50%;
  flex-shrink: 0;
}

.filter-label {
  color: #ddd;
  font-size: 13px;
  flex: 1;
}

.clear-btn {
  width: 100%;
  padding: 12px;
  background: transparent;
  color: #888;
  border: 1px solid var(--border-color);
  border-radius: 8px;
  cursor: pointer;
  font-weight: 600;
  font-size: 13px;
  transition: all 0.2s;
}

.clear-btn:hover {
  background: var(--border-subtle);
  color: #fff;
  border-color: #555;
}
</style>
