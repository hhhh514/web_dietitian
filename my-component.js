import { ref } from 'vue'
export default {
  setup() {
    const count = ref(0)
    return { count }
  },

  template: `<div><button @click="count++">{{ count }}</button></div>`
}  