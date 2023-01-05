import { createStore } from "redux"
import { persistStore, persistReducer } from "redux-persist"
import storage from "redux-persist/lib/storage"

import reducer from "./reducer"


export default (initialState = {}) => {
    const store = createStore(persistReducer({
        key: 'root',
        storage,
        whitelist: ['text'],
    }, reducer), initialState)

    console.log("initialState", store.getState())

    const persistor = persistStore(store, null, () => {
        console.log("restoredState", store.getState())
    })

    return { store, persistor }
}
