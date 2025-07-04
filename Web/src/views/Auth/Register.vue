<template>
  <div class="center-container">
    <!-- 添加动态环形装饰元素 -->
    <div v-for="(ring, index) in rings" :key="index" :class="['ring', `ring-${index}`]" :style="{
      width: ring.size + 'px',
      height: ring.size + 'px',
      borderColor: ring.color,
      borderWidth: ring.borderWidth + 'px',
      left: ring.left + '%',
      top: ring.top + '%'
    }"></div>
    <div class="auth-container">
      <h2>注册</h2>
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
          <label>邮箱</label>
          <input
            type="email"
            v-model="formData.email"
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
        <button type="submit" class="auth-button">注册</button>
      </form>
      <p>
        已有账号？<router-link to="/login">立即登录</router-link>
      </p>
    </div>
  </div>
</template>

<script setup>
import {ref, onMounted} from 'vue'
import {useRouter} from 'vue-router'
import {register} from '@/services/api'

const router = useRouter()
const formData = ref({
  user_id: '',
  email: '',
  password: ''
})
const error = ref('')
const rings = ref([])

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
  return Math.floor(Math.random() * 100) + 300
}

// 生成随机边框宽度（内外径差值）
const getRandomBorderWidth = () => {
  return Math.floor(Math.random() * 20) + 10
}

// 生成随机位置
const getRandomPosition = () => {
  return Math.floor(Math.random() * 130)
}

onMounted(() => {
  for (let i = 0; i < 10; i++) {
    rings.value.push({
      size: getRandomSize(),
      color: getRandomColor(),
      borderWidth: getRandomBorderWidth(),
      left: getRandomPosition(),
      top: getRandomPosition()
    })
  }
})

const handleSubmit = async () => {
  try {
    const response = await register(formData.value)
    if (response.data.status === 200) {
      error.value = '注册成功'
    } else if (response.data.status === 400) {
      error.value = '用户名不合法'
    } else if (response.data.status === 409) {
      error.value = '用户名已存在'
    } else {
      error.value = response.data.message || '注册失败'
    }
  } catch (err) {
    error.value = err.message
  }
}
</script>
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
  background: linear-gradient(-45deg, rgba(163, 238, 82, 0.14), rgba(60, 108, 231, 0.22), rgba(35, 166, 213, 0.25), rgba(35, 213, 171, 0.15));
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
  background: linear-gradient(-45deg, rgba(255, 107, 107, 0.82), rgba(245, 102, 255, 0.76), rgba(6, 48, 214, 0.7), rgba(17, 148, 178, 0.77));
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
  background-color: rgba(7, 187, 193, 0.8);
  color: white;
  border: none;
  border-radius: 4px;
  cursor: pointer;
  transition: background-color 0.3s ease;
}

.auth-button:hover {
  background-color: rgba(7, 187, 193, 0.8);
}

p {
  color: white;
  margin-top: 15px;
}

p a {
  color: rgba(7, 187, 193, 0.8);
  text-decoration: none;
}

p a:hover {
  text-decoration: underline;
}

.ring {
  position: absolute;
  border-style: solid;
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