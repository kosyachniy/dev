export function generete(length=32) {
    let symbols = "abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ1234567890".split("");
    let token = [];

    for (let i=0; i<length; i++) {
        let j = (Math.random() * (symbols.length-1)).toFixed(0);
        token[i] = symbols[j];
    }

    return token.join("");
}

export function getToken() {
    let token = localStorage.getItem('token');

    if (token === null) {
        token = generete();
        localStorage.setItem('token', token);
    }

    return token;
}
