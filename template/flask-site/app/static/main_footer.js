// Автоматическое изменение ширины в зависимости от контента

var d = {};

$('textarea').each(function() {
	if (!(this.className in d)) {
		d[this.className] = this.clientHeight + 2;
	}
	//start_height = d[this.className]; // +this.style.height.replace(/\D+/g, '');
		alert(this.className);
		alert(d[this.className]);
	//alert(this.clientHeight);
	this.setAttribute('style', 'height:' + (Math.max(this.scrollHeight, d[this.className])) + 'px; overflow-y:hidden;');
	}).on('input', function() {
		//this.style.height = 'auto';
		this.style.height = (Math.max(this.scrollHeight, d[this.className])) + 'px';
});