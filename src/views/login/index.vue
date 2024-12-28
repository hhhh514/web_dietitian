
<template>
  <div class="login-container">
    <h2>登入</h2>
    <form @submit.prevent="handleLogin">
      <div class="form-group">
        <label for="username">使用者帳號：</label>
        <input 
          type="text" 
          id="username" 
          v-model="username" 
          required 
          placeholder="請輸入帳號" />
      </div>

      <div class="form-group">
        <label for="password">密碼：</label>
        <input 
          type="password" 
          id="password" 
          v-model="password" 
          required 
          placeholder="請輸入密碼" />
      </div>

      <button type="submit">登入</button>

      <div v-if="errorMessage" class="error-message">
        <p>{{ errorMessage }}</p>
      </div>

      <div class="signup-link">
        <button type="button" class="signup-button" @click="$router.push({ name: 'register' })">
          創建帳號
        </button>
      </div>
    </form>
  </div>
</template>

<script setup>

import { ref } from 'vue';
import { useRouter } from 'vue-router'; // 引入 vue-router 用於頁面跳轉

const username = ref('');
const password = ref('');
const errorMessage = ref('');

// 獲取路由對象，用於跳轉
const router = useRouter();

const handleLogin = async () => {
  errorMessage.value = ''; // 清空舊的錯誤訊息
  try {
    // 向後端發送登入請求
    const response = await fetch('http://localhost:5000/login', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({
        username: username.value,
        password: password.value,
      }),
    });

    // 檢查是否成功
    if (!response.ok) {
      throw new Error('登入請求失敗');
    }

    const data = await response.json();

    if (data.message === '登入成功') {
      console.log('登入成功');
      const userId = data.user_id; // 提取 userid
      console.log(`User ID: ${userId}`);
      // 可選：將 userid 存儲到 localStorage 或 Vuex
      localStorage.setItem('user_id', userId);

      // 登入成功後跳轉到主頁面
      router.push({ name: 'robot', query: { user_id: userId } });
    } else {
      errorMessage.value = data.error || '未知錯誤';
    }
  } catch (error) {
    errorMessage.value = error.message || '伺服器無法連接，請稍後再試';
  }
};
</script>
<style scoped>
/* 與原始樣式相同 */
.login-container {
  width: 100%;
  max-width: 400px;
  margin: 0 auto;
  padding: 2rem;
  background-color: #2b2b2b;
  color: #fff;
  border-radius: 8px;
}

h2 {
  text-align: center;
  margin-bottom: 1rem;
}

.form-group {
  margin-bottom: 1.5rem;
}

label {
  display: block;
  margin-bottom: 0.5rem;
}

input {
  width: 100%;
  padding: 0.8rem;
  border-radius: 4px;
  border: 1px solid #ccc;
  background-color: #fff;
  color: #333;
}

button {
  width: 100%;
  padding: 0.8rem;
  background-color: #4CAF50;
  color: white;
  border: none;
  border-radius: 4px;
  cursor: pointer;
}

button:hover {
  background-color: #45a049;
}

.error-message {
  color: red;
  font-size: 0.9rem;
  margin-top: 1rem;
}

.signup-link {
  text-align: center;
  margin-top: 1rem;
}

.signup-button {
  padding: 0.8rem;
  background-color: #ff5f6d;
  color: white;
  border: none;
  border-radius: 4px;
  cursor: pointer;
  width: 100%;
}

.signup-button:hover {
  background-color: #ff4b57;
}</style>