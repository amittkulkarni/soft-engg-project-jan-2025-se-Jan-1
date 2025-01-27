import { createRouter, createWebHistory } from "vue-router";
import HomePage from "../components/HomePage.vue";
import Login from "../components/LoginPage.vue";
import Register from "../components/RegisterPage.vue";
import CoursePage from "../components/CoursePage.vue";

const routes = [
  {
    path: "/",
    name: "Home",
    component: HomePage,
  },
  {
    path: "/login",
    name: "Login",
    component: Login,
  },
  {
    path: "/register",
    name: "Register",
    component: Register,
  },
  {
    path: "/course",
    name: "Course",
    component: CoursePage
  }
];

const router = createRouter({
  history: createWebHistory(),
  routes,
});

export default router;

