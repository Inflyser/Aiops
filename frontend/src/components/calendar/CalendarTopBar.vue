<template>
  <div class="top-bar">

    <img src="@/assets/logo.svg" alt="Logo" class="logo" />
    <div class="time-display">{{ currentTime }}</div>
    <div class="menu-wrapper">
      <ThreeDotsMenu />
    </div>
    <div class="header-controls">

      <!-- Кнопка Tags -->
      <button
        class="tags-toggle-btn header-toggle"
        :class="{ active: showTagsPanel }"
        @click="$emit('toggle-tags')"
        title="Теги"
      >
        <img src="@/assets/icon-tags.svg" style="width: 20px; height: 20px;"/>
      </button>
      <!-- Кнопка Inbox -->
      <button
        v-if="currentView === 'week' || currentView === 'day'"
        class="inbox-toggle-btn header-toggle"
        :class="{ active: showInboxPanel }"
        @click="$emit('toggle-inbox')"
        title="Открыть Inbox"
      >
        <img src="@/assets/inbox.svg" style="width: 20px; height: 20px;"/>
      </button>
      <!-- Кнопка Важные -->
      <button
        v-if="currentView === 'week' || currentView === 'day'"
        class="important-toggle-btn header-toggle"
        :class="{ active: showImportantPanel }"
        @click="$emit('toggle-important')"
        title="Важные события"
      >
        <span class="toggle-icon important-icon">★</span>
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
  currentView: string
  showTagsPanel: boolean
  showInboxPanel: boolean
  showImportantPanel: boolean
}>()

defineEmits<{
  (e: 'toggle-tags'): void
  (e: 'toggle-inbox'): void
  (e: 'toggle-important'): void
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

.logo {
  width: 24px;
  height: 24px;
  object-fit: contain;
}

.time-display {
  font-size: 18px;
  color: #ffffff;
  font-weight: 500;
  margin-left: 12px;
  display: flex;
  align-items: center;
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
  margin-left: 8px;
}

.settings-btn:hover {
  opacity: 1;
}

.settings-btn img {
  width: 20px;
  height: 20px;
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

.header-toggle {
  border: 1px solid rgba(255, 255, 255, 0.15);
  width: 36px;
  height: 36px;
  border-radius: 50%;
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: center;
  transition: all 0.25s;
  margin-left: 8px;
  flex-shrink: 0;
  backdrop-filter: blur(8px);
  -webkit-backdrop-filter: blur(8px);
}

.tags-toggle-btn {
  background: rgba(200, 200, 200, 0.12);
  color: #ccc;
  font-size: 11px;
}

.tags-toggle-btn:hover {
  background: rgba(200, 200, 200, 0.22);
  border-color: rgba(255, 255, 255, 0.3);
}

.tags-toggle-btn.active {
  background: rgba(200, 200, 200, 0.25);
  border-color: rgba(200, 200, 200, 0.4);
  color: #eee;
}

.inbox-toggle-btn {
  background: rgba(200, 200, 200, 0.12);
  color: #ccc;
  font-size: 11px;
}

.inbox-toggle-btn:hover {
  background: rgba(200, 200, 200, 0.22);
  border-color: rgba(255, 255, 255, 0.3);
}

.inbox-toggle-btn.active {
  background: rgba(200, 200, 200, 0.25);
  border-color: rgba(200, 200, 200, 0.4);
  color: #eee;
}

.important-toggle-btn {
  background: rgba(200, 200, 200, 0.12);
  color: #ccc;
  font-size: 11px;
}

.important-toggle-btn:hover {
  background: rgba(200, 200, 200, 0.22);
  border-color: rgba(255, 255, 255, 0.3);
}

.important-toggle-btn.active {
  background: rgba(200, 200, 200, 0.25);
  border-color: rgba(200, 200, 200, 0.4);
  color: #eee;
}

.toggle-icon {
  font-size: 13px;
}

.important-icon {
  font-size: 18px;
}

</style>
