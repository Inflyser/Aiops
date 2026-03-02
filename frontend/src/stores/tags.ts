import { defineStore } from 'pinia'
import { ref } from 'vue'
import axios from 'axios'

interface Tag {
  id: string
  name: string
  color: string
  icon?: string
  user_id: string
}

export const useTagsStore = defineStore('tags', () => {
  const tags = ref<Tag[]>([])
  const loading = ref(false)
  const error = ref<string | null>(null)

  const api = axios.create({
    baseURL: '/api/v1/tags',
    headers: {
      'Content-Type': 'application/json'
    }
  })

  const fetchTags = async () => {
    loading.value = true
    error.value = null
    try {
      const response = await api.get('/')
      tags.value = response.data
    } catch (err: any) {
      error.value = err.response?.data?.detail || 'Ошибка загрузки тегов'
      console.error('Error fetching tags:', err)
    } finally {
      loading.value = false
    }
  }

  const createTag = async (tagData: { name: string; color: string; icon?: string }) => {
    loading.value = true
    error.value = null
    try {
      const response = await api.post('/', tagData)
      tags.value.push(response.data)
      return response.data
    } catch (err: any) {
      error.value = err.response?.data?.detail || 'Ошибка создания тега'
      console.error('Error creating tag:', err)
      throw err
    } finally {
      loading.value = false
    }
  }

  const updateTag = async (tagId: string, tagData: { name?: string; color?: string; icon?: string }) => {
    loading.value = true
    error.value = null
    try {
      const response = await api.put(`/${tagId}`, tagData)
      const index = tags.value.findIndex(t => t.id === tagId)
      if (index !== -1) {
        tags.value[index] = response.data
      }
      return response.data
    } catch (err: any) {
      error.value = err.response?.data?.detail || 'Ошибка обновления тега'
      console.error('Error updating tag:', err)
      throw err
    } finally {
      loading.value = false
    }
  }

  const deleteTag = async (tagId: string) => {
    loading.value = true
    error.value = null
    try {
      await api.delete(`/${tagId}`)
      tags.value = tags.value.filter(t => t.id !== tagId)
    } catch (err: any) {
      error.value = err.response?.data?.detail || 'Ошибка удаления тега'
      console.error('Error deleting tag:', err)
      throw err
    } finally {
      loading.value = false
    }
  }

  return {
    tags,
    loading,
    error,
    fetchTags,
    createTag,
    updateTag,
    deleteTag
  }
})
