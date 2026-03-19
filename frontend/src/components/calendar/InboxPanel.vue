<template>
  <div class="inbox-panel" :class="{ 'open': isOpen }">
    <div class="inbox-header">
      <h3 class="inbox-title">Inbox</h3>
      <button class="close-btn" @click="$emit('close')">
        ✕
      </button>
    </div>
    
    <div class="inbox-content">
      <div v-if="inboxTasks.length === 0" class="empty-inbox">
        <span class="empty-icon">📥</span>
        <span>Пусто</span>
      </div>
      
      <div 
        v-for="task in inboxTasks" 
        :key="task.id"
        class="inbox-task"
        draggable="true"
        @dragstart="handleDragStart($event, task)"
        @dragend="handleDragEnd"
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
</template>

<script setup lang="ts">
import { computed } from 'vue'
import { useTasksStore } from '@/stores/tasks'
import { useKanbanStore } from '@/stores/kanban'

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

const emit = defineEmits<{
  (e: 'close'): void
  (e: 'task-drag-start', task: Task): void
  (e: 'task-drag-end'): void
}>()

const tasksStore = useTasksStore()
const kanbanStore = useKanbanStore()

// Находим Inbox колонку
const inboxColumn = computed(() =>
  kanbanStore.columns.find(col => col.title === 'Inbox')
)

// Получаем задачи из Inbox
const inboxTasks = computed(() => {
  if (!inboxColumn.value) return []
  return tasksStore.tasks.filter((t: Task) => t.status === inboxColumn.value?.id || t.column_id === inboxColumn.value?.id)
})

const handleDragStart = (event: DragEvent, task: Task) => {
  if (event.dataTransfer) {
    event.dataTransfer.setData('text/plain', JSON.stringify(task))
    event.dataTransfer.effectAllowed = 'move'
  }
  emit('task-drag-start', task)
}

const handleDragEnd = () => {
  emit('task-drag-end')
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
  background: #1a1a1a;
  border-left: 1px solid #333;
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
  border-bottom: 1px solid #333;
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
  padding: 40px;
  color: #666;
}

.empty-icon {
  font-size: 48px;
  margin-bottom: 10px;
}

.inbox-task {
  display: flex;
  align-items: flex-start;
  padding: 12px;
  margin-bottom: 8px;
  background: #2a2a2a;
  border-radius: 8px;
  cursor: move;
  transition: background 0.2s, transform 0.2s;
}

.inbox-task:hover {
  background: #333;
}

.inbox-task:active {
  transform: scale(0.98);
}

.task-checkbox {
  width: 20px;
  height: 20px;
  border: 2px solid #666;
  border-radius: 4px;
  margin-right: 12px;
  margin-top: 2px;
  flex-shrink: 0;
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: center;
  transition: border-color 0.2s, background 0.2s;
}

.task-checkbox:hover {
  border-color: #4A90E2;
}

.task-checkbox .checked {
  color: #4A90E2;
  font-size: 14px;
  font-weight: bold;
}

.task-content {
  flex: 1;
  min-width: 0;
}

.task-title {
  color: #fff;
  font-size: 14px;
  word-break: break-word;
}

.task-description {
  color: #888;
  font-size: 12px;
  margin-top: 4px;
  word-break: break-word;
}
</style>
