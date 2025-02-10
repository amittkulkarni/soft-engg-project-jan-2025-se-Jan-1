import { createRouter, createWebHistory } from "vue-router";
import HomePage from "../components/HomePage.vue";
import Login from "../components/LoginPage.vue";
import Register from "../components/RegisterPage.vue";
import CoursePage from "../components/CoursePage.vue";
import ProgrammingPage from "@/components/ProgrammingPage.vue";
import LecturePage from "@/components/LecturePage.vue"
import AssignmentsPage from "@/components/AssignmentsPage.vue";

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
  },
  {
    path: "/grpa",
    name: "ProgrammingAssignment",
    component: ProgrammingPage
  },
  {
    path: "/lecture",
    name: "LecturePage",
    component: LecturePage
  },
  {
    path: "/ga",
    name: "AssignmentPage",
    component: AssignmentsPage
  }
];

const router = createRouter({
  history: createWebHistory(),
  routes,
});

export default router;

