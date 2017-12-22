<?php
include('sys/func.php');
start('ZODZU', '/', 'Полоз Алексей - Разработчик и энтузиаст')
?>

<style type="text/css">
.info {
	width: 100vw;
	color: #505050;
	font-size: 15px;
	text-align: center;
	margin: 10px 0 -10px 0;
}

@media all and (min-width: 480px) {
	hr {width: 75%}
	.info {display: none;}
}
</style>

<div class="info" onclick="change(this);">↑ Нажми на лого ↑</div>

<div class="list"><div>Основная информация</div>
	<a>Полоз Алексей Евгеньевич</a>
	<a>19 лет</a>
	<a href="https://www.google.ru/maps/place/Санкт-Петербург/">Санкт-Петербург, Россия</a>
</div>
<hr>

<div class="list"><div>Контакты</div>
	<a href="https://vk.com/freakiller">vk.com/freakiller</a>
	<a href="http://mail.ru/">polozhev@mail.ru</a>
	<a>+7 (981) 163-55-78</a>
</div>
<hr>

<div class="list"><div>Обучение</div>
	<a href="http://spbu.ru/">СПбГУ Прикладная Математика - Процессы Управления</a>
	<a href="http://www.fml31.ru/">31 лицей г. Челябинск</a>
</div>
<hr>

<div class="list"><div>Область деятельности</div>
	<a href="https://ru.wikipedia.org/wiki/Python">Python BackEnd</a>
	<a href="https://ru.wikipedia.org/wiki/Веб-программирование">Web Full-Stack</a>
	<a>Микроконтроллеры: Raspberry Pi, Arduino</a>
</div>
<hr>

<div class="list"><div>Интересы</div>
	<a href="https://ru.wikipedia.org/wiki/Искусственный_интеллект">Artificial Intelligence, Machine Vision, Machine Learning</a>
	<a href="https://ru.wikipedia.org/wiki/Автоматизированная_система">Роботизированные / автоматизированные системы</a>
	<a href="https://ru.wikipedia.org/wiki/Бот_(программа)">Боты Телеграмм, ВКонтакте</a>
	<a>Биржа</a>
</div>
<hr>

<div class="list"><div>Конкурсы</div><!-- Достижения !-->
	<a>Первое место на региональном уровне Всероссийской Олимпиады Школьников</a>
	<a href="http://abitu.net/conference/1315">Диплом III степени МФТИ</a>
	<a>Первые места в региональных IT конкурсах</a>
</div>
<hr>

<div class="list"><div>Проекты</div></div>
<div class="notes">
<?php

$list = [
	['Телеграм бот «Дневник криптотрейдеров»', 'Параллельный анализ нескольких бирж, ведение канала, парсер синтаксиса и выделение событий, распознания текста на сложных изображениях, прогнозирование', 'https://t.me/cryptotraders100ru'], 
	['Парсер синтаксиса «Lacuna»', '', ''], 
	['Система умного дома', 'Интернет вещей, Big Data, взаимосвязь различных средств, работающих в едином комплексе и подстраивающегося под конкретные ситуации', 'http://abitu.net/conference/1315'], 
	['Twitter бот', 'Имитация поведения человека в социальной сети, постинг, лайки, репосты, анализ взаимности, анализ популярности, автонакрутка', ''], 
	['Универсальный сайт', 'Социальная сеть с множеством других сервисов, тесно связанных и взаимодействующих между собой', ''], 
	['Категайзер текстов', 'Используя технологию Google Word2Vec и собственноручно прописанная модель нейронной сети', ''], 
	['Прогноз биржи Газпром', '', ''], 
	['СПбГУ газета «Source»', '', 'http://sourceme.ru/'], 
	['Сайт рекламного агентства «PR-Light»', 'Тонко подстраиваемый кабинет администратора', 'http://pr-light.ru/'],
	['Корпус слов', '', ''],
	['Умная кнопка жизни для людей с ограниченными возможностями', 'Управление специальными средствами, системой умного дома и экстренная помощь', '']
];

for ($i=0; $i<count($list); $i++) {
	/*
	if ($list[$i][2])
		$href = $list[$i][2];
	else
		$href = '?i=' . $i
	*/
	print '<a href="' . $list[$i][2] . '"><div style="background-image: url(../load/projects/' . ($i + 1) . '.jpg);"><div class="back"><div class="title">' . $list[$i][0] . '<div>' . $list[$i][1] . '</div></div></div></div></a>';
}

?>
</div>

</body>
</html>