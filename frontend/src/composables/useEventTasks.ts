import { ref, nextTick } from 'vue'
import dayjs from 'dayjs'

export interface EventTask {
  id: string
  title: string
  description?: string
  completed: boolean
}

export interface EventWithTasks {
  id: string | number
  start: string
  end: string
  description?: string
  eventTasks?: EventTask[]
  completed_task_count?: number
  title?: string
}

export interface TasksLayoutConfig {
  EVENT_PADDING: number
  TITLE_H: number
  TIME_H: number
  DESC_H: number
  TASK_H: number
  TASK_GAP: number
  PROGRESS_BAR_H: number
  ADD_TASK_H: number
  MORE_H: number
}

export function useEventTasks(
  hourHeight: import('vue').Ref<number> | number,
  config: TasksLayoutConfig,
  emit?: (event: string, ...args: any[]) => void
) {
  const hoveredEventId = ref<string | number | null>(null)
  const addTaskTitle = ref('')
  const activeAddTaskEventId = ref<string | number | null>(null)
  const quickAddEventId = ref<string | number | null>(null)
  const quickAddTitle = ref('')

  const editingTitleEventId = ref<string | number | null>(null)
  const editingTitleValue = ref('')
  const editingDescEventId = ref<string | number | null>(null)
  const editingDescValue = ref('')
  const tagPickerEventId = ref<string | number | null>(null)
  const titleInputRef = ref<HTMLInputElement | null>(null)

  function getHH(): number {
    return (hourHeight as import('vue').Ref<number>).value ?? (hourHeight as number)
  }

  function getTaskWord(count: number): string {
    const lastTwo = count % 100
    const lastOne = count % 10
    if (lastTwo >= 11 && lastTwo <= 14) return 'задач'
    if (lastOne === 1) return 'задача'
    if (lastOne >= 2 && lastOne <= 4) return 'задачи'
    return 'задач'
  }

  function getCurrentEventTimes(
    event: EventWithTasks,
    isResizingFn: (id: string | number) => boolean,
    resizeNewStart: import('vue').Ref<dayjs.Dayjs | null>,
    resizeNewEnd: import('vue').Ref<dayjs.Dayjs | null>
  ) {
    const start = isResizingFn(event.id) && resizeNewStart.value ? resizeNewStart.value : dayjs(event.start)
    const end = isResizingFn(event.id) && resizeNewEnd.value ? resizeNewEnd.value : dayjs(event.end)
    return { start, end }
  }

  function getVisibleTaskInfo(
    event: EventWithTasks,
    isResizingFn: (id: string | number) => boolean,
    resizeNewStart: import('vue').Ref<dayjs.Dayjs | null>,
    resizeNewEnd: import('vue').Ref<dayjs.Dayjs | null>
  ) {
    const tasks = event.eventTasks
    if (!tasks || tasks.length === 0) return { visible: 0, remaining: 0, eventHeight: 0 }

    const { start, end } = getCurrentEventTimes(event, isResizingFn, resizeNewStart, resizeNewEnd)
    const duration = end.diff(start, 'minute')
    const eventHeight = Math.max((duration / 60) * getHH(), 30)

    let usedHeight = config.EVENT_PADDING + config.TITLE_H + config.TIME_H
    if (event.description) usedHeight += config.DESC_H

    const available = eventHeight - usedHeight
    const taskHeight = config.TASK_H + config.TASK_GAP
    const availableForTasks = available - config.MORE_H
    const visible = Math.max(0, Math.floor(availableForTasks / taskHeight))
    const remaining = Math.max(0, tasks.length - visible)

    return { visible, remaining, eventHeight }
  }

  function canShowProgressBar(
    event: EventWithTasks,
    isResizingFn: (id: string | number) => boolean,
    resizeNewStart: import('vue').Ref<dayjs.Dayjs | null>,
    resizeNewEnd: import('vue').Ref<dayjs.Dayjs | null>
  ): boolean {
    const info = getVisibleTaskInfo(event, isResizingFn, resizeNewStart, resizeNewEnd)
    if (info.remaining > 0 || !event.eventTasks?.length || event.eventTasks.length < 5) return false
    const taskHeight = config.TASK_H + config.TASK_GAP
    const allTasksHeight = event.eventTasks.length * taskHeight - config.TASK_GAP
    let usedHeight = config.EVENT_PADDING + config.TITLE_H + config.TIME_H
    if (event.description) usedHeight += config.DESC_H
    usedHeight += allTasksHeight + config.MORE_H
    return info.eventHeight - usedHeight >= config.PROGRESS_BAR_H
  }

  function showTaskBadge(
    event: EventWithTasks,
    isResizingFn: (id: string | number) => boolean,
    resizeNewStart: import('vue').Ref<dayjs.Dayjs | null>,
    resizeNewEnd: import('vue').Ref<dayjs.Dayjs | null>
  ): boolean {
    const info = getVisibleTaskInfo(event, isResizingFn, resizeNewStart, resizeNewEnd)
    return (event.eventTasks?.length ?? 0) > 0 && info.visible === 0
  }

  function canShowAddTask(
    event: EventWithTasks,
    isResizingFn: (id: string | number) => boolean,
    resizeNewStart: import('vue').Ref<dayjs.Dayjs | null>,
    resizeNewEnd: import('vue').Ref<dayjs.Dayjs | null>
  ): boolean {
    const info = getVisibleTaskInfo(event, isResizingFn, resizeNewStart, resizeNewEnd)
    const taskHeight = config.TASK_H + config.TASK_GAP
    const visibleTasksHeight = info.visible * taskHeight
    let usedHeight = config.EVENT_PADDING + config.TITLE_H + config.TIME_H
    if (event.description) usedHeight += config.DESC_H
    usedHeight += visibleTasksHeight + config.MORE_H
    const remaining = info.eventHeight - usedHeight
    if (info.visible > 0 && info.remaining === 0) {
      return remaining >= config.PROGRESS_BAR_H + config.ADD_TASK_H
    }
    return remaining >= config.ADD_TASK_H
  }

  function getProgressPercent(event: EventWithTasks): number {
    if (!event.eventTasks || event.eventTasks.length === 0) return 0
    const completed = event.eventTasks.filter(t => t.completed).length
    return Math.round((completed / event.eventTasks.length) * 100)
  }

  async function toggleTaskInline(task: EventTask, calendarEvent: EventWithTasks) {
    try {
      const res = await fetch(`/api/v1/tasks/${task.id}`, {
        method: 'PUT',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ completed: !task.completed })
      })
      if (res.ok) {
        task.completed = !task.completed
        if (calendarEvent.eventTasks) {
          calendarEvent.completed_task_count = calendarEvent.eventTasks.filter(t => t.completed).length
        }
      }
    } catch (e) {
      console.error('Failed to toggle task:', e)
    }
  }

  function submitAddTask(event: EventWithTasks, emitFn?: (event: string, ...args: any[]) => void) {
    const title = addTaskTitle.value.trim()
    if (!title) return
    ;(emitFn || emit)?.(data('add-task-to-event'), { event, title })
    addTaskTitle.value = ''
  }

  function cancelAddTask() {
    addTaskTitle.value = ''
    activeAddTaskEventId.value = null
  }

  function handleAddTaskBlur() {
    if (!addTaskTitle.value.trim()) {
      activeAddTaskEventId.value = null
    }
  }

  function toggleQuickAdd(event: EventWithTasks) {
    if (quickAddEventId.value === event.id) {
      cancelQuickAdd()
    } else {
      quickAddEventId.value = event.id
      quickAddTitle.value = ''
      nextTick(() => {
        const el = document.querySelector('.event-quick-add-input') as HTMLInputElement
        el?.focus()
      })
    }
  }

  function submitQuickAdd(event: EventWithTasks, emitFn?: (event: string, ...args: any[]) => void) {
    const title = quickAddTitle.value.trim()
    if (!title) return
    ;(emitFn || emit)?.(data('add-task-to-event'), { event, title })
    quickAddEventId.value = null
    quickAddTitle.value = ''
  }

  function cancelQuickAdd() {
    quickAddEventId.value = null
    quickAddTitle.value = ''
  }

  // --- Inline editing ---
  function startEditTitle(event: EventWithTasks) {
    editingTitleValue.value = event.title || ''
    editingTitleEventId.value = event.id
    nextTick(() => {
      titleInputRef.value?.focus()
      document.addEventListener('mousedown', onDocumentMouseDown)
    })
  }

  function onDocumentMouseDown(e: MouseEvent) {
    if (!editingTitleEventId.value) {
      document.removeEventListener('mousedown', onDocumentMouseDown)
      return
    }
    const input = titleInputRef.value
    if (input && !input.contains(e.target as Node)) {
      cancelTitleEdit()
      document.removeEventListener('mousedown', onDocumentMouseDown)
    }
  }

  function saveTitle(event: EventWithTasks, emitFn?: (event: string, ...args: any[]) => void) {
    const val = editingTitleValue.value.trim()
    if (val && val !== event.title && (emitFn || emit)) {
      ;(emitFn || emit)!(data('event-update'), { event, changes: { title: val } })
    }
    editingTitleEventId.value = null
    document.removeEventListener('mousedown', onDocumentMouseDown)
  }

  function cancelTitleEdit() {
    editingTitleEventId.value = null
    document.removeEventListener('mousedown', onDocumentMouseDown)
  }

  function onTitleInputMouseDown(e: MouseEvent, event: EventWithTasks) {
    if (editingTitleEventId.value !== event.id) return
    const startX = e.clientX
    const startY = e.clientY
    const onMove = (e: MouseEvent) => {
      if (Math.abs(e.clientX - startX) > 3 || Math.abs(e.clientY - startY) > 3) {
        saveTitle(event)
        document.removeEventListener('mousemove', onMove)
        document.removeEventListener('mouseup', onUp)
      }
    }
    const onUp = () => {
      document.removeEventListener('mousemove', onMove)
      document.removeEventListener('mouseup', onUp)
    }
    document.addEventListener('mousemove', onMove)
    document.addEventListener('mouseup', onUp)
  }

  function startEditDesc(event: EventWithTasks) {
    editingDescValue.value = event.description || ''
    editingDescEventId.value = event.id
  }

  function saveDesc(event: EventWithTasks, emitFn?: (event: string, ...args: any[]) => void) {
    const val = editingDescValue.value.trim()
    if (val !== event.description && (emitFn || emit)) {
      ;(emitFn || emit)!(data('event-update'), { event, changes: { description: val || '' } })
    }
    editingDescEventId.value = null
  }

  function cancelDescEdit() {
    editingDescEventId.value = null
  }

  function selectTag(
    event: EventWithTasks & { tag_id?: string; color?: string },
    tagId: string | null,
    tags: { id: string; color: string }[],
    emitFn?: (event: string, ...args: any[]) => void
  ) {
    const curTagId = (event as any).tag_id || ''
    if (tagId !== curTagId) {
      const tag = tagId ? tags.find(t => t.id === tagId) : null
      ;(emitFn || emit)?.(data('event-update'), { event, changes: { tag_id: tag?.id || '', color: tag?.color || '' } })
    }
    tagPickerEventId.value = null
  }

  function handleEventClick(e: MouseEvent, calEvent?: EventWithTasks, emitFn?: (event: string, ...args: any[]) => void) {
    if (!calEvent) return
    const container = e.currentTarget as HTMLElement
    const iconAreas = container.querySelectorAll('.event-tag-icon-wrapper, .event-tag-icon')
    for (const el of iconAreas) {
      const r = el.getBoundingClientRect()
      if (e.clientX >= r.left && e.clientX <= r.right && e.clientY >= r.top && e.clientY <= r.bottom) {
        ;(emitFn || emit)?.(data('toggle-tags-panel'))
        return
      }
    }
    const titleEl = container.querySelector('[data-edit-title]')
    if (titleEl) {
      const r = titleEl.getBoundingClientRect()
      if (e.clientX >= r.left && e.clientX <= r.right && e.clientY >= r.top && e.clientY <= r.bottom) {
        startEditTitle(calEvent)
      }
    }
  }

  return {
    hoveredEventId,
    addTaskTitle,
    activeAddTaskEventId,
    quickAddEventId,
    quickAddTitle,
    editingTitleEventId,
    editingTitleValue,
    editingDescEventId,
    editingDescValue,
    tagPickerEventId,
    titleInputRef,
    getTaskWord,
    getCurrentEventTimes,
    getVisibleTaskInfo,
    canShowProgressBar,
    showTaskBadge,
    canShowAddTask,
    getProgressPercent,
    toggleTaskInline,
    submitAddTask,
    cancelAddTask,
    handleAddTaskBlur,
    toggleQuickAdd,
    submitQuickAdd,
    cancelQuickAdd,
    startEditTitle,
    saveTitle,
    cancelTitleEdit,
    onTitleInputMouseDown,
    startEditDesc,
    saveDesc,
    cancelDescEdit,
    selectTag,
    handleEventClick
  }
}

function data(name: string): string {
  return name
}
