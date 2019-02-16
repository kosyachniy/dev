require('style-loader!css-loader!../css/main.css');
var test = require('./test.js');

var user = {
	name : 'Poloz Alexey',
	cont : [
		'one',
		'two',
		'three'
	]
};

var test_module = new test(user);

test_module.f1(user);
test_module.f2(user);