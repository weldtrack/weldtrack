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
        children: [
          {
            path: '',
            name: 'customer-services',
            component: () => import('../views/dashboard/components/customer/CustomerServicesBrowse.vue'),
          },
          {
            path: 'booking',
            name: 'customer-booking',
            component: () => import('../views/dashboard/components/customer/CustomerBooking.vue'),
          },
          {
            path: 'addresses',
            name: 'customer-addresses',
            component: () => import('../views/dashboard/components/customer/CustomerAddresses.vue'),
          },
          {
            path: 'history',
            name: 'customer-history',
            component: () => import('../views/dashboard/components/customer/BookingHistory.vue'),
          },
          {
            path: 'feedback',
            name: 'customer-feedback',
            component: () => import('../views/dashboard/components/shared/ServiceFeedback.vue'),
          },
          {
            path: 'profile',
            name: 'customer-profile',
            component: () => import('../views/dashboard/ProfilePage.vue'),
          },
        ],
      },
      {
        path: '/dashboard/staff',
        name: 'staff-dashboard',
        redirect: { name: 'staff-attendance' },
        component: () => import('../views/dashboard/StaffDashboard.vue'),
        children: [
          {
            path: '',
            component: () => import('../views/dashboard/components/staff/StaffWorkspace.vue'),
            children: [
              {
                path: 'attendance',
                name: 'staff-attendance',
                component: () => import('../views/dashboard/components/staff/StaffAttendance.vue'),
              },
              {
                path: 'tasks',
                name: 'staff-tasks',
                component: () => import('../views/dashboard/components/staff/StaffTasks.vue'),
              },
              {
                path: 'contributions',
                name: 'staff-contributions',
                component: () => import('../views/dashboard/components/staff/StaffContributions.vue'),
              },
              {
                path: 'create',
                name: 'staff-create',
                component: () => import('../views/dashboard/components/staff/StaffCreate.vue'),
              },
              {
                path: 'feedback',
                name: 'staff-feedback',
                component: () => import('../views/dashboard/components/shared/ServiceFeedback.vue'),
              },
              {
                path: 'profile',
                name: 'staff-profile',
                component: () => import('../views/dashboard/ProfilePage.vue'),
              },
            ],
          },
        ],
      },
      {
        path: '/dashboard/admin',
        name: 'admin-dashboard',
        component: () => import('../views/dashboard/AdminDashboard.vue'),
        children: [
          {
            path: '',
            name: 'admin-overview',
            component: () => import('../views/dashboard/components/admin/AdminOverview.vue'),
          },
          {
            path: 'staff',
            name: 'admin-staff',
            redirect: { name: 'admin-staff-attendance' },
            component: () => import('../views/dashboard/components/staff/StaffWorkspace.vue'),
            children: [
              {
                path: 'attendance',
                name: 'admin-staff-attendance',
                component: () => import('../views/dashboard/components/staff/StaffAttendance.vue'),
              },
              {
                path: 'tasks',
                name: 'admin-staff-tasks',
                component: () => import('../views/dashboard/components/staff/StaffTasks.vue'),
              },
              {
                path: 'contributions',
                name: 'admin-staff-contributions',
                component: () => import('../views/dashboard/components/staff/StaffContributions.vue'),
              },
              {
                path: 'create',
                name: 'admin-staff-create',
                component: () => import('../views/dashboard/components/staff/StaffCreate.vue'),
              },
            ],
          },
          {
            path: 'users',
            name: 'admin-users',
            component: () => import('../views/dashboard/components/admin/AdminUsers.vue'),
          },
          {
            path: 'approval',
            name: 'admin-approval',
            component: () => import('../views/dashboard/components/admin/BookingApproval.vue'),
          },
          {
            path: 'inventory',
            name: 'admin-inventory',
            component: () => import('../views/dashboard/components/admin/InventoryManagement.vue'),
          },
          {
            path: 'reports',
            name: 'admin-reports',
            component: () => import('../views/dashboard/components/admin/Reports.vue'),
          },
          {
            path: 'services',
            name: 'admin-services',
            component: () => import('../views/dashboard/components/admin/ServiceManagement.vue'),
          },
          {
            path: 'projects',
            name: 'admin-projects',
            component: () => import('../views/dashboard/components/shared/ProjectHistory.vue'),
          },
          {
            path: 'feedback',
            name: 'admin-feedback',
            component: () => import('../views/dashboard/components/shared/ServiceFeedback.vue'),
            props: { isAdmin: true },
          },
          {
            path: 'profile',
            name: 'admin-profile',
            component: () => import('../views/dashboard/ProfilePage.vue'),
          },
        ],
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
      {
        path: '/privacy',
        name: 'privacy',
        component: () => import('../views/PrivacyPolicy.vue'),
      },
      {
        path: '/terms',
        name: 'terms',
        component: () => import('../views/TermsOfService.vue'),
      },
      {
        path: '/:pathMatch(.*)*',
        name: 'not-found',
        component: () => import('../views/NotFound.vue'),
      },
    ],
  })
}
