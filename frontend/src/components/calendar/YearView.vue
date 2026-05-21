<template>
  <div class="year-calendar">
    <div class="year-header">
      <h1 class="year-title">{{ currentYear }}</h1>
      <div class="year-nav">
        <button class="nav-btn1" @click="$emit('prev-year')"><</button>
        <button class="nav-btn1" @click="$emit('next-year')">></button>
      </div>
    </div>
    
    <div class="year-grid">
      <div 
        v-for="month in months" 
        :key="month.number"
        class="month-in-year"
      >
        <h3 class="month-name">{{ month.name }}</h3>
        <div class="mini-calendar">
          <div class="mini-day-names">
            <span v-for="dayName in miniDayNames" :key="dayName">{{ dayName }}</span>
          </div>
          <div class="mini-days">
            <div 
              v-for="day in month.days" 
              :key="day.date"
              class="mini-day"
              :class="{
                'today': day.isToday,
                'other-month': !day.isCurrentMonth
              }"
              @click="$emit('day-click', day)"
            >
              {{ day.number }}
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { computed } from 'vue'
import dayjs from 'dayjs'
import 'dayjs/locale/ru'

dayjs.locale('ru')

interface MiniDay {
  date: string
  number: number
  isToday: boolean
  isCurrentMonth: boolean
  isWeekend: boolean
  fullDate: dayjs.Dayjs
}

interface MonthData {
  number: number
  name: string
  days: MiniDay[]
}

const props = defineProps<{
  currentYear: number
}>()

defineEmits<{
  (e: 'prev-year'): void
  (e: 'next-year'): void
  (e: 'day-click', day: MiniDay): void
}>()

const miniDayNames = ['П', 'В', 'С', 'Ч', 'П', 'С', 'В']

const months = computed(() => {
  const monthsArray: MonthData[] = []
  const today = dayjs()
  
  for (let month = 0; month < 12; month++) {
    const monthDate = dayjs().year(props.currentYear).month(month).startOf('month')
    const days: MiniDay[] = []
    
    const startDay = monthDate.startOf('week')
    for (let i = 0; i < 42; i++) {
      const day = startDay.add(i, 'day')
      days.push({
        date: day.format('YYYY-MM-DD'),
        number: day.date(),
        isToday: day.isSame(today, 'day'),
        isCurrentMonth: day.month() === month,
        isWeekend: day.day() === 6 || day.day() === 0,
        fullDate: day
      })
    }
    
    monthsArray.push({
      number: month,
      name: monthDate.format('MMMM'),
      days: days
    })
  }
  return monthsArray
})
</script>

<style scoped>
.year-calendar {
  padding: 10px;
}

.year-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 20px;
  border-bottom: 1px solid #80808021;
}

.year-title {
  font-size: 42px;
  font-weight: bold;
  margin: 0;
}

.year-nav {
  display: flex;
  gap: 8px;
}

.nav-btn1 {
  background: transparent;
  border: none;
  color: #ffffff;
  font-size: 30px;
  cursor: pointer;
  font-weight: bold;
  padding: 0px 10px 15px 25px;
}

.year-grid {
  display: grid;
  grid-template-columns: repeat(6, 1fr);
  gap: 15px;
  padding: 20px;
}

.month-in-year {
  background: #0f0f0f;
  border-radius: 10px;
  padding: 15px;
  transition: transform 0.2s;
}

.month-in-year:hover {
  transform: translateY(-2px);
}

.month-name {
  font-size: 19px;
  margin: 0 0 15px 0;
  text-align: center;
  font-weight: 600;
  text-transform: capitalize;
}

.mini-calendar {
  background: #1a1a1a;
  border-radius: 8px;
  padding: 10px;
}

.mini-day-names {
  display: grid;
  grid-template-columns: repeat(7, 1fr);
  gap: 2px;
  margin-bottom: 5px;
  text-align: center;
}

.mini-day-names span {
  font-size: 10px;
  color: #888;
  font-weight: bold;
}

.mini-days {
  display: grid;
  grid-template-columns: repeat(7, 1fr);
  gap: 2px;
}

.mini-day {
  aspect-ratio: 1;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 11px;
  cursor: pointer;
  border-radius: 50%;
  transition: background-color 0.2s;
}

.mini-day:hover {
  background-color: #333;
}

.mini-day.today {
  background-color: #444444;
  color: white;
  font-weight: bold;
  border: 2px solid #444444;
}

.mini-day.other-month {
  opacity: 0.3;
  cursor: default;
}
</style>
