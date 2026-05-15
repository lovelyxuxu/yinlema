import { createRouter, createWebHistory } from "vue-router";
import HomeRecords from "../views/HomeRecords.vue";
import Today from "../views/Today.vue";
import Identity from "../views/Identity.vue";
import Auth from "../views/Auth.vue";
import { isLoggedIn } from "../stores/auth";

export const router = createRouter({
  history: createWebHistory(import.meta.env.BASE_URL),
  routes: [
    { path: "/auth", name: "auth", component: Auth, meta: { public: true } },
    { path: "/", name: "records", component: HomeRecords },
    { path: "/today", name: "today", component: Today },
    { path: "/identity", name: "identity", component: Identity },
  ],
});

router.beforeEach((to) => {
  if (!to.meta.public && !isLoggedIn.value) {
    return { name: "auth" };
  }
  if (to.name === "auth" && isLoggedIn.value) {
    return { name: "records" };
  }
});
