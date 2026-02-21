<template>
  <div class="top-bar">
    <div class="time-display">{{ currentTime }}</div>
    <div class="menu-wrapper">
      <ThreeDotsMenu />
    </div>
    <button
      class="compact-toggle-btn header-toggle"
      :class="{ active: compactMode }"
      @click="$emit('toggle-compact', !compactMode)"
      :title="compactMode ? 'Показать полный день (0:00–23:00)' : 'Рабочий день (7:00–23:00)'"
    >
      <span class="toggle-icon">{{ compactMode ? '☀' : '◑' }}</span>
      <span class="toggle-label">{{ compactMode ? '7–24' : '0–24' }}</span>
    </button>
  </div>
</template>

<script setup lang="ts">
import { onMounted, onUnmounted, ref } from 'vue'
import dayjs from 'dayjs'
import 'dayjs/locale/ru'
import ThreeDotsMenu from './ThreeDotsMenu.vue'

dayjs.locale('ru')

defineProps<{
  compactMode: boolean
}>()

defineEmits<{
  (e: 'toggle-compact', value: boolean): void
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
  justify-content: space-between;
  align-items: center;
  padding: 10px 20px;
  flex-shrink: 0;

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

.toggle-icon {
  font-size: 16px;
}

.toggle-label {
  font-weight: 500;
}

.menu-wrapper {
  display: flex;
  align-items: center;
  justify-content: center;
}

.time-display {
  font-size: 22px;
  color: #ffffff;
  font-weight: 500;
}
</style>
