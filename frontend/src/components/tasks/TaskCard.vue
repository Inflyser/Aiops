<template>
  <div class="task-card">
    <div class="card-top">
      <div class="card-title">{{ task.title }}</div>
      <div class="card-actions">
        <button
          class="small-btn edit-btn"
          @click="$emit('edit-task', task)"
          title="Редактировать задачу"
        >✎</button>
        <button
          class="small-btn delete-btn"
          @click="$emit('delete-task', task.id)"
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
defineEmits(['move-left', 'move-right', 'edit-task', 'delete-task'])

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

.card-top {
  display: flex;
  justify-content: space-between;
  align-items: center;
  gap: 8px;
}

.card-title {
  font-weight: 600;
  flex: 1;
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

.edit-btn {
  color: #ffd700;
}

.edit-btn:hover {
  background-color: #444;
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
