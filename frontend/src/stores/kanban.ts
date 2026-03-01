import { defineStore } from 'pinia'
import { ref } from 'vue'
import axios from 'axios'

interface KanbanColumn {
  id: string
  title: string
  order: number
  color: string
  user_id: string
}

export const useKanbanStore = defineStore('kanban', () => {
  const columns = ref<KanbanColumn[]>([])
  const loading = ref(false)
  const error = ref<string | null>(null)

  const api = axios.create({
    baseURL: '/api/v1/kanban',
    headers: {
      'Content-Type': 'application/json'
    }
  })

  const fetchColumns = async () => {
    loading.value = true
    error.value = null
    try {
      const response = await api.get('/')
      columns.value = response.data
    } catch (err: any) {
      error.value = err.response?.data?.detail || 'Ошибка загрузки колонок'
      console.error('Error fetching columns:', err)
    } finally {
      loading.value = false
    }
  }

  const createColumn = async (columnData: Partial<KanbanColumn>) => {
    loading.value = true
    error.value = null
    try {
      const response = await api.post('/', columnData)
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
      const response = await api.put(`/${columnId}`, columnData)
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
      await api.delete(`/${columnId}`)
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
      await api.post('/reorder', columnIds)
      columnIds.forEach((id, index) => {
        const col = columns.value.find(c => c.id === id)
        if (col) col.order = index
      })
      columns.value.sort((a, b) => a.order - b.order)
    } catch (err: any) {
      console.error('Error reordering columns:', err)
    }
  }

  const updateColumnOrder = async (columnIds: string[]) => {
    await reorderColumns(columnIds)
  }

  return {
    columns,
    loading,
    error,
    fetchColumns,
    createColumn,
    updateColumn,
    deleteColumn,
    reorderColumns,
    updateColumnOrder
  }
})
