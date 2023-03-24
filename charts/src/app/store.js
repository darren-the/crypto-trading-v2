import { configureStore } from '@reduxjs/toolkit'
import { dfReducers } from '../features/df/dfSlices'

export const store = configureStore({
  reducer: {
    ...dfReducers,
  },
  middleware: (getDefaultMiddleware) => getDefaultMiddleware({
    immutableCheck: { warnAfter: 128 },
    serializableCheck: { warnAfter: 128 },
  }),
})
