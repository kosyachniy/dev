import React from "react"
import { createRoot } from 'react-dom/client'
import { Provider, useSelector, useDispatch } from 'react-redux'
import { PersistGate } from "redux-persist/lib/integration/react"

import configureStore from "./store"


const App = () => {
    const dispatch = useDispatch()
    const state = useSelector((state) => state)

    const updateText = (text) => {
        return {
            type: "UPDATE",
            text
        }
    }
    const onUpdateText = e => dispatch(updateText(e.nativeEvent.target.value))

    return (
        <>
            <input value={state.text} onChange={onUpdateText} />
            <pre>{JSON.stringify(state, undefined, 4)}</pre>
        </>
    )
}

const { store, persistor } = configureStore()
const root = createRoot(document.getElementById('root'))

root.render(
    <Provider store={store}>
        <PersistGate persistor={persistor}>
            <App />
        </PersistGate>
    </Provider>
)
