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

    <!-- Navigation -->
    <div class="nav-controls">
      <button class="nav-btn" @click="goPrev"><</button>
      <div class="current-period">
        <span v-if="currentPeriod === 'day'">{{ currentDate.format('DD MMMM YYYY') }}</span>
        <span v-else-if="currentPeriod === 'week'">{{ weekRange }}</span>
        <span v-else-if="currentPeriod === 'month'">{{ currentDate.format('MMMM YYYY') }}</span>
        <span v-else-if="currentPeriod === 'year'">{{ currentDate.format('YYYY') }}</span>
      </div>
      <button class="nav-btn" @click="goNext">></button>
    </div>

    <!-- Day View: Percentage Chart -->
    <div v-if="currentPeriod === 'day'" class="chart-container">
      <h2 class="chart-title">Загруженность дня</h2>
      <div class="day-percentage">
        <div class="percentage-ring">
          <svg viewBox="0 0 100 100" class="percentage-svg">
            <circle cx="50" cy="50" r="45" fill="none" stroke="#333" stroke-width="8" />
            <circle 
              cx="50" cy="50" r="45" 
              fill="none" 
              stroke="#4a90e2" 
              stroke-width="8"
              stroke-linecap="round"
              :stroke-dasharray="circumference"
              :stroke-dashoffset="dashOffset"
              transform="rotate(-90 50 50)"
            />
          </svg>
          <div class="percentage-text">
            <span class="percentage-value">{{ dayPercentage }}%</span>
            <span class="percentage-label">дня занято</span>
          </div>
        </div>
        <div class="day-details">
          <div class="detail-item">
            <span class="detail-label">Занято:</span>
            <span class="detail-value">{{ occupiedHours.toFixed(1) }}ч</span>
          </div>
          <div class="detail-item">
            <span class="detail-label">Свободно:</span>
            <span class="detail-value">{{ freeHours.toFixed(1) }}ч</span>
          </div>
          <div class="detail-item">
            <span class="detail-label">Всего событий:</span>
            <span class="detail-value">{{ dayEvents.length }}</span>
          </div>
        </div>
      </div>
    </div>

    <!-- Week View -->
    <div v-else-if="currentPeriod === 'week'" class="chart-container">
      <h2 class="chart-title">Загруженность по дням недели</h2>
      <div class="week-chart">
        <div 
          v-for="(day, index) in weekDays" 
          :key="index"
          class="week-day"
        >
          <div class="week-day-label">{{ day.name }}</div>
          <div class="week-day-bar">
            <div 
              class="week-day-fill"
              :style="{ height: day.percentage + '%', backgroundColor: day.color }"
            ></div>
          </div>
          <div class="week-day-percentage">{{ day.percentage }}%</div>
          <div class="week-day-hours">{{ day.hours.toFixed(1) }}ч</div>
        </div>
      </div>
    </div>

    <!-- Month View -->
    <div v-else-if="currentPeriod === 'month'" class="chart-container">
      <h2 class="chart-title">Загруженность по дням месяца</h2>
      <div class="month-chart">
        <div 
          v-for="(day, index) in monthDays" 
          :key="index"
          class="month-day"
          :class="{ 'has-events': day.events > 0 }"
          :style="{ backgroundColor: day.color }"
          :title="`${day.date}: ${day.events} событий, ${day.percentage}%`"
        >
          <span class="month-day-number">{{ day.dayNumber }}</span>
        </div>
      </div>
    </div>

    <!-- Year View -->
    <div v-else-if="currentPeriod === 'year'" class="chart-container">
      <h2 class="chart-title">Загруженность по месяцам</h2>
      <div class="year-chart">
        <div 
          v-for="(month, index) in yearMonths" 
          :key="index"
          class="year-month"
        >
          <div class="year-month-label">{{ month.name }}</div>
          <div class="year-month-bar">
            <div 
              class="year-month-fill"
              :style="{ height: month.percentage + '%', backgroundColor: month.color }"
            ></div>
          </div>
          <div class="year-month-hours">{{ month.hours.toFixed(0) }}ч</div>
        </div>
      </div>
    </div>

    <!-- Tag Statistics -->
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

// Periods
const periods = [
  { value: 'day', label: 'День' },
  { value: 'week', label: 'Неделя' },
  { value: 'month', label: 'Месяц' },
  { value: 'year', label: 'Год' }
]

const currentPeriod = ref('week')
const currentDate = ref(dayjs())

// Navigation
const goPrev = () => {
  switch (currentPeriod.value) {
    case 'day':
      currentDate.value = currentDate.value.subtract(1, 'day')
      break
    case 'week':
      currentDate.value = currentDate.value.subtract(1, 'week')
      break
    case 'month':
      currentDate.value = currentDate.value.subtract(1, 'month')
      break
    case 'year':
      currentDate.value = currentDate.value.subtract(1, 'year')
      break
  }
}

const goNext = () => {
  switch (currentPeriod.value) {
    case 'day':
      currentDate.value = currentDate.value.add(1, 'day')
      break
    case 'week':
      currentDate.value = currentDate.value.add(1, 'week')
      break
    case 'month':
      currentDate.value = currentDate.value.add(1, 'month')
      break
    case 'year':
      currentDate.value = currentDate.value.add(1, 'year')
      break
  }
}

// Week range text
const weekRange = computed(() => {
  const start = currentDate.value.startOf('week')
  const end = currentDate.value.startOf('week').add(6, 'day')
  return `${start.format('DD MMM')} - ${end.format('DD MMM')}`
})

// Local state for statistics
const statisticsEvents = ref<any[]>([])
const loading = ref(false)

// Calculate date ranges
const getDateRange = () => {
  const now = currentDate.value
  let startDate: dayjs.Dayjs
  let endDate: dayjs.Dayjs
  
  switch (currentPeriod.value) {
    case 'day':
      startDate = now.startOf('day')
      endDate = now.endOf('day')
      break
    case 'week':
      startDate = now.startOf('week')
      endDate = now.startOf('week').add(6, 'day').endOf('day')
      break
    case 'month':
      startDate = now.startOf('month')
      endDate = now.endOf('month')
      break
    case 'year':
      startDate = now.startOf('year')
      endDate = now.endOf('year')
      break
    default:
      startDate = now.startOf('week')
      endDate = now.startOf('week').add(6, 'day')
  }
  
  return { startDate, endDate }
}

// Load events for statistics
const loadStatistics = async () => {
  loading.value = true
  const { startDate, endDate } = getDateRange()
  
  try {
    const startStr = startDate.format('YYYY-MM-DD')
    const endStr = endDate.format('YYYY-MM-DD')
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

// Day view - percentage calculation (from 7am to midnight = 17 hours)
const dayEvents = computed(() => {
  const day = currentDate.value.format('YYYY-MM-DD')
  return statisticsEvents.value.filter(e => {
    const eventDay = dayjs(e.start).format('YYYY-MM-DD')
    return eventDay === day
  })
})

const occupiedMinutes = computed(() => {
  return dayEvents.value.reduce((total, event) => {
    const start = dayjs(event.start)
    const end = dayjs(event.end)
    return total + Math.max(0, end.diff(start, 'minute'))
  }, 0)
})

const totalDayMinutes = 17 * 60 // 7am to midnight = 17 hours
const dayPercentage = computed(() => {
  return Math.min(100, Math.round((occupiedMinutes.value / totalDayMinutes) * 100))
})

const circumference = 2 * Math.PI * 45
const dashOffset = computed(() => {
  return circumference - (dayPercentage.value / 100) * circumference
})

const occupiedHours = computed(() => occupiedMinutes.value / 60)
const freeHours = computed(() => Math.max(0, 17 - occupiedHours.value))

// Week view
const weekDays = computed(() => {
  const start = currentDate.value.startOf('week')
  const days = []
  const dayNames = ['Пн', 'Вт', 'Ср', 'Чт', 'Пт', 'Сб', 'Вс']
  const colors = ['#2d5016', '#3a403c', '#3a1d19', '#47381f', '#4a5568', '#5d4037', '#6d4c41']
  
  for (let i = 0; i < 7; i++) {
    const day = start.add(i, 'day')
    const dayStr = day.format('YYYY-MM-DD')
    const dayEvents = statisticsEvents.value.filter(e => {
      const eventDay = dayjs(e.start).format('YYYY-MM-DD')
      return eventDay === dayStr
    })
    
    const minutes = dayEvents.reduce((total, event) => {
      const start = dayjs(event.start)
      const end = dayjs(event.end)
      return total + Math.max(0, end.diff(start, 'minute'))
    }, 0)
    
    const hours = minutes / 60
    const maxHours = 24
    const percentage = Math.min(100, Math.round((hours / maxHours) * 100))
    
    days.push({
      name: dayNames[i],
      date: dayStr,
      hours,
      percentage,
      color: colors[i]
    })
  }
  
  return days
})

// Month view
const monthDays = computed(() => {
  const start = currentDate.value.startOf('month')
  const end = currentDate.value.endOf('month')
  const days = []
  
  let current = start
  while (current.isBefore(end) || current.isSame(end, 'day')) {
    const dayStr = current.format('YYYY-MM-DD')
    const dayEvents = statisticsEvents.value.filter(e => {
      const eventDay = dayjs(e.start).format('YYYY-MM-DD')
      return eventDay === dayStr
    })
    
    const minutes = dayEvents.reduce((total, event) => {
      const start = dayjs(event.start)
      const end = dayjs(event.end)
      return total + Math.max(0, end.diff(start, 'minute'))
    }, 0)
    
    const hours = minutes / 60
    const maxHours = 24
    const percentage = Math.min(100, Math.round((hours / maxHours) * 100))
    
    // Color based on percentage
    let color = '#1a1a1a'
    if (percentage > 0) {
      if (percentage < 25) color = '#1a3a1a'
      else if (percentage < 50) color = '#2a5a2a'
      else if (percentage < 75) color = '#3a7a3a'
      else color = '#4a9a4a'
    }
    
    days.push({
      dayNumber: current.date(),
      date: dayStr,
      events: dayEvents.length,
      hours,
      percentage,
      color
    })
    
    current = current.add(1, 'day')
  }
  
  return days
})

// Year view
const yearMonths = computed(() => {
  const start = currentDate.value.startOf('year')
  const months = []
  const monthNames = ['Янв', 'Фев', 'Мар', 'Апр', 'Май', 'Июн', 'Июл', 'Авг', 'Сен', 'Окт', 'Ноя', 'Дек']
  const colors = ['#4a5568', '#5d4037', '#47381f', '#3a403c', '#3a1d19', '#2d5016', '#4a5568', '#5d4037', '#47381f', '#3a403c', '#3a1d19', '#2d5016']
  
  for (let i = 0; i < 12; i++) {
    const month = start.month(i)
    const monthStr = month.format('YYYY-MM')
    const monthEvents = statisticsEvents.value.filter(e => {
      const eventMonth = dayjs(e.start).format('YYYY-MM')
      return eventMonth === monthStr
    })
    
    const minutes = monthEvents.reduce((total, event) => {
      const start = dayjs(event.start)
      const end = dayjs(event.end)
      return total + Math.max(0, end.diff(start, 'minute'))
    }, 0)
    
    const hours = minutes / 60
    const maxHours = month.daysInMonth() * 24
    const percentage = Math.min(100, Math.round((hours / maxHours) * 100))
    
    months.push({
      name: monthNames[i],
      month: monthStr,
      hours,
      percentage,
      color: colors[i]
    })
  }
  
  return months
})

// Summary
const totalEvents = computed(() => statisticsEvents.value.length)

const totalHours = computed(() => {
  return statisticsEvents.value.reduce((total, event) => {
    const start = dayjs(event.start)
    const end = dayjs(event.end)
    return total + end.diff(start, 'hour', true)
  }, 0)
})

// Tag statistics
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

// Load data on mount and when period/date changes
onMounted(async () => {
  console.log('Statistics mounted, fetching tags and events...')
  await tagsStore.fetchTags()
  console.log('Tags loaded:', tagsStore.tags.length)
  await loadStatistics()
})

watch([currentPeriod, currentDate], async () => {
  await loadStatistics()
})
</script>

<style scoped>
.statistics-page {
  padding: 20px;
  min-height: 100vh;
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
  margin-bottom: 20px;
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

/* Navigation */
.nav-controls {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 20px;
  margin-bottom: 30px;
}

.nav-btn {
  background: transparent;
  border: 1px solid #333;
  color: #fff;
  font-size: 24px;
  width: 50px;
  height: 50px;
  border-radius: 8px;
  cursor: pointer;
  transition: all 0.2s;
}

.nav-btn:hover {
  background: #333;
  border-color: #555;
}

.current-period {
  font-size: 28px;
  font-weight: 600;
  min-width: 300px;
  text-align: center;
}

/* Chart Container */
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

/* Day View */
.day-percentage {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 60px;
  padding: 40px;
}

.percentage-ring {
  position: relative;
  width: 200px;
  height: 200px;
}

.percentage-svg {
  width: 100%;
  height: 100%;
}

.percentage-text {
  position: absolute;
  top: 50%;
  left: 50%;
  transform: translate(-50%, -50%);
  text-align: center;
}

.percentage-value {
  display: block;
  font-size: 48px;
  font-weight: bold;
  color: #4a90e2;
}

.percentage-label {
  display: block;
  font-size: 14px;
  color: #888;
}

.day-details {
  display: flex;
  flex-direction: column;
  gap: 16px;
}

.detail-item {
  display: flex;
  justify-content: space-between;
  gap: 40px;
}

.detail-label {
  color: #888;
}

.detail-value {
  font-weight: 600;
  font-size: 18px;
}

/* Week View */
.week-chart {
  display: flex;
  gap: 16px;
  height: 300px;
  align-items: flex-end;
  padding: 20px;
}

.week-day {
  flex: 1;
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 8px;
}

.week-day-label {
  font-size: 14px;
  color: #888;
}

.week-day-bar {
  width: 100%;
  height: 200px;
  background: #1a1a1a;
  border-radius: 8px;
  display: flex;
  align-items: flex-end;
  overflow: hidden;
}

.week-day-fill {
  width: 100%;
  border-radius: 8px;
  transition: height 0.3s ease;
  min-height: 4px;
}

.week-day-percentage {
  font-size: 16px;
  font-weight: 600;
}

.week-day-hours {
  font-size: 12px;
  color: #666;
}

/* Month View */
.month-chart {
  display: grid;
  grid-template-columns: repeat(7, 1fr);
  gap: 4px;
  max-width: 600px;
  margin: 0 auto;
}

.month-day {
  aspect-ratio: 1;
  border-radius: 4px;
  display: flex;
  align-items: center;
  justify-content: center;
  transition: transform 0.2s;
  cursor: default;
}

.month-day:hover {
  transform: scale(1.1);
}

.month-day-number {
  font-size: 10px;
  font-weight: 600;
  color: #888;
}

.month-day.has-events .month-day-number {
  color: #fff;
}

/* Year View */
.year-chart {
  display: flex;
  gap: 12px;
  height: 250px;
  align-items: flex-end;
  padding: 20px;
}

.year-month {
  flex: 1;
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 8px;
}

.year-month-label {
  font-size: 12px;
  color: #888;
}

.year-month-bar {
  width: 100%;
  height: 180px;
  background: #1a1a1a;
  border-radius: 6px;
  display: flex;
  align-items: flex-end;
  overflow: hidden;
}

.year-month-fill {
  width: 100%;
  border-radius: 6px;
  transition: height 0.3s ease;
  min-height: 4px;
}

.year-month-hours {
  font-size: 11px;
  color: #666;
}

/* Summary */
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

/* Bar Chart (Tags) */
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
</style>
