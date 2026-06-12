<template>
  <div class="landing">
    <div class="landing-content">
      <div class="hero">
        <div class="logo-wrapper">
          <img :src="logo" alt="Logo" class="logo" />
        </div>
        <h1 class="app-name">To-Do</h1>
        <p class="tagline">Управляй задачами, событиями и целями — всё в одном месте</p>
        <button class="sign-in-btn" @click="goToApp">Sign In</button>
      </div>
      <div class="features">
        <div class="feature">
          <img :src="calendarIcon" alt="Calendar" class="feature-icon" />
          <span class="feature-label">Календарь</span>
        </div>
        <div class="feature">
          <img :src="kanbanIcon" alt="Kanban" class="feature-icon" />
          <span class="feature-label">Канбан</span>
        </div>
        <div class="feature">
          <img :src="statsIcon" alt="Statistics" class="feature-icon" />
          <span class="feature-label">Статистика</span>
        </div>
        <div class="feature">
          <img :src="goalsIcon" alt="Goals" class="feature-icon" />
          <span class="feature-label">Цели</span>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { useRouter } from 'vue-router'
import logo from '../assets/logo.svg'
import calendarIcon from '../assets/icon-colendar.svg'
import kanbanIcon from '../assets/icon-kanban.svg'
import statsIcon from '../assets/icon/finance_24dp_B1B3B2_FILL0_wght400_GRAD0_opsz24.svg'
import goalsIcon from '../assets/icon/trophy_24dp_B1B3B2_FILL0_wght400_GRAD0_opsz24.svg'

const router = useRouter()

const goToApp = () => {
  router.push('/calendar')
}
</script>

<style scoped>
.landing {
  min-height: 100vh;
  background-color: var(--bg-primary);
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 20px;
}

.landing-content {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 80px;
  max-width: 600px;
}

.hero {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 24px;
  text-align: center;
}

.logo-wrapper {
  width: 100px;
  height: 100px;
  display: flex;
  align-items: center;
  justify-content: center;
}

.logo {
  width: 100%;
  height: 100%;
  object-fit: contain;
  filter: brightness(0) invert(1);
}

.app-name {
  font-size: 48px;
  font-weight: 800;
  color: var(--text-primary);
  margin: 0;
  letter-spacing: 2px;
}

.tagline {
  font-size: 18px;
  color: #888;
  margin: 0;
  max-width: 400px;
  line-height: 1.5;
}

.sign-in-btn {
  margin-top: 16px;
  padding: 14px 48px;
  font-size: 18px;
  font-weight: 700;
  color: var(--text-primary);
  background: transparent;
  border: 2px solid var(--text-primary);
  border-radius: 12px;
  cursor: pointer;
  transition: all 0.2s ease;
  letter-spacing: 1px;
}

.sign-in-btn:hover {
  background: var(--text-primary);
  color: #050505;
  transform: scale(1.05);
}

.features {
  display: flex;
  gap: 32px;
  flex-wrap: wrap;
  justify-content: center;
}

.feature {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 8px;
}

.feature-icon {
  width: 32px;
  height: 32px;
  object-fit: contain;
  filter: brightness(0) invert(1);
  opacity: 0.5;
}

.feature-label {
  font-size: 14px;
  color: #666;
  font-weight: 500;
}
</style>
