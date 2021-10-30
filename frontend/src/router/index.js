import { createRouter, createWebHistory } from "vue-router";

import RegisterRequest from "../views/RegisterRequest.vue";
import ConsentApproval from "../views/ConsentApproval.vue";
import UpdateAddress from "../views/UpdateAddress.vue";

const routes = [
  {
    path: "/",
    name: "Register Request",
    component: RegisterRequest,
  },
  {
    path: "/l/:request_id",
    name: "Landlord Consent Approval",
    component: ConsentApproval,
  },
  {
    path: "/r/:request_id",
    name: "Update Address",
    component: UpdateAddress,
  },
];

const router = createRouter({
  history: createWebHistory(process.env.BASE_URL),
  routes,
});

export default router;
