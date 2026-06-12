<template>
  <div 
    class="menu-container" 
    @mouseenter="openMenu" 
    @mouseleave="closeMenu"
  >
    <!-- Иконка из SVG вместо трех точек -->
    <div class="dots-icon">
      <img :src="dotsIcon" alt="Menu" class="dots-svg-icon" />
    </div>
    
    <!-- Анимированная панель с иконками -->
    <Transition name="menu">
      <div v-if="isMenuOpen" class="animated-menu">
        <div class="menu-panel">
          <!-- Календарь -->
          <div class="icon-wrapper" @click.stop="navigateToWeeklyCalendar">
            <img :src="calendarIcon" alt="Calendar" class="svg-icon" />
          </div>
          
          <!-- Канбан -->
          <div class="icon-wrapper" @click.stop="navigateToKanban">
            <img :src="kanbanIcon" alt="Kanban" class="svg-icon" />
          </div>
          
          <!-- Статистика -->
          <div class="icon-wrapper" @click.stop="navigateToStatistics">
            <img :src="statsIcon" alt="Statistics" class="svg-icon" />
          </div>

          <!-- Цели -->
          <div class="icon-wrapper" @click.stop="navigateToGoals">
            <img :src="goalsIcon" alt="Goals" class="svg-icon" />
          </div>

          <!-- Лендинг (временная кнопка) -->
          <div class="icon-wrapper" @click.stop="navigateToLanding">
            <img :src="homeIcon" alt="Landing" class="svg-icon" />
          </div>
        </div>
      </div>
    </Transition>
  </div>
</template>

<script setup lang="ts">
import { ref } from 'vue'
import { useRouter } from 'vue-router'

// Импортируем SVG иконки из assets
import calendarIcon from '@/assets/icon-colendar.svg'
import kanbanIcon from '@/assets/icon-kanban.svg'
import statsIcon from '@/assets/icon/finance_24dp_B1B3B2_FILL0_wght400_GRAD0_opsz24.svg'
import goalsIcon from '@/assets/icon/trophy_24dp_B1B3B2_FILL0_wght400_GRAD0_opsz24.svg'
import homeIcon from '@/assets/icon/home_24dp_B1B3B2_FILL0_wght400_GRAD0_opsz24.svg'
import dotsIcon from '@/assets/three-point.svg' // Иконка для трех точек

const isMenuOpen = ref(false)
const router = useRouter()

const openMenu = () => {
  isMenuOpen.value = true
}

const closeMenu = () => {
  isMenuOpen.value = false
}

const navigateToWeeklyCalendar = () => {
  router.push('/calendar')
  isMenuOpen.value = false
}

const navigateToKanban = () => {
  router.push('/kanban')
  isMenuOpen.value = false
}

const navigateToStatistics = () => {
  router.push('/statistics')
  isMenuOpen.value = false
}

const navigateToGoals = () => {
  router.push('/goals')
  isMenuOpen.value = false
}

const navigateToLanding = () => {
  router.push('/')
  isMenuOpen.value = false
}
</script>

<style scoped>
.menu-container {
  position: relative;
  cursor: pointer;
  width: 24px;
  height: 24px;
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 1000;
}

.dots-icon {
  display: flex;
  align-items: center;
  justify-content: center;
  width: 100px;
  height: 100px;
  transition: transform 0.3s ease;
}

.dots-icon:hover {
  transform: scale(1.3);
}

.dots-svg-icon {
  width: 100%;
  height: 100%;
  object-fit: contain;
  filter: brightness(0) invert(1);
}

.animated-menu {
  position: absolute;
  top: 0px;
  right: -70px;
  z-index: 1000;
}

.menu-panel {
  display: flex;
  flex-direction: row;
  background-color: var(--bg-secondary);
  border-radius: 10px;
  padding: 10px;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.3);
  backdrop-filter: blur(10px);
  min-width: 80px;
}

.menu-enter-active,
.menu-leave-active {
  transition: all 0.3s ease;
}

.menu-enter-from {
  opacity: 0;
  transform: translateY(-10px) scale(0.8);
}

.menu-enter-to {
  opacity: 1;
  transform: translateY(0) scale(1);
}

.menu-leave-from {
  opacity: 1;
  transform: translateY(0) scale(1);
}

.menu-leave-to {
  opacity: 0;
  transform: translateY(-10px) scale(0.8);
}

.icon-wrapper {
  display: flex;
  align-items: center;
  justify-content: center;
  width: 40px;
  height: 40px;
  border-radius: 8px;
  cursor: pointer;
  transition: all 0.2s ease;
}

.icon-wrapper:hover {
  background-color: var(--bg-elevated);
  transform: scale(1.1);
}

.svg-icon {
  width: 24px;
  height: 24px;
  object-fit: contain;
}
</style>
