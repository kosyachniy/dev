<?php
include ('../sys/func.php');
$db=db();
                   
$log=$_POST['user'];       
$pas=$_POST['pas'];

$time=date('d.m.Y H:i:s');
$f=0;

$res=mysqli_query($db,"SELECT * FROM `user` WHERE `mail`='$log'");
while($row=mysqli_fetch_array($res))
  if ($row['pas']==$pas)
    {
    $f=1;
    $_SESSION['auth']=2;
    $_SESSION['user']=$log;
    $_SESSION['access']=$row['admin'];
    $_SESSION['fio']=$row['nam'].' '.$row['fam'];
    setcookie('user', $log, time()+31536000);
    setcookie('password', $pas, time()+31536000);
    $str=$_SESSION['inp'];
    header("location: ".$str);
    act(9, 'Вошёл');
    }

if ($f==0)
    {
    $_SESSION['ban']++;
    act(9, 'Запретили вход');
    if ($_SESSION['ban']>=50) //Ограничение в количестве регистраций и попыток подбора пароля
      header("location: http://yandex.ru/");
     else
      header("location: ./?error=2");
    }
?>