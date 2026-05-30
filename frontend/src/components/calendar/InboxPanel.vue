<template>
  <div class="inbox-panel" :class="{ 'open': isOpen }">
    <div class="inbox-header">
      <h3 class="inbox-title">Inbox</h3>
      <button class="close-btn" @click="$emit('close')">
        ←
      </button>
    </div>
    
    <div class="inbox-content">
      <!-- Inbox Categories -->
      <div v-if="inboxCategories.length === 0" class="empty-inbox">
        <span class="empty-icon">📥</span>
        <span>Пусто</span>
      </div>
      
      <div 
        v-for="category in inboxCategories" 
        :key="category.id"
        class="inbox-category"
        draggable="true"
        @dragstart="handleCategoryDragStart($event, category)"
      >
        <div class="category-header">
          <span class="category-dot" :style="{ background: category.color }"></span>
          <span class="category-title">{{ category.title }}</span>
          <span class="category-count">{{ getCategoryTasks(category).length }}</span>
          <button
            class="collapse-btn"
            @click.stop="toggleCollapse(category.id)"
            title="Свернуть/развернуть"
          ><span :class="{ rotated: !isCollapsed(category.id) }">›</span></button>
        </div>
        
        <!-- Tasks in category -->
        <div v-show="!isCollapsed(category.id)" class="category-tasks">
          <div
            v-for="task in getCategoryTasks(category)"
            :key="task.id"
            class="inbox-task"
            draggable="true"
            @dragstart="handleTaskDragStart($event, task)"
            @dragend="handleTaskDragEnd"
          >
            <div class="task-checkbox" @click.stop="toggleTask(task)">
              <span v-if="task.completed" class="checked">✓</span>
            </div>
            <div class="task-content">
              <div class="task-title">{{ task.title }}</div>
              <div v-if="task.description" class="task-description">{{ task.description }}</div>
            </div>
          </div>
        </div>
      </div>
      
      <!-- Edit button -->
      <div class="edit-container">
        <button class="edit-btn" @click="editInbox">
          Редактировать
        </button>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { computed, ref } from 'vue'
import { useRouter } from 'vue-router'
import { useTasksStore } from '@/stores/tasks'
import { useKanbanStore } from '@/stores/kanban'
import type { InboxCategory } from '@/stores/kanban'

interface Task {
  id: string
  title: string
  description?: string
  completed: boolean
  status?: string
  column_id?: string
}

defineProps<{
  isOpen: boolean
}>()

defineEmits<{
  (e: 'close'): void
  (e: 'category-dropped-to-event', data: { event: { id: string }; category: InboxCategory }): void
}>()

const router = useRouter()
const tasksStore = useTasksStore()
const kanbanStore = useKanbanStore()

// Inbox categories
const inboxCategories = computed(() => kanbanStore.columns.filter(col => col.is_inbox_category))

// Collapse state (default: all expanded)
const collapsed = ref<Record<string, boolean>>({})
const isCollapsed = (id: string) => !!collapsed.value[id]
const toggleCollapse = (id: string) => {
  collapsed.value[id] = !collapsed.value[id]
}

// Получаем задачи категории
const getCategoryTasks = (category: InboxCategory) => {
  return tasksStore.tasks.filter((t: Task) => t.column_id === category.id)
}

// Переход в канбан
const editInbox = () => {
  router.push('/kanban')
}

// Drag and drop для задач
const handleTaskDragStart = (event: DragEvent, task: Task) => {
  if (event.dataTransfer) {
    event.dataTransfer.setData('text/plain', JSON.stringify(task))
    event.dataTransfer.effectAllowed = 'move'
  }
}

const handleTaskDragEnd = () => {
  // Ничего не делаем, задачи остаются в категории
}

// Drag and drop для категорий (перетаскиваем всю колонку на событие)
const handleCategoryDragStart = (event: DragEvent, category: InboxCategory) => {
  if (event.dataTransfer) {
    const categoryData = {
      type: 'category',
      categoryId: category.id,
      categoryTitle: category.title
    }
    event.dataTransfer.setData('text/plain', JSON.stringify(categoryData))
    event.dataTransfer.effectAllowed = 'move'
  }
}

const toggleTask = async (task: Task) => {
  await tasksStore.updateTask(task.id, { completed: !task.completed })
}
</script>

<style scoped>
.inbox-panel {
  position: fixed;
  top: 0;
  right: -320px;
  width: 320px;
  height: 100vh;
  background: #050505;
  border-left: 1px solid #33333357;
  transition: right 0.3s ease;
  z-index: 1000;
  display: flex;
  flex-direction: column;
}

.inbox-panel.open {
  right: 0;
}

.inbox-header {
  padding: 20px;
  border-bottom: 1px solid #33333357;
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.inbox-title {
  margin: 0;
  color: #fff;
  font-size: 14px;
  font-weight: 600;
}

.close-btn {
  background: none;
  border: none;
  color: #888;
  font-size: 19px;
  cursor: pointer;
  padding: 0;
  width: 30px;
  height: 30px;
  display: flex;
  align-items: center;
  justify-content: center;
  border-radius: 4px;
  transition: background 0.2s;
}

.close-btn:hover {
  background: #333;
  color: #fff;
}

.inbox-content {
  flex: 1;
  overflow-y: auto;
  padding: 10px;
}

.empty-inbox {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: 50px 20px;
  color: #666;
}

.empty-icon {
  font-size: 38px;
  margin-bottom: 10px;
}

.inbox-category {
  margin-bottom: 20px;
  border: 1px solid #33333357;
  border-radius: 8px;
  overflow: hidden;
}

.category-header {
  display: flex;
  align-items: center;
  padding: 12px;
  gap: 10px;
  background: #050505;
  border-bottom: 1px solid #33333357;
}

.category-dot {
  width: 12px;
  height: 12px;
  border-radius: 50%;
}

.category-title {
  color: #fff;
  font-weight: 600;
  flex: 1;
}

.category-count {
  color: #888;
  font-size: 10px;
}

.collapse-btn {
  background: none;
  border: none;
  color: #888;
  font-size: 16px;
  cursor: pointer;
  padding: 0;
  width: 24px;
  height: 24px;
  display: flex;
  align-items: center;
  justify-content: center;
  border-radius: 4px;
  transition: background 0.2s;
}

.collapse-btn:hover {
  background: #33333357;
  color: #fff;
}

.collapse-btn span {
  display: block;
  transition: transform 0.2s;
  line-height: 1;
}

.collapse-btn span.rotated {
  transform: rotate(90deg);
}

.category-tasks {
  padding: 10px;
  max-height: 300px;
  overflow-y: auto;
  background: #050505;
}

.inbox-task {
  display: flex;
  align-items: flex-start;
  padding: 8px;
  background: #050505;
  margin-bottom: 4px;
  border-radius: 4px;
  cursor: grab;
}

.inbox-task:active {
  cursor: grabbing;
}

.task-checkbox {
  width: 20px;
  height: 20px;
  border: 1px solid #33333357;
  border-radius: 4px;
  display: flex;
  align-items: center;
  justify-content: center;
  cursor: pointer;
  margin-right: 10px;
  flex-shrink: 0;
}

.checked {
  color: #4A90E2;
  font-weight: bold;
}

.task-content {
  flex: 1;
}

.task-title {
  color: #fff;
  font-weight: 500;
}

.task-description {
  color: #888;
  font-size: 10px;
  margin-top: 4px;
}

.edit-container {
  padding: 10px;
  border-top: 1px solid #333;
}

.edit-btn {
  width: 100%;
  padding: 12px;
  background: transparent;
  color: #888;
  border: 1px solid #333;
  border-radius: 8px;
  cursor: pointer;
  font-weight: 600;
  font-size: 13px;
  transition: all 0.2s;
}

.edit-btn:hover {
  background: #33333357;
  color: #fff;
  border-color: #555;
}
</style>
