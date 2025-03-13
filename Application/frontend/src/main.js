import { createApp } from "vue";
import App from "./App.vue";
import router from "./router/router";
import 'bootstrap/dist/css/bootstrap.min.css'
import 'bootstrap/dist/js/bootstrap.bundle.min.js'
import 'bootstrap-icons/font/bootstrap-icons.css' // for icons
import vue3GoogleLogin from 'vue3-google-login'

const app = createApp(App);
app.use(vue3GoogleLogin, {
    clientId: '859846322076-3u1k9ter70q7b5jqaum8i7e5jc506mnh.apps.googleusercontent.com'
  })
app.use(router).mount("#app");