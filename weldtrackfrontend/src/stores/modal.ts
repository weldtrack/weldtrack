import { defineStore } from 'pinia'

export type ModalVariant = 'info' | 'success' | 'warning' | 'error'

type ModalAction = () => void | Promise<void>

let pendingAction: ModalAction | null = null

export const useModalStore = defineStore('global-modal', {
  state: () => ({
    isOpen: false,
    title: '',
    message: '',
    variant: 'info' as ModalVariant,
    confirmLabel: 'OK',
    cancelLabel: '',
    showCancel: false,
  }),
  actions: {
    open(payload: {
      title: string
      message: string
      variant?: ModalVariant
      confirmLabel?: string
      cancelLabel?: string
      onConfirm?: ModalAction
    }) {
      this.isOpen = true
      this.title = payload.title
      this.message = payload.message
      this.variant = payload.variant ?? 'info'
      this.confirmLabel = payload.confirmLabel ?? 'OK'
      this.cancelLabel = payload.cancelLabel ?? ''
      this.showCancel = Boolean(payload.onConfirm)
      pendingAction = payload.onConfirm ?? null
    },
    async accept() {
      const action = pendingAction
      this.close()
      if (action) {
        await action()
      }
    },
    close() {
      this.isOpen = false
      this.title = ''
      this.message = ''
      this.variant = 'info'
      this.confirmLabel = 'OK'
      this.cancelLabel = ''
      this.showCancel = false
      pendingAction = null
    },
  },
})