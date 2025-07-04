<template>
  <div class="main-layout">
    <Sidebar />
    <div class="content-area">
      <!-- 新增：当前聊天对象用户名栏 -->
      <div class="chat-contact-bar">
        <span class="contact-name">{{ currentChatUsername || '未知联系人' }}</span>
      </div>
      
      <h2>聊天</h2>
      <div class="chat-messages">
        <div
          v-for="(message, index) in chatMessages"
          :key="index"
          :class="{ 'self-message': message.isSelf, 'other-message': !message.isSelf }"
        >
          <div class="message-content">
            <!-- 文本消息 -->
            <span v-if="message.message.type === 'text'">{{ message.message.content }}</span>
            <!-- 图片消息 -->
            <img 
              v-if="message.message.type === 'picture'" 
              :src="message.message.content" 
              alt="图片" 
              @error="handleImageError(message)"
              @click="openImageModal(message.message.content)"
              class="chat-image"
            />
            <!-- 语音消息 -->
            <audio 
              v-if="message.message.type === 'voice'" 
              controls 
              :src="message.message.content"
              class="chat-audio"
            ></audio>
            <!-- 隐藏消息 -->
            <span v-if="message.message.type === 'secret'">隐藏消息</span>
          </div>
          <div class="message-sender">
            {{ message.isSelf ? '我' : message.senderUsername }}
          </div>
        </div>
      </div>
      <div class="chat-input">
        <input
          type="text"
          v-model="newMessage"
          placeholder="输入消息..."
          @keyup.enter="sendMessage('text')"
        />
        <input type="file" @change="handleFileSelect" accept="image/*" />
        <button @click="startRecording">{{ isRecording ? '正在录音' : '录音' }}</button>
        <button @click="stopRecording" :disabled="!isRecording">{{ isRecording ? '停止' : '已停止' }}</button>
        <button @click="sendMessage('text')">发送</button>
        <button @click="sendMessage('secret')">隐藏</button>
      </div>
      <!-- 图片模态框 -->
      <div v-if="isImageModalOpen" class="image-modal" @click="closeImageModal">
        <div class="image-modal-content" @click.stop>
          <img 
            :src="currentImage" 
            alt="大图" 
            class="modal-image"
            :style="{ transform: `scale(${scale})` }"
            @wheel="handleMouseWheel"
          />
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted, watch, onBeforeUnmount } from 'vue';
import Sidebar from '@/components/Sidebar.vue';
import { sendMessage as apiSendMessage, getChatHistory, decryptImage } from '@/services/api';
import { useRoute } from 'vue-router';

const route = useRoute();
const chatMessages = ref([]);
const newMessage = ref('');
const selectedFile = ref(null);
const isImageModalOpen = ref(false);
const currentImage = ref('');
const scale = ref(1);
const minScale = ref(0.2);
const maxScale = ref(3);
const isRecording = ref(false);
const mediaRecorder = ref(null);
const audioChunks = ref([]);
const recordedAudioBlob = ref(null);

// 从localStorage获取当前登录用户
const currentUser = ref(localStorage.getItem('currentUsername') || '');

// 新增：计算当前聊天对象的用户名（从路由参数获取）
const currentChatUsername = computed(() => {
  return route.query.contactUsername || '未知联系人';
});

const fetchChatHistory = async (contactUsername) => {
  try {
    const response = await getChatHistory(contactUsername);
    if (response.data.status === 200) {
      const messages = response.data.data.messages.map((message) => {
        const isSelf = message.sender === currentUser.value;
        return {
          isSelf,
          timestamp: message.timestamp,
          message: message.message,
          senderUsername: message.sender,
          receiverUsername: message.receiver
        };
      });
      messages.sort((a, b) => a.timestamp - b.timestamp);
      chatMessages.value = messages;
    } else {
      console.error('获取聊天记录失败:', response.data.message);
    }
  } catch (error) {
    console.error('获取聊天记录失败:', error);
  }
};

onMounted(() => {
  if (route.query.contactUsername) {
    fetchChatHistory(route.query.contactUsername);
  }
  window.addEventListener('keydown', handleKeyDown);
});

onBeforeUnmount(() => {
  window.removeEventListener('keydown', handleKeyDown);
});

watch(() => route.query.contactUsername, (newContactUsername) => {
  if (newContactUsername) {
    fetchChatHistory(newContactUsername);
  }
});

const handleFileSelect = (event) => {
  selectedFile.value = event.target.files[0];
};

const startRecording = async () => {
  try {
    const stream = await navigator.mediaDevices.getUserMedia({ audio: true });
    mediaRecorder.value = new MediaRecorder(stream);
    audioChunks.value = [];

    mediaRecorder.value.ondataavailable = (event) => {
      if (event.data.size > 0) {
        audioChunks.value.push(event.data);
      }
    };

    mediaRecorder.value.onstop = () => {
      recordedAudioBlob.value = new Blob(audioChunks.value, { type: 'audio/webm' });
      isRecording.value = false;
    };

    mediaRecorder.value.start();
    isRecording.value = true;
  } catch (error) {
    console.error('录音失败:', error);
    isRecording.value = false;
  }
};

const stopRecording = () => {
  if (mediaRecorder.value) {
    mediaRecorder.value.stop();
  }
};

const sendMessage = async (messageType) => {
  if (!currentUser.value) {
    console.error('未获取到当前用户，请先登录');
    return;
  }

  if (!newMessage.value.trim() && !selectedFile.value && !recordedAudioBlob.value) return;

  try {
    let messageData;
    if (recordedAudioBlob.value) {
      const reader = new FileReader();
      reader.readAsDataURL(recordedAudioBlob.value);
      await new Promise((resolve) => {
        reader.onload = () => {
          messageData = {
            data: {
              friend_id: route.query.contactUsername,
              message: {
                type: 'voice',
                content: reader.result
              }
            }
          };
          resolve();
        };
      });
      recordedAudioBlob.value = null;
    } else if (selectedFile.value) {
      const reader = new FileReader();
      reader.readAsDataURL(selectedFile.value);
      await new Promise((resolve) => {
        reader.onload = () => {
          messageData = {
            data: {
              friend_id: route.query.contactUsername,
              message: {
                type: 'picture',
                content: reader.result
              }
            }
          };
          resolve();
        };
      });
    } else {
      messageData = {
        data: {
          friend_id: route.query.contactUsername,
          message: {
            type: messageType,
            content: newMessage.value
          }
        }
      };
    }

    const response = await apiSendMessage(messageData);

    if (response.data.status === 200) {
      chatMessages.value.push({
        isSelf: true,
        timestamp: Date.now(),
        message: messageData.data.message,
        senderUsername: currentUser.value,
        receiverUsername: route.query.contactUsername
      });

      newMessage.value = '';
      selectedFile.value = null;
    } else if (response.data.status === 404) {
      console.error('发送失败:', response.data.message);
    } else {
      console.error('发送失败:', response.data.message);
    }
  } catch (error) {
    console.error('API调用失败:', error);
  }
};

const handleImageError = (message) => {
  console.error('图片加载失败:', message);
};

const openImageModal = (imageSrc) => {
  currentImage.value = imageSrc;
  scale.value = 1;
  isImageModalOpen.value = true;
};

const closeImageModal = () => {
  isImageModalOpen.value = false;
};

const handleMouseWheel = (event) => {
  event.preventDefault();
  const delta = event.deltaY > 0 ? -0.1 : 0.1;
  const newScale = scale.value + delta;
  if (newScale >= minScale.value && newScale <= maxScale.value) {
    scale.value = newScale;
  }
};

const handleKeyDown = (event) => {
  if (isImageModalOpen.value) {
    if (event.key === '+') {
      const newScale = scale.value + 0.1;
      if (newScale <= maxScale.value) {
        scale.value = newScale;
      }
    } else if (event.key === '-') {
      const newScale = scale.value - 0.1;
      if (newScale >= minScale.value) {
        scale.value = newScale;
      }
    }
  }
};

const decryptImageMessage = async (timestamp) => {
  try {
    const response = await decryptImage({ timestamp });
    if (response.data.status === 200) {
      // 显示解密后的图片
      console.log('解密后的图片数据:', response.data.data);
    } else {
      console.error('解密失败:', response.data.message);
    }
  } catch (error) {
    console.error('解密请求失败:', error);
  }
};
</script>

<style scoped>
.main-layout {
  display: flex;
  height: 100vh;
}

.content-area {
  flex: 1;
  padding: 20px;
  display: flex;
  flex-direction: column;
  background-color: rgba(255, 255, 255, 0.44);
  border-radius: 8px;
  margin: 20px;
  box-shadow: 0 2px 10px rgba(0, 0, 0, 0.1);
}

.chat-messages {
  flex: 1;
  overflow-y: auto;
  padding: 10px;
  border: 1px solid #ddd;
  border-radius: 4px;
  background-color: white;
  margin-bottom: 10px;
}

.self-message,
.other-message {
  margin-bottom: 10px;
}

.self-message {
  text-align: right;
}

.message-content {
  display: inline-block;
  padding: 8px 12px;
  border-radius: 4px;
  max-width: 70%;
}

.self-message .message-content {
  background-color: #07C160;
  color: white;
}

.other-message .message-content {
  background-color: #e0e0e0;
}

.message-sender {
  font-size: 12px;
  color: #888;
  margin-top: 3px;
}

.chat-input {
  display: flex;
}

.chat-input input {
  flex: 1;
  padding: 8px 10px;
  border: 1px solid #ddd;
  border-radius: 4px 0 0 4px;
}

.chat-input button {
  padding: 8px 15px;
  background-color: #07C160;
  color: white;
  border: none;
  border-radius: 0 4px 4px 0;
  cursor: pointer;
  transition: background-color 0.3s ease;
}

.chat-input button:hover {
  background-color: #06a453;
}

.chat-image {
  width: 150px;
  height: 150px;
  object-fit: cover;
  cursor: pointer;
}

.image-modal {
  position: fixed;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  background-color: rgba(0, 0, 0, 0.8);
  display: flex;
  justify-content: center;
  align-items: center;
  z-index: 1000;
}

.image-modal-content {
  position: relative;
  text-align: center;
  display: flex;
  flex-direction: column;
  align-items: center;
  background-color: white;
  padding: 20px;
  border-radius: 8px;
}

.modal-image {
  max-width: 90%;
  max-height: 90%;
  background-color: transparent;
  transition: transform 0.3s ease;
}
</style>