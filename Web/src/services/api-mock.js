// api-mock.js
export const login = async (formData) => {
  // 模拟网络请求延迟
  await new Promise(resolve => setTimeout(resolve, 500));
  
  // 无论输入什么，都返回登录成功
  return {
    status: 200,
    data: {
      token: 'mock-auth-token',
      user: {
        email: formData.email,
        role: 'admin'
      }
    }
  };
};