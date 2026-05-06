import { createRouter as createVueRouter, createWebHistory } from 'vue-router'

export function createRouter() {
  return createVueRouter({
    history: createWebHistory(),
    routes: [
      {
        path: '/',
        name: 'webpage',
        component: () => import('../views/Webpage.vue'),
      },
      {
        path: '/dashboard',
        name: 'customer-dashboard',
        component: () => import('../views/dashboard/CustomerDashboard.vue'),
      },
      {
        path: '/dashboard/staff',
        name: 'staff-dashboard',
        component: () => import('../views/dashboard/StaffDashboard.vue'),
      },
      {
        path: '/dashboard/admin',
        name: 'admin-dashboard',
        component: () => import('../views/dashboard/AdminDashboard.vue'),
      },
      {
        path: '/login',
        name: 'login',
        component: () => import('../views/auth/LoginPage.vue'),
      },
      {
        path: '/signup',
        name: 'signup',
        component: () => import('../views/auth/SignupPage.vue'),
      },
    ],
  })
}
