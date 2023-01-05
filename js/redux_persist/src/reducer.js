export default (state={
    text: 'initial',
}, action) => {
    switch(action.type) {
        case 'UPDATE':
            return {
                ...state,
                text: action.text,
                foo: {
                    ...state.foo,
                    bar: action.text,
                },
            }
        default:
            return state
    }
}
