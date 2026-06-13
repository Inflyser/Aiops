<template>
  <div class="landing">
    <div class="landing-content">
      <div class="hero">
        <div class="hero-text">
          <div class="heading-row">
            <h1 class="app-name">Aoips — Time Tracker</h1>
            <img :src="lendImg" alt="" class="heading-lend" />
          </div>
          <p class="description">Understand how you spend your time and how<br />things you do affect your mental state.</p>
          <button class="sign-in-btn" @click="goToApp">Sign In</button>
        </div>
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
import lendImg from '../assets/lend.svg'
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
  max-width: 1100px;
  width: 100%;
}

.hero {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 60px;
  width: 100%;
}

.hero-text {
  flex: 1;
  display: flex;
  flex-direction: column;
  gap: 24px;
}

.heading-row {
  position: relative;
  display: inline-block;
  white-space: nowrap;
  margin-left: -30px;
}

.app-name {
  font-family: 'Mitr', sans-serif;
  font-size: 90px;
  font-weight: 700;
  color: var(--text-primary);
  margin: 0;
  line-height: 1.05;
  letter-spacing: 1px;
  position: relative;
  z-index: 1;
}

.heading-lend {
  position: absolute;
  right: -80px;
  top: 50%;
  transform: translateY(-50%);
  z-index: 0;
  width: 456px;
  pointer-events: none;
}

.description {
  font-size: 32px;
  color: #888;
  margin: 0;
  line-height: 1.3;
}

.sign-in-btn {
  margin-top: 8px;
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
  align-self: flex-start;
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

@media (max-width: 900px) {
  .hero {
    flex-direction: column;
    text-align: center;
  }

  .hero-text {
    align-items: center;
  }

  .heading-row {
    white-space: normal;
  }

  .app-name {
    font-size: 48px;
  }

  .heading-lend {
    display: none;
  }

  .description {
    font-size: 20px;
  }

  .sign-in-btn {
    align-self: center;
  }

  .landing-content {
    gap: 48px;
  }
}
</style>
