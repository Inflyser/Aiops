<template>
  <div 
    class="task-card" 
    :class="{ 'task-completed': task.completed }"
    @dblclick.stop="$emit('edit-task', task)"
  >
    <div class="card-top">
      <!-- Checkbox for completion -->
      <button
        class="task-checkbox"
        :class="{ checked: task.completed }"
        @click.stop="$emit('toggle-task', task.id)"
        :title="task.completed ? 'Отметить как невыполненную' : 'Отметить как выполненную'"
      >
        <span v-if="task.completed">✓</span>
      </button>
      <div class="card-title" :class="{ completed: task.completed }">{{ task.title }}</div>
      <div class="card-actions">
        <button
          class="small-btn delete-btn"
          @click.stop="$emit('delete-task', task.id)"
          title="Удалить задачу"
        >✕</button>
      </div>
    </div>
    <div v-if="task.description" class="card-desc">{{ task.description }}</div>
    <div class="card-meta">
      <span v-if="task.due_date">📅 {{ formatDate(task.due_date) }}</span>
      <span class="priority" :class="`p-${task.priority}`">{{ task.priority }}</span>
    </div>
  </div>
</template>

<script setup lang="ts">
import dayjs from 'dayjs'

interface Props {
  task: any
  status: string
}

defineProps<Props>()
defineEmits(['move-left', 'move-right', 'edit-task', 'delete-task', 'toggle-task'])

const formatDate = (d: string) => dayjs(d).format('DD.MM.YYYY')
</script>

<style scoped>
.task-card {
  background: #111;
  border: 1px solid #222;
  padding: 12px;
  border-radius: 8px;
  color: #eee;
  transition: transform 0.2s cubic-bezier(0.4, 0, 0.2, 1), 
              box-shadow 0.2s cubic-bezier(0.4, 0, 0.2, 1),
              border-color 0.2s;
}

.task-card:hover {
  transform: translateY(-3px) scale(1.02);
  box-shadow: 0 8px 16px rgba(0, 0, 0, 0.3);
  border-color: #444;
}

.task-completed {
  opacity: 0.7;
}

.card-top {
  display: flex;
  justify-content: space-between;
  align-items: center;
  gap: 8px;
}

/* Checkbox styles */
.task-checkbox {
  width: 20px;
  height: 20px;
  min-width: 20px;
  border: 2px solid #555;
  border-radius: 50%;
  background: transparent;
  color: #4caf50;
  font-size: 12px;
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: center;
  transition: all 0.2s;
}

.task-checkbox:hover {
  border-color: #4caf50;
}

.task-checkbox.checked {
  background: #4caf50;
  border-color: #4caf50;
  color: #fff;
}

.card-title {
  font-weight: 600;
  flex: 1;
}

.card-title.completed {
  text-decoration: line-through;
  color: #777;
}

.card-actions {
  display: flex;
  gap: 6px;
}

.small-btn {
  background: transparent;
  border: 1px solid #333;
  color: #ddd;
  padding: 4px 6px;
  border-radius: 4px;
  cursor: pointer;
  transition: background-color 0.2s;
}

.small-btn:hover {
  background-color: #333;
}

.small-btn:disabled {
  opacity: 0.3;
  cursor: default;
}

.delete-btn {
  color: #ff6b6b;
}

.delete-btn:hover {
  background-color: #5a1818;
}

.card-desc {
  color: #aaa;
  margin-top: 8px;
  font-size: 14px
}

.card-meta {
  margin-top: 10px;
  font-size: 12px;
  color: #999;
  display: flex;
  gap: 8px;
  align-items: center
}

.priority {
  padding: 2px 6px;
  border-radius: 4px;
  font-size: 11px
}

.p-low {
  background: #2d5016;
  color: #7cb342
}

.p-medium {
  background: #47381f;
  color: #ff9800
}

.p-high {
  background: #3a1d19;
  color: #f44336
}
</style>
