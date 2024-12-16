import { createRouter, createWebHistory } from 'vue-router'
import HomeIndex from '../views/home/index.vue'
import login from '../views/login/index.vue'
import robot from '../views/robot/index.vue'
import register from '../views/register/index.vue'
const routes = [
  // ...其他路由
  {
    path: '/home',
    name: 'Home',
    component: HomeIndex
  },

  {
    path: '/login',
    name: 'login',
    component: login,

  },
  {
    path: '/robot',
    name: 'robot',
    component: robot,
  },
  {
    path: '/register',
    name: 'register',
    component: register,
  },
]

const router = createRouter({
  history: createWebHistory(import.meta.env.BASE_URL),
  routes
})


export default router;