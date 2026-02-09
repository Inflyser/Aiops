<template>
  <div class="weekly-calendar">
    <!-- Top Bar -->
    <div class="top-bar">
      <div class="time-display">{{ currentTime }}</div>
      <div class="menu-wrapper">
        <ThreeDotsMenu />
      </div>
      <!-- Убрали пустую кнопку или добавили контент -->
      <!-- <button class="nav-btn"></button> -->
    </div>
    <h1>Kanban Desk</h1>
    <div class="kanban-board">
      <div class="kanban-columns">
        <div
          v-for="(col, colIdx) in columns"
          :key="col.key"
          class="kanban-column"
        >
          <div class="column-header">
            <h3>{{ col.label }}</h3>
            <button 
              class="del-col-btn" 
              v-if="columns.length > 1" 
              @click="removeColumn(col.key)"
              type="button"
            >
              ✕
            </button>
          </div>
          <draggable
            class="column-body"
            :list="getColumnTasks(col.key)"
            :group="{ name: 'tasks', pull: true, put: true }"
            item-key="id"
            @change="(e: any) => onTaskChange(e, col.key)"
            @end="(e: any) => onTaskDrop(e, col.key)"
            ghost-class="ghost"
            chosen-class="chosen"
            drag-class="drag"
            :move="onMove"
          >
            <template #item="{ element: task }">
              <div class="kanban-card-wrapper">
                <TaskCard
                  :task="task"
                  :status="statusMap[task.id]"
                />
              </div>
            </template>
          </draggable>
          <div v-if="tasksByColumn(col.key).length === 0" class="empty-column">Пусто</div>
          <form class="add-task-form" @submit.prevent="addTask(col.key)">
            <input 
              :value="newTaskTitles[col.key]" 
              @input="updateTaskTitle(col.key, ($event.target as HTMLInputElement).value)"
              placeholder="Новая задача..." 
            />
            <button type="submit">+</button>
          </form>
        </div>
        <div class="add-col">
          <form @submit.prevent="addColumn">
            <input v-model="newColTitle" placeholder="Новый столбец..." />
            <button type="submit">+</button>
          </form>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted, onUnmounted, reactive } from 'vue'
import dayjs from 'dayjs'
import 'dayjs/locale/ru'
import ThreeDotsMenu from '../components/ThreeDotsMenu.vue'
import TaskCard from '../components/TaskCard.vue'
import { useTasksStore } from '../stores/tasks'
import { mockKanbanTasks } from '../mock/kanbanData'
import draggable from 'vuedraggable'
import type { MoveEvent, ChangeEvent } from 'vuedraggable'

dayjs.locale('ru')

const currentTime = ref('')
const updateTime = () => {
  currentTime.value = dayjs().format('HH:mm DD MMMM')
}

const tasksStore = useTasksStore()

// Локальная карта статусов для канбана
const statusMap = ref<Record<string, string>>({})

const columns = ref([
  { key: 'todo', label: 'To Do' },
  { key: 'in-progress', label: 'In Progress' },
  { key: 'done', label: 'Done' }
])

const newColTitle = ref('')
// Используем реактивный объект для заголовков новых задач
const newTaskTitles = reactive<Record<string, string>>({})

// Инициализируем пустые значения для каждой колонки
const initializeTaskTitles = () => {
  columns.value.forEach(col => {
    if (!newTaskTitles[col.key]) {
      newTaskTitles[col.key] = ''
    }
  })
}

const updateTaskTitle = (colKey: string, value: string) => {
  newTaskTitles[colKey] = value
}

const initializeStatusMap = async () => {
  try {
    await tasksStore.fetchTasks()
  } catch (err) {
    console.warn('Failed to fetch tasks from server, using mock data:', err)
    // Если не удалось загрузить с сервера, используем моковые данные
    if (tasksStore.tasks.length === 0) {
      tasksStore.tasks.push(...mockKanbanTasks)
    }
  }

  // Инициализируем статусы задач
  tasksStore.tasks.forEach((t: any) => {
    if (!statusMap.value[t.id]) {
      statusMap.value[t.id] = t.completed ? 'done' : 'todo'
    }
  })
  
  // Инициализируем заголовки для форм
  initializeTaskTitles()
}

const tasksByColumn = (colKey: string) => {
  return tasksStore.tasks.filter((t: any) => statusMap.value[t.id] === colKey)
}

const getColumnTasks = (colKey: string) => {
  return tasksStore.tasks.filter((t: any) => statusMap.value[t.id] === colKey)
}

const onMove = () => {
  return true
}

const addColumn = () => {
  const title = newColTitle.value.trim()
  if (!title) return
  const key = title.toLowerCase().replace(/\s+/g, '-') + '-' + Date.now()
  columns.value.push({ key, label: title })
  newTaskTitles[key] = '' // Добавляем пустое значение для новой колонки
  newColTitle.value = ''
}

const removeColumn = (colKey: string) => {
  if (columns.value.length === 1) return
  
  // Получаем задачи, которые были в удаляемой колонке
  const tasksToRemove = tasksByColumn(colKey)
  
  // Удаляем колонку
  const index = columns.value.findIndex(col => col.key === colKey)
  columns.value.splice(index, 1)
  
  // Удаляем из newTaskTitles
  delete newTaskTitles[colKey]
  
  // Перемещаем задачи в первую доступную колонку
  if (columns.value.length > 0) {
    const firstColumnKey = columns.value[0].key
    tasksToRemove.forEach((t: any) => {
      statusMap.value[t.id] = firstColumnKey
      tasksStore.updateTask(t.id, { completed: firstColumnKey === 'done' })
        .catch(err => {
          console.error('Failed to update task after column removal:', err)
        })
    })
  }
}

const addTask = async (colKey: string) => {
  const title = newTaskTitles[colKey]?.trim()
  if (!title) return
  try {
    const taskData = { 
      title, 
      completed: colKey === 'done', 
      priority: 'medium' 
    }
    const newTask = await tasksStore.createTask(taskData)
    statusMap.value[newTask.id] = colKey
    newTaskTitles[colKey] = ''
  } catch (err) {
    console.error('Failed to create task:', err)
  }
}

const onTaskChange = (evt: ChangeEvent, colKey: string) => {
  if (evt.added) {
    const task = evt.added.element
    if (task && statusMap.value[task.id] !== colKey) {
      const prevStatus = statusMap.value[task.id]
      statusMap.value[task.id] = colKey

      tasksStore.updateTask(task.id, { completed: colKey === 'done' })
        .then(() => {
          console.log(`Task ${task.id} moved from ${prevStatus} to ${colKey}`)
        })
        .catch(err => {
          console.error('Failed to update task status on server:', err)
          statusMap.value[task.id] = prevStatus
        })
    }
  } else if (evt.moved) {
    console.log('Task moved within column', evt.moved)
  }
}

const onTaskDrop = (evt: any, colKey: string) => {
  // Обработка завершения перетаскивания
}

let timeInterval: ReturnType<typeof setInterval>

onMounted(async () => {
  updateTime()
  timeInterval = setInterval(updateTime, 1000)
  await initializeStatusMap()
})

onUnmounted(() => {
  clearInterval(timeInterval)
})
</script>

<style scoped>
.weekly-calendar {
  width: 100%;
  min-height: 100vh;
  background-color: #050505;
  color: #ffffff;
  overflow: hidden;
}

.top-bar {
  margin-top: 5px;
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 10px 20px;
}

.menu-wrapper {
  display: flex;
  align-items: center;
  justify-content: center;
}

.nav-btn {
  background: transparent;
  border: none;
  color: #ffffff;
  font-size: 18px;
  cursor: pointer;
  padding: 5px 10px;
}

.time-display {
  font-size: 22px;
  color: #ffffff;
  font-weight: 500;
}

.kanban-board {
  padding: 20px;
}

.kanban-columns {
  display: flex;
  gap: 16px;
  align-items: flex-start;
  width: 100%;
  overflow-x: auto;
  padding-bottom: 10px;
}

.kanban-column {
  background: #0b0b0b;
  border: 1px solid #222;
  border-radius: 8px;
  padding: 12px;
  min-width: 260px;
  min-height: 300px;
  flex: 0 0 auto;
  display: flex;
  flex-direction: column;
  box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
}

.kanban-column:hover {
  box-shadow: 0 8px 15px rgba(0, 0, 0, 0.2);
  border-color: #444;
}

.add-col {
  min-width: 180px;
  align-self: stretch;
  display: flex;
  align-items: flex-start;
  justify-content: center;
  padding: 12px;
}

.add-col form {
  display: flex;
  gap: 6px;
  width: 100%;
}

.add-col input {
  flex: 1;
  padding: 8px 12px;
  border-radius: 4px;
  border: 1px solid #333;
  background: #181818;
  color: #fff;
  font-size: 14px;
}

.add-col button {
  background: #4a5568;
  color: #fff;
  border: none;
  border-radius: 4px;
  padding: 8px 12px;
  cursor: pointer;
  font-size: 16px;
}

.add-task-form {
  display: flex;
  gap: 6px;
  margin-top: 10px;
}

.add-task-form input {
  flex: 1;
  padding: 8px 12px;
  border-radius: 4px;
  border: 1px solid #333;
  background: #181818;
  color: #fff;
  font-size: 14px;
}

.add-task-form button {
  background: #4a5568;
  color: #fff;
  border: none;
  border-radius: 4px;
  padding: 8px 12px;
  cursor: pointer;
  font-size: 16px;
}

.del-col-btn {
  background: transparent;
  border: none;
  color: #888;
  font-size: 18px;
  margin-left: 8px;
  cursor: pointer;
  padding: 0;
  width: 24px;
  height: 24px;
  display: flex;
  align-items: center;
  justify-content: center;
}

.column-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 12px;
  padding-bottom: 8px;
  border-bottom: 1px solid #333;
}

.column-header h3 {
  margin: 0;
  font-weight: 500;
  font-size: 18px;
}

.column-body {
  display: flex;
  flex-direction: column;
  gap: 12px;
  flex: 1;
  min-height: 200px;
  padding: 8px;
  border-radius: 4px;
  transition: background-color 0.2s ease;
}

.column-body.drag-over {
  background-color: rgba(74, 144, 226, 0.1);
}

.kanban-card-wrapper {
  cursor: grab;
}

.kanban-card-wrapper:active {
  cursor: grabbing;
}

.empty-column {
  color: #777;
  padding: 20px;
  text-align: center;
  font-style: italic;
  flex: 1;
  display: flex;
  align-items: center;
  justify-content: center;
}

/* Стили для перетаскивания */
.ghost {
  opacity: 0.5;
  background: #c8ebfb;
  transform: rotate(5deg);
}

.chosen {
  border: 2px solid #4a90e2;
  background-color: #1a1a1a;
  transform: scale(1.02);
}

.drag {
  user-select: none;
}
</style>