<template>
  <div class="kanban-desk">
    <!-- Top Bar -->
    <div class="top-bar">
      <div class="time-display">{{ currentTime }}</div>
      <div class="menu-wrapper">
        <ThreeDotsMenu />
      </div>
      <button class="nav-btn"> </button>
    </div>

    <!-- Board Header -->
    <div class="board-header">
      <h1 class="board-title">Kanban</h1>
      <div class="board-meta">
        <span class="task-count">{{ tasksStore.tasks.length }} задач</span>
      </div>
    </div>

    <!-- Kanban Board -->
    <div class="kanban-board">
      <div class="kanban-columns">
        <div
          v-for="col in columns"
          :key="col.key"
          class="kanban-column"
        >
          <!-- Column Header -->
          <div class="column-header">
            <div class="column-header-left">
              <span class="column-dot" :class="`dot-${col.key}`"></span>
              <h3 class="column-title">{{ col.label }}</h3>
              <span class="column-count">{{ tasksByColumn(col.key).length }}</span>
            </div>
            <button
              class="del-col-btn"
              v-if="canRemoveColumn(col.key)"
              @click="removeColumn(col.key)"
              type="button"
              title="Удалить колонку"
            >✕</button>
          </div>

          <!-- Draggable Task List -->
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
                  :status="task.status"
                  @edit-task="openEditTaskModal"
                  @delete-task="deleteTask"
                  @toggle-task="toggleTask"
                />
              </div>
            </template>
          </draggable>

          <!-- Empty State -->
          <div v-if="tasksByColumn(col.key).length === 0" class="empty-column">
            <span class="empty-icon">○</span>
            <span>Пусто</span>
          </div>

          <!-- Add Task Form -->
          <form class="add-task-form" @submit.prevent="addTask(col.key)">
            <input
              :value="newTaskTitles[col.key]"
              @input="updateTaskTitle(col.key, ($event.target as HTMLInputElement).value)"
              placeholder="Добавить задачу..."
              class="task-input"
            />
            <button type="submit" class="add-task-btn" title="Добавить">+</button>
          </form>
        </div>

        <!-- Add Column -->
        <div class="add-col">
          <div class="add-col-inner">
            <p class="add-col-label">Новая колонка</p>
            <form @submit.prevent="addColumn" class="add-col-form">
              <input
                v-model="newColTitle"
                placeholder="Название..."
                class="task-input"
              />
              <button type="submit" class="add-task-btn" title="Создать">+</button>
            </form>
          </div>
        </div>
      </div>
    </div>

    <!-- Edit Task Modal -->
    <EditTaskModal
      v-if="editingTask"
      :task="editingTask"
      :visible="!!editingTask"
      @update:visible="editingTask = null"
      @save="updateTask"
    />
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted, onUnmounted, reactive, computed } from 'vue'
import dayjs from 'dayjs'
import 'dayjs/locale/ru'
import ThreeDotsMenu from '../components/ui/ThreeDotsMenu.vue'
import TaskCard from '../components/tasks/TaskCard.vue'
import EditTaskModal from '../components/modals/EditTaskModal.vue'
import { useTasksStore } from '../stores/tasks'
import { useCalendarStore } from '../stores/calendar'
import { useKanbanStore } from '../stores/kanban'
import draggable from 'vuedraggable'

dayjs.locale('ru')

const currentTime = ref('')
const updateTime = () => {
  currentTime.value = dayjs().format('HH:mm DD MMMM')
}

const tasksStore = useTasksStore()
const kanbanStore = useKanbanStore()

// Получаем колонки из store
const columns = computed(() => kanbanStore.columns.map(col => ({
  key: col.id,
  label: col.title,
  color: col.color
})))

const newColTitle = ref('')
const newTaskTitles = reactive<Record<string, string>>({})

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

const initializeTasks = async () => {
  await tasksStore.fetchTasks()
  
  // Инициализируем status для задач без него (миграция уже выполнена)
  tasksStore.tasks.forEach((t: any) => {
    if (!t.status) {
      t.status = t.completed ? 'done' : 'todo'
    }
  })

  initializeTaskTitles()
}

// Используем статус из задачи напрямую
const tasksByColumn = (colKey: string) => {
  return tasksStore.tasks.filter((t: any) => t.status === colKey)
}

const getColumnTasks = (colKey: string) => {
  return tasksStore.tasks.filter((t: any) => t.status === colKey)
}

const onMove = () => true

const addColumn = async () => {
  const title = newColTitle.value.trim()
  if (!title) return
  try {
    const newCol = await kanbanStore.createColumn({ title, color: '#555555' })
    newTaskTitles[newCol.id] = ''
    newColTitle.value = ''
  } catch (err) {
    console.error('Failed to create column:', err)
  }
}

const removeColumn = async (colKey: string) => {
  if (kanbanStore.columns.length <= 1) return
  
  const tasksToRemove = tasksByColumn(colKey)
  
  try {
    await kanbanStore.deleteColumn(colKey)
    delete newTaskTitles[colKey]
    
    // Переносим задачи в первую колонку
    if (kanbanStore.columns.length > 0) {
      const firstColumn = kanbanStore.columns[0]
      for (const t of tasksToRemove) {
        await tasksStore.updateTask(t.id, { column_id: firstColumn.id })
      }
    }
  } catch (err) {
    console.error('Failed to delete column:', err)
  }
}

const canRemoveColumn = (_colKey: string) => {
  return kanbanStore.columns.length > 1
}

const addTask = async (colKey: string) => {
  const title = newTaskTitles[colKey]?.trim()
  if (!title) return
  try {
    const taskData = {
      title,
      status: colKey,
      completed: colKey === 'done',
      priority: 'medium',
      description: ''
    }
    await tasksStore.createTask(taskData)
    newTaskTitles[colKey] = ''
  } catch (err) {
    console.error('Failed to create task:', err)
  }
}

const onTaskChange = async (evt: any, colKey: string) => {
  if (evt.added) {
    const task = evt.added.element
    if (task && task.status !== colKey) {
      const prevStatus = task.status
      task.status = colKey
      try {
        await tasksStore.updateTask(task.id, { 
          status: colKey,
          completed: colKey === 'done' 
        })
      } catch (err) {
        console.error('Failed to update task status on server:', err)
        task.status = prevStatus
      }
    }
  }
}

const onTaskDrop = async (_evt: any, _colKey: string) => {
  // Bulk update порядка задач после перетаскивания
  const bulkItems: any[] = []
  columns.value.forEach((col, colIndex) => {
    const tasksInCol = getColumnTasks(col.key)
    tasksInCol.forEach((task: any, taskIndex: number) => {
      bulkItems.push({
        task_id: task.id,
        status: col.key,
        order: colIndex * 100 + taskIndex
      })
    })
  })
  
  if (bulkItems.length > 0) {
    try {
      await tasksStore.bulkUpdateTasks(bulkItems)
    } catch (err) {
      console.error('Failed to bulk update tasks order:', err)
    }
  }
}

let timeInterval: ReturnType<typeof setInterval>

onMounted(async () => {
  updateTime()
  timeInterval = setInterval(updateTime, 1000)
  await kanbanStore.fetchColumns()
  await initializeTasks()
  window.addEventListener('keydown', handleKeydown)
})

onUnmounted(() => {
  clearInterval(timeInterval)
  window.removeEventListener('keydown', handleKeydown)
})

const editingTask = ref<any>(null)

const openEditTaskModal = (task: any) => {
  editingTask.value = { ...task }
}

const updateTask = async (updatedTask: any) => {
  try {
    await tasksStore.updateTask(updatedTask.id, updatedTask)
  } catch (err) {
    console.error('Failed to update task:', err)
  }
}

const deleteTask = async (taskId: string) => {
  try {
    await tasksStore.deleteTask(taskId)
  } catch (err) {
    console.error('Failed to delete task:', err)
  }
}

const toggleTask = async (taskId: string) => {
  try {
    await tasksStore.toggleTask(taskId)
  } catch (err) {
    console.error('Failed to toggle task:', err)
  }
}

// Keyboard handler for Ctrl+Z / Ctrl+Я
const handleKeydown = (event: KeyboardEvent) => {
  // Ctrl+Z или Ctrl+Я (русская раскладка) - отменить действие
  if (event.ctrlKey && (event.key === 'z' || event.key === 'я')) {
    event.preventDefault()
    // Используем undo из calendar store (общий)
    const calendarStore = useCalendarStore()
    calendarStore.undo().then(() => {
      // Перезагрузить задачи
      tasksStore.fetchTasks()
    })
  }
}
</script>

<style scoped>
/* ─── Base ─────────────────────────────────────────────── */
.kanban-desk {
  width: 100%;
  min-height: 100vh;
  background-color: #050505;
  color: #ffffff;
  overflow: hidden;
}

/* ─── Top Bar ───────────────────────────────────────────── */
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

/* ─── Board Header ──────────────────────────────────────── */
.board-header {
  padding: 20px 28px 0;
  display: flex;
  align-items: baseline;
  gap: 20px;
  border-bottom: 1px solid #80808021;
  padding-bottom: 18px;
}

.board-title {
  font-size: 52px;
  font-weight: bold;
  margin: 0;
  line-height: 1;
}

.board-meta {
  display: flex;
  align-items: center;
  gap: 12px;
}

.task-count {
  font-size: 14px;
  color: #555;
  font-weight: 400;
}

/* ─── Board Layout ──────────────────────────────────────── */
.kanban-board {
  padding: 24px 20px;
  overflow-x: auto;
}

.kanban-columns {
  display: flex;
  gap: 16px;
  align-items: flex-start;
  min-width: max-content;
  padding-bottom: 12px;
}

/* ─── Column ────────────────────────────────────────────── */
.kanban-column {
  background: #0f0f0f;
  border: 1px solid #1e1e1e;
  border-radius: 12px;
  padding: 16px;
  width: 300px;
  flex-shrink: 0;
  display: flex;
  flex-direction: column;
  gap: 0;
  transition: border-color 0.2s;
}

.kanban-column:hover {
  border-color: #2a2a2a;
}

/* ─── Column Header ─────────────────────────────────────── */
.column-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 14px;
  padding-bottom: 12px;
  border-bottom: 1px solid #1e1e1e;
}

.column-header-left {
  display: flex;
  align-items: center;
  gap: 8px;
}

.column-dot {
  width: 8px;
  height: 8px;
  border-radius: 50%;
  flex-shrink: 0;
}

.dot-todo        { background: #555; }
.dot-in-progress { background: #888; }
.dot-done        { background: #ccc; }

/* Для динамических колонок — нейтральный цвет */
.column-dot:not(.dot-todo):not(.dot-in-progress):not(.dot-done) {
  background: #444;
}

.column-title {
  margin: 0;
  font-size: 15px;
  font-weight: 600;
  color: #e0e0e0;
  letter-spacing: 0.02em;
}

.column-count {
  font-size: 12px;
  color: #444;
  background: #1a1a1a;
  border: 1px solid #2a2a2a;
  border-radius: 10px;
  padding: 1px 7px;
  font-weight: 500;
}

.del-col-btn {
  background: transparent;
  border: none;
  color: #333;
  font-size: 13px;
  cursor: pointer;
  padding: 3px 5px;
  border-radius: 4px;
  line-height: 1;
  transition: color 0.2s, background 0.2s;
}

.del-col-btn:hover {
  color: #888;
  background: #1a1a1a;
}

/* ─── Column Body (droppable zone) ─────────────────────── */
.column-body {
  display: flex;
  flex-direction: column;
  gap: 8px;
  min-height: 120px;
  border-radius: 8px;
  padding: 4px 0;
  transition: background-color 0.15s;
}

.column-body.sortable-drag-over {
  background-color: rgba(255, 255, 255, 0.03);
}

/* ─── Card Wrapper ──────────────────────────────────────── */
.kanban-card-wrapper {
  cursor: grab;
  transition: transform 0.15s;
}

.kanban-card-wrapper:hover {
  transform: translateY(-1px);
}

.kanban-card-wrapper:active {
  cursor: grabbing;
}

/* ─── Empty State ───────────────────────────────────────── */
.empty-column {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  gap: 6px;
  padding: 24px 0;
  color: #2e2e2e;
  font-size: 13px;
  font-style: italic;
  flex: 1;
}

.empty-icon {
  font-size: 20px;
  line-height: 1;
}

/* ─── Add Task Form ─────────────────────────────────────── */
.add-task-form {
  display: flex;
  gap: 6px;
  margin-top: 12px;
  padding-top: 12px;
  border-top: 1px solid #1a1a1a;
}

.task-input {
  flex: 1;
  padding: 8px 12px;
  border-radius: 6px;
  border: 1px solid #1e1e1e;
  background: #0a0a0a;
  color: #ccc;
  font-size: 13px;
  outline: none;
  transition: border-color 0.2s;
}

.task-input::placeholder {
  color: #333;
}

.task-input:focus {
  border-color: #333;
  color: #fff;
}

.add-task-btn {
  background: #1a1a1a;
  color: #666;
  border: 1px solid #1e1e1e;
  border-radius: 6px;
  padding: 8px 12px;
  cursor: pointer;
  font-size: 18px;
  line-height: 1;
  transition: background 0.2s, color 0.2s;
  flex-shrink: 0;
}

.add-task-btn:hover {
  background: #222;
  color: #fff;
}

/* ─── Add Column ────────────────────────────────────────── */
.add-col {
  width: 260px;
  flex-shrink: 0;
  border: 1px dashed #1e1e1e;
  border-radius: 12px;
  padding: 16px;
  display: flex;
  align-items: flex-start;
  transition: border-color 0.2s, background 0.2s;
}

.add-col:hover {
  border-color: #333;
  background: #0a0a0a;
}

.add-col-inner {
  width: 100%;
}

.add-col-label {
  font-size: 12px;
  color: #333;
  margin: 0 0 10px;
  text-transform: uppercase;
  letter-spacing: 0.08em;
  font-weight: 600;
}

.add-col-form {
  display: flex;
  gap: 6px;
}

/* ─── Drag & Drop States ────────────────────────────────── */
.ghost {
  opacity: 0.3;
  background: #1a1a1a;
  border-radius: 8px;
}

.chosen {
  opacity: 0.9;
  box-shadow: 0 8px 24px rgba(0, 0, 0, 0.6);
}

.drag {
  user-select: none;
}
</style>
