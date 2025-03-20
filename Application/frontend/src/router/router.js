import {createRouter, createWebHistory} from "vue-router";
import Login from "../components/LoginPage.vue";
import Register from "../components/RegisterPage.vue";
import CoursePage from "../components/CoursePage.vue";
import ProgrammingPage from "@/components/ProgrammingPage.vue";
import LecturePage from "@/components/LecturePage.vue"
import AssignmentsPage from "@/components/AssignmentsPage.vue";
import GenerateMock from "@/components/GenerateMock.vue";
import KiaPage from "@/components/KiaPage.vue";
import MockQuizPage from "@/components/MockQuizPage.vue";

const routes = [
  {
    path: "/login",
    alias: "/",
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
    path: "/programming/:id",
    name: "ProgrammingAssignment",
    component: ProgrammingPage
  },
  {
    path: "/lecture",
    name: "LecturePage",
    component: LecturePage
  },
  {
    path: "/assignment/:id",
    name: "AssignmentPage",
    component: AssignmentsPage,
  },
  {
    path: "/generate-topic-mock",
    name: "GenerateTopicMock",
    component: GenerateMock
  },
  {
    path: "/kia",
    name: "KiaPage",
    component: KiaPage
  },
  {
    path: '/mock-quiz',
    name: 'MockQuiz',
    component: MockQuizPage
  }
];

const router = createRouter({
  history: createWebHistory(),
  routes,
});

export default router;

