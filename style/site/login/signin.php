<?php
include('../sys/func.php');
$db = db();
       
$log = $_POST['user'];       
$pas = $_POST['pas'];
$time = date('d.m.Y H:i:s');

$f = true;

$res = mysqli_query($db, "SELECT * FROM `users` WHERE `login`='$log'");
while ($row=mysqli_fetch_array($res))
    if ($row['pass'] == $pas) {
        $f = false;

        $_SESSION['auth'] = 2;
        $_SESSION['user'] = $log;
        //$_SESSION['access'] = $row['admin'];
        $_SESSION['fio'] = $row['name'] . ' ' . $row['surname'];

        setcookie('user', $log, time()+31536000);
        setcookie('password', $pas, time()+31536000);

        $str = $_SESSION['inp'];
        header("location: " . $str);

        act('Вошёл', 9);
    }

if ($f) {
    $_SESSION['ban']++;
    act('Запретили вход', 9);

    //Ограничение в количестве регистраций и попыток подбора пароля
    if ($_SESSION['ban'] >= 50)
        header("location: http://yandex.ru/");
    else
        header("location: ./?error=2");
}
?>