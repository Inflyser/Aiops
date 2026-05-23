<template>
  <div v-if="show" class="modal-overlay" @click.self="$emit('close')">
    <div class="settings-modal">
      <div class="modal-header">
        <h3>Настройки</h3>
        <button class="close-btn" @click="$emit('close')">&times;</button>
      </div>

      <div class="modal-body">
        <div class="settings-section">
          <div class="settings-row">
            <div class="settings-info">
              <span class="settings-label">Акцент событий</span>
              <span class="settings-hint">Нейтральный фон + цветная полоска и иконка</span>
            </div>
            <label class="toggle-switch">
              <input type="checkbox" :checked="eventAccentMode" @change="$emit('update:eventAccentMode', ($event.target as HTMLInputElement).checked)" />
              <span class="toggle-slider"></span>
            </label>
          </div>
        </div>

        <div class="settings-divider"></div>

        <div class="settings-section">
          <div class="settings-section-title">Фон календаря</div>

          <div class="current-background" v-if="localBackgroundUrl">
            <p>Текущий фон:</p>
            <img :src="localBackgroundUrl" class="preview-img" />
          </div>

          <div class="upload-section">
            <label class="upload-label">
              <input
                type="file"
                accept="image/*"
                @change="handleBackgroundUpload"
                class="file-input"
              />
              <span>Загрузить картинку</span>
            </label>
          </div>

          <div class="opacity-section" v-if="localBackgroundUrl">
            <label>Прозрачность: {{ localBackgroundOpacity }}</label>
            <input
              type="range"
              min="0.1"
              max="1"
              step="0.1"
              v-model.number="localBackgroundOpacity"
              @input="updateBackgroundOpacity"
              class="opacity-slider"
            />
          </div>

          <button
            v-if="localBackgroundUrl"
            class="remove-bg-btn"
            @click="removeBackground"
          >
            Убрать фон
          </button>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, watch } from 'vue'

const props = defineProps<{
  show: boolean
  eventAccentMode: boolean
}>()

const emit = defineEmits<{
  (e: 'close'): void
  (e: 'update:eventAccentMode', value: boolean): void
  (e: 'background-changed', data: { url: string; opacity: number }): void
  (e: 'background-removed'): void
}>()

const localBackgroundUrl = ref<string | null>(null)
const localBackgroundOpacity = ref(0.5)

watch(() => props.show, (val) => {
  if (val) {
    const saved = localStorage.getItem('app-background')
    if (saved) {
      const { url, opacity } = JSON.parse(saved)
      localBackgroundUrl.value = url
      localBackgroundOpacity.value = opacity
    } else {
      localBackgroundUrl.value = null
      localBackgroundOpacity.value = 0.5
    }
  }
})

const saveBackground = () => {
  if (localBackgroundUrl.value) {
    localStorage.setItem('app-background', JSON.stringify({
      url: localBackgroundUrl.value,
      opacity: localBackgroundOpacity.value
    }))
  }
}

const handleBackgroundUpload = (event: Event) => {
  const target = event.target as HTMLInputElement
  const file = target.files?.[0]
  if (file) {
    const reader = new FileReader()
    reader.onload = (e) => {
      const url = e.target?.result as string
      localBackgroundUrl.value = url
      saveBackground()
      emit('background-changed', { url, opacity: localBackgroundOpacity.value })
    }
    reader.readAsDataURL(file)
  }
}

const updateBackgroundOpacity = () => {
  if (localBackgroundUrl.value) {
    saveBackground()
    emit('background-changed', { url: localBackgroundUrl.value, opacity: localBackgroundOpacity.value })
  }
}

const removeBackground = () => {
  localBackgroundUrl.value = null
  localBackgroundOpacity.value = 0.5
  localStorage.removeItem('app-background')
  emit('background-removed')
}
</script>

<style scoped>
.modal-overlay {
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

.settings-modal {
  background-color: #121212;
  border: 1px solid #444;
  border-radius: 25px;
  padding: 20px;
  width: 90%;
  max-width: 400px;
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

.settings-modal .modal-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 20px;
}

.settings-modal .modal-header h3 {
  margin: 0;
  font-size: 16px;
  color: #fff;
}

.settings-modal .close-btn {
  background: none;
  border: none;
  color: #888;
  font-size: 22px;
  cursor: pointer;
  padding: 0;
  line-height: 1;
}

.settings-modal .close-btn:hover {
  color: #fff;
}

.settings-modal .modal-body {
  display: flex;
  flex-direction: column;
  gap: 16px;
}

.settings-section {
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.settings-section-title {
  font-size: 12px;
  color: #888;
  font-weight: 600;
  text-transform: uppercase;
  letter-spacing: 0.5px;
}

.settings-row {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 12px;
}

.settings-info {
  display: flex;
  flex-direction: column;
  gap: 2px;
}

.settings-label {
  font-size: 13px;
  color: #fff;
  font-weight: 500;
}

.settings-hint {
  font-size: 10px;
  color: #888;
}

.settings-divider {
  height: 1px;
  background: #333;
  margin: 4px 0;
}

.toggle-switch {
  position: relative;
  width: 40px;
  height: 22px;
  flex-shrink: 0;
}

.toggle-switch input {
  display: none;
}

.toggle-slider {
  position: absolute;
  top: 0; left: 0; right: 0; bottom: 0;
  background: #333;
  border-radius: 11px;
  cursor: pointer;
  transition: background 0.2s;
}

.toggle-slider::before {
  content: '';
  position: absolute;
  top: 2px; left: 2px;
  width: 18px;
  height: 18px;
  background: #888;
  border-radius: 50%;
  transition: all 0.2s;
}

.toggle-switch input:checked + .toggle-slider {
  background: #8b5cf6;
}

.toggle-switch input:checked + .toggle-slider::before {
  background: #fff;
  transform: translateX(18px);
}

.current-background {
  text-align: center;
}

.current-background p {
  color: #888;
  font-size: 11px;
  margin: 0 0 10px 0;
}

.preview-img {
  max-width: 100%;
  max-height: 150px;
  border-radius: 10px;
  border: 1px solid #444;
}

.upload-label {
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 12px;
  background: #2a2a2a;
  border: 1px dashed #444;
  border-radius: 10px;
  cursor: pointer;
  color: #aaa;
  font-size: 11px;
  transition: all 0.2s;
}

.upload-label:hover {
  background: #333;
  border-color: #666;
  color: #fff;
}

.file-input {
  display: none;
}

.opacity-section {
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.opacity-section label {
  color: #888;
  font-size: 10px;
}

.opacity-slider {
  width: 100%;
  height: 6px;
  background: #333;
  border-radius: 3px;
  outline: none;
  cursor: pointer;
  -webkit-appearance: none;
}

.opacity-slider::-webkit-slider-thumb {
  -webkit-appearance: none;
  width: 16px;
  height: 16px;
  background: #1c3496;
  border-radius: 50%;
  cursor: pointer;
}

.remove-bg-btn {
  padding: 10px;
  background: #333;
  border: none;
  border-radius: 8px;
  color: #fff;
  font-size: 11px;
  cursor: pointer;
  transition: background 0.2s;
}

.remove-bg-btn:hover {
  background: #444;
}
</style>
