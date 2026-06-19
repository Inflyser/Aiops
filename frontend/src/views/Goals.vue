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
      <button class="add-goal-btn" @click="openCreateModal">+ Цель</button>
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
            @click="openEditModal(goal)"
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

    <!-- Goal Modal -->
    <div v-if="showModal" class="modal-overlay" @click.self="closeModal">
      <div class="goal-modal">
        <div class="goal-modal-header">
          <h2>{{ editingGoal ? 'Редактировать цель' : 'Новая цель' }}</h2>
          <button class="modal-close-btn" @click="closeModal">✕</button>
        </div>

        <div class="goal-modal-body">
          <div class="form-group">
            <label>Название</label>
            <input v-model="form.title" class="form-input" placeholder="Название цели" />
          </div>

          <div class="form-group">
            <label>Описание</label>
            <textarea v-model="form.description" class="form-textarea" placeholder="Описание цели" rows="3"></textarea>
          </div>

          <div class="form-group">
            <label>Тип цели</label>
            <div class="type-toggle">
              <button
                class="type-btn"
                :class="{ active: form.goal_type === 'concrete' }"
                @click="form.goal_type = 'concrete'"
              >Конкретная</button>
              <button
                class="type-btn"
                :class="{ active: form.goal_type === 'numeric' }"
                @click="form.goal_type = 'numeric'"
              >Числовая</button>
            </div>
          </div>

          <template v-if="form.goal_type === 'numeric'">
            <div class="form-row">
              <div class="form-group flex-1">
                <label>Целевое значение</label>
                <input v-model.number="form.target_value" type="number" class="form-input" placeholder="1000" />
              </div>
              <div class="form-group flex-1">
                <label>Единица</label>
                <input v-model="form.target_unit" class="form-input" placeholder="$, км, раз..." />
              </div>
            </div>
          </template>
          <template v-if="form.goal_type === 'numeric' && editingGoal">
            <div class="form-group">
              <label>Текущее значение ({{ form.current_value }})</label>
              <input v-model.number="form.current_value" type="number" class="form-input" placeholder="0" />
            </div>
          </template>

          <div class="form-group">
            <label>Дедлайн</label>
            <input v-model="form.deadline" type="date" class="form-input" />
          </div>

          <div class="form-group">
            <label>Статус</label>
            <div class="status-select">
              <button
                v-for="s in statuses"
                :key="s.value"
                class="status-btn"
                :class="{ active: form.status === s.value }"
                :style="form.status === s.value ? { backgroundColor: s.color + '22', color: s.color, borderColor: s.color } : {}"
                @click="form.status = s.value"
              >{{ s.label }}</button>
            </div>
          </div>

          <div class="form-group">
            <label>Иконка</label>
            <div class="icon-grid">
              <div
                v-for="icon in availableIcons"
                :key="icon"
                class="icon-option"
                :class="{ selected: form.icon === icon }"
                @click="form.icon = form.icon === icon ? undefined : icon"
              >
                <img :src="getIconPath(icon)" class="icon-option-img" />
              </div>
            </div>
          </div>
        </div>

        <div class="goal-modal-footer">
          <button v-if="editingGoal" class="btn-delete" @click="deleteCurrentGoal">Удалить</button>
          <div class="footer-right">
            <button class="btn-cancel" @click="closeModal">Отмена</button>
            <button class="btn-save" @click="saveGoal" :disabled="!form.title.trim()">Сохранить</button>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted, onUnmounted } from 'vue'
import dayjs from 'dayjs'
import 'dayjs/locale/ru'
import ThreeDotsMenu from '../components/ui/ThreeDotsMenu.vue'
import { useGoalsStore, type Goal } from '../stores/goals'

dayjs.locale('ru')

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

const availableIcons = computed(() => {
  return Object.keys(iconModules).map(p => {
    const name = p.split('/').pop()?.replace('.svg', '') || ''
    return name
  })
})

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
    openEditModal(goal)
  }
}

const numericProgress = (goal: Goal) => {
  if (!goal.target_value || goal.target_value === 0) return 0
  return Math.min(100, Math.round((goal.current_value / goal.target_value) * 100))
}

// Modal
const showModal = ref(false)
const editingGoal = ref<Goal | null>(null)

const form = ref({
  title: '',
  description: '',
  goal_type: 'concrete',
  target_value: undefined as number | undefined,
  target_unit: '',
  current_value: 0,
  deadline: '',
  status: 'active',
  icon: undefined as string | undefined
})

const resetForm = () => {
  form.value = {
    title: '',
    description: '',
    goal_type: 'concrete',
    target_value: undefined,
    target_unit: '',
    current_value: 0,
    deadline: '',
    status: 'active',
    icon: undefined
  }
}

const openCreateModal = () => {
  resetForm()
  editingGoal.value = null
  showModal.value = true
}

const openEditModal = (goal: Goal) => {
  editingGoal.value = goal
  form.value = {
    title: goal.title,
    description: goal.description || '',
    goal_type: goal.goal_type,
    target_value: goal.target_value,
    target_unit: goal.target_unit || '',
    current_value: goal.current_value,
    deadline: goal.deadline ? dayjs(goal.deadline).format('YYYY-MM-DD') : '',
    status: goal.status,
    icon: goal.icon
  }
  showModal.value = true
}

const closeModal = () => {
  showModal.value = false
  editingGoal.value = null
  resetForm()
}

const saveGoal = async () => {
  if (!form.value.title.trim()) return

  const data: any = {
    title: form.value.title,
    description: form.value.description || undefined,
    goal_type: form.value.goal_type,
    target_value: form.value.goal_type === 'numeric' ? form.value.target_value : undefined,
    target_unit: form.value.goal_type === 'numeric' ? form.value.target_unit : undefined,
    current_value: form.value.goal_type === 'numeric' ? form.value.current_value : 0,
    deadline: form.value.deadline ? dayjs(form.value.deadline).toISOString() : undefined,
    status: form.value.status,
    icon: form.value.icon || undefined
  }

  try {
    if (editingGoal.value) {
      await goalsStore.updateGoal(editingGoal.value.id, data)
    } else {
      await goalsStore.createGoal(data)
    }
    closeModal()
  } catch (err) {
    console.error('Failed to save goal:', err)
  }
}

const deleteCurrentGoal = async () => {
  if (!editingGoal.value) return
  if (!confirm(`Удалить цель "${editingGoal.value.title}"?`)) return
  try {
    await goalsStore.deleteGoal(editingGoal.value.id)
    closeModal()
  } catch (err) {
    console.error('Failed to delete goal:', err)
  }
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

/* Modal */
.modal-overlay {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: rgba(0, 0, 0, 0.7);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 1000;
}

.goal-modal {
  background: var(--bg-tertiary);
  border: 1px solid #2a2a2a;
  border-radius: 16px;
  width: 540px;
  max-height: 90vh;
  display: flex;
  flex-direction: column;
}

.goal-modal-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 24px 24px 0;
}

.goal-modal-header h2 {
  margin: 0;
  font-size: 19px;
  color: #fff;
}

.modal-close-btn {
  background: transparent;
  border: none;
  color: #888;
  font-size: 18px;
  cursor: pointer;
  padding: 4px 8px;
  border-radius: 6px;
}

.modal-close-btn:hover {
  background: #2a2a2a;
  color: #fff;
}

.goal-modal-body {
  padding: 24px;
  overflow-y: auto;
  display: flex;
  flex-direction: column;
  gap: 18px;
}

.form-group {
  display: flex;
  flex-direction: column;
  gap: 6px;
}

.form-group label {
  font-size: 11px;
  color: #888;
  font-weight: 600;
  text-transform: uppercase;
  letter-spacing: 0.05em;
}

.form-input, .form-textarea {
  width: 100%;
  padding: 12px;
  background: #0a0a0a;
  border: 1px solid #2a2a2a;
  border-radius: 8px;
  color: #fff;
  font-size: 13px;
  outline: none;
  box-sizing: border-box;
  transition: border-color 0.2s;
}

.form-input:focus, .form-textarea:focus {
  border-color: #4a9eff;
}

.form-textarea {
  resize: vertical;
  font-family: inherit;
}

.form-row {
  display: flex;
  gap: 12px;
}

.flex-1 {
  flex: 1;
}

.type-toggle {
  display: flex;
  gap: 8px;
}

.type-btn {
  flex: 1;
  padding: 10px;
  background: #0a0a0a;
  border: 1px solid #2a2a2a;
  border-radius: 8px;
  color: #888;
  font-size: 12px;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.2s;
}

.type-btn.active {
  background: #4a9eff22;
  border-color: #4a9eff;
  color: #4a9eff;
}

.status-select {
  display: flex;
  gap: 8px;
}

.status-btn {
  flex: 1;
  padding: 8px;
  background: #0a0a0a;
  border: 1px solid #2a2a2a;
  border-radius: 8px;
  color: #888;
  font-size: 11px;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.2s;
}

.icon-grid {
  display: grid;
  grid-template-columns: repeat(8, 1fr);
  gap: 6px;
  max-height: 160px;
  overflow-y: auto;
  padding: 4px 0;
}

.icon-option {
  width: 100%;
  aspect-ratio: 1;
  display: flex;
  align-items: center;
  justify-content: center;
  background: #0a0a0a;
  border: 1px solid #2a2a2a;
  border-radius: 8px;
  cursor: pointer;
  transition: all 0.2s;
  padding: 6px;
  box-sizing: border-box;
}

.icon-option:hover {
  border-color: #4a4a4a;
}

.icon-option.selected {
  background: #4a9eff22;
  border-color: #4a9eff;
}

.icon-option-img {
  width: 100%;
  height: 100%;
  object-fit: contain;
  filter: brightness(0) invert(1);
  opacity: 0.6;
}

.icon-option.selected .icon-option-img {
  opacity: 1;
}

.goal-modal-footer {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 0 24px 24px;
}

.footer-right {
  display: flex;
  gap: 8px;
  margin-left: auto;
}

.btn-cancel, .btn-save, .btn-delete {
  padding: 10px 20px;
  border-radius: 8px;
  font-size: 12px;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.2s;
  border: none;
}

.btn-cancel {
  background: transparent;
  border: 1px solid #2a2a2a;
  color: #ccc;
}

.btn-cancel:hover {
  background: #1a1a1a;
}

.btn-save {
  background: #4a9eff;
  color: #fff;
}

.btn-save:hover {
  background: #3a8eef;
}

.btn-save:disabled {
  opacity: 0.4;
  cursor: not-allowed;
}

.btn-delete {
  background: transparent;
  border: 1px solid #5a1a1a;
  color: #ff6b6b;
}

.btn-delete:hover {
  background: #3a1a1a;
}
</style>
