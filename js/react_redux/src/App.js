import React from 'react';

import Main from './components/Main'

import { Provider } from 'react-redux';
import { store } from './redus';


function App(props) {
  return (
    <Provider store={store}>
      <Main />
    </Provider>
  );
}

export default App;
