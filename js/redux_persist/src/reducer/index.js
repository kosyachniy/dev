const defaultState = {
    text: 'initial',
    foo: {
        bar: 'zoo',
        nested: {
            veryDeep: true,
        },
    },
};

export default function(state=defaultState, action = {}) {
    switch(action.type) {
        case 'UPDATE':
            return {
                ...state,
                text: action.text,
                foo: {
                    ...state.foo,
                    bar: action.text,
                },
            };
        default:
            return state;
    }
};
