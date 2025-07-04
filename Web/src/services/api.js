// // 模拟的用户数据
// const mockUsers = [];
// // 模拟的好友关系数据
// const mockContacts = {};
// // 模拟的聊天记录数据
// const mockChatHistories = {};

// // 模拟网络请求延迟
// const simulateDelay = () => {
//   return new Promise((resolve) => setTimeout(resolve, 500));
// };

// // 注册
// export const register = async (userData) => {
//   await simulateDelay();

//   const existingUser = mockUsers.find((user) => user.username === userData.username);
//   if (existingUser) {
//     return {
//       data: {
//         status: 409,
//         message: '用户名已存在'
//       }
//     };
//   }

//   mockUsers.push(userData);
//   return {
//     data: {
//       status: 200,
//       message: '注册成功'
//     }
//   };
// };

// // 登录
// export const login = async (credentials) => {
//   await simulateDelay();

//   const user = mockUsers.find(
//     (user) => user.username === credentials.username && user.password === credentials.password
//   );
//   if (user) {
//     return {
//       data: {
//         status: 200,
//         data: {
//           token: 'mock-auth-token',
//           user: {
//             email: user.email,
//             role: 'user'
//           }
//         }
//       }
//     };
//   }

//   return {
//     data: {
//       status: 404,
//       message: '用户不存在'
//     }
//   };
// };

// // 退出登录
// export const logout = async () => {
//   await simulateDelay();
//   return {
//     data: {
//       status: 200,
//       message: '退出登录成功'
//     }
//   };
// };

// // 获取好友列表
// export const getContacts = async () => {
//   await simulateDelay();

//   const currentUser = localStorage.getItem('token') ? mockUsers[0] : null;
//   if (!currentUser) {
//     return {
//       data: {
//         status: 401,
//         message: '未登录'
//       }
//     };
//   }

//   const contacts = mockContacts[currentUser.username] || [];
//   const contactDetails = contacts.map((contactUsername) => {
//     const contact = mockUsers.find((user) => user.username === contactUsername);
//     return {
//       user_id: contact.username,
//       flag: Math.random() > 0.5 ? 1 : 0, // 随机模拟flag位
//       isOnline: Math.random() > 0.5 // 随机模拟在线状态
//     };
//   });

//   return {
//     data: {
//       status: 200,
//       data: {
//         contacts: contactDetails
//       }
//     }
//   };
// };

// // 添加好友
// export const addContact = async (contactData) => {
//   await simulateDelay();

//   const currentUser = localStorage.getItem('token') ? mockUsers[0] : null;
//   if (!currentUser) {
//     return {
//       data: {
//         status: 401,
//         message: '未登录'
//       }
//     };
//   }

//   const contact = mockUsers.find((user) => user.username === contactData.friend_id);
//   if (!contact) {
//     return {
//       data: {
//         status: 404,
//         message: '好友不存在'
//       }
//     };
//   }

//   if (!mockContacts[currentUser.username]) {
//     mockContacts[currentUser.username] = [];
//   }
//   if (mockContacts[currentUser.username].includes(contact.username)) {
//     return {
//       data: {
//         status: 409,
//         message: '已提交好友'
//       }
//     };
//   }

//   mockContacts[currentUser.username].push(contact.username);
//   return {
//     data: {
//       status: 200,
//       message: '添加好友成功'
//     }
//   };
// };

// // 删除好友
// export const deleteContact = async (contactData) => {
//   await simulateDelay();

//   const currentUser = localStorage.getItem('token') ? mockUsers[0] : null;
//   if (!currentUser) {
//     return {
//       data: {
//         status: 401,
//         message: '未登录'
//       }
//     };
//   }

//   const contactUsername = contactData.friend_id;
//   if (!mockContacts[currentUser.username] || !mockContacts[currentUser.username].includes(contactUsername)) {
//     return {
//       data: {
//         status: 404,
//         message: '好友不存在'
//       }
//     };
//   }

//   mockContacts[currentUser.username] = mockContacts[currentUser.username].filter(
//     (username) => username !== contactUsername
//   );
//   return {
//     data: {
//       status: 200,
//       message: '删除好友成功'
//     }
//   };
// };

// // 获取聊天记录
// export const getChatHistory = async (contactUsername) => {
//   await simulateDelay();

//   const currentUser = localStorage.getItem('token') ? mockUsers[0] : null;
//   if (!currentUser) {
//     return {
//       data: {
//         status: 401,
//         message: '未登录'
//       }
//     };
//   }

//   const chatKey = [currentUser.username, contactUsername].sort().join('-');
//   const messages = mockChatHistories[chatKey] || [];

//   return {
//     data: {
//       status: 200,
//       data: {
//         messages
//       }
//     }
//   };
// };

// // 发送消息
// export const sendMessage = async (messageData) => {
//   await simulateDelay();

//   const currentUser = localStorage.getItem('token') ? mockUsers[0] : null;
//   if (!currentUser) {
//     return {
//       data: {
//         status: 401,
//         message: '未登录'
//       }
//     };
//   }

//   const contactUsername = messageData.data.friend_id;
//   const chatKey = [currentUser.username, contactUsername].sort().join('-');
//   if (!mockChatHistories[chatKey]) {
//     mockChatHistories[chatKey] = [];
//   }

//   const newMessage = {
//     sender: currentUser.username,
//     receiver: contactUsername,
//     timestamp: messageData.data.timestamp,
//     message: messageData.data.message
//   };
//   mockChatHistories[chatKey].push(newMessage);

//   return {
//     data: {
//       status: 200,
//       message: '消息发送成功'
//     }
//   };
// };

// // 判断好友是否在线
// export const checkFriendOnline = async (friendUsername) => {
//   await simulateDelay();

//   const currentUser = localStorage.getItem('token') ? mockUsers[0] : null;
//   if (!currentUser) {
//     return {
//       data: {
//         status: 401,
//         message: '未登录'
//       }
//     };
//   }

//   const isOnline = Math.random() > 0.5; // 随机模拟在线状态
//   return {
//     data: {
//       status: isOnline ? 200 : 400,
//       message: isOnline ? '好友在线' : '好友离线'
//     }
//   };
// };

// // 同意或拒绝好友请求
// export const agreeFriendRequest = async (contactUsername, flag) => {
//   await simulateDelay();

//   const currentUser = localStorage.getItem('token') ? mockUsers[0] : null;
//   if (!currentUser) {
//     return {
//       data: {
//         status: 401,
//         message: '未登录'
//       }
//     };
//   }

//   if (!mockContacts[currentUser.username]) {
//     mockContacts[currentUser.username] = [];
//   }
//   if (flag === 1 && !mockContacts[currentUser.username].includes(contactUsername)) {
//     mockContacts[currentUser.username].push(contactUsername);
//   }

//   return {
//     data: {
//       status: 200,
//       message: flag === 1 ? '同意好友请求成功' : '拒绝好友请求成功'
//     }
//   };
// };

// // 图片解密
// export const decryptImage = async (data) => {
//   await simulateDelay();
//   return {
//     data: {
//       status: 200,
//       data: {
//         decryptedImage: 'mock-decrypted-image-data'
//       }
//     }
//   };
// };













import axios from 'axios'

const API_BASE_URL = 'http://10.21.148.196:8888'

const api = axios.create({
  baseURL: API_BASE_URL
})

// 请求拦截器 - 添加token
api.interceptors.request.use(config => {
  const token = localStorage.getItem('token')
  if (token) {
    config.headers.Authorization = `Bearer ${token}`
  }
  return config
}, error => {
  return Promise.reject(error)
})

// 注册
export const register = (userData) => {
  return api.post('/register', { data: userData })
}
// 登录
export const login = (credentials) => {
  return api.post('/login', { data: credentials })
}
// 退出登录
export const logout = () => {
  return api.post('/logout');
}
// 获取好友列表
export const getContacts = () => {
  return api.get('/contacts')
}
// 添加好友
export const addContact = (contactData) => {
  return api.post('/contacts', { data: contactData })
}
// 删除好友
export const deleteContact = (contactData) => {
  return api.delete('/contacts', { data: { data: contactData } })
}
// 获取聊天记录
export const getChatHistory = (contactUsername) => {
  return api.post('/history', { data: { friend_id: contactUsername } })
}
// 发送消息
export const sendMessage = (messageData) => {
  return api.post('/chat', messageData);
}
// 判断好友是否在线
export const checkFriendOnline = (friendUsername) => {
  return api.post('/online', { data: { friend_id: friendUsername } });
}
// 同意或拒绝好友请求
// export const agreeFriendRequest = (contactUsername, flag) => {
//   return api.post('/agree', { data: { friend_id: contactUsername, flag } });
// }
// 图片解密
export const decryptImage = (data) => {
  return api.post('/decipher', { data });
}