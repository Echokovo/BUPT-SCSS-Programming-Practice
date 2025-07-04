<template>
  <div class="contact-list horizontal-list">
    <div v-if="contacts.length === 0" class="empty-message">暂无联系人</div>
    <ContactItem
      v-for="contact in contacts"
      :key="contact.user_id"
      :contact="contact"
      @delete-contact="$emit('delete-contact', contact.user_id)"
      @click="handleContactClick(contact)"
    />
  </div>
</template>

<script setup>
import ContactItem from './ContactItem.vue';
import { defineProps, defineEmits, ref } from 'vue';
import { useRouter } from 'vue-router';
import { checkFriendOnline } from '../services/api';

const props = defineProps({
  contacts: {
    type: Array,
    required: true,
    default: () => []
  }
});

const emits = defineEmits(['delete-contact']);
const router = useRouter();

const getFriendStatus = async (contact) => {
  try {
    const response = await checkFriendOnline(contact.user_id);
    if (response.data.status === 200) {
      contact.isOnline = true;
    } else if (response.data.status === 400) {
      contact.isOnline = false;
    }
  } catch (error) {
    contact.isOnline = false;
  }
};

props.contacts.forEach(contact => {
  getFriendStatus(contact);
});

const handleContactClick = (contact) => {
  router.push({ name: 'Chat', query: { contactUsername: contact.user_id } });
  // 这里可以通过事件总线或状态管理库通知 Chat.vue 选中联系人
};
</script>

<style scoped>
.contact-list {
  border-top: 1px solid #eee;
}

.horizontal-list {
  display: flex;
  flex-wrap: wrap;
  gap: 15px; /* 卡片之间的间距 */
}

.horizontal-list .contact-card {
  flex-basis: calc((100% - 5 * 15px) / 6); /* 一行最多 6 个元素，减去间距 */
  box-sizing: border-box;
}

.empty-message {
  padding: 20px;
  text-align: center;
  color: #888;
}
</style>