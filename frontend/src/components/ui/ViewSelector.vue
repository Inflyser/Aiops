<template>
  <div class="top-bar2">
    <div class="view-selector">
      <!-- Moving indicator -->
      <div 
        class="view-indicator"
        :style="indicatorStyle"
      ></div>
      
      <button 
        class="view-btn" 
        :class="{ active: currentView === 'day' }"
        @click="$emit('update:modelValue', 'day')"
      >
        day
      </button>
      <button 
        class="view-btn" 
        :class="{ active: currentView === 'week' }"
        @click="$emit('update:modelValue', 'week')"
      >
        week
      </button>
      <button 
        class="view-btn" 
        :class="{ active: currentView === 'month' }"
        @click="$emit('update:modelValue', 'month')"
      >
        month
      </button>

    </div>
  </div>
</template>

<script setup lang="ts">
import { computed } from 'vue'
import { toRefs } from 'vue'

const props = defineProps<{
  currentView: string
}>()

const { currentView } = toRefs(props)

defineEmits<{
  (e: 'update:modelValue', value: string): void
}>()

const views = ['day', 'week', 'month']

const indicatorStyle = computed(() => {
  const index = views.indexOf(currentView.value)
  const buttonWidth = 90
  const gap = 20
  const left = index * (buttonWidth + gap)
  
  return {
    transform: `translateX(${left}px)`,
    width: `${buttonWidth}px`
  }
})
</script>

<style scoped>
.top-bar2 {
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 0;
  flex-shrink: 0;
}

.view-selector {
  display: flex;
  gap: 20px;
  background-color: #0f0f0f;
  padding: 5px;
  border-radius: 15px;
  position: relative;
}

/* Moving indicator */
.view-indicator {
  position: absolute;
  top: 5px;
  left: 5px;
  height: calc(100% - 10px);
  background: #333;
  border-radius: 12px;
  transition: transform 0.3s cubic-bezier(0.4, 0, 0.2, 1);
  z-index: 0;
}

.view-btn {
  position: relative;
  z-index: 1;
  background: transparent;
  border: none;
  color: #888;
  padding: 10px 20px;
  cursor: pointer;
  font-size: 18px;
  transition: color 0.3s ease;
  font-weight: bold;
  min-width: 90px;
  text-align: center;
}

.view-btn:hover {
  color: #aaa;
}

.view-btn.active {
  color: #ffffff;
}
</style>
