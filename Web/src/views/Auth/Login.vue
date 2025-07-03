<template>
  <div class="center-container">
    <!-- 添加动态圆形装饰元素 -->
    <div v-for="(circle, index) in circles" :key="index" :class="['circle', `circle-${index}`]" :style="{
      width: circle.size + 'px',
      height: circle.size + 'px',
      backgroundColor: circle.color,
      left: circle.left + '%',
      top: circle.top + '%'
    }"></div>
    <div class="auth-container">
      <h2>登录</h2>
      <div v-if="error" class="error-message">{{ error }}</div>
      <form @submit.prevent="handleSubmit">
        <div class="form-group">
          <label>用户名</label>
          <input
            type="text"
            v-model="formData.user_id"
            required
            class="input-field"
          />
        </div>
        <div class="form-group">
          <label>密码</label>
          <input
            type="password"
            v-model="formData.password"
            required
            class="input-field"
          />
        </div>
        <button type="submit" class="auth-button">登录</button>
      </form>
      <p>
        没有账号？<router-link to="/register">立即注册</router-link>
      </p>
    </div>
  </div>
</template>


<script setup>
import {ref, onMounted} from 'vue'
import {useRouter} from 'vue-router'
import { login } from '@/services/api';

const router = useRouter()
const formData = ref({
  user_id: '',
  password: ''
})
const error = ref('')
const loading = ref(false)
const circles = ref([])

// 生成随机颜色
const getRandomColor = () => {
  const letters = '0123456789ABCDEF'
  let color = '#'
  for (let i = 0; i < 6; i++) {
    color += letters[Math.floor(Math.random() * 16)]
  }
  return color
}

// 生成随机大小
const getRandomSize = () => {
  return Math.floor(Math.random() * 150) + 100
}

// 生成随机位置
const getRandomPosition = () => {
  return Math.floor(Math.random() * 100)
}

onMounted(() => {
  for (let i = 0; i < 10; i++) {
    circles.value.push({
      size: getRandomSize(),
      color: getRandomColor(),
      left: getRandomPosition(),
      top: getRandomPosition()
    })
  }
})

const handleSubmit = async () => {
  loading.value = true
  error.value = ''

  try {
    const response = await login(formData.value);

    if (response.data.status === 200) {
      localStorage.setItem('token', response.data.data.token)
      router.push('/')
    } else if (response.data.status === 401) {
      error.value = '密码错误'
    } else if (response.data.status === 404) {
      error.value = '用户不存在'
    } else {
      error.value = response.data.message || '登录失败'
    }
  } catch (err) {
    error.value = err.message
  } finally {
    loading.value = false
  }
}
</script>




<!-- ****************************************************** -->
<!-- <script setup>
import {ref, onMounted} from 'vue'
import {useRouter} from 'vue-router'

const router = useRouter()
const formData = ref({
  user_id: '',
  password: ''
})
const error = ref('')
const loading = ref(false)
const circles = ref([])

// 生成随机颜色
const getRandomColor = () => {
  const letters = '0123456789ABCDEF'
  let color = '#'
  for (let i = 0; i < 6; i++) {
    color += letters[Math.floor(Math.random() * 16)]
  }
  return color
}

// 生成随机大小
const getRandomSize = () => {
  return Math.floor(Math.random() * 150) + 100
}

// 生成随机位置
const getRandomPosition = () => {
  return Math.floor(Math.random() * 100)
}

onMounted(() => {
  for (let i = 0; i < 10; i++) {
    circles.value.push({
      size: getRandomSize(),
      color: getRandomColor(),
      left: getRandomPosition(),
      top: getRandomPosition()
    })
  }
})

// 模拟登录函数
const mockLogin = async () => {
  await new Promise(resolve => setTimeout(resolve, 500))
  return {
    status: 200,
    data: {
      token: 'mock-auth-token-' + Date.now(),
      user: {
        email: formData.value.email,
        role: 'tester'
      }
    }
  }
}

const handleSubmit = async () => {
  loading.value = true
  error.value = ''

  try {
    // 使用模拟登录代替真实API调用
    const response = await mockLogin()

    if (response.status === 200) {
      localStorage.setItem('token', response.data.token)
      router.push('/')
    } else {
      error.value = '模拟登录失败'
    }
  } catch (err) {
    error.value = '模拟登录异常'
  } finally {
    loading.value = false
  }
}
</script> -->
<!-- ***************************************** -->







<style scoped>
/* 禁止页面滚动 */
html, body {
  overflow: hidden;
}

.center-container {
  display: flex;
  justify-content: center;
  align-items: center;
  height: 100vh;
  /* 添加渐变背景 */
  background: linear-gradient(-45deg, rgba(238, 119, 82, 0.24), rgba(214, 60, 231, 0.06), rgba(35, 166, 213, 0.29), rgba(35, 213, 171, 0.41));
  background-size: 400% 400%;
  animation: gradient 15s ease infinite;
  position: fixed; /* 固定在页面 */
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
}

@keyframes gradient {
  0% {
    background-position: 0% 50%;
  }
  50% {
    background-position: 100% 50%;
  }
  100% {
    background-position: 0% 50%;
  }
}

.auth-container {
  width: 800px;
  height: 500px;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  background: linear-gradient(-45deg, rgba(238, 119, 82, 0.61), rgba(231, 60, 126, 0.62), rgba(35, 166, 213, 0.79), rgba(35, 213, 171, 0.78));
  background-size: 400% 400%;
  animation: gradient 15s ease infinite;
  border-radius: 8px;
  box-shadow: 0 2px 10px rgba(0, 0, 0, 0.1);
  z-index: 1;
}

@keyframes gradient {
  0% {
    background-position: 0% 50%;
  }
  50% {
    background-position: 100% 50%;
  }
  100% {
    background-position: 0% 50%;
  }
}

h2 {
  color: white;
  margin-bottom: 20px;
}

.error-message {
  color: #f44336;
  margin-bottom: 15px;
}

.form-group {
  margin-bottom: 15px;
  width: 300px;
}

label {
  display: block;
  color: white;
  margin-bottom: 5px;
}

.input-field {
  width: 100%;
  padding: 10px;
  border: none;
  border-radius: 4px;
  transition: all 0.3s ease;
}

.input-field:focus {
  box-shadow: 0 0 5px rgba(255, 255, 255, 0.8);
  outline: none;
  transform: scale(1.05);
}

.auth-button {
  width: 300px;
  padding: 10px;
  background-color: #07C160;
  color: white;
  border: none;
  border-radius: 4px;
  cursor: pointer;
  transition: background-color 0.3s ease;
}

.auth-button:hover {
  background-color: #06a453;
}

p {
  color: white;
  margin-top: 15px;
}

p a {
  color: #07C160;
  text-decoration: none;
}

p a:hover {
  text-decoration: underline;
}

.circle {
  position: absolute;
  border-radius: 50%;
  opacity: 0.5;
  animation: move 20s linear infinite;
}

@keyframes move {
  0% {
    transform: translate(0, 0);
  }
  25% {
    transform: translate(20px, 20px);
  }
  50% {
    transform: translate(0, 40px);
  }
  75% {
    transform: translate(-20px, 20px);
  }
  100% {
    transform: translate(0, 0);
  }
}
</style>








