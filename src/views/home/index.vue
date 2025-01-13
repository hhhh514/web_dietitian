<script setup>
import { ref, onMounted } from 'vue';
import { gsap } from 'gsap';

const title = ref(null);
const subtitle = ref(null);

onMounted(() => {
  const tl = gsap.timeline();

  // 標題從左側飛入效果
  tl.fromTo(
    title.value,
    { x: '-100vw', opacity: 0 },
    { x: 0, opacity: 1, duration: 1.5, ease: 'power4.out' }
  );

  // 副標題從右側飛入效果
  tl.fromTo(
    subtitle.value,
    { x: '100vw', opacity: 0 },
    { x: 0, opacity: 1, duration: 1.5, ease: 'power4.out' },
    '-=1'
  );
});
</script>

<template>
  <main class="app-container">
    <div class="hero">
      <h1 ref="title" class="hero-title">AI營養師</h1>
      <p ref="subtitle" class="hero-description">專屬你的健康管理助手，個性化營養建議即刻展開。</p>
      <button @click="$router.push({ name: 'login' })" class="hero-button">立即開始諮詢</button>
    </div>
  </main>
  <div class="runner">
    <img src="@/assets/images/animated-cat-image-0072.gif" alt="Running Character" class="runner-image" />
  </div>
</template>

<style scoped>
/* 主容器設置 */
.app-container {
  display: flex;
  justify-content: center;
  align-items: center;
  height: 100vh;
  width: 100vw;
  background-color: #2b2b2b;
  color: #fff;
  overflow: hidden;
  transform: translateX(-30px);
}

/* 內容區塊 */
.hero {
  text-align: center;
  padding: 20px;
}

/* 標題樣式 */
.hero-title {
  font-size: 3em;
  color: #ffffff;
  text-shadow: 0 4px 10px rgba(0, 0, 0, 0.2);
  font-family: 'Pacifico', 'ZCOOL KuaiLe', cursive; /* 使用英文和中文手寫字體 */
}

/* 描述文字 */
.hero-description {
  font-size: 1.2em;
  color: #f1f1f1;
  margin: 10px 0 20px;
  font-family: 'Noto Sans TC', 'Roboto Slab', serif; /* 中文支持字體搭配西文字體 */
}

/* 按鈕樣式 */
.hero-button {
  background-color: #ff5f6d;
  color: #ffffff;
  padding: 10px 20px;
  border: none;
  border-radius: 20px;
  font-size: 1em;
  cursor: pointer;
  transition: transform 0.3s;
  font-family: 'Noto Sans TC', 'Roboto Slab', serif;
}

.hero-button:hover {
  transform: scale(1.1);
}
</style>


<style scoped>

/* 跑步的小人容器 */
.runner {
  position: absolute;
  bottom: 20px;
  left: 0;
  width: 100px;
  height: 100px;
  overflow: hidden;
  animation: moveRunner 10s linear infinite; /* Increased duration from 5s to 10s */
}

/* 跑步的小人圖片 */
.runner-image {
  width: 100%;
  height: 100%;
  animation: run 1s steps(8) infinite;
}

/* 跑步動畫 */
@keyframes run {
  from {
    background-position: 0;
  }
  to {
    background-position: -800px; /* 假設每幀圖片寬度為100px，共8幀 */
  }
}

/* 小人從左到右移動動畫 */
@keyframes moveRunner {
  from {
    left: 0;
  }
  to {
    left: 100vw;
  }
}
</style>

