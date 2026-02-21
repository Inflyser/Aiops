<template>
  <div class="top-bar2">
    <div class="view-selector">
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
      <button 
        class="view-btn" 
        :class="{ active: currentView === 'year' }"
        @click="$emit('update:modelValue', 'year')"
      >
        year
      </button>
    </div>
  </div>
</template>

<script setup lang="ts">
defineProps<{
  currentView: string
}>()

defineEmits<{
  (e: 'update:modelValue', value: string): void
}>()
</script>

<style scoped>
.top-bar2 {
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 30px 0px 0px 0px;
  flex-shrink: 0;

}

.view-selector {
  display: flex;
  gap: 25px;
  background-color: #0f0f0f;
  padding: 5px 25px 5px 25px;
  border-radius: 15px;
}

.view-btn {
  background: transparent;
  border: none;
  color: #888;
  padding: 5px 10px;
  cursor: pointer;
  font-size: 22px;
  transition: color 0.2s;
  font-weight: bold;
}

.view-btn.active {
  color: #ffffff;
  background: #333;
  padding: 10px 25px 10px 25px;
  border-radius: 15px;
}
</style>
