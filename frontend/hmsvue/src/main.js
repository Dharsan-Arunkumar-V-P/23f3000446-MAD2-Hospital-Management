// SETUP: Imports
import { createApp } from "vue";
import App from "./App.vue";
import router from "./router";

// SETUP: Styles (Bootstrap)
import "bootstrap/dist/css/bootstrap.min.css";
import "bootstrap";

// INIT: Create app and mount
createApp(App).use(router).mount("#app");
