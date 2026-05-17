<template>
  <div class="top-bar">

    <div class="time-display">{{ currentTime }}</div>
    <div class="menu-wrapper">
      <ThreeDotsMenu />
    </div>
    <div class="header-controls">
      <!-- Кнопка переключения 0-24 / 7-24 для недельного и дневного вида -->
      <button
        v-if="currentView === 'week' || currentView === 'day'"
        class="compact-toggle-btn header-toggle"
        :class="{ active: compactMode }"
        @click="$emit('toggle-compact', !compactMode)"
        :title="compactMode ? 'Показать полный день (0:00–23:00)' : 'Рабочий день (7:00–23:00)'"
      >
        <span class="toggle-icon">{{ compactMode ? '☀' : '◑' }}</span>
        <span class="toggle-label">{{ compactMode ? '7–24' : '0–24' }}</span>
      </button>
      <!-- Кнопка Tags -->
      <button
        class="tags-toggle-btn header-toggle"
        :class="{ active: showTagsPanel }"
        @click="$emit('toggle-tags')"
        title="Теги"
      >
        <img src="@/assets/icon-tags.svg" style="width: 20px; height: 20px;"/>
        <span class="toggle-label">Tags</span>
      </button>
      <!-- Кнопка Inbox -->
      <button
        v-if="currentView === 'week'"
        class="inbox-toggle-btn header-toggle"
        :class="{ active: showInboxPanel }"
        @click="$emit('toggle-inbox')"
        title="Открыть Inbox"
      >
        <span class="toggle-icon">📥</span>
        <span class="toggle-label">Inbox</span>
      </button>
      <!-- Кнопка настроек -->
      <button class="settings-btn" @click="$emit('open-settings')" title="Настройки">
        <img src="@/assets/icon-settings_alert.svg" alt="Настройки" />
      </button>
    </div>
  </div>
</template>

<script setup lang="ts">
import { onMounted, onUnmounted, ref } from 'vue'
import dayjs from 'dayjs'
import 'dayjs/locale/ru'
import ThreeDotsMenu from '../ui/ThreeDotsMenu.vue'

dayjs.locale('ru')

defineProps<{
  compactMode: boolean
  currentView: string
  showTagsPanel: boolean
  showInboxPanel: boolean
}>()

defineEmits<{
  (e: 'toggle-compact', value: boolean): void
  (e: 'toggle-tags'): void
  (e: 'toggle-inbox'): void
  (e: 'open-settings'): void
}>()

const currentTime = ref('')

const updateTime = () => {
  currentTime.value = dayjs().format('HH:mm DD MMMM')
}

let timeInterval: ReturnType<typeof setInterval>

onMounted(() => {
  updateTime()
  timeInterval = setInterval(updateTime, 1000)
})

onUnmounted(() => {
  if (timeInterval) {
    clearInterval(timeInterval)
  }
})
</script>

<style scoped>
.top-bar {
  margin-top: 5px;
  display: flex;
  align-items: center;
  padding: 10px 20px;
  flex-shrink: 0;
  position: relative;
  z-index: 100;
}

.time-display {
  font-size: 22px;
  color: #ffffff;
  font-weight: 500;
  margin-left: 12px;
}

.settings-btn {
  background: none;
  border: none;
  cursor: pointer;
  padding: 4px;
  display: flex;
  align-items: center;
  justify-content: center;
  transition: opacity 0.2s;
}

.settings-btn:hover {
  opacity: 1;
}

.settings-btn img {
  width: 24px;
  height: 24px;
}

.menu-wrapper {
  position: absolute;
  left: 50%;
  transform: translateX(-50%);
  display: flex;
  align-items: center;
  justify-content: center;
}

.header-controls {
  display: flex;
  align-items: center;
  margin-left: auto;
}

.compact-toggle-btn {
  background: #333;
  border: none;
  border-radius: 8px;
  padding: 8px 12px;
  cursor: pointer;
  display: flex;
  align-items: center;
  gap: 6px;
  color: #aaa;
  font-size: 14px;
  transition: all 0.2s;
}

.compact-toggle-btn:hover {
  background: #444;
}

.compact-toggle-btn.active {
  background: #4a5568;
  color: #fff;
}

.tags-toggle-btn {
  background: #333;
  border: none;
  border-radius: 8px;
  padding: 8px 12px;
  cursor: pointer;
  display: flex;
  align-items: center;
  gap: 6px;
  color: #aaa;
  font-size: 14px;
  transition: all 0.2s;
  margin-left: 8px;
}

.tags-toggle-btn:hover {
  background: #444;
}

.tags-toggle-btn.active {
  background: #4a5568;
  color: #fff;
}

.inbox-toggle-btn {
  background: #333;
  border: none;
  border-radius: 8px;
  padding: 8px 12px;
  cursor: pointer;
  display: flex;
  align-items: center;
  gap: 6px;
  color: #aaa;
  font-size: 14px;
  transition: all 0.2s;
  margin-left: 8px;
}

.inbox-toggle-btn:hover {
  background: #444;
}

.inbox-toggle-btn.active {
  background: #4A90E2;
  border-color: #4A90E2;
  color: #fff;
}

.toggle-icon {
  font-size: 16px;
}

.toggle-label {
  font-weight: 500;
}
</style>
