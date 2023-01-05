import { createStore, combineReducers } from "redux";
import { persistStore, persistReducer } from "redux-persist";
import storage from "redux-persist/lib/storage";
import rootReducer from "./reducer/index";

function configureStore(initialState = {}) {
    const reducer = combineReducers({
        auth: () => ({ mock: true }),
        form: persistReducer({
            key: "form", // key for localStorage key, will be: "persist:form"
            storage,
            debug: true,
            blacklist: ['foo'],
        }, rootReducer),
    });

    const store = createStore(persistReducer({
        key: "root",
        debug: true,
        storage,
        whitelist: ['auth'],
    }, reducer), initialState);

    console.log("initialState", store.getState());

    const persistor = persistStore(store, null, () => {
        console.log("restoredState", store.getState());
    });

    return { store, persistor };
}

export default configureStore;
