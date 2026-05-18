import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import axios from 'axios'

interface KanbanBoard {
  id: string
  title: string
  order: number
  user_id: string
}

interface KanbanColumn {
  id: string
  title: string
  order: number
  color: string
  is_static: boolean
  is_inbox_category: boolean
  board_id: string | null
}

export type InboxCategory = KanbanColumn

export const useKanbanStore = defineStore('kanban', () => {
  const boards = ref<KanbanBoard[]>([])
  const columns = ref<KanbanColumn[]>([])
  const currentBoardId = ref<string | null>(null)
  const loading = ref(false)
  const error = ref<string | null>(null)

  const api = axios.create({
    baseURL: '/api/v1/kanban',
    headers: {
      'Content-Type': 'application/json'
    }
  })

  // ==================== BOARDS ====================

  const fetchBoards = async () => {
    loading.value = true
    error.value = null
    try {
      const response = await api.get('/boards')
      boards.value = response.data
      
      // Set current board to first board
      if (!currentBoardId.value) {
        currentBoardId.value = boards.value[0]?.id || null
      }
    } catch (err: any) {
      error.value = err.response?.data?.detail || 'Ошибка загрузки досок'
      console.error('Error fetching boards:', err)
    } finally {
      loading.value = false
    }
  }

  const createBoard = async (boardData: Partial<KanbanBoard>) => {
    loading.value = true
    error.value = null
    try {
      const response = await api.post('/boards', boardData)
      boards.value.push(response.data)
      return response.data
    } catch (err: any) {
      error.value = err.response?.data?.detail || 'Ошибка создания доски'
      console.error('Error creating board:', err)
      throw err
    } finally {
      loading.value = false
    }
  }

  const updateBoard = async (boardId: string, boardData: Partial<KanbanBoard>) => {
    loading.value = true
    error.value = null
    try {
      const response = await api.put(`/boards/${boardId}`, boardData)
      const index = boards.value.findIndex(b => b.id === boardId)
      if (index !== -1) {
        boards.value[index] = response.data
      }
      return response.data
    } catch (err: any) {
      error.value = err.response?.data?.detail || 'Ошибка обновления доски'
      console.error('Error updating board:', err)
      throw err
    } finally {
      loading.value = false
    }
  }

  const deleteBoard = async (boardId: string) => {
    loading.value = true
    error.value = null
    try {
      await api.delete(`/boards/${boardId}`)
      boards.value = boards.value.filter(b => b.id !== boardId)
      
      // Switch to another board if current board was deleted
      if (currentBoardId.value === boardId) {
        currentBoardId.value = boards.value[0]?.id || null
      }
    } catch (err: any) {
      error.value = err.response?.data?.detail || 'Ошибка удаления доски'
      console.error('Error deleting board:', err)
      throw err
    } finally {
      loading.value = false
    }
  }

  const reorderBoards = async (boardIds: string[]) => {
    try {
      await api.post('/boards/reorder', boardIds)
      boardIds.forEach((id, index) => {
        const board = boards.value.find(b => b.id === id)
        if (board) board.order = index
      })
      boards.value.sort((a, b) => a.order - b.order)
    } catch (err: any) {
      console.error('Error reordering boards:', err)
    }
  }

  const setCurrentBoard = async (boardId: string) => {
    currentBoardId.value = boardId
    columns.value = []
    if (boardId === '' || boardId === null) {
      await fetchInboxCategories()
    } else {
      await fetchColumns()
    }
  }

  const currentBoard = computed(() => {
    return boards.value.find(b => b.id === currentBoardId.value) || null
  })

  // ==================== COLUMNS ====================

  const fetchColumns = async () => {
    if (!currentBoardId.value) return
    
    loading.value = true
    error.value = null
    try {
      const response = await api.get(`/boards/${currentBoardId.value}/columns`)
      columns.value = response.data
    } catch (err: any) {
      error.value = err.response?.data?.detail || 'Ошибка загрузки колонок'
      console.error('Error fetching columns:', err)
    } finally {
      loading.value = false
    }
  }

  const createColumn = async (columnData: Partial<KanbanColumn>) => {
    if (!currentBoardId.value) throw new Error('No board selected')
    
    loading.value = true
    error.value = null
    try {
      const response = await api.post(`/boards/${currentBoardId.value}/columns`, {
        ...columnData,
        board_id: currentBoardId.value
      })
      columns.value.push(response.data)
      return response.data
    } catch (err: any) {
      error.value = err.response?.data?.detail || 'Ошибка создания колонки'
      console.error('Error creating column:', err)
      throw err
    } finally {
      loading.value = false
    }
  }

  const updateColumn = async (columnId: string, columnData: Partial<KanbanColumn>) => {
    loading.value = true
    error.value = null
    try {
      const response = await api.put(`/columns/${columnId}`, columnData)
      const index = columns.value.findIndex(c => c.id === columnId)
      if (index !== -1) {
        columns.value[index] = response.data
      }
      return response.data
    } catch (err: any) {
      error.value = err.response?.data?.detail || 'Ошибка обновления колонки'
      console.error('Error updating column:', err)
      throw err
    } finally {
      loading.value = false
    }
  }

  const deleteColumn = async (columnId: string) => {
    loading.value = true
    error.value = null
    try {
      await api.delete(`/columns/${columnId}`)
      columns.value = columns.value.filter(c => c.id !== columnId)
    } catch (err: any) {
      error.value = err.response?.data?.detail || 'Ошибка удаления колонки'
      console.error('Error deleting column:', err)
      throw err
    } finally {
      loading.value = false
    }
  }

  const reorderColumns = async (columnIds: string[]) => {
    try {
      await api.post('/columns/reorder', columnIds)
      columnIds.forEach((id, index) => {
        const col = columns.value.find(c => c.id === id)
        if (col) col.order = index
      })
      columns.value.sort((a, b) => a.order - b.order)
    } catch (err: any) {
      console.error('Error reordering columns:', err)
    }
  }

  // ==================== INBOX CATEGORIES ====================
  
  const fetchInboxCategories = async () => {
    loading.value = true
    error.value = null
    try {
      const response = await api.get('/inbox/categories')
      columns.value = response.data
    } catch (err: any) {
      error.value = err.response?.data?.detail || 'Ошибка загрузки Inbox категорий'
      console.error('Error fetching inbox categories:', err)
    } finally {
      loading.value = false
    }
  }
  
  const createInboxCategory = async (columnData: Partial<KanbanColumn>) => {
    loading.value = true
    error.value = null
    try {
      const response = await api.post('/inbox/categories', columnData)
      columns.value.push(response.data)
      return response.data
    } catch (err: any) {
      error.value = err.response?.data?.detail || 'Ошибка создания Inbox категории'
      console.error('Error creating inbox category:', err)
      throw err
    } finally {
      loading.value = false
    }
  }
  
  return {
    boards,
    columns,
    currentBoardId,
    currentBoard,
    loading,
    error,
    fetchBoards,
    createBoard,
    updateBoard,
    deleteBoard,
    reorderBoards,
    setCurrentBoard,
    fetchColumns,
    createColumn,
    updateColumn,
    deleteColumn,
    reorderColumns,
    fetchInboxCategories,
    createInboxCategory
  }
})
