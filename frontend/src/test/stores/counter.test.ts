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

  it('increments by specific amount', () => {
    const store = useCounterStore()
    store.incrementBy(5)
    expect(store.count).toBe(5)
  })

  it('decrements by specific amount', () => {
    const store = useCounterStore()
    store.incrementBy(10)
    store.decrementBy(3)
    expect(store.count).toBe(7)
  })

  it('handles negative increments', () => {
    const store = useCounterStore()
    store.incrementBy(-5)
    expect(store.count).toBe(-5)
  })

  it('handles zero increments', () => {
    const store = useCounterStore()
    store.incrementBy(0)
    expect(store.count).toBe(0)
  })

  it('maintains state across multiple operations', () => {
    const store = useCounterStore()
    
    store.increment()
    expect(store.count).toBe(1)
    
    store.incrementBy(5)
    expect(store.count).toBe(6)
    
    store.decrement()
    expect(store.count).toBe(5)
    
    store.decrementBy(2)
    expect(store.count).toBe(3)
    
    store.reset()
    expect(store.count).toBe(0)
  })

  it('handles large numbers', () => {
    const store = useCounterStore()
    store.incrementBy(1000000)
    expect(store.count).toBe(1000000)
  })

  it('handles decimal increments', () => {
    const store = useCounterStore()
    store.incrementBy(0.5)
    expect(store.count).toBe(0.5)
  })
})
