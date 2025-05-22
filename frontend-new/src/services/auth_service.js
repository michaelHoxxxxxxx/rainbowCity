import axios from 'axios';

// 使用相对路径，请求会通过代理转发到后端
const API_URL = '/auth/';

// 设置请求拦截器，在每个请求中添加认证令牌
axios.interceptors.request.use(
  (config) => {
    const token = localStorage.getItem('token');
    if (token) {
      config.headers['Authorization'] = `Bearer ${token}`;
    }
    return config;
  },
  (error) => {
    return Promise.reject(error);
  }
);

// 注册新用户
export const register = async (userData) => {
  try {
    const response = await axios.post(API_URL + 'register', userData);
    return response.data;
  } catch (error) {
    throw error.response?.data?.error || '注册失败，请稍后再试';
  }
};

// 用户登录
export const login = async (email, password) => {
  try {
    const response = await axios.post(API_URL + 'login', { email, password });
    if (response.data.token) {
      localStorage.setItem('token', response.data.token);
      localStorage.setItem('user', JSON.stringify(response.data.user));
    }
    return response.data;
  } catch (error) {
    throw error.response?.data?.error || '登录失败，请检查邮箱和密码';
  }
};

// 用户登出
export const logout = () => {
  localStorage.removeItem('token');
  localStorage.removeItem('user');
};

// 获取当前用户信息
export const getCurrentUser = () => {
  const userStr = localStorage.getItem('user');
  if (userStr) return JSON.parse(userStr);
  return null;
};

// 获取用户详细信息（从服务器刷新）
export const getUserProfile = async () => {
  try {
    const response = await axios.get(API_URL + 'profile');
    // 更新本地存储的用户信息
    localStorage.setItem('user', JSON.stringify(response.data));
    return response.data;
  } catch (error) {
    throw error.response?.data?.error || '获取用户信息失败';
  }
};

// 更新用户个人资料
export const updateUserProfile = async (profileData) => {
  try {
    const response = await axios.put(API_URL + 'profile', profileData);
    // 更新本地存储的用户信息
    localStorage.setItem('user', JSON.stringify(response.data.user));
    return response.data;
  } catch (error) {
    throw error.response?.data?.error || '更新个人资料失败';
  }
};

// 修改密码
export const changePassword = async (currentPassword, newPassword) => {
  try {
    const response = await axios.post(API_URL + 'change-password', {
      current_password: currentPassword,
      new_password: newPassword
    });
    return response.data;
  } catch (error) {
    throw error.response?.data?.error || '修改密码失败';
  }
};

// 验证邀请码
export const verifyInviteCode = async (code) => {
  try {
    const response = await axios.post(API_URL + 'verify-invite-code', { code });
    return response.data;
  } catch (error) {
    throw error.response?.data?.error || '无效的邀请码';
  }
};

// 获取用户的邀请码
export const getUserInviteCodes = async () => {
  try {
    const response = await axios.get(API_URL + 'invite-codes');
    return response.data;
  } catch (error) {
    throw error.response?.data?.error || '获取邀请码失败';
  }
};

// 检查用户是否已登录
export const isAuthenticated = () => {
  return localStorage.getItem('token') !== null;
};

// 检查用户是否是VIP
export const isVIP = () => {
  const user = getCurrentUser();
  return user && user.is_vip;
};

// 检查用户是否有特定角色
export const hasRole = (role) => {
  const user = getCurrentUser();
  return user && user.roles && user.roles.includes(role);
};
