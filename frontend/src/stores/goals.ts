import { defineStore } from 'pinia'
import { ref } from 'vue'
import axios from 'axios'

export interface Goal {
  id: string
  title: string
  description?: string
  status: string
  goal_type: string
  target_value?: number
  target_unit?: string
  current_value: number
  deadline?: string
  icon?: string
  is_featured: boolean
  featured_position?: number
  order: number
  user_id: string
  created_at: string
  updated_at?: string
}

export const useGoalsStore = defineStore('goals', () => {
  const goals = ref<Goal[]>([])
  const loading = ref(false)
  const error = ref<string | null>(null)

  const api = axios.create({
    baseURL: '/api/v1/goals',
    headers: {
      'Content-Type': 'application/json'
    }
  })

  const fetchGoals = async () => {
    loading.value = true
    error.value = null
    try {
      const response = await api.get('/')
      goals.value = response.data
    } catch (err: any) {
      error.value = err.response?.data?.detail || 'Ошибка загрузки целей'
      console.error('Error fetching goals:', err)
    } finally {
      loading.value = false
    }
  }

  const createGoal = async (goalData: Partial<Goal>) => {
    loading.value = true
    error.value = null
    try {
      const response = await api.post('/', {
        ...goalData,
        goal_type: goalData.goal_type || 'concrete',
        status: goalData.status || 'active'
      })
      goals.value.push(response.data)
      return response.data
    } catch (err: any) {
      error.value = err.response?.data?.detail || 'Ошибка создания цели'
      console.error('Error creating goal:', err)
      throw err
    } finally {
      loading.value = false
    }
  }

  const updateGoal = async (goalId: string, goalData: Partial<Goal>) => {
    loading.value = true
    error.value = null
    try {
      const response = await api.put(`/${goalId}`, goalData)
      const index = goals.value.findIndex(g => g.id === goalId)
      if (index !== -1) {
        goals.value[index] = response.data
      }
      return response.data
    } catch (err: any) {
      error.value = err.response?.data?.detail || 'Ошибка обновления цели'
      console.error('Error updating goal:', err)
      throw err
    } finally {
      loading.value = false
    }
  }

  const deleteGoal = async (goalId: string) => {
    loading.value = true
    error.value = null
    try {
      await api.delete(`/${goalId}`)
      goals.value = goals.value.filter(g => g.id !== goalId)
    } catch (err: any) {
      error.value = err.response?.data?.detail || 'Ошибка удаления цели'
      console.error('Error deleting goal:', err)
      throw err
    } finally {
      loading.value = false
    }
  }

  return {
    goals,
    loading,
    error,
    fetchGoals,
    createGoal,
    updateGoal,
    deleteGoal
  }
})
