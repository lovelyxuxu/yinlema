import { createRouter, createWebHistory } from "vue-router";
import HomeRecords from "../views/HomeRecords.vue";
import Today from "../views/Today.vue";
import Identity from "../views/Identity.vue";
import Auth from "../views/Auth.vue";
import SocialHub from "../views/social/SocialHub.vue";
import SocialRank from "../views/social/SocialRank.vue";
import SocialPlaza from "../views/social/SocialPlaza.vue";
import SocialTeams from "../views/social/SocialTeams.vue";
import { isLoggedIn } from "../stores/auth";

export const router = createRouter({
  history: createWebHistory(import.meta.env.BASE_URL),
  routes: [
    { path: "/auth", name: "auth", component: Auth, meta: { public: true } },
    { path: "/", name: "records", component: HomeRecords, meta: { title: "瘾了吗" } },
    { path: "/today", name: "today", component: Today, meta: { title: "今日检定" } },
    { path: "/identity", name: "identity", component: Identity, meta: { title: "人设" } },
    {
      path: "/social",
      component: SocialHub,
      meta: { title: "社交" },
      children: [
        { path: "", redirect: "/social/rank" },
        { path: "rank", name: "social-rank", component: SocialRank },
        { path: "plaza", name: "social-plaza", component: SocialPlaza },
        { path: "teams", name: "social-teams", component: SocialTeams },
      ],
    },
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
