import { configureStore } from "@reduxjs/toolkit"
import {
    persistStore, persistReducer,
    FLUSH, REHYDRATE, PAUSE, PERSIST, PURGE, REGISTER,
} from "redux-persist"
import storage from "redux-persist/lib/storage"

import reducer from "./reducer"


export default () => {
    const store = configureStore({
        reducer: persistReducer({
            key: 'root',
            storage,
            whitelist: ['text'],
        }, reducer),
        middleware: (getDefaultMiddleware) => getDefaultMiddleware({
            serializableCheck: {
                ignoredActions: [
                    FLUSH, REHYDRATE, PAUSE, PERSIST, PURGE, REGISTER,
                ],
            },
        }),
    })

    console.log("initialState", store.getState())

    const persistor = persistStore(store, null, () => {
        console.log("restoredState", store.getState())
    })

    return { store, persistor }
}
