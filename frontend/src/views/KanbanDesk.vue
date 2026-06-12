<template>
  <div class="kanban-desk">
    <!-- Top Bar -->
    <div class="top-bar">
      <div class="time-display">{{ currentTime }}</div>
      <div class="menu-wrapper">
        <ThreeDotsMenu />
      </div>
    </div>

    <!-- Board Tabs (Browser-like tabs) -->
    <div class="board-tabs">
      <draggable
        v-model="boardOrder"
        class="tabs-container"
        group="boards"
        item-key="id"
        handle=".tab-drag-handle"
        @end="onBoardReorder"
      >
        <template #item="{ element: board }">
          <div
            class="board-tab"
            :class="{ 'tab-active': currentBoardId === board.id && !isInboxActive }"
            @click="selectBoard(board.id)"
          >
            <div class="tab-drag-handle" title="Перетащить вкладку">⋮⋮</div>
            <span class="tab-title">{{ board.title }}</span>
            <button
              v-if="boards.length > 1"
              class="tab-close"
              @click.stop="deleteBoard(board.id)"
              title="Закрыть вкладку"
            >✕</button>
          </div>
        </template>
        <template #footer>
          <!-- Add Board Button - inside draggable, right after tabs -->
          <button class="add-tab-btn" @click="showAddBoardModal = true" title="Добавить доску">
            +
          </button>
        </template>
      </draggable>
      
      <!-- Inbox Tab (always last) -->
      <div
        class="board-tab inbox-tab"
        :class="{ 'tab-active': isInboxActive }"
        @click="selectInbox"
      >
        <span class="tab-title">Inbox</span>
      </div>
    </div>

    <!-- Board Header -->
    <div class="board-header">
      <h1 class="board-title">{{ isInboxActive ? 'Inbox' : (currentBoard?.title || 'Kanban') }}</h1>
      <div class="board-meta">
        <span class="task-count">{{ tasksStore.tasks.length }} задач</span>
      </div>
    </div>

    <!-- Kanban Board -->
    <div class="kanban-board">
      <draggable
        v-model="columnOrder"
        class="kanban-columns"
        group="columns"
        item-key="key"
        handle=".column-drag-handle"
        @end="onColumnReorder"
      >
        <template #item="{ element: col }">
          <div
            class="kanban-column"
            :class="{ 'column-collapsed': collapsedColumns[col.key] }"
          >
            <!-- Column Header -->
            <div class="column-header" :class="{ 'header-collapsed': collapsedColumns[col.key] }">
              <div class="column-drag-handle" title="Перетащить колонку">
                ⋮⋮
              </div>
              <div class="column-header-left">
                <span class="column-dot" :class="`dot-${col.key}`"></span>
                <h3 class="column-title" :class="{ 'title-collapsed': collapsedColumns[col.key] }">{{ col.label }}</h3>
                <span class="column-count">{{ tasksByColumn(col.key).length }}</span>
              </div>
              <div class="header-buttons">
                <button
                  class="collapse-col-btn"
                  @click="toggleCollapse(col.key)"
                  type="button"
                  :title="collapsedColumns[col.key] ? 'Развернуть' : 'Свернуть'"
                >
                  {{ collapsedColumns[col.key] ? '▶' : '▼' }}
                </button>
                <button
                  class="del-col-btn"
                  v-if="canRemoveColumn(col.key)"
                  @click="removeColumn(col.key)"
                  type="button"
                  title="Удалить колонку"
                >✕</button>
              </div>
            </div>

            <!-- Column Content (collapsible) -->
            <template v-if="!collapsedColumns[col.key]">
              <!-- Draggable Task List -->
              <draggable
                class="column-body"
                v-model="columnTasks[col.key]"
                :group="{ name: 'tasks', pull: true, put: true }"
                item-key="id"
                @change="(e: any) => onTaskChange(e, col.key)"
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
              <div class="add-task-container">
                <!-- Кнопка добавления -->
                <button 
                  v-if="!isAddingTask[col.key]" 
                  class="add-task-btn-new"
                  @click="startAddTask(col.key)"
                >
                  + Добавить карточку
                </button>
               
                <!-- Поле ввода при добавлении -->
                <form 
                  v-else 
                  class="add-task-form" 
                  @submit.prevent="addTask(col.key)"
                  @mouseleave="cancelAddTask(col.key)"
                >
                  <input
                    :id="`task-input-${col.key}`"
                    :value="newTaskTitles[col.key]"
                    @input="updateTaskTitle(col.key, ($event.target as HTMLInputElement).value)"
                    placeholder="Введите название задачи..."
                    class="task-input"
                    @keydown.escape="cancelAddTask(col.key)"
                  />
                </form>
              </div>
            </template>
          </div>
        </template>
      </draggable>

      <!-- Add Column (at the end) - показываем и в Inbox и на досках -->
      <div class="add-col">
        <div class="add-col-inner">
          <p class="add-col-label">{{ isInboxActive ? 'Новая категория' : 'Новая колонка' }}</p>
          <form @submit.prevent="addColumn" class="add-col-form">
            <input
              v-model="newColTitle"
              :placeholder="isInboxActive ? 'Название категории...' : 'Название...'"
              class="task-input"
            />
            <button type="submit" class="add-task-btn" title="Создать">+</button>
          </form>
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

    <!-- Add Board Modal -->
    <div v-if="showAddBoardModal" class="modal-overlay" @click.self="showAddBoardModal = false">
      <div class="modal-content">
        <h2>Новая доска</h2>
        <form @submit.prevent="addBoard" class="add-board-form">
          <input
            v-model="newBoardTitle"
            placeholder="Название доски..."
            class="task-input"
          />
          <div class="modal-buttons">
            <button type="button" class="btn-cancel" @click="showAddBoardModal = false">Отмена</button>
            <button type="submit" class="btn-confirm">Создать</button>
          </div>
        </form>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted, onUnmounted, reactive, computed, nextTick, watch } from 'vue'
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

// Boards
const boards = computed(() => kanbanStore.boards)
const currentBoardId = computed(() => kanbanStore.currentBoardId)
const currentBoard = computed(() => kanbanStore.currentBoard)
const boardOrder = ref<{ id: string; title: string }[]>([])

// Inbox state
const isInboxActive = ref(true)

// Sync boardOrder with boards
watch(boards, (newBoards) => {
  if (boardOrder.value.length !== newBoards.length ||
      newBoards.some((b, i) => b.id !== boardOrder.value[i]?.id)) {
    boardOrder.value = [...newBoards]
  }
}, { immediate: true, deep: true })

// Select board
const selectBoard = async (boardId: string) => {
  isInboxActive.value = false
  await kanbanStore.setCurrentBoard(boardId)
  await initializeTasks()
}

// Select Inbox (always active by default)
const selectInbox = async () => {
  isInboxActive.value = true
  // Clear current board to show all tasks
  kanbanStore.setCurrentBoard('')
  // Загружаем Inbox категории вместо колонок доски
  await kanbanStore.fetchInboxCategories()
  await initializeTasks()
}

// Add board
const showAddBoardModal = ref(false)
const newBoardTitle = ref('')

const addBoard = async () => {
  const title = newBoardTitle.value.trim()
  if (!title) return
  
  try {
    const newBoard = await kanbanStore.createBoard({ title })
    await kanbanStore.setCurrentBoard(newBoard.id)
    await initializeTasks()
    newBoardTitle.value = ''
    showAddBoardModal.value = false
  } catch (err) {
    console.error('Failed to create board:', err)
  }
}

// Delete board
const deleteBoard = async (boardId: string) => {
  if (!confirm('Удалить эту доску? Все задачи будут перемещены на дефолтную доску.')) return
  
  try {
    await kanbanStore.deleteBoard(boardId)
    await initializeTasks()
  } catch (err) {
    console.error('Failed to delete board:', err)
  }
}

// Reorder boards
const onBoardReorder = () => {
  const newOrder = boardOrder.value.map(b => b.id)
  kanbanStore.reorderBoards(newOrder)
}

// Получаем колонки из store
const columns = computed(() => {
  // Если активна вкладка Inbox - показываем Inbox категории
  if (isInboxActive.value) {
    return kanbanStore.columns.map(col => ({
      key: col.id,
      label: col.title,
      color: col.color
    }))
  }
  // Иначе показываем колонки текущей доски
  return kanbanStore.columns.map(col => ({
    key: col.id,
    label: col.title,
    color: col.color
  }))
})

const newColTitle = ref('')
const newTaskTitles = reactive<Record<string, string>>({})
const isAddingTask = reactive<Record<string, boolean>>({})
const collapsedColumns = reactive<Record<string, boolean>>({})

const columnTasks = ref<Record<string, any[]>>({})

const distributeTasksToColumns = () => {
  columns.value.forEach(col => {
    if (isInboxActive.value && col.key === 'inbox') {
      columnTasks.value[col.key] = tasksStore.tasks.filter((t: any) =>
        !t.column_id && t.status === 'todo'
      )
    } else {
      columnTasks.value[col.key] = tasksStore.tasks.filter((t: any) => t.column_id === col.key)
    }
  })
}

watch(() => tasksStore.tasks, () => {
  distributeTasksToColumns()
}, { immediate: true, deep: true })

// Ref for column order (drag and drop) - синхронизирован с store
const columnOrder = ref<{ key: string; label: string; color?: string }[]>([])

watch(columns, (newColumns) => {
  distributeTasksToColumns()
  if (columnOrder.value.length !== newColumns.length || 
      newColumns.some((c, i) => c.key !== columnOrder.value[i]?.key)) {
    columnOrder.value = [...newColumns]
  }
  newColumns.forEach(col => {
    if (!newTaskTitles[col.key]) {
      newTaskTitles[col.key] = ''
    }
  })
}, { immediate: true })

// Toggle column collapse
const toggleCollapse = (colKey: string) => {
  collapsedColumns[colKey] = !collapsedColumns[colKey]
}

// Handle column reorder
const onColumnReorder = () => {
  // Сохраняем новый порядок в kanbanStore
  const newOrder = columnOrder.value.map(c => c.key)
  kanbanStore.reorderColumns(newOrder)
}

// Функции для управления добавлением задачи
const startAddTask = async (colKey: string) => {
  isAddingTask[colKey] = true
  newTaskTitles[colKey] = ''
  // Фокус на input после рендера
  await nextTick()
  const inputEl = document.querySelector(`#task-input-${colKey}`) as HTMLInputElement
  if (inputEl) {
    inputEl.focus()
  }
}

const cancelAddTask = (colKey: string) => {
  isAddingTask[colKey] = false
  newTaskTitles[colKey] = ''
}

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

  tasksStore.tasks.forEach((t: any) => {
    if (!t.status) {
      t.status = t.completed ? 'done' : 'todo'
    }
  })

  initializeTaskTitles()
}

// Используем статус из задачи напрямую
const tasksByColumn = (colKey: string) => {
  return columnTasks.value[colKey] || []
}

const onMove = () => true

const addColumn = async () => {
  const title = newColTitle.value.trim()
  if (!title) return
  try {
    let newCol
    if (isInboxActive.value) {
      // Создаём Inbox категорию
      newCol = await kanbanStore.createInboxCategory({ title, color: '#555555' })
    } else {
      // Создаём обычную колонку для доски
      newCol = await kanbanStore.createColumn({ title, color: '#555555' })
    }
    newTaskTitles[newCol.id] = ''
    newColTitle.value = ''
  } catch (err) {
    console.error('Failed to create column:', err)
  }
}

const removeColumn = async (colKey: string) => {
  // Не позволяем удалять колонку Inbox во вкладке Inbox
  if (isInboxActive.value && colKey === 'inbox') return
  
  // Не позволяем удалять последнюю колонку на доске
  if (!isInboxActive.value && kanbanStore.columns.length <= 1) return
  
  const column = kanbanStore.columns.find(c => c.id === colKey)
  if (!confirm(`Удалить колонку "${column?.title || colKey}"? Все задачи будут перемещены.`)) return
  
  const tasksToRemove = tasksByColumn(colKey)
  
  try {
    await kanbanStore.deleteColumn(colKey)
    delete newTaskTitles[colKey]
    
    // Переносим задачи в первую колонку
    if (kanbanStore.columns.length > 0) {
      const firstColumn = kanbanStore.columns[0]
      for (const t of tasksToRemove) {
        await tasksStore.updateTask(t.id, { status: firstColumn.id })
      }
    }
  } catch (err) {
    console.error('Failed to delete column:', err)
  }
}

const canRemoveColumn = (colKey: string) => {
  // Не позволяем удалять Inbox колонку во вкладке Inbox
  if (isInboxActive.value && colKey === 'inbox') return false
  
  const column = kanbanStore.columns.find(c => c.id === colKey)
  return kanbanStore.columns.length > 1 && !column?.is_static
}

const addTask = async (colKey: string) => {
  const title = newTaskTitles[colKey]?.trim()
  if (!title) {
    // Если пустое название - отменяем
    cancelAddTask(colKey)
    return
  }
  try {
    const taskData: any = {
      title,
      completed: false,
      priority: undefined,
      description: ''
    }
    
    if (isInboxActive.value && colKey === 'inbox') {
      // Для Inbox не устанавливаем column_id, задача будет в Inbox
      taskData.status = 'todo'
    } else {
      // Для обычных колонок устанавливаем column_id
      taskData.column_id = colKey
      taskData.status = colKey
    }
    
    await tasksStore.createTask(taskData)
    newTaskTitles[colKey] = ''
    // Закрываем режим добавления после создания
    isAddingTask[colKey] = false
  } catch (err) {
    console.error('Failed to create task:', err)
  }
}

const onTaskChange = async (evt: any, colKey: string) => {
  if (evt.added) {
    const task = evt.added.element
    const updateData: any = {
      completed: task.completed
    }
    
    if (isInboxActive.value && colKey === 'inbox') {
      // При перемещении в Inbox - убираем column_id
      updateData.column_id = null
      updateData.status = 'todo'
    } else {
      // При перемещении в обычную колонку - устанавливаем column_id
      updateData.column_id = colKey
      updateData.status = colKey
    }
    
    if (task && (task.status !== updateData.status || task.column_id !== updateData.column_id)) {
      const prevStatus = task.status
      const prevColumnId = task.column_id
      task.status = updateData.status
      task.column_id = updateData.column_id
      try {
        await tasksStore.updateTask(task.id, updateData)
      } catch (err) {
        console.error('Failed to update task status on server:', err)
        task.status = prevStatus
        task.column_id = prevColumnId
      }
    }
  }
  if (evt.moved) {
    const bulkItems: any[] = []
    columns.value.forEach((col, colIndex) => {
      const tasksInCol = columnTasks.value[col.key] || []
      tasksInCol.forEach((task: any, taskIndex: number) => {
        const updateData: any = {
          task_id: task.id,
          order: colIndex * 100 + taskIndex,
        }
        
        if (isInboxActive.value && col.key === 'inbox') {
          updateData.status = 'todo'
          updateData.column_id = null
        } else {
          updateData.status = col.key
          updateData.column_id = col.key
        }
        
        bulkItems.push(updateData)
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
}

let timeInterval: ReturnType<typeof setInterval>

onMounted(async () => {
  updateTime()
  timeInterval = setInterval(updateTime, 1000)
  
  await kanbanStore.fetchBoards()
  
  // Set Inbox as active by default
  isInboxActive.value = true
  kanbanStore.setCurrentBoard('')
  await kanbanStore.fetchInboxCategories()
  
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
    const updatedTask = tasksStore.tasks.find((t: any) => t.id === taskId)
    for (const colKey of Object.keys(columnTasks.value)) {
      const taskInCol = columnTasks.value[colKey].find((t: any) => t.id === taskId)
      if (taskInCol && updatedTask) {
        taskInCol.completed = updatedTask.completed
        break
      }
    }
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
      // Перезагружаем задачи
      tasksStore.fetchTasks()
    })
  }
}
</script>

<style scoped>
/* ─── Base ─────────────────────────────────────────────── */
.kanban-desk {
  width: 100%;
  height: 100vh;
  background-color: var(--bg-primary);
  color: var(--text-primary);
  display: flex;
  flex-direction: column;
  overflow: hidden;
}

/* ─── Top Bar ───────────────────────────────────────────── */
.top-bar {
  flex-shrink: 0;
  margin-top: 5px;
  display: flex;
  justify-content: space-between;
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

/* ─── Board Tabs ────────────────────────────────────────── */
.board-tabs {
  flex-shrink: 0;
  display: flex;
  align-items: center;
  padding: 8px 20px 0;
  gap: 4px;
  background: transparent;
  border-bottom: 1px solid #1e1e1e;
}

.tabs-container {
  display: flex;
  align-items: center;
  gap: 2px;
  flex-wrap: wrap;
}

.board-tab {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 8px;
  padding: 8px 16px;
  background: var(--bg-tertiary);
  border: 1px solid #2a2a2a;
  border-radius: 8px 8px 0 0;
  cursor: pointer;
  transition: all 0.2s;
  min-width: 120px;
  max-width: 200px;
  position: relative;
}

.board-tab:hover {
  background: #252525;
  border-color: #3a3a3a;
}

.board-tab.tab-active {
  background: #0f0f0f;
  border-color: #3a3a3a;
  border-bottom-color: #0f0f0f;
}

.board-tab.tab-default .tab-title {
  font-weight: 600;
}

.tab-drag-handle {
  font-size: 10px;
  color: #666;
  cursor: grab;
  opacity: 0;
  transition: opacity 0.2s;
}

.board-tab:hover .tab-drag-handle {
  opacity: 1;
}

.tab-title {
  font-size: 11px;
  color: #ccc;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
  text-align: center;
  display: block;
}

.board-tab.tab-active .tab-title {
  color: #fff;
}

.tab-close {
  background: none;
  border: none;
  color: #666;
  cursor: pointer;
  padding: 2px 6px;
  border-radius: 4px;
  font-size: 11px;
  transition: all 0.2s;
}

.tab-close:hover {
  background: #3a3a3a;
  color: #fff;
}

.add-tab-btn {
  background: var(--bg-tertiary);
  border: 1px dashed #3a3a3a;
  color: #666;
  width: 28px;
  height: 28px;
  border-radius: 8px;
  cursor: pointer;
  font-size: 14px;
  display: flex;
  align-items: center;
  justify-content: center;
  transition: all 0.2s;
  flex-shrink: 0;
  line-height: 1;
  margin-left: auto;
}

.add-tab-btn:hover {
  background: #252525;
  color: #fff;
  border-color: #3a3a3a;
}

/* ─── Inbox Tab ─────────────────────────────────────────── */
.inbox-tab {
  background: var(--bg-tertiary);
  border: 1px solid #2a2a2a;
  margin-left: auto;
}

.inbox-tab:hover {
  background: #252525;
  border-color: #3a3a3a;
}

.inbox-tab.tab-active {
  background: var(--bg-secondary);
  border-color: #3a3a3a;
  border-bottom-color: var(--bg-secondary);
}

/* ─── Board Header ──────────────────────────────────────── */
.board-header {
  flex-shrink: 0;
  padding: 20px 28px 0;
  display: flex;
  align-items: baseline;
  gap: 20px;
  border-bottom: 1px solid #80808021;
  padding-bottom: 18px;
}

.board-title {
  font-size: 42px;
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
  font-size: 11px;
  color: #555;
  font-weight: 400;
}

/* ─── Board Layout ──────────────────────────────────────── */
.kanban-board {
  flex: 1;
  padding: 24px 20px;
  overflow-x: auto;
  overflow-y: auto;
  display: flex;
  gap: 16px;
  align-items: flex-start;
  min-width: max-content;
  padding-bottom: 12px;
}

/* Override for draggable to align items at top */
.kanban-columns {
  align-items: flex-start;
  min-width: max-content;
  display: flex;
  gap: 16px;
}

/* ─── Column ────────────────────────────────────────────── */
.kanban-column {
  background: var(--bg-secondary);
  border: 1px solid #1e1e1e;
  border-radius: 12px;
  padding: 16px;
  width: 450px;
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
  font-size: 14px;
  font-weight: 600;
  color: #e0e0e0;
  letter-spacing: 0.02em;
}

.column-count {
  font-size: 10px;
  color: #444;
  background: var(--bg-tertiary);
  border: 1px solid #2a2a2a;
  border-radius: 10px;
  padding: 2px 8px;
}

.header-buttons {
  display: flex;
  gap: 4px;
}

.collapse-col-btn {
  background: transparent;
  border: none;
  color: #666;
  cursor: pointer;
  padding: 4px 8px;
  border-radius: 4px;
  font-size: 10px;
  transition: all 0.2s;
}

.collapse-col-btn:hover {
  background: var(--bg-tertiary);
  color: #fff;
}

.del-col-btn {
  background: transparent;
  border: none;
  color: #666;
  cursor: pointer;
  padding: 4px 8px;
  border-radius: 4px;
  font-size: 11px;
  transition: all 0.2s;
}

.del-col-btn:hover {
  background: #3a1a1a;
  color: #ff6b6b;
}

/* ─── Column Body ───────────────────────────────────────── */
.column-body {
  flex: 1;
  display: flex;
  flex-direction: column;
  gap: 8px;
  min-height: 100px;
  max-height: calc(100vh - 300px);
  overflow-y: auto;
  padding: 8px 4px 8px 0;
}

.kanban-card-wrapper {
  padding: 0 4px;
}

.column-body::-webkit-scrollbar {
  width: 6px;
}

.column-body::-webkit-scrollbar-track {
  background: #0a0a0a;
}

.column-body::-webkit-scrollbar-thumb {
  background: #2a2a2a;
  border-radius: 3px;
}

.column-body::-webkit-scrollbar-thumb:hover {
  background: #3a3a3a;
}

/* ─── Column Collapsed ─────────────────────────────────── */
.column-collapsed {
  min-height: auto;
}

.column-collapsed .column-body {
  display: none;
}

.header-collapsed {
  margin-bottom: 0;
  padding-bottom: 8px;
}

.title-collapsed {
  font-size: 11px;
}

/* ─── Task Card Wrapper ─────────────────────────────────── */
.kanban-card-wrapper {
  cursor: grab;
}

.kanban-card-wrapper:active {
  cursor: grabbing;
}

/* ─── Empty Column ─────────────────────────────────────── */
.empty-column {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: 40px 20px;
  color: #444;
  gap: 12px;
}

.empty-icon {
  font-size: 26px;
  opacity: 0.5;
}

/* ─── Add Task ─────────────────────────────────────────── */
.add-task-container {
  margin-top: 12px;
}

.add-task-btn-new {
  width: 100%;
  padding: 12px;
  background: var(--bg-tertiary);
  border: 1px dashed #3a3a3a;
  border-radius: 8px;
  color: #666;
  cursor: pointer;
  font-size: 11px;
  transition: all 0.2s;
}

.add-task-btn-new:hover {
  background: #252525;
  color: #fff;
  border-color: #3a3a3a;
}

.add-task-form {
  width: 100%;
}

.task-input {
  width: 100%;
  padding: 12px;
  background: #0a0a0a;
  border: 1px solid #2a2a2a;
  border-radius: 8px;
  color: #fff;
  font-size: 11px;
  outline: none;
  transition: border-color 0.2s;
}

.task-input:focus {
  border-color: #3a3a3a;
}

.task-input::placeholder {
  color: #444;
}

/* ─── Add Column ───────────────────────────────────────── */
.add-col {
  width: 300px;
  flex-shrink: 0;
  padding: 16px;
  border: 2px dashed #2a2a2a;
  border-radius: 12px;
  display: flex;
  align-items: center;
  justify-content: center;
  min-height: 100px;
}

.add-col-inner {
  width: 100%;
}

.add-col-label {
  font-size: 10px;
  color: #444;
  margin-bottom: 12px;
  text-align: center;
}

.add-col-form {
  display: flex;
  gap: 8px;
}

.add-task-btn {
  background: #3a3a3a;
  border: none;
  color: #fff;
  width: 40px;
  border-radius: 8px;
  cursor: pointer;
  font-size: 16px;
  transition: all 0.2s;
}

.add-task-btn:hover {
  background: #4a4a4a;
}

/* ─── Modal ───────────────────────────────────────────── */
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

.modal-content {
  background: var(--bg-tertiary);
  border: 1px solid #2a2a2a;
  border-radius: 16px;
  padding: 32px;
  width: 400px;
}

.modal-content h2 {
  margin: 0 0 24px;
  font-size: 19px;
  color: #fff;
}

.add-board-form {
  display: flex;
  flex-direction: column;
  gap: 20px;
}

.modal-buttons {
  display: flex;
  gap: 12px;
  justify-content: flex-end;
}

.btn-cancel,
.btn-confirm {
  padding: 12px 24px;
  border-radius: 8px;
  font-size: 11px;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.2s;
}

.btn-cancel {
  background: transparent;
  border: 1px solid #3a3a3a;
  color: #ccc;
}

.btn-cancel:hover {
  background: #252525;
  color: #fff;
}

.btn-confirm {
  background: #3a3a3a;
  border: none;
  color: #fff;
}

.btn-confirm:hover {
  background: #4a4a4a;
}

/* ─── Drag and Drop ───────────────────────────────────── */
.ghost {
  opacity: 0.4;
  background: var(--bg-tertiary);
}

.chosen {
  opacity: 0.8;
}

.drag {
  opacity: 0.5;
}
</style>
