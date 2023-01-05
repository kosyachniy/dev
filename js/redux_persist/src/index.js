import React from "react";
import { render } from "react-dom";
import configureStore from "./store";
import { Provider, connect } from "react-redux";
import { PersistGate } from "redux-persist/lib/integration/react";

// action creator
function updateText(text) {
    return {
        type: "UPDATE",
        text
    };
}

const styles = {
    fontFamily: "sans-serif",
    textAlign: "center"
};

const { store, persistor } = configureStore();

class App extends React.Component {
    onUpdateText = e => {
        this.props.dispatch(updateText(e.nativeEvent.target.value));
    };

    render() {
        return (
            <div style={styles}>
                <input value={this.props.text} onChange={this.onUpdateText} />
                <pre style={{ textAlign: 'left' }}>
                    {JSON.stringify(this.props, undefined, 2)}
                </pre>
            </div>
        );
    }
    }

const mapStateToProps = state => ({
    text: state.form.text,
    foo: state.form.foo,
});

const ConnectedApp = connect(mapStateToProps)(App);

render(
    <Provider store={store}>
        <PersistGate persistor={persistor}>
            <ConnectedApp />
        </PersistGate>
    </Provider>,
    document.getElementById("root")
);
