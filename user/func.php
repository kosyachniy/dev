<?php
function user($b)
  {
  $ip=$_SERVER['REMOTE_ADDR'];
  $cookie=$_COOKIE['user'];
  
  if ($_SESSION['auth']!=2 && $_SESSION['auth']!=1)
  {
  if ($cookie=='')
    {
    if ($_SESSION['auth']!=1 && $_SESSION['auth']!=2)
      { // Сообщение при первом входе в день
      $_SESSION['access']=11;
      $_SESSION['auth']=1;
      $_SESSION['user']=$ip;
      }
    }
   else
    {
    $u=mysqli_query($db,"SELECT * FROM `user` WHERE `user`='$cookie'");
    if ($u)
      {
      while ($a=mysqli_fetch_array($u))
        if ($_COOKIE['password']==$a['pas'])
          {
          $_SESSION['access']=$a['admin'];
          $_SESSION['user']=$cookie;
          $_SESSION['auth']=2;
          $_SESSION['fio']=$a['nam'].' '.$a['fam'];
          }
      }
    }
    }
  
  //1-Администратор, 2-Главный модератер(блокирование пользователей, изменение статей, добавление новостей сайта, служба поддержки), 10-Обычный пользователь, 11-Не авторизованный, 12-Пытался загрузить вирус, 13-Спамит, 14-Нарушает правила сайта(отпугивает людей от сайта, ...), 15-Взламывал сайт.
  ?>