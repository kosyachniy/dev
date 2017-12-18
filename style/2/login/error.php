<?php
  $error=$_GET['error'];
  if ($error==1)
    echo '<font color="green">Вы успешно зарегистрировались!</font>';
  if ($error==2)
    echo '<font color="red">Пароль не верен!</font>'; 
  if ($error==3)
    echo '<font color="red">Вы оставили пустое поле!</font>';  
  if ($error==4)
    echo '<font color="red">Такой пользователь уже существует!</font>'; 
  if ($error==5)
    echo '<font color="red">Вы не правильно повторили пароль!</font>';
  if ($error==6)
    echo '<font color="red">Слишком длинный логин (max-длина 12)!</font>';  
  if ($error==7)
    echo '<font color="red">Вы неправильно ввели код с картинки!</font>';  
  if ($error==8)
    echo '<font color="red">Слишком короткий логин (min-длина 4)!</font>';
  if ($error==9)
    echo '<font color="red">Ошибка сервера!</font>';
  if ($error==10)
    echo '<font color="red">Нельзя в логине использовать символ `;`!</font>';
?>