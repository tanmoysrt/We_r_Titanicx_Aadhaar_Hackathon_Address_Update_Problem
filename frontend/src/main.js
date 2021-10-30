import { createApp } from "vue";
import App from "./App.vue";
import router from "./router";
import VueToast from "vue-toast-notification";
import "vue-toast-notification/dist/theme-sugar.css";
import "./assets/css/style.css";

const app = createApp(App)
app.use(router);
app.use(VueToast, {
  position: "top",
});
app.mount("#app");


  // Force dismiss specific toast
// instance.dismiss();
// Dismiss all opened toast immediately
// app.$toast.clear();