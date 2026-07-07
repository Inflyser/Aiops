<template>
  <div class="goal-edit-page">
    <div class="top-bar">
      <div class="time-display">{{ currentTime }}</div>
      <div class="menu-wrapper">
        <ThreeDotsMenu />
      </div>
    </div>

    <div class="edit-header">
      <button class="back-btn" @click="router.push('/goals')">← Назад</button>
      <h1 class="edit-title">{{ isNew ? 'Новая цель' : 'Редактировать цель' }}</h1>
    </div>

    <div class="edit-scroll">
      <div class="edit-body">
        <template v-if="!isNew && !goal && !loading">
          <div class="not-found">
            <span class="not-found-icon">🎯</span>
            <span class="not-found-text">Цель не найдена</span>
            <button class="btn-cancel" @click="router.push('/goals')">Вернуться к списку</button>
          </div>
        </template>

        <template v-else>
          <!-- Left Sidebar: Cover, Icon, Description -->
          <div class="edit-sidebar">
            <div class="sidebar-section">
              <label class="sidebar-label">Обложка</label>
              <div class="cover-area" @click="triggerCoverInput">
                <img v-if="form.cover_image" :src="form.cover_image" class="cover-preview" />
                <div v-else class="cover-placeholder">
                  <svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="#666" stroke-width="2"><rect x="3" y="3" width="18" height="18" rx="2"/><circle cx="8.5" cy="8.5" r="1.5"/><path d="M21 15l-5-5L5 21"/></svg>
                  <span>Загрузить обложку</span>
                </div>
                <input ref="coverInput" type="file" accept="image/*" class="cover-input" @change="onCoverChange" />
                <button v-if="form.cover_image" class="cover-remove" @click.stop="form.cover_image = undefined">✕</button>
              </div>
            </div>

            <div class="sidebar-section">
              <label class="sidebar-label">Иконка</label>
              <div class="icon-trigger" @click="showIconPicker = !showIconPicker">
                <div class="icon-trigger-preview">
                  <img v-if="form.icon && getIconPath(form.icon)" :src="getIconPath(form.icon)" class="icon-trigger-img" />
                  <span v-else class="icon-trigger-emoji">🏆</span>
                </div>
                <span class="icon-trigger-text">{{ form.icon ? form.icon : 'Выбрать иконку' }}</span>
                <svg :class="['icon-chevron', { open: showIconPicker }]" width="12" height="12" viewBox="0 0 12 12" fill="none" stroke="#888" stroke-width="2"><path d="M4 4l4 4 4-4"/></svg>
              </div>
              <div v-if="showIconPicker" class="icon-dropdown">
                <div class="icon-grid">
                  <div v-for="icon in availableIcons" :key="icon" class="icon-option" :class="{ selected: form.icon === icon }" @click="form.icon = form.icon === icon ? undefined : icon; showIconPicker = false">
                    <img :src="getIconPath(icon)" class="icon-option-img" />
                  </div>
                </div>
              </div>
            </div>

            <div class="sidebar-section sidebar-description">
              <label class="sidebar-label">Описание</label>
              <textarea v-model="form.description" class="form-textarea" placeholder="Описание цели" rows="6"></textarea>
            </div>
          </div>

          <!-- Right Main: Form fields -->
          <div class="edit-main">
            <div class="main-section">
              <div class="main-row">
                <div class="form-group flex-2">
                  <label>Название</label>
                  <input v-model="form.title" class="form-input" placeholder="Название цели" />
                </div>
                <div class="form-group flex-1">
                  <label>Статус</label>
                  <select v-model="form.status" class="form-input">
                    <option v-for="s in statuses" :key="s.value" :value="s.value">{{ s.label }}</option>
                  </select>
                </div>
              </div>
            </div>

            <div class="main-section">
              <label class="main-section-label">Тип цели</label>
              <div class="type-toggle">
                <button class="type-btn" :class="{ active: form.goal_type === 'concrete' }" @click="form.goal_type = 'concrete'">Конкретная</button>
                <button class="type-btn" :class="{ active: form.goal_type === 'numeric' }" @click="form.goal_type = 'numeric'">Числовая</button>
              </div>
              <template v-if="form.goal_type === 'numeric'">
                <div class="main-row">
                  <div class="form-group flex-1">
                    <label>Целевое значение</label>
                    <input v-model.number="form.target_value" type="number" class="form-input" placeholder="1000" />
                  </div>
                  <div class="form-group flex-1">
                    <label>Единица</label>
                    <input v-model="form.target_unit" class="form-input" placeholder="$, км, раз..." />
                  </div>
                  <div class="form-group flex-1">
                    <label>Текущее значение</label>
                    <input v-model.number="form.current_value" type="number" class="form-input" placeholder="0" />
                  </div>
                </div>
              </template>
            </div>

            <div class="main-section">
              <label class="main-section-label">Срок</label>
              <div class="main-row">
                <div class="form-group flex-1">
                  <label>Дедлайн</label>
                  <input v-model="form.deadline" type="date" class="form-input" />
                </div>
              </div>
            </div>

            <div class="main-actions">
              <button v-if="!isNew" class="btn-delete" @click="deleteGoal">Удалить цель</button>
              <div class="actions-right">
                <button class="btn-cancel" @click="router.push('/goals')">Отмена</button>
                <button class="btn-save" @click="saveGoal" :disabled="!form.title.trim()">
                  {{ isNew ? 'Создать' : 'Сохранить' }}
                </button>
              </div>
            </div>
          </div>
        </template>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted, onUnmounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import dayjs from 'dayjs'
import 'dayjs/locale/ru'
import ThreeDotsMenu from '../components/ui/ThreeDotsMenu.vue'
import { useGoalsStore, type Goal } from '../stores/goals'

dayjs.locale('ru')

const route = useRoute()
const router = useRouter()
const goalsStore = useGoalsStore()

const currentTime = ref('')
const updateTime = () => {
  currentTime.value = dayjs().format('HH:mm DD MMMM')
}
let timeInterval: ReturnType<typeof setInterval>

onMounted(async () => {
  updateTime()
  timeInterval = setInterval(updateTime, 1000)
  if (goalsStore.goals.length === 0) {
    await goalsStore.fetchGoals()
  }
  loadGoal()
})

onUnmounted(() => {
  if (timeInterval) clearInterval(timeInterval)
})

const isNew = computed(() => route.params.id === 'new')

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

const statuses = [
  { value: 'active', label: 'Активная' },
  { value: 'completed', label: 'Выполнена' },
  { value: 'archived', label: 'В архиве' }
]

const loading = ref(true)
const goal = ref<Goal | null>(null)
const showIconPicker = ref(false)
const coverInput = ref<HTMLInputElement>()

const form = ref({
  title: '',
  description: '',
  goal_type: 'concrete',
  target_value: undefined as number | undefined,
  target_unit: '',
  current_value: 0,
  deadline: '',
  status: 'active',
  icon: undefined as string | undefined,
  cover_image: undefined as string | undefined
})

const loadGoal = () => {
  if (isNew.value) {
    loading.value = false
    return
  }
  const id = route.params.id as string
  const found = goalsStore.goals.find(g => g.id === id)
  if (found) {
    goal.value = found
    form.value = {
      title: found.title,
      description: found.description || '',
      goal_type: found.goal_type,
      target_value: found.target_value,
      target_unit: found.target_unit || '',
      current_value: found.current_value,
      deadline: found.deadline ? dayjs(found.deadline).format('YYYY-MM-DD') : '',
      status: found.status,
      icon: found.icon,
      cover_image: found.cover_image
    }
  }
  loading.value = false
}

const triggerCoverInput = () => {
  coverInput.value?.click()
}

const onCoverChange = (e: Event) => {
  const file = (e.target as HTMLInputElement).files?.[0]
  if (!file) return
  const reader = new FileReader()
  reader.onload = () => {
    form.value.cover_image = reader.result as string
  }
  reader.readAsDataURL(file)
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
    icon: form.value.icon || undefined,
    cover_image: form.value.cover_image || undefined
  }

  try {
    if (isNew.value) {
      await goalsStore.createGoal(data)
    } else if (goal.value) {
      await goalsStore.updateGoal(goal.value.id, data)
    }
    router.push('/goals')
  } catch (err) {
    console.error('Failed to save goal:', err)
  }
}

const deleteGoal = async () => {
  if (!goal.value) return
  if (!confirm(`Удалить цель "${goal.value.title}"?`)) return
  try {
    await goalsStore.deleteGoal(goal.value.id)
    router.push('/goals')
  } catch (err) {
    console.error('Failed to delete goal:', err)
  }
}
</script>

<style scoped>
.goal-edit-page {
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

.edit-header {
  flex-shrink: 0;
  display: flex;
  align-items: center;
  gap: 16px;
  padding: 20px 28px;
  border-bottom: 1px solid #80808021;
}

.back-btn {
  background: transparent;
  border: 1px solid #2a2a2a;
  color: #ccc;
  padding: 8px 16px;
  border-radius: 8px;
  font-size: 13px;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.2s;
}

.back-btn:hover {
  background: #1a1a1a;
  border-color: #3a3a3a;
}

.edit-title {
  font-size: 28px;
  font-weight: bold;
  margin: 0;
}

.edit-scroll {
  flex: 1;
  overflow-y: auto;
  min-height: 0;
}

.edit-body {
  max-width: 960px;
  margin: 0 auto;
  padding: 32px 28px;
  display: flex;
  gap: 32px;
  align-items: flex-start;
}

/* Sidebar */
.edit-sidebar {
  width: 260px;
  flex-shrink: 0;
  display: flex;
  flex-direction: column;
  gap: 20px;
  position: sticky;
  top: 0;
}

.sidebar-section {
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.sidebar-label {
  font-size: 11px;
  color: #888;
  font-weight: 600;
  text-transform: uppercase;
  letter-spacing: 0.05em;
}

.sidebar-description {
  flex: 1;
}

/* Cover */
.cover-area {
  position: relative;
  width: 100%;
  aspect-ratio: 16 / 9;
  background: var(--bg-secondary);
  border: 1px dashed #2a2a2a;
  border-radius: 12px;
  overflow: hidden;
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: center;
  transition: border-color 0.2s;
}

.cover-area:hover {
  border-color: #4a4a4a;
}

.cover-preview {
  width: 100%;
  height: 100%;
  object-fit: cover;
}

.cover-placeholder {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 8px;
  color: #555;
  font-size: 12px;
}

.cover-input {
  display: none;
}

.cover-remove {
  position: absolute;
  top: 6px;
  right: 6px;
  width: 24px;
  height: 24px;
  border-radius: 6px;
  border: none;
  background: rgba(0,0,0,0.6);
  color: #fff;
  font-size: 12px;
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: center;
  opacity: 0;
  transition: opacity 0.2s;
}

.cover-area:hover .cover-remove {
  opacity: 1;
}

.cover-remove:hover {
  background: rgba(200,0,0,0.7);
}

/* Icon picker */
.icon-trigger {
  display: flex;
  align-items: center;
  gap: 10px;
  padding: 10px 12px;
  background: var(--bg-secondary);
  border: 1px solid #2a2a2a;
  border-radius: 8px;
  cursor: pointer;
  transition: border-color 0.2s;
}

.icon-trigger:hover {
  border-color: #4a4a4a;
}

.icon-trigger-preview {
  width: 28px;
  height: 28px;
  display: flex;
  align-items: center;
  justify-content: center;
  flex-shrink: 0;
}

.icon-trigger-img {
  width: 100%;
  height: 100%;
  object-fit: contain;
  filter: brightness(0) invert(1);
  opacity: 0.7;
}

.icon-trigger-emoji {
  font-size: 20px;
}

.icon-trigger-text {
  flex: 1;
  font-size: 13px;
  color: #ccc;
}

.icon-chevron {
  transition: transform 0.2s;
  flex-shrink: 0;
}

.icon-chevron.open {
  transform: rotate(180deg);
}

.icon-dropdown {
  background: var(--bg-secondary);
  border: 1px solid #2a2a2a;
  border-radius: 8px;
  padding: 12px;
  max-height: 200px;
  overflow-y: auto;
}

.icon-grid {
  display: grid;
  grid-template-columns: repeat(6, 1fr);
  gap: 6px;
}

.icon-option {
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
}

.icon-option:hover {
  border-color: #4a4a4a;
}

.icon-option.selected {
  background: #4a9eff18;
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

/* Main */
.edit-main {
  flex: 1;
  display: flex;
  flex-direction: column;
  gap: 24px;
  min-width: 0;
}

.main-section {
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.main-section-label {
  font-size: 13px;
  font-weight: 700;
  color: #888;
  text-transform: uppercase;
  letter-spacing: 0.08em;
}

.main-row {
  display: flex;
  gap: 12px;
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

.flex-1 {
  flex: 1;
}

.flex-2 {
  flex: 2;
}

.form-input, .form-textarea {
  padding: 12px;
  background: var(--bg-secondary);
  border: 1px solid #2a2a2a;
  border-radius: 8px;
  color: #fff;
  font-size: 14px;
  outline: none;
  transition: border-color 0.2s;
  font-family: inherit;
}

.form-input:focus, .form-textarea:focus {
  border-color: #4a9eff;
}

.form-textarea {
  resize: vertical;
}

select.form-input {
  cursor: pointer;
  appearance: none;
  background-image: url("data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' width='12' height='12' viewBox='0 0 12 12'%3E%3Cpath fill='%23888' d='M6 8L1 3h10z'/%3E%3C/svg%3E");
  background-repeat: no-repeat;
  background-position: right 12px center;
  padding-right: 36px;
}

select.form-input option {
  background: #1a1a1a;
  color: #fff;
}

.type-toggle {
  display: flex;
  gap: 8px;
}

.type-btn {
  flex: 1;
  padding: 12px;
  background: var(--bg-secondary);
  border: 1px solid #2a2a2a;
  border-radius: 8px;
  color: #888;
  font-size: 13px;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.2s;
}

.type-btn.active {
  background: #4a9eff18;
  border-color: #4a9eff;
  color: #4a9eff;
}

.main-actions {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding-top: 12px;
  border-top: 1px solid #1e1e1e;
  margin-top: 8px;
}

.actions-right {
  display: flex;
  gap: 8px;
  margin-left: auto;
}

.btn-cancel, .btn-save, .btn-delete {
  padding: 12px 24px;
  border-radius: 8px;
  font-size: 13px;
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

.not-found {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 16px;
  padding: 60px;
  color: #666;
}

.not-found-icon {
  font-size: 48px;
  opacity: 0.4;
}

.not-found-text {
  font-size: 14px;
}
</style>
