import { defineStore } from 'pinia'
import axios from 'axios'
import type { BookingItem } from '../types/bookings'
import * as bookingService from '../api/bookings'

export const useBookingsStore = defineStore('bookings', {
  state: () => ({
    bookings: [] as BookingItem[],
  }),
  actions: {
    async fetchBookings(params?: Record<string, any>) {
      try {
        const normalizedBookings = await bookingService.fetchBookings(params)
        this.bookings = normalizedBookings ?? []
        return this.bookings
      } catch (error) {
        if (axios.isAxiosError(error) && error.response?.status === 404) {
          this.bookings = []
          return this.bookings
        }
        throw error
      }
    },

    async createBooking(payload: Partial<BookingItem>) {
      const created = await bookingService.createBooking(payload)
      this.bookings.unshift(created)
      return created
    },

    async getBooking(id: string) {
      const booking = await bookingService.getBooking(id)
      const idx = this.bookings.findIndex((b) => b.id === id)
      if (idx > -1) this.bookings[idx] = booking
      else this.bookings.unshift(booking)
      return booking
    },

    async updateBooking(id: string, patch: Partial<BookingItem>) {
      const updated = await bookingService.updateBooking(id, patch)
      const idx = this.bookings.findIndex((b) => b.id === id)
      if (idx > -1) this.bookings[idx] = updated
      return updated
    },
  },
})
