// SETUP: Imports
import { createRouter, createWebHistory } from "vue-router";
import LoginView from "./views/LoginView.vue";
import AdminDashboard from "./views/AdminDashboard.vue";
import DoctorDashboard from "./views/DoctorDashboard.vue";
import PatientDashboard from "./views/PatientDashboard.vue";
import RegisterView from "./views/RegisterView.vue";


// INIT: Simple auth helpers
function isLoggedIn() {
  return !!localStorage.getItem("token");
}

function getRole() {
  return localStorage.getItem("role");
}

// SETUP: Routes
const routes = [
  { path: "/login", name: "login", component: LoginView },
  { path: "/register", name: "register", component: RegisterView },
  {
    path: "/admin",
    name: "admin",
    component: AdminDashboard,
    meta: { requiresAuth: true, role: "admin" },
  },
  {
    path: "/doctor",
    name: "doctor",
    component: DoctorDashboard,
    meta: { requiresAuth: true, role: "doctor" },
  },
  {
    path: "/patient",
    name: "patient",
    component: PatientDashboard,
    meta: { requiresAuth: true, role: "patient" },
  },
  { path: "/:pathMatch(.*)*", redirect: "/login" },
];

// INIT: Router
const router = createRouter({
  history: createWebHistory(),
  routes,
});

// PROCESS: Route guard
router.beforeEach((to, from, next) => {
  if (!to.meta.requiresAuth) {
    return next();
  }

  if (!isLoggedIn()) {
    return next({ name: "login" });
  }

  const role = getRole();
  if (to.meta.role && to.meta.role !== role) {
    if (role === "admin") return next({ name: "admin" });
    if (role === "doctor") return next({ name: "doctor" });
    if (role === "patient") return next({ name: "patient" });
  }

  return next();
});

export default router;
