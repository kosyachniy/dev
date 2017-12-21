<?php
include('../sys/func.php');

$nam = $_POST['nam'];
$sur = $_POST['fam'];
$log = $_POST['mail'];
$pas = $_POST['pas'];

$f = true;
$time = date('d.m.Y H:i:s');
$user_shadow = $_SERVER['REMOTE_ADDR'];

if ($nam == '' | $sur == '' | $log == '' | $pas == '') {
	$f = false;
	header("location: ./?error=3");
	act('Ошибка регистрации: 3', 9);
}

$res = mysqli_query($db, "SELECT * FROM `users`");
while($row=mysqli_fetch_array($res))
	if ($row['mail'] == $log) {
	$f = false;
	header("location: ./?error=4");
	act('Ошибка регистрации: 4', 9);
	}

if (strlen($log)<4) {
	$f = false;
	header("location: ../?error=8");
	act('Ошибка регистрации: 8', 9);
}

if (stripos($log, ';')) {
	$f = false;
	header("location: ./?error=10");
	act('Ошибка регистрации: 10', 9);
}

if ($f) {
	$_SESSION['ban']++;
	if ($_SESSION['ban'] >= 50)
		header("location: http://yandex.ru/");
	else {
		setcookie('user', $log, time()+31536000);
		setcookie('password', $pas, time()+31536000);
		$_SESSION['auth'] = 2;
		$_SESSION['user'] = $log;
		$_SESSION['access'] = 10;
		$_SESSION['fio'] = $nam . ' ' . $sur;
		$db = db();
		mysqli_query($db, "INSERT INTO `users` (login, pass, name, surname, mail) VALUES ('$log', '$pas', '$nam', '$sur', '$log');") or die(header("location: ./?error=9"));
		header('location: ../');
		mail ($log, 'Вы успешно зарегистрировались на сайте ZODZU', 'Ваш логин: ' . $log . '
		Ваш пароль: ' . $pas . ' 
		Благодарим вас за регистрацию на сайта Полоз Алексея, ZODZU.', 'Вы успешно зарегистрировались на сайте ZODZU');
		act('Успешно зарегистрироваля!', 9);
	}
}
?>