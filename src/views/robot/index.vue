<template>
  <div class="app-container">
    <aside class="sidebar">
      <h2>AI Dietitian</h2>
      <ul class="history-list">
        <li v-for="(item, index) in history" :key="index" @click="loadHistory(item)">
          {{ item }}
        </li>
      </ul>
    </aside>
    <main class="chat-area">
      <h2 class="chat-title">AI Dietitian</h2>
      <div class="chat-box">
        <div v-for="(message, index) in messages" :key="index" :class="message.type">
          <span class="username">{{ message.type === 'bot' ? 'AI Dietitian' : 'You' }}:</span>
          <p>{{ message.text }}</p>
        </div>
        <div v-if="isLoading" class="loading">
          <p>Loading...</p>
        </div>
      </div>

      <!-- 單一輸入框 -->
      <div class="input-area">
        <input v-model="userInput" @keyup.enter="sendMessage" placeholder="Type your question here..." />
        <button @click="sendMessage">Send</button>
      </div>

      <div v-if="recommendations.length > 0">
        <h3>Today's Meal Recommendations:</h3>
        <ul>
          <li v-for="(meal, index) in recommendations" :key="index">{{ meal }}</li>
        </ul>
      </div>
      <div v-if="errorMessage" class="error-message">
        <p>{{ errorMessage }}</p>
      </div>
    </main>
  </div>
</template>

<script>
export default {
  data() {
  return {
    userInput: '', // 用戶輸入的問題
    messages: [
      { text: "Hello! How can I assist you today?", type: "bot" }
    ],
    history: JSON.parse(localStorage.getItem('chatHistory')) || [],
    recommendations: {}, // 假設後端返回的是物件
    errorMessage: '',
    isLoading: false,
    userId: 1, // 默認用戶 ID
    height: null, // 用戶身高
    weight: null, // 用戶體重
    age: null, // 用戶年齡
    gender: null, // 用戶性別 (1 表示男，0 表示女)
  };
},
methods: {
  sendMessage() {
  const userInput = this.userInput.trim();
  if (!userInput) return; // 如果沒有輸入任何資料，則不執行

  // 解析輸入的身高、體重、年齡和性別
  const heightMatch = userInput.match(/身高(\d+)/);
  const weightMatch = userInput.match(/體重(\d+)/);
  const ageMatch = userInput.match(/年齡(\d+)/);
  const genderMatch = userInput.match(/性別(男|女)/);

  // 如果輸入包含餐點做法的查詢
  const recipeQueryMatch = userInput.match(/(\S+)的做法/); // 檢查是否為查詢餐點做法

  if (recipeQueryMatch) {
    const dishName = recipeQueryMatch[1]; // 取得餐點名稱

    // 發送查詢做法的請求
    this.isLoading = true;
    fetch('http://localhost:5000/recipe', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json'
      },
      body: JSON.stringify({ dish: dishName })
    })
    .then(response => response.json())
    .then(data => {
      this.isLoading = false; // 隱藏加載中
      if (data.error) {
        this.errorMessage = data.error;
        this.messages.push({ text: this.errorMessage, type: "bot" });
      } else {
        const recipeMessage = `餐點「${dishName}」的做法：\n${data.recipe}`;
        this.messages.push({ text: recipeMessage, type: "bot" });
      }
    })
    .catch(error => {
      this.isLoading = false;
      console.error('Error:', error);
      this.errorMessage = 'Failed to fetch recipe';
      this.messages.push({ text: this.errorMessage, type: "bot" });
    });

    this.messages.push({ text: userInput, type: "user" });
    this.userInput = ''; // 清空輸入框
    return; // 如果是查詢做法的話，直接返回，不處理身高、體重等信息
  }

  // 解析身高、體重、年齡和性別
  if (heightMatch) {
    this.height = parseInt(heightMatch[1]);
  }

  if (weightMatch) {
    this.weight = parseInt(weightMatch[1]);
  }

  if (ageMatch) {
    this.age = parseInt(ageMatch[1]);
  }

  if (genderMatch) {
    this.gender = genderMatch[1] === "男" ? 1 : 0; // "男" 對應 1，"女" 對應 0
  }

  // 驗證所有必要參數是否存在
  if (!this.height || !this.weight || !this.age || this.gender === null) {
    this.errorMessage = "請提供有效的資料EX身高170體重65年齡30性別男。";
    this.messages.push({ text: this.errorMessage, type: "bot" });
    this.userInput = ''; // 清空輸入框
    return;
  }

  // 顯示加載中訊息
  this.isLoading = true;

  // 發送 POST 請求到後端
  fetch('http://localhost:5000/recommend', {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json'
    },
    body: JSON.stringify({
      height: this.height,
      weight: this.weight,
      age: this.age,
      gender: this.gender,
      user_id: this.userId
    })
  })
  .then(response => response.json())
  .then(data => {
    this.isLoading = false; // 隱藏加載中
    if (data.error) {
      this.errorMessage = data.error;
      this.messages.push({ text: this.errorMessage, type: "bot" });
    } else {
      // 先對餐點類型進行排序：早餐、午餐、晚餐
      const mealOrder = ['早餐', '午餐', '晚餐'];
      let recommendationsMessage = "Today's Meal Recommendations: ";

      mealOrder.forEach(mealType => {
        if (data[mealType]) {
          const mealList = data[mealType].join(", ");
          recommendationsMessage += `${mealType}: ${mealList} | `;
        }
      });

      // 移除最後的 " | "
      recommendationsMessage = recommendationsMessage.slice(0, -2);

      // 把餐點建議加到訊息中
      this.messages.push({ text: recommendationsMessage, type: "bot" });
    }
  })
  .catch(error => {
    this.isLoading = false;
    console.error('Error:', error);
    this.errorMessage = 'Failed to fetch recommendations';
    this.messages.push({ text: this.errorMessage, type: "bot" });
  });

  // 把用戶輸入也顯示在聊天框
  this.messages.push({ text: userInput, type: "user" });

  // 清空輸入框
  this.userInput = '';
}
}


};

</script>


<style scoped>
.app-container {
  display: flex;
  height: 100vh;
  width: 100vw;
  background-color: #2b2b2b;
  color: #fff;
  overflow: hidden;
  padding-left: 320px;
  box-sizing: border-box;
}

.sidebar {
  width: 240px;
  background-color: #1c1c1c;
  padding: 10px;
  display: flex;
  flex-direction: column;
  align-items: center;
  color: #aaa;
  border-right: 1px solid #333;
}

.chat-area {
  flex: 1;
  display: flex;
  flex-direction: column;
  justify-content: space-between;
  padding: 20px;
  background-color: #2b2b2b;
}

.sidebar h2 {
  font-size: 1.2em;
  margin-bottom: 20px;
}

.history-list {
  list-style: none;
  padding: 0;
  width: 100%;
}

.history-list li {
  padding: 10px;
  cursor: pointer;
  border-bottom: 1px solid #333;
}

.history-list li:hover {
  background-color: #333;
}

.chat-title {
  text-align: center;
  color: #ddd;
}

.chat-box {
  flex-grow: 1;
  overflow-y: auto;
  padding: 20px;
  background-color: #3b3b3b;
  border-radius: 8px;
  margin-bottom: 10px;
}

.username {
  font-weight: bold;
  margin-right: 5px;
}

.user {
  text-align: right;
  background-color: #4b88a2;
  color: #fff;
  padding: 8px;
  margin: 5px 0;
  border-radius: 5px;
}

.bot {
  text-align: left;
  background-color: #4d4d4d;
  color: #fff;
  padding: 8px;
  margin: 5px 0;
  border-radius: 5px;
}

.input-area {
  display: flex;
  gap: 10px;
}

input {
  flex: 1;
  padding: 10px;
  border-radius: 5px;
  border: 1px solid #333;
  background-color: #2b2b2b;
  color: #fff;
}

button {
  padding: 10px;
  border-radius: 5px;
  border: none;
  background-color: #5a5a5a;
  color: #fff;
  cursor: pointer;
}

button:hover {
  background-color: #757575;
}

.error-message {
  color: red;
  margin-top: 20px;
  text-align: center;
  font-size: 1.2em;
}

.loading {
  text-align: center;
  color: #aaa;
  font-size: 1.2em;
}
</style>
