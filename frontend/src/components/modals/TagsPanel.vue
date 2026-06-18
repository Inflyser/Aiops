<template>
  <div class="tags-panel" :class="{ 'open': isOpen }">
    <div class="tags-panel-header">
      <h3 class="tags-title">
        <svg class="tags-header-icon" xmlns="http://www.w3.org/2000/svg" height="18px" viewBox="0 -960 960 960" width="18px" fill="#ccc"><path d="M200-120v-640q0-33 23.5-56.5T280-840h400q33 0 56.5 23.5T760-760v640L480-240 200-120Zm80-122 200-86 200 86v-518H280v518Zm0-518h400-400Z"/></svg>
        Теги
      </h3>
      <button class="close-btn" @click="$emit('close')">→</button>
    </div>

    <div class="block block--tags">
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
    </div>

    <div class="add-tag-form">
      <div class="block block--color">
        <div class="block__header">
          <svg xmlns="http://www.w3.org/2000/svg" height="14px" viewBox="0 -960 960 960" width="14px" fill="#888"><path d="M480-80q-83 0-156-31.5T197-197q-54-54-85.5-127T80-480q0-166 117-283t283-117q166 0 283 117t117 283q0 51-19 98t-52 84q-33 37-79 58t-99 21q-33 0-63.5-11T610-248q-10 28-32 44t-49 16q-38 0-62-24t-24-62q0-12 3-23t9-21q5-8 8-17t3-19q0-38-26-64t-64-26q-20 0-38 8t-31 22q-13 14-32 22t-40 8q-38 0-62-24t-24-62q0-78 55-133t133-55q20 0 38.5 4t35.5 12q17 8 35.5 12t38.5 4q38 0 64-26t26-64q0-20-8-38t-22-31q-14-13-22-32t-8-40q0-38 24-62t62-24q14 0 28.5 3t27.5 9q50 23 91.5 57t74.5 74q33 40 52 88t19 102q0 51-19 98t-52 84q-33 37-79 58t-99 21q-18 0-35.5-4.5T608-206q-4 12-14 19t-23 7q-10 0-17.5-7.5T546-205q0-8 3-16t9-15q7-9 10-18t3-20q0-22-16-38t-38-16q-22 0-38 16t-16 38q0 18-5 34t-13 30q-8 14-13 30t-5 34q0 22 16 38t38 16h40q13 0 21.5-8.5T524-280q0-13 8.5-21.5T554-310q13 0 21.5 8.5T584-280v20q0 17 4.5 32t12.5 28q13 18 32 29t40 11q23 0 42-9.5t33-25.5q26-30 42-67t16-78q0-66-25-124.5T689-585q-44-47-104-74t-125-27q-83 0-141.5 58.5T260-486q0 38 26 64t64 26q25 0 47.5-10t39.5-28q17-18 39.5-28t47.5-10q38 0 64 26t26 64q0 38-26 64t-64 26q-12 0-23.5-3t-20.5-9q-9-6-20.5-9t-23.5-3q-22 0-38 16t-16 38q0 18 4.5 34t13.5 30q12 18 19 38t7 42q0 24-8.5 45.5T613-146q-23 25-56 41.5T490-88h-10Z"/></svg>
          Цвет
        </div>
        <div class="color-picker-wrap">
          <div class="recent-colors">
            <button
              v-for="c in recentColors"
              :key="c"
              class="recent-color-swatch"
              :style="{ backgroundColor: c }"
              :class="{ active: newTagColor === c }"
              @click="selectRecentColor(c)"
              :title="c"
            ></button>
          </div>
          <span class="color-divider"></span>
          <button
            class="eyedropper-btn"
            @click="triggerColorPicker"
            title="Выбрать цвет"
          >
            <svg xmlns="http://www.w3.org/2000/svg" height="18px" viewBox="0 -960 960 960" width="18px" fill="#aaa"><path d="M440-120q-33 0-56.5-23.5T360-200q0-33 23.5-56.5T440-280h40v-240L200-760q-17-17-17-40t17-40q17-17 40-17t40 17l280 280q11 11 11 28t-11 28q-11 11-28 11t-28-11l-84-84v228h40q33 0 56.5 23.5T600-480v280q0 33-23.5 56.5T520-120H440Zm200-400q-17 0-28.5-11.5T600-560q0-17 11.5-28.5T640-600h40v-128l-32-32-32 32q-12 12-28.5 12T559-728q-12-12-12-28.5t12-28.5l72-72q12-12 28.5-12t28.5 12q12 12 12 28.5T688-800l-8 8v152h40q17 0 28.5 11.5T760-600q0 17-11.5 28.5T720-560h-80Z"/></svg>
          </button>
          <button
            type="button"
            class="palette-toggle-btn"
            @click="showPalettes = !showPalettes"
            :title="showPalettes ? 'Свернуть' : 'Выбрать палитру'"
          >
            <span
              v-for="c in currentPalette.colors"
              :key="c"
              class="palette-swatch"
              :style="{ backgroundColor: c }"
            ></span>
            <svg class="toggle-arrow" :class="{ open: showPalettes }" xmlns="http://www.w3.org/2000/svg" height="14px" viewBox="0 -960 960 960" width="14px" fill="#888"><path d="M480-344 240-584l56-56 184 184 184-184 56 56-240 240Z"/></svg>
          </button>
          <span class="palette-label">{{ currentPalette.label }}</span>
          <input
            ref="colorInputRef"
            v-model="newTagColor"
            type="color"
            class="color-input-hidden"
            title="Выберите цвет"
            @input="onColorPicked"
          />
        </div>
        <div v-if="showPalettes" class="color-palettes">
          <div
            v-for="palette in colorPalettes"
            :key="palette.label"
            class="palette-card"
            :class="{ active: palette.colors.includes(newTagColor) }"
          >
            <span class="palette-card-label">{{ palette.label }}</span>
            <span class="palette-card-colors">
              <button
                v-for="c in palette.colors"
                :key="c"
                class="palette-swatch-btn"
                :class="{ active: newTagColor === c }"
                :style="{ backgroundColor: c }"
                @click="selectColor(c)"
                :title="c"
              ></button>
            </span>
          </div>
        </div>
      </div>

      <div class="block block--details">
        <input
          v-model="newTagName"
          type="text"
          placeholder="Название тега"
          class="tag-input"
        />

        <div class="form-row">
          <label class="form-label" @click="showIcons = !showIcons">
            Иконка
            <svg class="icon-arrow" :class="{ open: showIcons }" xmlns="http://www.w3.org/2000/svg" height="12px" viewBox="0 -960 960 960" width="12px" fill="#888"><path d="M480-344 240-584l56-56 184 184 184-184 56 56-240 240Z"/></svg>
          </label>
          <div class="icon-toggle-row">
            <button
              type="button"
              class="icon-toggle-btn"
              @click="showIcons = !showIcons"
              :title="showIcons ? 'Свернуть' : 'Выбрать иконку'"
            >
              <img v-if="newTagIcon" :src="getIconPath(newTagIcon)" class="icon-preview" />
              <span v-else class="icon-preview none">—</span>
              <svg class="toggle-arrow" :class="{ open: showIcons }" xmlns="http://www.w3.org/2000/svg" height="14px" viewBox="0 -960 960 960" width="14px" fill="#888"><path d="M480-344 240-584l56-56 184 184 184-184 56 56-240 240Z"/></svg>
            </button>
            <span class="icon-filename">{{ newTagIcon || 'без иконки' }}</span>
          </div>
          <div v-if="showIcons" class="icon-selector">
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

const RECENT_COLORS_KEY = 'tagRecentColors'
const MAX_RECENT = 3

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
const colorInputRef = ref<HTMLInputElement | null>(null)
const showIcons = ref(false)
const showPalettes = ref(false)

const recentColors = ref<string[]>(loadRecentColors())

interface Palette {
  label: string
  colors: string[]
}

const currentPalette = computed<Palette>(() => {
  const found = colorPalettes.find(p => p.colors[0] === newTagColor.value)
  return found || colorPalettes[0]
})

const colorPalettes: Palette[] = [
  { label: 'Matcha Fog', colors: ['#A3C48D', '#5D7F4C', '#E6F4D9'] },
  { label: 'Slate Mono', colors: ['#4C5564', '#111828', '#E6E7EB'] },
  { label: 'Icy Indigo', colors: ['#5B8DFD', '#294A8D', '#DDE7FF'] },
  { label: 'Warm Sandstone', colors: ['#F4A072', '#BF5B3A', '#FFE5DA'] },
  { label: 'Rose Dust', colors: ['#E8A0BF', '#BF5A7D', '#FDE8F0'] },
  { label: 'Deep Teal', colors: ['#2DD4BF', '#0F766E', '#CCFBF1'] },
]

function selectRecentColor(color: string) {
  newTagColor.value = color
  saveRecentColor(color)
}

function selectColor(color: string) {
  newTagColor.value = color
  saveRecentColor(color)
}

function loadRecentColors(): string[] {
  try {
    const saved = localStorage.getItem(RECENT_COLORS_KEY)
    return saved ? JSON.parse(saved) : ['#3B82F6', '#EF4444', '#10B981']
  } catch {
    return ['#3B82F6', '#EF4444', '#10B981']
  }
}

function saveRecentColor(color: string) {
  const list = recentColors.value.filter(c => c !== color)
  list.unshift(color)
  recentColors.value = list.slice(0, MAX_RECENT)
  localStorage.setItem(RECENT_COLORS_KEY, JSON.stringify(recentColors.value))
}

function onColorPicked() {
  saveRecentColor(newTagColor.value)
}

function triggerColorPicker() {
  colorInputRef.value?.click()
}

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
    saveRecentColor(newTagColor.value)
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
  background: var(--bg-primary);
  border-right: 1px solid var(--border-subtle);
  transition: left 0.3s ease;
  z-index: 1000;
  display: flex;
  flex-direction: column;
}

.tags-panel.open {
  left: 0;
}

.tags-panel-header {
  padding: 14px 16px;
  border-bottom: 1px solid var(--border-subtle);
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.tags-title {
  margin: 0;
  color: #fff;
  font-size: 13px;
  font-weight: 600;
  display: flex;
  align-items: center;
  gap: 6px;
}

.tags-header-icon {
  flex-shrink: 0;
}

.close-btn {
  background: none;
  border: none;
  color: #888;
  font-size: 16px;
  cursor: pointer;
  padding: 0;
  width: 26px;
  height: 26px;
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

.tags-list {
  padding: 0;
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
  gap: 8px;
  padding: 10px 12px 14px;
}

.block {
  background: #0d0d0d;
  border: 1px solid var(--border-subtle);
  border-radius: 14px;
  padding: 10px 12px;
}

.block--tags {
  margin: 0 12px;
  max-height: 35vh;
  overflow-y: auto;
  padding: 6px 8px;
}

.block--color {
  border-radius: 20px 20px 14px 14px;
  overflow: hidden;
}

.block--details {
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.block--details .tag-input {
  margin-bottom: 0;
}

.block__header {
  display: flex;
  align-items: center;
  gap: 6px;
  font-size: 9px;
  font-weight: 600;
  color: #888;
  text-transform: uppercase;
  letter-spacing: 0.5px;
  margin-bottom: 8px;
}

.tag-input {
  width: 100%;
  background: #0d0d0d;
  border: 1px solid var(--border-subtle);
  border-radius: 5px;
  padding: 7px 10px;
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
  gap: 4px;
}

.form-label {
  font-size: 9px;
  color: #888;
  text-transform: uppercase;
  letter-spacing: 0.5px;
  display: flex;
  align-items: center;
  gap: 4px;
}

.icon-arrow {
  transition: transform 0.2s;
}

.icon-arrow.open {
  transform: rotate(180deg);
}

.color-picker-wrap {
  position: relative;
  display: flex;
  align-items: center;
  gap: 6px;
  flex-wrap: wrap;
  row-gap: 4px;
  justify-content: center;
}

.color-picker-wrap .palette-toggle-btn {
  display: flex;
  align-items: center;
  gap: 4px;
  padding: 4px 8px;
  border: 1px solid var(--border-subtle);
  border-radius: 5px;
  background: #0d0d0d;
  cursor: pointer;
  transition: all 0.15s;
}

.color-picker-wrap .palette-toggle-btn:hover {
  background: #151515;
  border-color: #555;
}

.color-picker-wrap .palette-label {
  font-size: 10px;
  color: #888;
  white-space: nowrap;
}

.recent-colors {
  display: flex;
  gap: 4px;
}

.recent-color-swatch {
  width: 22px;
  height: 22px;
  border-radius: 4px;
  border: 1.5px solid transparent;
  cursor: pointer;
  padding: 0;
  transition: all 0.15s;
}

.recent-color-swatch:hover {
  transform: scale(1.15);
}

.recent-color-swatch.active {
  border-color: #fff;
}

.color-divider {
  width: 1px;
  height: 18px;
  background: #444;
  flex-shrink: 0;
}

.eyedropper-btn {
  width: 26px;
  height: 26px;
  border: 1px solid var(--border-subtle);
  border-radius: 5px;
  background: #0d0d0d;
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 0;
  transition: all 0.15s;
}

.eyedropper-btn:hover {
  background: var(--bg-tertiary);
  border-color: #555;
}

.color-input-hidden {
  position: absolute;
  width: 0;
  height: 0;
  padding: 0;
  border: none;
  opacity: 0;
  pointer-events: none;
}



.color-palettes {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 6px;
  padding: 8px 4px 2px;
}

.palette-card {
  display: flex;
  flex-direction: column;
  gap: 6px;
  padding: 10px;
  border: 1.5px solid var(--border-subtle);
  border-radius: 8px;
  background: #0d0d0d;
  transition: all 0.15s;
}

.palette-card:hover {
  background: #151515;
  border-color: #666;
}

.palette-card.active {
  border-color: #3B82F6;
  background: #3B82F610;
}

.palette-swatch-btn {
  width: 22px;
  height: 22px;
  border-radius: 4px;
  border: 1.5px solid transparent;
  cursor: pointer;
  padding: 0;
  transition: all 0.15s;
}

.palette-swatch-btn:hover {
  transform: scale(1.2);
}

.palette-swatch-btn.active {
  border-color: #fff;
}

.palette-card-label {
  font-size: 10px;
  font-weight: 500;
  color: #ccc;
  text-align: center;
  text-transform: none;
  letter-spacing: 0.3px;
}

.palette-card-colors {
  display: flex;
  gap: 4px;
  justify-content: center;
}

.palette-swatch {
  width: 22px;
  height: 22px;
  border-radius: 4px;
}

.icon-toggle-row {
  display: flex;
  align-items: center;
  gap: 8px;
}

.icon-toggle-btn {
  display: flex;
  align-items: center;
  gap: 4px;
  padding: 4px 8px;
  border: 1px solid var(--border-subtle);
  border-radius: 5px;
  background: #0d0d0d;
  cursor: pointer;
  transition: all 0.15s;
}

.icon-toggle-btn:hover {
  background: #151515;
  border-color: #555;
}

.icon-preview {
  width: 18px;
  height: 18px;
  object-fit: contain;
}

.icon-preview.none {
  font-size: 14px;
  line-height: 18px;
  text-align: center;
  color: #888;
}

.toggle-arrow {
  transition: transform 0.2s;
}

.toggle-arrow.open {
  transform: rotate(180deg);
}

.icon-filename {
  font-size: 10px;
  color: #888;
  max-width: 180px;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.icon-selector {
  display: flex;
  flex-wrap: wrap;
  gap: 4px;
  max-height: 120px;
  overflow-y: auto;
  padding: 4px;
  margin-top: 4px;
}

.icon-selector::-webkit-scrollbar {
  width: 6px;
}

.icon-selector::-webkit-scrollbar-track {
  background: var(--bg-tertiary);
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
  width: 28px;
  height: 28px;
  border: 1px solid var(--border-subtle);
  border-radius: 4px;
  background: #0d0d0d;
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 5px;
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
  padding: 8px;
  background: #3B82F6;
  border: none;
  border-radius: 6px;
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
  background: var(--border-subtle);
  cursor: not-allowed;
}
</style>
