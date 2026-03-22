import apiClient from './apiClient';
import AsyncStorage from '@react-native-async-storage/async-storage';

// 家长认证服务
export const parentAuthService = {
  // 家长注册
  register: async (username, email, password) => {
    try {
      const response = await apiClient.post('/auth/parent/register', {
        username,
        email,
        password,
      });
      return response.data;
    } catch (error) {
      throw error.response?.data || error;
    }
  },

  // 家长登录
  login: async (username, password) => {
    try {
      const response = await apiClient.post('/auth/parent/login', {
        username,
        password,
      });
      // 保存token
      if (response.data.access_token) {
        await AsyncStorage.setItem('access_token', response.data.access_token);
        await AsyncStorage.setItem('user_type', 'parent');
        await AsyncStorage.setItem('parent_id', response.data.parent_id.toString());
      }
      return response.data;
    } catch (error) {
      throw error.response?.data || error;
    }
  },

  // 获取家长信息
  getInfo: async () => {
    try {
      const response = await apiClient.get('/auth/parent/me');
      return response.data;
    } catch (error) {
      throw error.response?.data || error;
    }
  },
};

// 孩子认证服务
export const childAuthService = {
  // 孩子注册
  register: async (parentId, name, age, password) => {
    try {
      const response = await apiClient.post('/auth/child/register', {
        parent_id: parentId,
        name,
        age,
        password,
      });
      return response.data;
    } catch (error) {
      throw error.response?.data || error;
    }
  },

  // 孩子登录
  login: async (childId, password) => {
    try {
      const response = await apiClient.post('/auth/child/login', {
        child_id: childId,
        password,
      });
      if (response.data.access_token) {
        await AsyncStorage.setItem('access_token', response.data.access_token);
        await AsyncStorage.setItem('user_type', 'child');
        await AsyncStorage.setItem('child_id', response.data.child_id.toString());
      }
      return response.data;
    } catch (error) {
      throw error.response?.data || error;
    }
  },
};

// 练琴服务
export const practiceService = {
  // 添加练琴记录
  addRecord: async (date, practiceMinutes, notes = '') => {
    try {
      const response = await apiClient.post('/practice/record', {
        date,
        practice_minutes: practiceMinutes,
        notes,
      });
      return response.data;
    } catch (error) {
      throw error.response?.data || error;
    }
  },

  // 获取练琴记录
  getRecords: async (childId, startDate = null, endDate = null) => {
    try {
      let url = `/practice/records/${childId}`;
      const params = [];
      if (startDate) params.push(`start_date=${startDate}`);
      if (endDate) params.push(`end_date=${endDate}`);
      if (params.length > 0) {
        url += '?' + params.join('&');
      }
      const response = await apiClient.get(url);
      return response.data;
    } catch (error) {
      throw error.response?.data || error;
    }
  },

  // 获取统计数据
  getStatistics: async (childId, period = 'month') => {
    try {
      const response = await apiClient.get(`/practice/statistics/${childId}?period=${period}`);
      return response.data;
    } catch (error) {
      throw error.response?.data || error;
    }
  },
};

// 奖励服务
export const awardService = {
  // 发放游戏时间
  giveAward: async (childId, gameMinutes, reason = '') => {
    try {
      const response = await apiClient.post('/awards/give', {
        child_id: childId,
        game_minutes: gameMinutes,
        reason,
      });
      return response.data;
    } catch (error) {
      throw error.response?.data || error;
    }
  },

  // 获取游戏时间余额
  getBalance: async (childId) => {
    try {
      const response = await apiClient.get(`/awards/balance/${childId}`);
      return response.data;
    } catch (error) {
      throw error.response?.data || error;
    }
  },

  // 获取奖励历史
  getHistory: async (childId) => {
    try {
      const response = await apiClient.get(`/awards/history/${childId}`);
      return response.data;
    } catch (error) {
      throw error.response?.data || error;
    }
  },

  // 使用游戏时间
  deductTime: async (gameMinutes) => {
    try {
      const response = await apiClient.post('/awards/deduct', {
        game_minutes: gameMinutes,
      });
      return response.data;
    } catch (error) {
      throw error.response?.data || error;
    }
  },
};

// 登出
export const logout = async () => {
  try {
    await AsyncStorage.removeItem('access_token');
    await AsyncStorage.removeItem('user_type');
    await AsyncStorage.removeItem('parent_id');
    await AsyncStorage.removeItem('child_id');
  } catch (error) {
    console.error('登出失败:', error);
  }
};
