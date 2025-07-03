<template>
  <div class="sidebar">
    <div class="sidebar-header">
      <h3>模块</h3>
    </div>
    <nav class="sidebar-nav">
      <router-link
        to="/"
        :class="['nav-item', { active: route.path === '/' }]"
      >
        <i class="fas fa-comment"></i>
        <span>聊天</span>
      </router-link>
      <router-link
        to="/contacts"
        :class="['nav-item', { active: route.path === '/contacts' }]"
      >
        <i class="fas fa-address-book"></i>
        <span>通讯录</span>
      </router-link>
    </nav>
    <div class="sidebar-footer">
      <button @click="handleLogout" class="logout-button">
        <i class="fas fa-sign-out-alt"></i>
        <span>退出登录</span>
      </button>
    </div>
  </div>
</template>

<script setup>
import { useRouter, useRoute } from 'vue-router'
import { logout } from '@/services/api'

const router = useRouter()
const route = useRoute()

const handleLogout = async () => {
  try {
    await logout()
    localStorage.removeItem('token')
    router.push('/login')
  } catch (error) {
    console.error('退出登录失败:', error)
  }
}
</script>

<style scoped>
.sidebar {
  width: 220px;
  background-color: rgba(46, 50, 56, 0.8);
  color: white;
  display: flex;
  flex-direction: column;
  border-radius: 8px;
  margin: 20px;
  box-shadow: 0 2px 10px rgba(0, 0, 0, 0.1);
}

.sidebar-header {
  padding: 20px;
  border-bottom: 1px solid #3A3F45;
}

.sidebar-nav {
  flex: 1;
  padding: 10px 0;
}

.nav-item {
  display: flex;
  align-items: center;
  padding: 12px 20px;
  color: #BABEC3;
  text-decoration: none;
}

.nav-item:hover {
  background-color: #3A3F45;
  color: white;
}

.nav-item.active {
  background-color: rgba(58, 63, 69, 0.73);
  color: white;
}

.nav-item i {
  margin-right: 10px;
}

.sidebar-footer {
  padding: 15px 20px;
  border-top: 1px solid #3A3F45;
}

.logout-button {
  background: none;
  border: none;
  color: #BABEC3;
  cursor: pointer;
  display: flex;
  align-items: center;
  padding: 0;
}

.logout-button:hover {
  color: white;
}
</style>