<template>
  <div class="gradient-background" @click="handleClick">
    <router-view />
  </div>
</template>

<script>
export default {
  name: 'App',
  methods: {
    handleClick(event) {
      const clickEffect = document.createElement('div');
      clickEffect.classList.add('click-effect');
      clickEffect.style.left = `${event.clientX - 10}px`;
      clickEffect.style.top = `${event.clientY - 10}px`;
      document.body.appendChild(clickEffect);

      setTimeout(() => {
        document.body.removeChild(clickEffect);
      }, 500);
    }
  }
}
</script>