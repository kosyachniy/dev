<?php
header('Content-type: text/html; charset=utf-8');
session_start();

function db($name='') {
	$db = mysqli_connect('mysql.hostinger.ru', 'u696001181_k', 'asdrqwerty09', 'u696001181_k'.$name);
	if (mysqli_connect_errno()) print 'Ошибка 1. '.mysqli_connect_errno();
	mysqli_query($db, 'SET names "utf8"');
	return $db;
}

function user($type) {
	$ip = $_SERVER['REMOTE_ADDR'];
	$cookie = $_COOKIE['user'];

	if ($_SESSION['auth'] != 2 && $_SESSION['auth'] != 1) {
		if ($cookie == '') {
			// Сообщение при первом входе в день
			if ($_SESSION['auth'] != 1 && $_SESSION['auth'] != 2) {
				$_SESSION['access'] = 11;
				$_SESSION['auth'] = 1;
				$_SESSION['user'] = $ip;
			}
		}
		else {
			$u = mysqli_query($db, "SELECT * FROM `user` WHERE `user`='$cookie'");
			if ($u)
				while ($a=mysqli_fetch_array($u))
					if ($_COOKIE['password'] == $a['pas']) {
						$_SESSION['access'] = $a['admin'];
						$_SESSION['user'] = $cookie;
						$_SESSION['auth'] = 2;
						$_SESSION['fio'] = $a['nam'] . ' ' . $a['fam'];
					}
		}
	}

	if ($_SESSION['access'] > 12)
		print 'Ошибка 2. Вы заблокированы.';
	else {
		if ($_SESSION['auth'] == 2) {
			if ($type == 1)
				return $_SESSION['user'];
			elseif ($type == 3)
				return $_SESSION['user'] . ' <a href="/sys/php/out.php">Выйти</a>';
			elseif ($type == 4)
				return 'Вы сейчас в пользователе ' . $_SESSION['user'];
			elseif ($type == 5)
				return $_SESSION['access'];
			elseif ($type == 6)
				return $_SESSION['fio'];
		}
		else {
			if ($type == 1)
				return $ip;
			elseif ($type == 2)
				return 'Гость';
			elseif ($type == 3)
				return 'Гость <a href="/set/login/">Войти</a>';
			elseif ($type == 4)
				return 'Вы не вошли';
			elseif ($type == 5)
				return $_SESSION['access'];
		}
	}
}


function act($action, $type=0) {
	$db = db();
	$user = user(1);
	$time = date('d.m.Y H:i:s');

	if ($type == 1) $t = 'Просмотрел';
	elseif ($type == 2) $t = 'Добавил';
	elseif ($type == 3) $t = 'Загрузил';
	elseif ($type == 4) $t = 'Прокомментировал';
	elseif ($type == 5) $t = 'Изменил';
	elseif ($type == 6) $t = 'Удалил';
	elseif ($type == 7) $t = 'Нравится';
	elseif ($type == 8) $t = 'Навёл';
	elseif ($type == 9) $t = 'Логин';
	elseif ($type == 10) $t = 'Запрос';
	elseif ($type == 11) $t = 'Настройки';
	elseif ($type == 12) $t = 'Ошибка';
	elseif ($type == 13) $t = 'Сообщение';
	elseif ($type == 14) $t = 'Обратная связь';
	elseif ($type == 15) $t = 'Поиск';
	elseif ($type == 16) $t = 'Другое:';

	$t .= ' ' . $action;
	mysqli_query($db, "INSERT INTO `act`(`user`, `cont`, `time`) VALUES ('$user', '$t', '$time');");
}

function start($title, $source, $description) {
	act($source, 1);
	include('main.tpl');
}
?>