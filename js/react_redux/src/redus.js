import { combineReducers, createStore } from 'redux';

// actions.js
export const activateGeod = geod => ({
  type: 'ACTIVATE_GEOD',
  geod,
});

export const closeGeod = () => ({
  type: 'CLOSE_GEOD',
});

// reducers.js
export const geod = (state = {}, action) => {
  switch (action.type) {
    case 'ACTIVATE_GEOD':
      return action.geod;
    case 'CLOSE_GEOD':
      return {};
    default:
      return state;
  }
};

export const reducers = combineReducers({
  geod,
});

// store.js
export function configureStore(initialState = {}) {
  const store = createStore(reducers, initialState);
  return store;
}

export const store = configureStore();
