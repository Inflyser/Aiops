<template>
  <div class="app-background" :style="backgroundStyle"></div>
  <router-view v-slot="{ Component }">
    <Transition name="page-fade" mode="out-in">
      <component :is="Component" />
    </Transition>
  </router-view>
</template>

<script setup lang="ts">
import { ref, computed, onMounted, watch, provide } from 'vue'
import { useRouter } from 'vue-router'

const router = useRouter()

const LAST_ROUTE_KEY = 'app-last-route'

const backgroundImage = ref<string | null>(null)
const backgroundOpacity = ref(0.5)

const backgroundStyle = computed(() => {
  if (!backgroundImage.value) return {}
  return {
    backgroundImage: `url(${backgroundImage.value})`,
    opacity: backgroundOpacity.value
  }
})

const setBackground = (url: string, opacity: number = 0.5) => {
  backgroundImage.value = url
  backgroundOpacity.value = opacity
  localStorage.setItem('app-background', JSON.stringify({ url, opacity }))
}

const clearBackground = () => {
  backgroundImage.value = null
  localStorage.removeItem('app-background')
}

onMounted(() => {
  const saved = localStorage.getItem('app-background')
  if (saved) {
    const { url, opacity } = JSON.parse(saved)
    backgroundImage.value = url
    backgroundOpacity.value = opacity
  }

  const lastRoute = localStorage.getItem(LAST_ROUTE_KEY)
  if (lastRoute && lastRoute !== router.currentRoute.value.path) {
    router.push(lastRoute)
  }
})

watch(() => router.currentRoute.value.path, (path) => {
  localStorage.setItem(LAST_ROUTE_KEY, path)
})

provide('backgroundUrl', backgroundImage)
provide('backgroundOpacity', backgroundOpacity)
provide('setBackground', setBackground)
provide('clearBackground', clearBackground)
</script>

<style>
.app-background {
  position: fixed;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  background-size: cover;
  background-position: center;
  pointer-events: none;
  z-index: -1;
}

/* Global page transitions */
.page-fade-enter-active,
.page-fade-leave-active {
  transition: opacity 0.25s ease, transform 0.25s ease;
}

.page-fade-enter-from {
  opacity: 0;
  transform: translateY(10px);
}

.page-fade-leave-to {
  opacity: 0;
  transform: translateY(-10px);
}
</style>




