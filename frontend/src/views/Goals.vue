<template>
  <div class="goals-page">
    <div class="top-bar">
      <div class="time-display">{{ currentTime }}</div>
      <div class="menu-wrapper">
        <ThreeDotsMenu />
      </div>
    </div>

    <div class="goals-header">
      <h1 class="goals-title">Цели</h1>
    </div>

    <div class="goals-content">
      <div class="placeholder-section">
        <div class="placeholder-icon">
          <img :src="trophyIcon" alt="Goals" class="trophy-svg" />
        </div>
        <p class="placeholder-text">Здесь будут ваши цели</p>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted, onUnmounted } from 'vue'
import dayjs from 'dayjs'
import 'dayjs/locale/ru'
import ThreeDotsMenu from '../components/ui/ThreeDotsMenu.vue'
import trophyIcon from '../assets/icon/trophy_24dp_B1B3B2_FILL0_wght400_GRAD0_opsz24.svg'

dayjs.locale('ru')

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
  if (timeInterval) clearInterval(timeInterval)
})
</script>

<style scoped>
.goals-page {
  padding: 0 20px;
  min-height: 100vh;
  background-color: #050505;
  color: #ffffff;
  overflow-y: auto;
}

.top-bar {
  margin-top: 5px;
  display: flex;
  align-items: center;
  padding: 10px 20px;
  flex-shrink: 0;
  position: relative;
}

.menu-wrapper {
  position: absolute;
  left: 50%;
  transform: translateX(-50%);
  display: flex;
  align-items: center;
  justify-content: center;
}

.time-display {
  font-size: 18px;
  color: #ffffff;
  font-weight: 500;
}

.goals-header {
  padding: 20px;
}

.goals-title {
  font-size: 28px;
  font-weight: 700;
  color: #ffffff;
  margin: 0;
}

.goals-content {
  display: flex;
  justify-content: center;
  align-items: center;
  min-height: 50vh;
}

.placeholder-section {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 20px;
  padding: 40px;
  background: #0f0f0f;
  border-radius: 16px;
  border: 1px dashed #3a3a3a;
}

.placeholder-icon {
  width: 64px;
  height: 64px;
  display: flex;
  align-items: center;
  justify-content: center;
}

.trophy-svg {
  width: 100%;
  height: 100%;
  object-fit: contain;
  filter: brightness(0) invert(1);
  opacity: 0.4;
}

.placeholder-text {
  font-size: 18px;
  color: #888;
  margin: 0;
}
</style>
