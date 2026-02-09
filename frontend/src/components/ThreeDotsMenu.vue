<template>
  <div class="menu-container" @click.stop="toggleMenu">
    <!-- Иконка из SVG вместо трех точек -->
    <div v-if="!isMenuOpen" class="dots-icon">
      <img :src="dotsIcon" alt="Menu" class="dots-svg-icon" />
    </div>
    
    <!-- Анимированная панель с иконками -->
    <Transition name="menu">
      <div v-if="isMenuOpen" class="animated-menu" @click.stop>
        <div class="menu-panel">
          <!-- Календарь -->
          <div class="icon-wrapper" @click.stop="navigateToWeeklyCalendar">
            <img :src="calendarIcon" alt="Calendar" class="svg-icon" />
          </div>
          
          <!-- Канбан -->
          <div class="icon-wrapper" @click.stop="navigateToKanban">
            <img :src="kanbanIcon" alt="Kanban" class="svg-icon" />
          </div>
        </div>
      </div>
    </Transition>
  </div>
</template>

<script setup lang="ts">
import { ref, onUnmounted } from 'vue'
import { useRouter } from 'vue-router'

// Импортируем SVG иконки из assets
import calendarIcon from '@/assets/icon-colendar.svg'
import kanbanIcon from '@/assets/icon-kanban.svg'
import dotsIcon from '@/assets/three-point.svg' // Иконка для трех точек

const isMenuOpen = ref(false)
const router = useRouter()

const toggleMenu = () => {
  isMenuOpen.value = !isMenuOpen.value
}

const navigateToWeeklyCalendar = () => {
  router.push('/')
  isMenuOpen.value = false
}

const navigateToKanban = () => {
  router.push('/kanban')
  isMenuOpen.value = false
}

// Закрыть меню при клике вне его области
const closeMenu = (event: MouseEvent) => {
  const menuElement = document.querySelector('.menu-container')
  if (menuElement && !menuElement.contains(event.target as Node)) {
    isMenuOpen.value = false
  }
}

// Добавляем слушатель событий для закрытия меню при клике вне его области
document.addEventListener('click', closeMenu)

// Очищаем слушатель при уничтожении компонента
onUnmounted(() => {
  document.removeEventListener('click', closeMenu)
})
</script>

<style scoped>
.menu-container {
  position: relative;
  cursor: pointer;
  width: 24px;
  height: 24px;
  margin-right: 125px;
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
  filter: brightness(0) invert(1); /* Делает иконку белой (если она черная) */
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
  background-color: #0f0f0f;
  border-radius: 10px;
  padding: 10px;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.3);
  backdrop-filter: blur(10px);
  min-width: 80px;
}

/* Анимации появления и исчезновения */
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
  background-color: #333;
  transform: scale(1.1);
}

.svg-icon {
  width: 24px;
  height: 24px;
  object-fit: contain;
}
</style>