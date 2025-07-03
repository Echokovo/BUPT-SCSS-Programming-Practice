<template>
  <div class="main-layout">
    <Sidebar />
    <div class="content-area">
      <h2>通讯录</h2>
      <div v-if="error" class="error-message">{{ error }}</div>
      
      <div class="add-contact-form">
        <input
          type="text"
          v-model="newContactUsername"
          placeholder="输入好友用户名"
        />
        <button @click="handleAddContact">添加好友</button>
      </div>
      
      <div v-if="loading">加载中...</div>
      <div v-else>
        <div v-for="contact in contacts" :key="contact.user_id">
          <div v-if="contact.flag === 1">
            <ContactList 
              :contacts="[contact]"
              @delete-contact="handleDeleteContact"
            />
          </div>
          <div v-else>
            <div class="contact-item">
              <div class="contact-info">
                <div class="contact-name">{{ contact.user_id }}</div>
                <div class="contact-status">请求添加你为好友</div>
              </div>
              <button 
                class="agree-button"
                @click="handleAgreeFriendRequest(contact.user_id)"
              >
                同意
              </button>
              <button 
                class="reject-button"
                @click="handleRejectFriendRequest(contact.user_id)"
              >
                拒绝
              </button>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue';
import Sidebar from '@/components/Sidebar.vue';
import ContactList from '@/components/ContactList.vue';
import { getContacts, addContact, deleteContact } from '@/services/api';

const contacts = ref([]);
const newContactUsername = ref('');
const error = ref('');
const loading = ref(false);

onMounted(() => {
  fetchContacts();
});

const fetchContacts = async () => {
  loading.value = true;
  try {
    const response = await getContacts();
    if (response.data.status === 200) {
      contacts.value = response.data.data.contacts;
    } else {
      error.value = response.data.message || '获取通讯录失败';
    }
  } catch (err) {
    error.value = err.message;
  } finally {
    loading.value = false;
  }
};

const handleAddContact = async () => {
  if (!newContactUsername.value) return;
  
  try {
    const response = await addContact({ friend_id: newContactUsername.value });
    if (response.data.status === 200) {
      newContactUsername.value = '';
      fetchContacts();
    } else if (response.data.status === 404) {
      error.value = '该用户不存在';
    } else if (response.data.status === 409) {
      error.value = '已提交好友';
    } else {
      error.value = response.data.message || '添加联系人失败';
    }
  } catch (err) {
    error.value = err.message;
  }
};

const handleDeleteContact = async (username) => {
  try {
    const response = await deleteContact({ friend_id: username });
    if (response.data.status === 200) {
      fetchContacts();
    } else if (response.data.status === 404) {
      error.value = '好友不存在';
    } else {
      error.value = response.data.message || '删除联系人失败';
    }
  } catch (err) {
    error.value = err.message;
  }
};

const handleAgreeFriendRequest = async (username) => {
  try {
    const response = await addContact({ friend_id: username });
    if (response.data.status === 200) {
      fetchContacts();
    } else if (response.data.status === 404) {
      error.value = '该用户不存在';
    } else if (response.data.status === 409) {
      error.value = '已提交好友';
    } else {
      error.value = response.data.message || '处理好友请求失败';
    }
  } catch (err) {
    error.value = err.message;
  }
};

const handleRejectFriendRequest = async (username) => {
  // 这里可以添加拒绝逻辑，如果需要从某个列表中移除请求等
  // 目前简单模拟移除请求后刷新通讯录
  fetchContacts();
};
</script>

<style scoped>
.main-layout {
  display: flex;
  height: 100vh;
}
.content-area {
  flex: 1; /* 占满剩余空间 */
  padding: 0 5%; /* 左右各留5%的间距，总间距10% */
}

.add-contact-form {
  display: flex;
  margin-bottom: 20px;
  width: 100%; /* 占满父容器宽度 */
}

.add-contact-form input {
  flex: 1; /* 输入框占据除按钮外的所有空间 */
  padding: 8px 10px;
  border: 1px solid #ddd;
  border-radius: 4px 0 0 4px;
  min-width: 300px; /* 设置最小宽度，防止在极窄屏幕下输入框过窄 */
}

.add-contact-form button {
  padding: 8px 15px;
  background-color: #07C160;
  color: white;
  border: none;
  border-radius: 0 4px 4px 0;
  cursor: pointer;
  white-space: nowrap; /* 防止按钮文字换行 */
}
.error-message {
  color: #f44336;
  margin-bottom: 15px;
}

.reject-button {
  background-color: #f44336;
  color: white;
  border: none;
  border-radius: 4px;
  padding: 5px 10px;
  cursor: pointer;
  margin-left: 10px;
}

.reject-button:hover {
  background-color: #d32f2f;
}
</style>