import { createRouter, createWebHistory } from "vue-router";
import HomeRecords from "../views/HomeRecords.vue";
import Today from "../views/Today.vue";
import Identity from "../views/Identity.vue";

export const router = createRouter({
  history: createWebHistory(import.meta.env.BASE_URL),
  routes: [
    { path: "/", name: "records", component: HomeRecords },
    { path: "/today", name: "today", component: Today },
    { path: "/identity", name: "identity", component: Identity },
  ],
});
