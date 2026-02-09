import { defineStore } from 'pinia'
import { ref } from 'vue'
import axios from 'axios'

interface Task {
  id: string
  title: string
  description?: string
  completed: boolean
  due_date?: string
  priority: string
  tags?: string[]
  project_id?: string
  user_id: string
  created_at: string
  updated_at?: string
}

export const useTasksStore = defineStore('tasks', () => {
  const tasks = ref<Task[]>([])
  const loading = ref(false)
  const error = ref<string | null>(null)

  const api = axios.create({
    baseURL: import.meta.env.VITE_API_BASE_URL || '/api/v1/tasks',
    headers: {
      'Content-Type': 'application/json'
    }
  })

  const fetchTasks = async (completed?: boolean, projectId?: string) => {
    loading.value = true
    error.value = null
    try {
      const params: any = {}
      if (completed !== undefined) params.completed = completed
      if (projectId) params.project_id = projectId
      
      const response = await api.get('/', { params })
      tasks.value = response.data
    } catch (err: any) {
      error.value = err.response?.data?.detail || 'Ошибка загрузки задач'
      console.error('Error fetching tasks:', err)
    } finally {
      loading.value = false
    }
  }

  const createTask = async (taskData: Partial<Task>) => {
    loading.value = true
    error.value = null
    try {
      const response = await api.post('/', taskData)
      tasks.value.push(response.data)
      return response.data
    } catch (err: any) {
      error.value = err.response?.data?.detail || 'Ошибка создания задачи'
      console.error('Error creating task:', err)
      throw err
    } finally {
      loading.value = false
    }
  }

  const updateTask = async (taskId: string, taskData: Partial<Task>) => {
    loading.value = true
    error.value = null
    try {
      const response = await api.put(`/${taskId}`, taskData)
      const index = tasks.value.findIndex(t => t.id === taskId)
      if (index !== -1) {
        tasks.value[index] = response.data
      }
      return response.data
    } catch (err: any) {
      error.value = err.response?.data?.detail || 'Ошибка обновления задачи'
      console.error('Error updating task:', err)
      throw err
    } finally {
      loading.value = false
    }
  }

  const deleteTask = async (taskId: string) => {
    loading.value = true
    error.value = null
    try {
      await api.delete(`/${taskId}`)
      tasks.value = tasks.value.filter(t => t.id !== taskId)
    } catch (err: any) {
      error.value = err.response?.data?.detail || 'Ошибка удаления задачи'
      console.error('Error deleting task:', err)
      throw err
    } finally {
      loading.value = false
    }
  }

  const toggleTask = async (taskId: string) => {
    const task = tasks.value.find(t => t.id === taskId)
    if (task) {
      await updateTask(taskId, { completed: !task.completed })
    }
  }

  return {
    tasks,
    loading,
    error,
    fetchTasks,
    createTask,
    updateTask,
    deleteTask,
    toggleTask
  }
})




