<template>
  <div class="statistics-page">
    <!-- Top Bar -->
    <div class="top-bar">
      <div class="time-display">{{ currentTime }}</div>
      <div class="menu-wrapper">
        <ThreeDotsMenu />
      </div>
    </div>

    <!-- Header -->
    <div class="stats-header">
      <h1 class="stats-title">Статистика</h1>
      <div class="period-selector">
        <button 
          v-for="period in periods" 
          :key="period.value"
          class="period-btn"
          :class="{ active: currentPeriod === period.value }"
          @click="currentPeriod = period.value"
        >
          {{ period.label }}
        </button>
      </div>
    </div>

    <!-- Bar Chart -->
    <div class="chart-container">
      <h2 class="chart-title">Время по тегам</h2>
      <div class="bar-chart">
        <div 
          v-for="tagStat in tagStats" 
          :key="tagStat.tagId"
          class="bar-row"
        >
          <div class="bar-label">{{ tagStat.tagName }}</div>
          <div class="bar-wrapper">
            <div 
              class="bar"
              :style="{ 
                width: tagStat.percentage + '%',
                backgroundColor: tagStat.color
              }"
            >
              <span class="bar-value">{{ tagStat.hours.toFixed(1) }}ч</span>
            </div>
          </div>
        </div>
        <div v-if="tagStats.length === 0" class="no-data">
          Нет данных за выбранный период
        </div>
      </div>
    </div>

    <!-- Summary -->
    <div class="summary">
      <div class="summary-item">
        <span class="summary-label">Всего событий:</span>
        <span class="summary-value">{{ totalEvents }}</span>
      </div>
      <div class="summary-item">
        <span class="summary-label">Общее время:</span>
        <span class="summary-value">{{ totalHours.toFixed(1) }} часов</span>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted, onUnmounted, watch } from 'vue'
import dayjs from 'dayjs'
import 'dayjs/locale/ru'
import axios from 'axios'
import { useTagsStore } from '../stores/tags'
import ThreeDotsMenu from '../components/ui/ThreeDotsMenu.vue'

dayjs.locale('ru')

const tagsStore = useTagsStore()

// Current time
const currentTime = ref('')
const updateTime = () => {
  currentTime.value = dayjs().format('HH:mm DD MMMM')
}
let timeInterval: ReturnType<typeof setInterval>

onMounted(() => {
  updateTime()
  timeInterval = setInterval(updateTime, 1000)
})

onUnmounted(() => {
  if (timeInterval) {
    clearInterval(timeInterval)
  }
})

// Local state for statistics
const statisticsEvents = ref<any[]>([])
const loading = ref(false)

const periods = [
  { value: 'week', label: 'Неделя' },
  { value: 'month', label: 'Месяц' },
  { value: 'year', label: 'Год' }
]

const currentPeriod = ref('week')

// Load events for statistics
const loadStatistics = async () => {
  loading.value = true
  const now = dayjs()
  let startDate: dayjs.Dayjs
  
  switch (currentPeriod.value) {
    case 'week':
      startDate = now.startOf('week')
      break
    case 'month':
      startDate = now.startOf('month')
      break
    case 'year':
      startDate = now.startOf('year')
      break
    default:
      startDate = now.startOf('week')
  }
  
  try {
    const startStr = startDate.format('YYYY-MM-DD')
    const endStr = now.format('YYYY-MM-DD')
    console.log('Loading statistics:', startStr, 'to', endStr)
    
    const response = await axios.get('/api/v1/calendar/', {
      params: {
        start: startStr,
        end: endStr
      }
    })
    console.log('Statistics loaded:', response.data.length, 'events')
    statisticsEvents.value = response.data
  } catch (err: any) {
    console.error('Error loading statistics:', err)
    statisticsEvents.value = []
  } finally {
    loading.value = false
  }
}

// Compute tag statistics
const tagStats = computed(() => {
  const tagsMap = new Map()
  
  // Get all tags
  const tags = tagsStore.tags
  tags.forEach(tag => {
    tagsMap.set(tag.id, {
      tagId: tag.id,
      tagName: tag.name,
      color: tag.color,
      totalMinutes: 0
    })
  })
  
  // Calculate time spent on each tag
  statisticsEvents.value.forEach(event => {
    const tagId = event.tag_id
    if (tagId && tagsMap.has(tagId)) {
      const start = dayjs(event.start)
      const end = dayjs(event.end)
      const durationMinutes = end.diff(start, 'minute')
      const stat = tagsMap.get(tagId)
      stat.totalMinutes += durationMinutes
    }
  })
  
  // Convert to hours and calculate percentages
  const stats = Array.from(tagsMap.values())
    .filter(stat => stat.totalMinutes > 0)
    .map(stat => ({
      ...stat,
      hours: stat.totalMinutes / 60
    }))
  
  // Find max hours for percentage calculation
  const maxHours = Math.max(...stats.map(s => s.hours), 1)
  
  return stats.map(stat => ({
    ...stat,
    percentage: (stat.hours / maxHours) * 100
  }))
})

const totalEvents = computed(() => statisticsEvents.value.length)

const totalHours = computed(() => {
  return statisticsEvents.value.reduce((total, event) => {
    const start = dayjs(event.start)
    const end = dayjs(event.end)
    return total + end.diff(start, 'hour', true)
  }, 0)
})

// Load data on mount and when period changes
onMounted(async () => {
  console.log('Statistics mounted, fetching tags and events...')
  await tagsStore.fetchTags()
  console.log('Tags loaded:', tagsStore.tags.length)
  await loadStatistics()
})

watch(currentPeriod, async () => {
  await loadStatistics()
})
</script>

<style scoped>
.statistics-page {
  padding: 20px;
  height: 100vh;
  background-color: #050505;
  color: #ffffff;
  overflow-y: auto;
}

/* Top Bar */
.top-bar {
  margin-top: 5px;
  display: flex;
  align-items: center;
  padding: 10px 20px;
  flex-shrink: 0;
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
  font-size: 22px;
  color: #ffffff;
  font-weight: 500;
}

.stats-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  margin-bottom: 40px;
}

.stats-title {
  font-size: 52px;
  font-weight: bold;
  margin: 0;
}

.period-selector {
  display: flex;
  gap: 10px;
  background-color: #0f0f0f;
  padding: 5px;
  border-radius: 10px;
}

.period-btn {
  background: transparent;
  border: none;
  color: #888;
  padding: 10px 20px;
  cursor: pointer;
  font-size: 16px;
  font-weight: 600;
  border-radius: 8px;
  transition: all 0.2s;
}

.period-btn:hover {
  color: #fff;
}

.period-btn.active {
  background: #333;
  color: #fff;
}

.chart-container {
  background: #0f0f0f;
  border-radius: 12px;
  padding: 24px;
  margin-bottom: 30px;
}

.chart-title {
  font-size: 24px;
  margin: 0 0 24px;
  color: #ccc;
}

.bar-chart {
  display: flex;
  flex-direction: column;
  gap: 16px;
}

.bar-row {
  display: flex;
  align-items: center;
  gap: 16px;
}

.bar-label {
  width: 120px;
  font-size: 16px;
  color: #aaa;
  text-align: right;
  flex-shrink: 0;
}

.bar-wrapper {
  flex: 1;
  background: #1a1a1a;
  border-radius: 8px;
  height: 40px;
  overflow: hidden;
}

.bar {
  height: 100%;
  border-radius: 8px;
  display: flex;
  align-items: center;
  justify-content: flex-end;
  padding-right: 12px;
  min-width: 60px;
  transition: width 0.3s ease;
}

.bar-value {
  font-size: 14px;
  font-weight: 600;
  color: white;
  white-space: nowrap;
}

.no-data {
  text-align: center;
  color: #666;
  font-size: 18px;
  padding: 40px;
}

.summary {
  display: flex;
  gap: 40px;
  justify-content: center;
}

.summary-item {
  background: #0f0f0f;
  padding: 20px 40px;
  border-radius: 12px;
  display: flex;
  flex-direction: column;
  align-items: center;
}

.summary-label {
  font-size: 14px;
  color: #888;
  margin-bottom: 8px;
}

.summary-value {
  font-size: 32px;
  font-weight: bold;
}
</style>
