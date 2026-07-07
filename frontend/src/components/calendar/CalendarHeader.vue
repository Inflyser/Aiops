<template>
  <div class="calendar-header">
    <div class="calendar-header2">
      <h1 class="month-year">{{ monthYear }}</h1>
      <div class="week-nav">
        <button class="nav-btn1" @click="$emit('prev-week')"><</button>
        <button class="nav-btn1" @click="$emit('next-week')">></button>
      </div>
    </div>
    <div class="days-header">
      <!-- Empty column for time labels + sleep toggle -->
      <div class="time-header">
        <div
          class="sleep-toggle"
          @click="$emit('toggle-sleep', !props.sleepMode)"
          :title="props.sleepMode ? 'Выключить режим сна' : 'Включить режим сна'"
        >
          <img v-if="props.sleepMode" src="@/assets/sun.svg" class="toggle-svg" />
          <img v-else src="@/assets/moon.svg" class="toggle-svg" />
        </div>
      </div>
      <div
        v-for="day in weekDays"
        :key="day.date"
        class="day-header"
        :class="{ 'is-today': day.isToday }"
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
  sleepMode: boolean
}>()

defineEmits<{
  (e: 'prev-week'): void
  (e: 'next-week'): void
  (e: 'toggle-sleep', value: boolean): void
}>()

const weekDays = computed(() => {
  const days = []
  const today = dayjs().format('YYYY-MM-DD')
  for (let i = 0; i < 7; i++) {
    const date = props.currentWeekStart.add(i, 'day')
    const dateStr = date.format('YYYY-MM-DD')
    days.push({
      date: dateStr,
      shortName: date.format('ddd').toUpperCase().slice(0, 2),
      number: date.date(),
      fullDate: date,
      isToday: dateStr === today
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
  padding: 0;
  flex-shrink: 0;
  width: 100%;
  box-sizing: border-box;
}

.calendar-header2 {
  display: flex;
  align-items: center;
  padding-left: 12px;
}

.month-year {
  font-size: 42px;
  margin-bottom: 20px;
  text-transform: capitalize;
  font-weight: bold;
  flex: 1;
}

.week-nav {
  display: flex;
  gap: 10px;
}

.nav-btn1 {
  background: transparent;
  border: none;
  color: var(--text-primary);
  font-size: 30px;
  cursor: pointer;
  font-weight: bold;
  padding: 0px 10px 15px 25px;
}

.days-header {
  display: grid;
  grid-template-columns: 60px repeat(7, 1fr);
  box-sizing: border-box;
  padding-left: 0;
  margin-left: 0;
  width: 100%;
}

.time-header {
  width: 60px;
  box-sizing: border-box;
  display: flex;
  align-items: center;
  justify-content: center;
}

.sleep-toggle {
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: center;
  transition: opacity 0.2s;
  opacity: 0.6;
}

.sleep-toggle:hover {
  opacity: 1;
}

.toggle-svg {
  width: 24px;
  height: 24px;
}

.day-header {
  text-align: center;
  border-right: 1px solid var(--border-subtle);
  box-sizing: border-box;
}

.day-header:last-child {
  border-right: none;
}

.day-name {
  font-size: 19px;
  color: #888;
  margin-bottom: 5px;
  font-weight: 700;
}

.day-number {
  font-size: 18px;
  font-weight: 700;
}

.is-today .day-number {
  background-color: var(--bg-elevated);
  color: white;
  width: 42px;
  height: 42px;
  border-radius: 50%;
  display: inline-flex;
  align-items: center;
  justify-content: center;
}
</style>
