// Автоматическое изменение ширины в зависимости от контента

$('textarea').each(function () {
	this.setAttribute('style', 'height:' + (Math.max(this.scrollHeight, +this.style.height.replace(/\D+/g, ''))) + 'px; overflow-y:hidden;');
	}).on('input', function () {
		//this.style.height = 'auto';
		this.style.height = (Math.max(this.scrollHeight, +this.style.height.replace(/\D+/g, ''))) + 'px';
});