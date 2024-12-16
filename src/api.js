import axios from 'axios';
import {reactive,toRaw} from 'https://unpkg.com/vue@3/dist/vue.esm-browser.js';
async function getfieldList(onSuccess) {
  const data = reactive({
    newsdata: '',
  })
  axios.get('http://203.64.91.71/pms/v1/Book/majorList')
    .then((res) => {
      data.newsdata=res.data;
      
      onSuccess(toRaw(data.newsdata));
    });
}
export default getfieldList
