<template>
  <div class="planning-page">
    <!-- Top Bar -->
    <div class="top-bar">
      <div class="time-display">{{ currentTime }}</div>
      <div class="menu-wrapper">
        <ThreeDotsMenu />
      </div>
      <button class="nav-btn"> </button>
    </div>

    <!-- Page Header -->
    <div class="page-header">
      <h1 class="page-title">Планирование</h1>
    </div>

    <!-- Timer Section -->
    <div class="timer-section">
      <div class="timer-display">
        {{ formattedTime }}
      </div>
      <div class="timer-controls">
        <button class="timer-btn" @click="toggleTimer">
          {{ isRunning ? 'Пауза' : 'Старт' }}
        </button>
        <button class="timer-btn reset" @click="resetTimer">
          Сброс
        </button>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted, onUnmounted } from 'vue'
import dayjs from 'dayjs'
import 'dayjs/locale/ru'
import ThreeDotsMenu from '../components/ui/ThreeDotsMenu.vue'

dayjs.locale('ru')

const currentTime = ref('')
const updateTime = () => {
  currentTime.value = dayjs().format('HH:mm DD MMMM')
}

// Timer state
const timerSeconds = ref(0)
const isRunning = ref(false)
let timerInterval: ReturnType<typeof setInterval> | null = null

const formattedTime = computed(() => {
  const hours = Math.floor(timerSeconds.value / 3600)
  const minutes = Math.floor((timerSeconds.value % 3600) / 60)
  const seconds = timerSeconds.value % 60
  return `${hours.toString().padStart(2, '0')}:${minutes.toString().padStart(2, '0')}:${seconds.toString().padStart(2, '0')}`
})

const toggleTimer = () => {
  if (isRunning.value) {
    // Pause
    if (timerInterval) {
      clearInterval(timerInterval)
      timerInterval = null
    }
    isRunning.value = false
  } else {
    // Start
    timerInterval = setInterval(() => {
      timerSeconds.value++
    }, 1000)
    isRunning.value = true
  }
}

const resetTimer = () => {
  if (timerInterval) {
    clearInterval(timerInterval)
    timerInterval = null
  }
  isRunning.value = false
  timerSeconds.value = 0
}

let timeInterval: ReturnType<typeof setInterval>

onMounted(() => {
  updateTime()
  timeInterval = setInterval(updateTime, 1000)
})

onUnmounted(() => {
  clearInterval(timeInterval)
  if (timerInterval) {
    clearInterval(timerInterval)
  }
})
</script>

<style scoped>
.planning-page {
  width: 100%;
  min-height: 100vh;
  background-color: #050505;
  color: #ffffff;
  overflow: hidden;
}

/* Top Bar */
.top-bar {
  margin-top: 5px;
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 10px 20px;
}

.menu-wrapper {
  display: flex;
  align-items: center;
  justify-content: center;
}

.nav-btn {
  background: transparent;
  border: none;
  color: #ffffff;
  font-size: 18px;
  cursor: pointer;
  padding: 5px 10px;
}

.time-display {
  font-size: 22px;
  color: #ffffff;
  font-weight: 500;
}

/* Page Header */
.page-header {
  padding: 20px 28px 0;
  display: flex;
  align-items: baseline;
  gap: 20px;
  border-bottom: 1px solid #80808021;
  padding-bottom: 18px;
}

.page-title {
  font-size: 52px;
  font-weight: bold;
  margin: 0;
  line-height: 1;
}

/* Timer Section */
.timer-section {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding-top: 100px;
  gap: 30px;
}

.timer-display {
  font-size: 80px;
  font-weight: bold;
  font-family: monospace;
  color: #ffffff;
}

.timer-controls {
  display: flex;
  gap: 20px;
}

.timer-btn {
  background: #1a1a1a;
  color: #fff;
  border: 1px solid #333;
  border-radius: 8px;
  padding: 12px 30px;
  font-size: 18px;
  cursor: pointer;
  transition: background 0.2s;
}

.timer-btn:hover {
  background: #333;
}

.timer-btn.reset {
  background: transparent;
  color: #888;
}

.timer-btn.reset:hover {
  background: #1a1a1a;
  color: #fff;
}
</style>
