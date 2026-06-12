<template>
  <div v-if="show" class="modal-overlay" @click.self="$emit('close')">
    <div class="settings-modal">
      <div class="settings-sidebar">
        <div class="sidebar-header">
          <h2>Настройки</h2>
        </div>
        <nav class="sidebar-nav">
          <button
            v-for="tab in tabs"
            :key="tab.id"
            class="nav-btn"
            :class="{ active: activeTab === tab.id }"
            @click="activeTab = tab.id"
          >
            <span class="nav-icon">{{ tab.icon }}</span>

            <span class="nav-label">{{ tab.label }}</span>
          </button>
        </nav>
        <div class="sidebar-footer">
          <button class="close-btn" @click="$emit('close')">
            <span class="nav-icon">✕</span>
            <span class="nav-label">Закрыть</span>
          </button>
        </div>
      </div>

      <div class="settings-content">
        <!-- ==================== Внешний вид ==================== -->
        <div v-if="activeTab === 'appearance'" class="tab-content">
          <h3 class="tab-title">Внешний вид</h3>

          <div class="setting-card">
            <div class="setting-row">
              <div class="setting-info">
                <span class="setting-label">Тема оформления</span>
                <span class="setting-hint">Тёмная или светлая тема</span>
              </div>
              <div class="theme-selector">
                <button class="theme-btn" :class="{ active: selectedTheme === 'dark' }" @click="selectedTheme = 'dark'">
                  <span class="theme-icon">◐</span>
                  <span>Тёмная</span>
                </button>
                <button class="theme-btn" :class="{ active: selectedTheme === 'light' }" @click="selectedTheme = 'light'">
                  <span class="theme-icon">○</span>
                  <span>Светлая</span>
                </button>
              </div>
            </div>
          </div>

          <div class="setting-card">
            <div class="setting-row">
              <div class="setting-info">
                <span class="setting-label">Акцент событий</span>
                <span class="setting-hint">Нейтральный фон + цветная полоска и иконка</span>
              </div>
              <label class="toggle-switch">
                <input type="checkbox" :checked="eventAccentMode" @change="$emit('update:eventAccentMode', ($event.target as HTMLInputElement).checked)" />
                <span class="toggle-slider"></span>
              </label>
            </div>
          </div>

          <div class="setting-card">
            <div class="setting-section-title">Фон календаря</div>
            <div class="current-background" v-if="localBackgroundUrl">
              <img :src="localBackgroundUrl" class="preview-img" />
            </div>
            <div class="upload-section">
              <label class="upload-label">
                <input type="file" accept="image/*" @change="handleBackgroundUpload" class="file-input" />
                <span>Загрузить картинку</span>
              </label>
            </div>
            <div class="opacity-section" v-if="localBackgroundUrl">
              <div class="opacity-header">
                <span>Прозрачность</span>
                <span class="opacity-value">{{ Math.round(localBackgroundOpacity * 100) }}%</span>
              </div>
              <input
                type="range" min="0.1" max="1" step="0.1"
                v-model.number="localBackgroundOpacity"
                @input="updateBackgroundOpacity"
                class="opacity-slider"
              />
            </div>
            <button v-if="localBackgroundUrl" class="remove-bg-btn" @click="removeBackground">
              Убрать фон
            </button>
          </div>
        </div>

        <!-- ==================== Календарь ==================== -->
        <div v-if="activeTab === 'calendar'" class="tab-content">
          <h3 class="tab-title">Календарь</h3>

          <div class="setting-card">
            <div class="setting-row" style="margin-bottom: 12px;">
              <div class="setting-info">
                <span class="setting-label">{{ props.sleepMode ? 'Режим сна' : 'Дневной интервал по умолчанию' }}</span>
                <span class="setting-hint">{{ props.sleepMode ? 'Скрываемый временной промежуток (время сна)' : 'Отображаемый временной промежуток в дневном и недельном виде' }}</span>
              </div>
              <label class="toggle-switch">
                <input type="checkbox" :checked="props.sleepMode" @change="emit('update:sleepMode', ($event.target as HTMLInputElement).checked)" />
                <span class="toggle-slider"></span>
              </label>
            </div>
            <div class="time-range-display">
              <span class="time-label">{{ formatTime(props.sleepMode ? props.sleepStartHour : props.dayStartHour) }}</span>
              <span class="time-separator">—</span>
              <span class="time-label">{{ formatTime(props.sleepMode ? props.sleepEndHour : props.dayEndHour) }}</span>
            </div>
            <div class="range-slider-wrapper">
              <div class="range-track">
                <div
                  class="range-fill"
                  :style="{
                    left: ((props.sleepMode ? props.sleepStartHour : props.dayStartHour) / 24) * 100 + '%',
                    width: (((props.sleepMode ? props.sleepEndHour : props.dayEndHour) - (props.sleepMode ? props.sleepStartHour : props.dayStartHour)) / 24) * 100 + '%'
                  }"
                ></div>
              </div>
              <input
                type="range" min="0" max="24" step="1"
                :value="props.sleepMode ? props.sleepStartHour : props.dayStartHour"
                @input="props.sleepMode
                  ? emit('update:sleepStartHour', parseFloat(($event.target as HTMLInputElement).value))
                  : emit('update:dayStartHour', parseFloat(($event.target as HTMLInputElement).value))"
                class="range-input range-start"
              />
              <input
                type="range" min="0" max="24" step="1"
                :value="props.sleepMode ? props.sleepEndHour : props.dayEndHour"
                @input="props.sleepMode
                  ? emit('update:sleepEndHour', parseFloat(($event.target as HTMLInputElement).value))
                  : emit('update:dayEndHour', parseFloat(($event.target as HTMLInputElement).value))"
                class="range-input range-end"
              />
            </div>
            <div class="range-labels">
              <span>00:00</span>
              <span>06:00</span>
              <span>12:00</span>
              <span>18:00</span>
              <span>24:00</span>
            </div>
          </div>
        </div>

        <!-- ==================== Уведомления ==================== -->
        <div v-if="activeTab === 'notifications'" class="tab-content">
          <h3 class="tab-title">Уведомления</h3>

          <div class="setting-card">
            <div class="setting-row">
              <div class="setting-info">
                <span class="setting-label">Звук</span>
                <span class="setting-hint">Воспроизводить звук при напоминаниях</span>
              </div>
              <label class="toggle-switch">
                <input type="checkbox" v-model="soundEnabled" />
                <span class="toggle-slider"></span>
              </label>
            </div>
          </div>

          <div class="setting-card">
            <div class="setting-row">
              <div class="setting-info">
                <span class="setting-label">Уведомления</span>
                <span class="setting-hint">Показывать уведомления о событиях</span>
              </div>
              <label class="toggle-switch">
                <input type="checkbox" v-model="notificationsEnabled" />
                <span class="toggle-slider"></span>
              </label>
            </div>
          </div>
        </div>

        <!-- ==================== Интеграции ==================== -->
        <div v-if="activeTab === 'integrations'" class="tab-content">
          <h3 class="tab-title">Интеграции</h3>

          <div class="setting-card">
            <div class="setting-row">
              <div class="setting-info">
                <span class="setting-label">Telegram</span>
                <span class="setting-hint">Привяжите Telegram для получения уведомлений</span>
              </div>
              <button class="connect-btn" @click="connecting = !connecting">
                {{ connecting ? 'Подключено' : 'Подключить' }}
              </button>
            </div>
            <div v-if="connecting" class="integration-hint">
              <span>Telegram интегрирован (демо-режим)</span>
            </div>
          </div>

          <div class="setting-card">
            <div class="setting-row">
              <div class="setting-info">
                <span class="setting-label">Язык</span>
                <span class="setting-hint">Язык интерфейса</span>
              </div>
              <select class="language-select" v-model="selectedLanguage">
                <option value="ru">Русский</option>
                <option value="en">English</option>
              </select>
            </div>
          </div>
        </div>

        <!-- ==================== О программе ==================== -->
        <div v-if="activeTab === 'about'" class="tab-content">
          <h3 class="tab-title">О программе</h3>

          <div class="setting-card about-card">
            <div class="about-info">
              <div class="app-name">Personal Flow</div>
              <div class="app-version">MVP v1.3</div>
              <p class="app-desc">
                Персональный органайзер с Канбан-доской, календарём и аналитикой.
              </p>
            </div>
          </div>

          <div class="setting-card">
            <div class="setting-row">
              <div class="setting-info">
                <span class="setting-label">Поддержать автора</span>
                <span class="setting-hint">Если проект вам полезен, поддержите разработку</span>
              </div>
              <button class="support-btn" @click="supportClicked = !supportClicked">
                Поддержать
              </button>
            </div>
            <div v-if="supportClicked" class="support-message">
              Спасибо за поддержку! (демо-режим)
            </div>
          </div>
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
  dayStartHour: number
  dayEndHour: number
  sleepMode: boolean
  sleepStartHour: number
  sleepEndHour: number
}>()

const emit = defineEmits<{
  (e: 'close'): void
  (e: 'update:eventAccentMode', value: boolean): void
  (e: 'update:dayStartHour', value: number): void
  (e: 'update:dayEndHour', value: number): void
  (e: 'update:sleepMode', value: boolean): void
  (e: 'update:sleepStartHour', value: number): void
  (e: 'update:sleepEndHour', value: number): void
  (e: 'background-changed', data: { url: string; opacity: number }): void
  (e: 'background-removed'): void
}>()

const tabs = [
  { id: 'appearance', label: 'Внешний вид', icon: '*' },
  { id: 'calendar', label: 'Календарь', icon: '▦' },
  { id: 'notifications', label: 'Уведомления', icon: '♪' },
  { id: 'integrations', label: 'Интеграции', icon: '⇌' },
  { id: 'about', label: 'О программе', icon: 'ⓘ' },
]

const activeTab = ref('appearance')
const selectedTheme = ref('dark')
const soundEnabled = ref(true)
const notificationsEnabled = ref(true)
const connecting = ref(false)
const selectedLanguage = ref('ru')
const supportClicked = ref(false)

const formatTime = (hour: number) => {
  const h = Math.floor(hour)
  const m = (hour % 1) * 60
  return `${String(h).padStart(2, '0')}:${String(m).padStart(2, '0')}`
}

const localBackgroundUrl = ref<string | null>(null)
const localBackgroundOpacity = ref(0.5)

watch(() => props.show, (val) => {
  if (val) {
    activeTab.value = 'appearance'
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
  background-color: rgba(0, 0, 0, 0.85);
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
  display: flex;
  width: 95vw;
  height: 90vh;
  background-color: #121212;
  border: 1px solid #2a2a2a;
  border-radius: 25px;
  animation: scaleIn 0.3s cubic-bezier(0.16, 1, 0.3, 1);
  overflow: hidden;
}

@keyframes scaleIn {
  from {
    opacity: 0;
    transform: scale(0.92);
  }
  to {
    opacity: 1;
    transform: scale(1);
  }
}

/* ===== Sidebar ===== */
.settings-sidebar {
  width: 220px;
  flex-shrink: 0;
  display: flex;
  flex-direction: column;
  border-right: 1px solid #2a2a2a;
  padding: 20px 0;
}

.sidebar-header {
  padding: 0 20px 20px;
  border-bottom: 1px solid #2a2a2a;
}

.sidebar-header h2 {
  margin: 0;
  font-size: 20px;
  color: #fff;
  font-weight: 700;
}

.sidebar-nav {
  flex: 1;
  display: flex;
  flex-direction: column;
  padding: 12px 8px;
  gap: 2px;
  overflow-y: auto;
}

.nav-btn {
  display: flex;
  align-items: center;
  gap: 10px;
  padding: 10px 14px;
  background: transparent;
  border: none;
  color: #888;
  font-size: 14px;
  cursor: pointer;
  border-radius: 10px;
  transition: all 0.2s;
  text-align: left;
  width: 100%;
}

.nav-btn:hover {
  background: #1e1e1e;
  color: #ccc;
}

.nav-btn.active {
  background: #2a2a2a;
  color: #fff;
}

.nav-icon {
  font-size: 16px;
  width: 24px;
  text-align: center;
  flex-shrink: 0;
}

.nav-label {
  font-weight: 500;
}

.sidebar-footer {
  padding: 12px 8px 0;
  border-top: 1px solid #2a2a2a;
  margin: 0 8px;
}

.sidebar-footer .close-btn {
  display: flex;
  align-items: center;
  gap: 10px;
  padding: 10px 14px;
  background: transparent;
  border: none;
  color: #888;
  font-size: 14px;
  cursor: pointer;
  border-radius: 10px;
  transition: all 0.2s;
  text-align: left;
  width: 100%;
}

.sidebar-footer .close-btn:hover {
  background: #2a2a2a;
  color: #fff;
}

/* ===== Content ===== */
.settings-content {
  flex: 1;
  padding: 32px 40px;
  overflow-y: auto;
  min-width: 0;
}

.tab-content {
  max-width: 640px;
}

.tab-title {
  font-size: 24px;
  color: #fff;
  margin: 0 0 24px;
  font-weight: 700;
}

/* ===== Setting Cards ===== */
.setting-card {
  background: #1a1a1a;
  border: 1px solid #2a2a2a;
  border-radius: 16px;
  padding: 20px;
  margin-bottom: 12px;
}

.setting-row {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 16px;
}

.setting-info {
  display: flex;
  flex-direction: column;
  gap: 4px;
}

.setting-label {
  font-size: 15px;
  color: #fff;
  font-weight: 500;
}

.setting-hint {
  font-size: 12px;
  color: #666;
}

.setting-section-title {
  font-size: 11px;
  color: #888;
  font-weight: 600;
  text-transform: uppercase;
  letter-spacing: 0.5px;
  margin-bottom: 12px;
}

/* ===== Toggle ===== */
.toggle-switch {
  position: relative;
  width: 44px;
  height: 24px;
  flex-shrink: 0;
}

.toggle-switch input {
  display: none;
}

.toggle-slider {
  position: absolute;
  top: 0; left: 0; right: 0; bottom: 0;
  background: #333;
  border-radius: 12px;
  cursor: pointer;
  transition: background 0.2s;
}

.toggle-slider::before {
  content: '';
  position: absolute;
  top: 2px; left: 2px;
  width: 20px;
  height: 20px;
  background: #888;
  border-radius: 50%;
  transition: all 0.2s;
}

.toggle-switch input:checked + .toggle-slider {
  background: #8b5cf6;
}

.toggle-switch input:checked + .toggle-slider::before {
  background: #fff;
  transform: translateX(20px);
}

/* ===== Theme Selector ===== */
.theme-selector {
  display: flex;
  gap: 8px;
  flex-shrink: 0;
}

.theme-btn {
  display: flex;
  align-items: center;
  gap: 6px;
  padding: 8px 16px;
  background: #2a2a2a;
  border: 1px solid transparent;
  border-radius: 10px;
  color: #888;
  font-size: 13px;
  cursor: pointer;
  transition: all 0.2s;
}

.theme-btn:hover {
  background: #333;
  color: #ccc;
}

.theme-btn.active {
  background: #2a2a2a;
  border-color: #8b5cf6;
  color: #fff;
}

.theme-icon {
  font-size: 16px;
}

/* ===== Background ===== */
.current-background {
  margin-bottom: 12px;
}

.preview-img {
  max-width: 100%;
  max-height: 120px;
  border-radius: 10px;
  border: 1px solid #333;
  display: block;
}

.upload-label {
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 14px;
  background: #2a2a2a;
  border: 1px dashed #444;
  border-radius: 12px;
  cursor: pointer;
  color: #aaa;
  font-size: 13px;
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
  margin-top: 12px;
}

.opacity-header {
  display: flex;
  justify-content: space-between;
  color: #888;
  font-size: 12px;
  margin-bottom: 8px;
}

.opacity-value {
  color: #aaa;
}

.opacity-slider {
  width: 100%;
  height: 6px;
  background: #333;
  border-radius: 3px;
  outline: none;
  cursor: pointer;
  -webkit-appearance: none;
  appearance: none;
}

.opacity-slider::-webkit-slider-thumb {
  -webkit-appearance: none;
  width: 18px;
  height: 18px;
  background: #8b5cf6;
  border-radius: 50%;
  cursor: pointer;
  border: 2px solid #1a1a1a;
}

.remove-bg-btn {
  width: 100%;
  padding: 12px;
  margin-top: 12px;
  background: #2a2a2a;
  border: none;
  border-radius: 10px;
  color: #e74c3c;
  font-size: 13px;
  cursor: pointer;
  transition: background 0.2s;
}

.remove-bg-btn:hover {
  background: #333;
}

/* ===== Time Range Slider ===== */
.time-range-display {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 12px;
  margin-bottom: 16px;
}

.time-label {
  font-size: 28px;
  font-weight: 700;
  color: #fff;
  letter-spacing: 1px;
}

.time-separator {
  font-size: 24px;
  color: #555;
}

.range-slider-wrapper {
  position: relative;
  height: 40px;
  margin: 0 4px;
}

.range-track {
  position: absolute;
  top: 50%;
  left: 0;
  right: 0;
  height: 4px;
  background: #333;
  border-radius: 2px;
  transform: translateY(-50%);
  pointer-events: none;
}

.range-fill {
  position: absolute;
  top: 0;
  height: 100%;
  background: #8b5cf6;
  border-radius: 2px;
  pointer-events: none;
}

.range-input {
  position: absolute;
  top: 0;
  width: 100%;
  height: 100%;
  -webkit-appearance: none;
  appearance: none;
  background: transparent;
  pointer-events: none;
  outline: none;
  margin: 0;
}

.range-input::-webkit-slider-thumb {
  -webkit-appearance: none;
  width: 22px;
  height: 22px;
  background: #8b5cf6;
  border-radius: 50%;
  cursor: pointer;
  pointer-events: auto;
  border: 3px solid #1a1a1a;
  box-shadow: 0 0 0 1px rgba(139, 92, 246, 0.3);
  transition: transform 0.15s;
}

.range-input::-webkit-slider-thumb:hover {
  transform: scale(1.15);
}

.range-start {
  z-index: 2;
}

.range-end {
  z-index: 3;
}

.range-labels {
  display: flex;
  justify-content: space-between;
  margin-top: 8px;
  font-size: 11px;
  color: #555;
  padding: 0 2px;
}

/* ===== Integration ===== */
.connect-btn {
  padding: 8px 20px;
  background: #2a2a2a;
  border: 1px solid #444;
  border-radius: 10px;
  color: #ccc;
  font-size: 13px;
  cursor: pointer;
  transition: all 0.2s;
  flex-shrink: 0;
}

.connect-btn:hover {
  background: #333;
  border-color: #8b5cf6;
  color: #fff;
}

.integration-hint {
  margin-top: 12px;
  padding: 10px 14px;
  background: rgba(139, 92, 246, 0.1);
  border: 1px solid rgba(139, 92, 246, 0.2);
  border-radius: 10px;
  color: #8b5cf6;
  font-size: 12px;
}

/* ===== Language ===== */
.language-select {
  padding: 8px 16px;
  background: #2a2a2a;
  border: 1px solid #444;
  border-radius: 10px;
  color: #ccc;
  font-size: 13px;
  cursor: pointer;
  outline: none;
  transition: all 0.2s;
  min-width: 140px;
}

.language-select:hover {
  border-color: #666;
}

.language-select:focus {
  border-color: #8b5cf6;
}

/* ===== About ===== */
.about-card {
  text-align: center;
  padding: 32px;
}

.about-info {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 8px;
}

.app-name {
  font-size: 28px;
  font-weight: 700;
  color: #fff;
}

.app-version {
  font-size: 14px;
  color: #888;
}

.app-desc {
  font-size: 13px;
  color: #666;
  margin: 8px 0 0;
  max-width: 360px;
  line-height: 1.5;
}

.support-btn {
  padding: 8px 20px;
  background: linear-gradient(135deg, #8b5cf6, #6d28d9);
  border: none;
  border-radius: 10px;
  color: #fff;
  font-size: 13px;
  font-weight: 600;
  cursor: pointer;
  transition: opacity 0.2s;
  flex-shrink: 0;
}

.support-btn:hover {
  opacity: 0.9;
}

.support-message {
  margin-top: 12px;
  padding: 10px 14px;
  background: rgba(34, 197, 94, 0.1);
  border: 1px solid rgba(34, 197, 94, 0.2);
  border-radius: 10px;
  color: #22c55e;
  font-size: 12px;
  text-align: center;
}
</style>
