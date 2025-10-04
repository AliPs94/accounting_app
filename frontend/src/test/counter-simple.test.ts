import { describe, it, expect, beforeEach } from 'vitest'
import { setActivePinia, createPinia } from 'pinia'
import { useCounterStore } from '@/stores/counter'

describe('Counter Store', () => {
  beforeEach(() => {
    setActivePinia(createPinia())
  })

  it('initializes with zero count', () => {
    const store = useCounterStore()
    expect(store.count).toBe(0)
  })

  it('increments count', () => {
    const store = useCounterStore()
    store.increment()
    expect(store.count).toBe(1)
  })

  it('decrements count', () => {
    const store = useCounterStore()
    store.increment()
    store.decrement()
    expect(store.count).toBe(0)
  })

  it('does not decrement below zero', () => {
    const store = useCounterStore()
    store.decrement()
    expect(store.count).toBe(0)
  })

  it('resets count to zero', () => {
    const store = useCounterStore()
    store.increment()
    store.increment()
    store.reset()
    expect(store.count).toBe(0)
  })
})
