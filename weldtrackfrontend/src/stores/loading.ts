import { defineStore } from 'pinia'

export const useLoadingStore = defineStore('global-loading', {
  state: () => ({
    pendingRequests: 0,
  }),
  getters: {
    isLoading: (state) => state.pendingRequests > 0,
  },
  actions: {
    start() {
      this.pendingRequests += 1
    },
    finish() {
      this.pendingRequests = Math.max(0, this.pendingRequests - 1)
    },
    reset() {
      this.pendingRequests = 0
    },
  },
})