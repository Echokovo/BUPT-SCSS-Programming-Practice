<template>
  <div class="contact-card">
    <div class="contact-info">
      <div class="contact-name">{{ displayUsername(contact.username) }}</div>
      <div class="contact-status">
        {{ contact.isOnline ? '在线' : '离线' }}
      </div>
    </div>
    <button
      class="delete-button"
      @click="$emit('delete-contact', contact.username)"
    >
      删除
    </button>
  </div>
</template>

<script setup>
import {defineProps, defineEmits} from 'vue';

defineProps({
  contact: {
    type: Object,
    required: true
  }
})

defineEmits(['delete-contact'])

const displayUsername = (username) => {
  if (username.length > 13) {
    return username.slice(0, 13) + '...';
  }
  return username;
};
</script>

<style scoped>
.contact-card {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 15px;
  border: 1px solid #eee;
  border-radius: 8px;
  margin-bottom: 15px;
  background-color: white;
  box-shadow: 0 2px 5px rgba(0, 0, 0, 0.1);
  transition: box-shadow 0.3s ease;
}

.contact-card:hover {
  box-shadow: 0 4px 10px rgba(0, 0, 0, 0.2);
}

.contact-info {
  flex: 1;
}

.contact-name {
  font-weight: 500;
  margin-bottom: 5px;
}

.contact-status {
  color: #07C160; /* 在线状态颜色 */
  font-size: 12px;
}

.delete-button {
  background-color: #f44336;
  color: white;
  border: none;
  border-radius: 4px;
  padding: 5px 10px;
  cursor: pointer;
}

.delete-button:hover {
  background-color: #d32f2f;
}
</style>