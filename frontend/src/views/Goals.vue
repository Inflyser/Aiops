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
      <button class="add-goal-btn" @click="router.push('/goals/new')">+ Цель</button>
    </div>

    <div class="goals-scroll">
      <div class="goals-content">
        <!-- Featured Slots -->
        <div class="featured-section">
          <div
            v-for="pos in 3"
            :key="'featured-' + pos"
            class="featured-slot"
            :class="{ 'has-goal': featuredAtPos(pos) }"
            @click="handleFeaturedClick(pos)"
          >
            <template v-if="featuredAtPos(pos)">
              <div class="featured-card" :style="{ borderColor: getStatusColor(featuredAtPos(pos)!.status) }">
                <div class="featured-icon">
                  <img v-if="featuredAtPos(pos)!.icon && getIconPath(featuredAtPos(pos)!.icon!)" :src="getIconPath(featuredAtPos(pos)!.icon!)" />
                  <span v-else>🏆</span>
                </div>
                <div class="featured-info">
                  <div class="featured-title">{{ featuredAtPos(pos)!.title }}</div>
                  <div class="featured-meta">
                    <span class="featured-status" :style="{ color: getStatusColor(featuredAtPos(pos)!.status) }">
                      {{ statusLabel(featuredAtPos(pos)!.status) }}
                    </span>
                    <span v-if="featuredAtPos(pos)!.deadline" class="featured-deadline">
                      📅 {{ dayjs(featuredAtPos(pos)!.deadline).format('DD.MM.YYYY') }}
                    </span>
                  </div>
                  <div v-if="featuredAtPos(pos)!.goal_type === 'numeric'" class="featured-progress">
                    <div class="featured-progress-bar">
                      <div class="featured-progress-fill" :style="{ width: numericProgress(featuredAtPos(pos)!) + '%' }"></div>
                    </div>
                    <span class="featured-progress-text">{{ featuredAtPos(pos)!.current_value }}/{{ featuredAtPos(pos)!.target_value }} {{ featuredAtPos(pos)!.target_unit }}</span>
                  </div>
                </div>
                <button class="featured-unpin" @click.stop="unpinGoal(pos)" title="Открепить">✕</button>
              </div>
            </template>
            <template v-else>
              <div class="featured-empty">
                <span class="featured-empty-icon">+</span>
                <span class="featured-empty-label">Важная цель</span>
              </div>
            </template>
          </div>
        </div>

        <!-- Goals List -->
        <div class="goals-list">
          <div v-if="nonFeaturedGoals.length === 0 && featuredGoals.length === 0" class="empty-state">
            <span class="empty-icon">🎯</span>
            <span class="empty-text">Нет целей. Создайте первую!</span>
          </div>

          <div
            v-for="goal in sortedGoals"
            :key="goal.id"
            class="goal-card"
            @click="router.push('/goals/' + goal.id)"
          >
            <div class="goal-card-left">
              <div class="goal-icon" :style="{ backgroundColor: getStatusColor(goal.status) + '22' }">
                <img v-if="goal.icon && getIconPath(goal.icon)" :src="getIconPath(goal.icon)" class="goal-svg-icon" />
                <span v-else class="goal-emoji-icon">🏆</span>
              </div>
            </div>
            <div class="goal-card-body">
              <div class="goal-card-top">
                <div class="goal-title">{{ goal.title }}</div>
                <div class="goal-card-actions">
                  <span class="goal-status-badge" :style="{ backgroundColor: getStatusColor(goal.status) + '22', color: getStatusColor(goal.status) }">
                    {{ statusLabel(goal.status) }}
                  </span>
                  <button
                    class="goal-pin-btn"
                    :class="{ pinned: goal.is_featured }"
                    :title="goal.is_featured ? 'Открепить' : 'Закрепить в важные'"
                    @click.stop="toggleFeatured(goal)"
                  >
                    📌
                  </button>
                </div>
              </div>
              <div class="goal-card-meta">
                <span v-if="goal.deadline" class="goal-deadline">📅 {{ dayjs(goal.deadline).format('DD.MM.YYYY') }}</span>
                <span v-if="goal.description" class="goal-desc-preview">{{ goal.description }}</span>
              </div>
              <div v-if="goal.goal_type === 'numeric'" class="goal-progress">
                <div class="goal-progress-bar">
                  <div class="goal-progress-fill" :style="{ width: numericProgress(goal) + '%' }"></div>
                </div>
                <span class="goal-progress-text">{{ goal.current_value }}/{{ goal.target_value }} {{ goal.target_unit }}</span>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>

  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted, onUnmounted } from 'vue'
import { useRouter } from 'vue-router'
import dayjs from 'dayjs'
import 'dayjs/locale/ru'
import ThreeDotsMenu from '../components/ui/ThreeDotsMenu.vue'
import { useGoalsStore, type Goal } from '../stores/goals'

dayjs.locale('ru')

const router = useRouter()
const goalsStore = useGoalsStore()

const currentTime = ref('')
const updateTime = () => {
  currentTime.value = dayjs().format('HH:mm DD MMMM')
}
let timeInterval: ReturnType<typeof setInterval>

onMounted(() => {
  updateTime()
  timeInterval = setInterval(updateTime, 1000)
  goalsStore.fetchGoals()
})

onUnmounted(() => {
  if (timeInterval) clearInterval(timeInterval)
})

// Icons
const iconModules = import.meta.glob<{ default: string }>('../assets/icon/*.svg', { query: '?url', import: 'default', eager: true })

const getIconPath = (iconName: string): string => {
  for (const [path, url] of Object.entries(iconModules)) {
    if (path.includes(`/${iconName}.svg`) || path.includes(`/${iconName}`)) {
      return url as unknown as string
    }
  }
  return ''
}

// Statuses
const statuses = [
  { value: 'active', label: 'Активная', color: '#4a9eff' },
  { value: 'completed', label: 'Выполнена', color: '#4caf50' },
  { value: 'archived', label: 'В архиве', color: '#888' }
]

const getStatusColor = (status: string) => {
  return statuses.find(s => s.value === status)?.color || '#888'
}

const statusLabel = (status: string) => {
  return statuses.find(s => s.value === status)?.label || status
}

// Featured
const featuredAtPos = (pos: number) => {
  return goalsStore.goals.find(g => g.is_featured && g.featured_position === pos) || null
}

const featuredGoals = computed(() => goalsStore.goals.filter(g => g.is_featured))
const nonFeaturedGoals = computed(() => goalsStore.goals.filter(g => !g.is_featured))

const sortedGoals = computed(() => {
  return [...nonFeaturedGoals.value].sort((a, b) => a.order - b.order)
})

const toggleFeatured = async (goal: Goal) => {
  const currentlyFeatured = goalsStore.goals.filter(g => g.is_featured && g.id !== goal.id)

  if (!goal.is_featured) {
    const freePos = [1, 2, 3].find(p => !currentlyFeatured.find(g => g.featured_position === p))
    if (freePos === undefined) return
    await goalsStore.updateGoal(goal.id, { is_featured: true, featured_position: freePos })
  } else {
    await goalsStore.updateGoal(goal.id, { is_featured: false, featured_position: undefined })
  }
}

const unpinGoal = async (pos: number) => {
  const goal = featuredAtPos(pos)
  if (!goal) return
  await goalsStore.updateGoal(goal.id, { is_featured: false, featured_position: undefined })
}

const handleFeaturedClick = async (pos: number) => {
  const goal = featuredAtPos(pos)
  if (goal) {
    router.push('/goals/' + goal.id)
  }
}

const numericProgress = (goal: Goal) => {
  if (!goal.target_value || goal.target_value === 0) return 0
  return Math.min(100, Math.round((goal.current_value / goal.target_value) * 100))
}
</script>

<style scoped>
.goals-page {
  width: 100%;
  height: 100vh;
  background-color: var(--bg-primary);
  color: var(--text-primary);
  display: flex;
  flex-direction: column;
  overflow: hidden;
}

.top-bar {
  flex-shrink: 0;
  margin-top: 5px;
  display: flex;
  align-items: center;
  padding: 10px 20px;
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
  color: var(--text-primary);
  font-weight: 500;
}

.goals-header {
  flex-shrink: 0;
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 20px 28px;
  border-bottom: 1px solid #80808021;
}

.goals-title {
  font-size: 42px;
  font-weight: bold;
  margin: 0;
}

.add-goal-btn {
  background: var(--bg-tertiary);
  border: 1px solid #2a2a2a;
  color: #fff;
  padding: 10px 24px;
  border-radius: 8px;
  font-size: 13px;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.2s;
}

.add-goal-btn:hover {
  background: #252525;
  border-color: #3a3a3a;
}

.goals-scroll {
  flex: 1;
  overflow-y: auto;
  min-height: 0;
}

.goals-content {
  max-width: 900px;
  margin: 0 auto;
  padding: 32px 20px;
}

/* Featured */
.featured-section {
  display: flex;
  gap: 16px;
  margin-bottom: 40px;
}

.featured-slot {
  flex: 1;
  min-height: 160px;
  border: 2px dashed #2a2a2a;
  border-radius: 16px;
  display: flex;
  align-items: center;
  justify-content: center;
  cursor: pointer;
  transition: border-color 0.2s, background 0.2s;
}

.featured-slot:hover {
  border-color: #3a3a3a;
  background: rgba(255,255,255,0.02);
}

.featured-slot.has-goal {
  border-style: solid;
  border-color: #3a3a3a;
  cursor: pointer;
  padding: 12px;
}

.featured-empty {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 8px;
  color: #444;
}

.featured-empty-icon {
  font-size: 28px;
  font-weight: 300;
}

.featured-empty-label {
  font-size: 11px;
  color: #444;
}

.featured-card {
  width: 100%;
  border-left: 3px solid;
  border-radius: 12px;
  padding: 14px;
  background: var(--bg-secondary);
  position: relative;
}

.featured-icon {
  width: 32px;
  height: 32px;
  margin-bottom: 8px;
}

.featured-icon img {
  width: 100%;
  height: 100%;
  object-fit: contain;
  filter: brightness(0) invert(1);
  opacity: 0.7;
}

.featured-icon span {
  font-size: 24px;
}

.featured-title {
  font-size: 14px;
  font-weight: 600;
  margin-bottom: 6px;
  color: #fff;
  word-break: break-word;
}

.featured-meta {
  display: flex;
  gap: 8px;
  align-items: center;
  font-size: 10px;
  margin-bottom: 6px;
}

.featured-status {
  font-weight: 600;
}

.featured-deadline {
  color: #888;
}

.featured-progress {
  display: flex;
  align-items: center;
  gap: 8px;
}

.featured-progress-bar {
  flex: 1;
  height: 4px;
  background: #1a1a1a;
  border-radius: 2px;
  overflow: hidden;
}

.featured-progress-fill {
  height: 100%;
  background: #4a9eff;
  border-radius: 2px;
  transition: width 0.3s;
}

.featured-progress-text {
  font-size: 10px;
  color: #888;
  white-space: nowrap;
}

.featured-unpin {
  position: absolute;
  top: 6px;
  right: 6px;
  background: transparent;
  border: none;
  color: #666;
  font-size: 12px;
  cursor: pointer;
  padding: 4px 6px;
  border-radius: 4px;
  opacity: 0;
  transition: opacity 0.2s;
}

.featured-card:hover .featured-unpin {
  opacity: 1;
}

.featured-unpin:hover {
  background: #3a1a1a;
  color: #ff6b6b;
}

/* Goals List */
.goals-list {
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.empty-state {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 12px;
  padding: 60px;
  color: #666;
}

.empty-icon {
  font-size: 48px;
  opacity: 0.4;
}

.empty-text {
  font-size: 14px;
}

.goal-card {
  display: flex;
  gap: 16px;
  background: var(--bg-secondary);
  border: 1px solid #1e1e1e;
  border-radius: 16px;
  padding: 18px;
  cursor: pointer;
  transition: border-color 0.2s;
}

.goal-card:hover {
  border-color: #2a2a2a;
}

.goal-card-left {
  flex-shrink: 0;
}

.goal-icon {
  width: 48px;
  height: 48px;
  border-radius: 12px;
  display: flex;
  align-items: center;
  justify-content: center;
}

.goal-svg-icon {
  width: 24px;
  height: 24px;
  object-fit: contain;
  filter: brightness(0) invert(1);
  opacity: 0.7;
}

.goal-emoji-icon {
  font-size: 22px;
}

.goal-card-body {
  flex: 1;
  min-width: 0;
}

.goal-card-top {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  gap: 12px;
}

.goal-title {
  font-size: 16px;
  font-weight: 600;
  color: #fff;
  word-break: break-word;
}

.goal-card-actions {
  display: flex;
  gap: 8px;
  align-items: center;
  flex-shrink: 0;
}

.goal-status-badge {
  font-size: 10px;
  font-weight: 600;
  padding: 4px 10px;
  border-radius: 20px;
  white-space: nowrap;
}

.goal-pin-btn {
  background: transparent;
  border: none;
  font-size: 16px;
  cursor: pointer;
  padding: 4px;
  border-radius: 6px;
  opacity: 0.3;
  transition: opacity 0.2s;
}

.goal-card:hover .goal-pin-btn {
  opacity: 0.6;
}

.goal-pin-btn:hover, .goal-pin-btn.pinned {
  opacity: 1;
}

.goal-card-meta {
  display: flex;
  gap: 12px;
  align-items: center;
  margin-top: 6px;
}

.goal-deadline {
  font-size: 11px;
  color: #888;
}

.goal-desc-preview {
  font-size: 11px;
  color: #666;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.goal-progress {
  display: flex;
  align-items: center;
  gap: 10px;
  margin-top: 8px;
}

.goal-progress-bar {
  flex: 1;
  max-width: 200px;
  height: 6px;
  background: #1a1a1a;
  border-radius: 3px;
  overflow: hidden;
}

.goal-progress-fill {
  height: 100%;
  background: #4a9eff;
  border-radius: 3px;
  transition: width 0.3s;
}

.goal-progress-text {
  font-size: 11px;
  color: #888;
  white-space: nowrap;
}


</style>
