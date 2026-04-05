<template>
  <div class="inbox-panel" :class="{ 'open': isOpen }">
    <div class="inbox-header">
      <h3 class="inbox-title">Inbox</h3>
      <button class="close-btn" @click="$emit('close')">
        ✕
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
            v-if="!category.is_static"
            class="delete-category-btn"
            @click.stop="deleteCategory(category)"
            title="Удалить категорию"
          >✕</button>
        </div>
        
        <!-- Tasks in category -->
        <div class="category-tasks">
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
      
      <!-- Add Category Button -->
      <div v-if="!isAddingCategory" class="add-category-container">
        <button class="add-category-btn" @click="startAddCategory">
          + Добавить категорию
        </button>
      </div>
      
      <!-- Add Category Form -->
      <form 
        v-else 
        class="add-category-form" 
        @submit.prevent="addCategory"
        @mouseleave="cancelAddCategory"
      >
        <input
          v-model="newCategoryTitle"
          placeholder="Название категории..."
          class="category-input"
          @keydown.escape="cancelAddCategory"
        />
        <button type="submit" class="add-category-submit" title="Создать">+</button>
      </form>
    </div>
  </div>
</template>

<script setup lang="ts">
import { computed, ref } from 'vue'
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

const tasksStore = useTasksStore()
const kanbanStore = useKanbanStore()

// Inbox categories
const inboxCategories = computed(() => kanbanStore.columns.filter(col => col.is_inbox_category))

// Получаем задачи категории
const getCategoryTasks = (category: InboxCategory) => {
  return tasksStore.tasks.filter((t: Task) => t.column_id === category.id)
}

// Добавление категории
const isAddingCategory = ref(false)
const newCategoryTitle = ref('')

const startAddCategory = () => {
  isAddingCategory.value = true
  newCategoryTitle.value = ''
}

const cancelAddCategory = () => {
  isAddingCategory.value = false
  newCategoryTitle.value = ''
}

const addCategory = async () => {
  const title = newCategoryTitle.value.trim()
  if (!title) return
  
  try {
    await kanbanStore.createInboxCategory({
      title,
      color: getRandomColor()
    })
    newCategoryTitle.value = ''
    isAddingCategory.value = false
  } catch (err) {
    console.error('Failed to create category:', err)
  }
}

const deleteCategory = async (category: InboxCategory) => {
  if (!confirm(`Удалить категорию "${category.title}"? Все задачи будут перемещены в Inbox.`)) return
  
  try {
    // Переносим задачи в Inbox (column_id = undefined)
    const tasksToMove = getCategoryTasks(category)
    for (const task of tasksToMove) {
      await tasksStore.updateTask(task.id, { column_id: undefined, status: 'todo' })
    }
    
    // Удаляем категорию
    await kanbanStore.deleteColumn(category.id)
  } catch (err) {
    console.error('Failed to delete category:', err)
  }
}

const getRandomColor = () => {
  const colors = ['#4A90E2', '#50C878', '#FF6B6B', '#F59E0B', '#6B7280', '#EC4899', '#8B5CF6', '#10B981', '#F59F0F']
  return colors[Math.floor(Math.random() * colors.length)]
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
  right: -400px;
  width: 400px;
  height: 100vh;
  background: #0a0a0a;
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
  font-size: 18px;
  font-weight: 600;
}

.close-btn {
  background: none;
  border: none;
  color: #888;
  font-size: 24px;
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
  font-size: 48px;
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
  background: #0d0d0d;
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
  font-size: 12px;
}

.delete-category-btn {
  background: none;
  border: none;
  color: #888;
  font-size: 16px;
  cursor: pointer;
  padding: 4px 8px;
  border-radius: 4px;
  transition: background 0.2s;
}

.delete-category-btn:hover {
  background: #33333357;
  color: #fff;
}

.category-tasks {
  padding: 10px;
  max-height: 300px;
  overflow-y: auto;
  background: #0a0a0a;
}

.inbox-task {
  display: flex;
  align-items: flex-start;
  padding: 8px;
  background: #0d0d0d;
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
  font-size: 12px;
  margin-top: 4px;
}

.add-category-container {
  padding: 10px;
  border-top: 1px solid #333;
}

.add-category-btn {
  width: 100%;
  padding: 12px;
  background: #4A90E2;
  color: #fff;
  border: none;
  border-radius: 4px;
  cursor: pointer;
  font-weight: 600;
  transition: background 0.2s;
}

.add-category-btn:hover {
  background: #3a7bd5;
}

.add-category-form {
  padding: 10px;
  border-top: 1px solid #33333357;
}

.category-input {
  width: 100%;
  padding: 10px;
  background: #0d0d0d;
  color: #fff;
  border: 1px solid #33333357;
  border-radius: 4px;
  font-size: 14px;
}

.category-input:focus {
  outline: none;
  border-color: #4A90E2;
  background: #101010;
}

.add-category-submit {
  position: absolute;
  right: 10px;
  top: 10px;
  width: 30px;
  height: 30px;
  background: #4A90E2;
  color: #fff;
  border: none;
  border-radius: 4px;
  cursor: pointer;
  font-weight: bold;
  font-size: 18px;
}

.add-category-submit:hover {
  background: #3a7bd5;
  transform: scale(1.05);
}
</style>
