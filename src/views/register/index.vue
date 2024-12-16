<template>
  <div class="registration-form">
    <h2>註冊畫面</h2>
    <form @submit.prevent="handleSubmit">
        
      <div class="form-group">
        <label for="username">帳號：</label>
        <input type="text" id="username" v-model="formData.username" required />
      </div>

      <div class="form-group">
        <label for="password">密碼：</label>
        <input type="password" id="password" v-model="formData.password" required />
      </div>

      <div class="form-group">
        <label for="name">姓名：</label>
        <input type="text" id="name" v-model="formData.name" required />
      </div>

      <div class="form-group">
        <label for="gender">性別：</label>
        <select id="gender" v-model="formData.gender" required>
          <option value="">選擇性別</option>
          <option value="male">男性</option>
          <option value="female">女性</option>
          <option value="other">其他</option>
        </select>
      </div>

      <div class="form-group">
        <label for="height">身高 (cm)：</label>
        <input type="number" id="height" v-model="formData.height" required />
      </div>

      <div class="form-group">
        <label for="weight">體重 (kg)：</label>
        <input type="number" id="weight" v-model="formData.weight" required />
      </div>

      <button type="submit">註冊</button>
    </form>

    <div v-if="submitted" class="submission-info">
      <h3>已提交資訊：</h3>
      <p>姓名：{{ formData.name }}</p>
      <p>性別：{{ formData.gender }}</p>
      <p>身高：{{ formData.height }} cm</p>
      <p>體重：{{ formData.weight }} kg</p>
      <p>帳號：{{ formData.username }}</p>
    </div>

    <div v-if="errorMessage" class="error-message">
      <p>{{ errorMessage }}</p>
    </div>
  </div>
</template>

<script>
import { reactive, ref } from 'vue';
import { useRouter } from 'vue-router';

export default {
  name: 'RegistrationForm',
  setup() {
    const router = useRouter(); // 引入 Vue Router
    const formData = reactive({
      name: '',
      gender: '',
      height: null,
      weight: null,
      username: '',
      password: '',
    });

    const submitted = ref(false);
    const errorMessage = ref('');

    const handleSubmit = async () => {
      errorMessage.value = ''; // 清空錯誤訊息
      const data = {
        account: formData.username,
        password: formData.password,
        name: formData.name,
        gender: formData.gender,
        height: formData.height,
        weight: formData.weight,
      };

      try {
        const response = await fetch('http://localhost:5000/register', {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json',
          },
          body: JSON.stringify(data),
        });

        const result = await response.json();

        if (response.ok) {
          submitted.value = true; // 顯示提交資訊
          setTimeout(() => {
            router.push({ name: 'login' }); // 成功後導航到登入頁
          }, 1000);
        } else {
          errorMessage.value = result.error || '註冊失敗，請稍後再試';
        }
      } catch (error) {
        errorMessage.value = '伺服器無法連接，請稍後再試';
        console.error('Error:', error);
      }
    };

    return {
      formData,
      submitted,
      handleSubmit,
      errorMessage,
    };
  },
};
</script>

<style scoped>
.registration-form {
  max-width: 400px;
  margin: 0 auto;
}

.form-group {
  margin-bottom: 1em;
}

button {
  background-color: #4CAF50;
  color: white;
  border: none;
  padding: 10px;
  cursor: pointer;
}

button:hover {
  background-color: #45a049;
}

.submission-info {
  margin-top: 1em;
  background-color: #f9f9f9;
  padding: 1em;
  border-radius: 5px;
}

.error-message {
  color: red;
  margin-top: 1em;
}
</style>
