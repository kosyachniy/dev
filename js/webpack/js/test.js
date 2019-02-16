var $ = require('jquery');
var _ = require('underscore');

function test(user) {
	this.f1 = function() {
		$("#one").text('Hello, ' + user.name);
	}

	this.f2 = function() {
		_.each(user.cont, function(el) {
			$(".two").append('<li>' + el);
		});
	}
}

module.exports = test;