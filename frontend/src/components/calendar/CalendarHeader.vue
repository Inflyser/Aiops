<template>
  <div class="calendar-header">
    <div class="calendar-header2">
      <h1 class="month-year">{{ monthYear }}</h1>
      <button class="nav-btn1" @click="$emit('prev-week')"><</button>
      <button class="nav-btn1" @click="$emit('next-week')">></button>
    </div>
    <div class="days-header">
      <div 
        v-for="day in weekDays" 
        :key="day.date"
        class="day-header"
      >
        <div class="day-name">{{ day.shortName }}</div>
        <div class="day-number">{{ day.number }}</div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { computed } from 'vue'
import dayjs from 'dayjs'
import 'dayjs/locale/ru'

dayjs.locale('ru')

const props = defineProps<{
  currentWeekStart: dayjs.Dayjs
}>()

defineEmits<{
  (e: 'prev-week'): void
  (e: 'next-week'): void
}>()

const weekDays = computed(() => {
  const days = []
  for (let i = 0; i < 7; i++) {
    const date = props.currentWeekStart.add(i, 'day')
    days.push({
      date: date.format('YYYY-MM-DD'),
      shortName: date.format('ddd').toUpperCase().slice(0, 2),
      number: date.date(),
      fullDate: date
    })
  }
  return days
})

const monthYear = computed(() => {
  return props.currentWeekStart.format('MMMM YYYY')
})
</script>

<style scoped>
.calendar-header {
  padding: 20px;
  border-bottom: 1px solid #80808021;
  flex-shrink: 0;

}

.calendar-header2 {
  display: flex;
}

.month-year {
  font-size: 52px;
  font-weight: 300;
  margin-bottom: 20px;
  text-transform: capitalize;
  font-weight: bold;
}

.nav-btn1 {
  background: transparent;
  border: none;
  color: #ffffff;
  font-size: 38px;
  cursor: pointer;
  font-weight: bold;
  padding: 0px 10px 15px 25px;
}

.days-header {
  display: grid;
  grid-template-columns: repeat(7, 1fr);
  gap: 0px;
  margin-bottom: 10px;
  margin-left: 60px;
}

.day-header {
  text-align: center;
}

.day-name {
  font-size: 24px;
  color: #888;
  margin-bottom: 5px;
  font-weight: 700;
}

.day-number {
  font-size: 22px;
  font-weight: 700;
}
</style>
