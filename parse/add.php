<?php
include('func.php');
$db=db();
$time=date('d.m.Y H:i:s');
$user=$_SERVER['REMOTE_ADDR'];
//set_time_limit(200);
$file=fopen('db.txt', 'r');

$i=0;
while (!feof($file))
  {
  $i++;
  $link[$i]=fgets($file);
  }
fclose($file);
$start='http://russian2015.ucoz.com';
$str='style="text-align: justify;">';
$first='Исходный текст';
$second=['Пример сжатого изложения','<em>Сжатое изложение</em>','<strong>Сжатое изложение</strong>','Сжатое изложение</span>','Пример сжатого&nbsp;изложения'];
$stop='';
$plus=strlen($str)+30;

for ($i=1; $i<=count($link)-1; $i++)
  {
  $step=0;
  $f=fopen($start.$link[$i], 'r');
  $orig='';
  $chang='';
  print '!!!'.$link[$i].'<br><br>';
  while (!feof($f))
    {
    $line=fgets($f);
    if (stripos($line, $first))
      $step=1;
    else
      for ($j=0; $j<=count($second)-1; $j++)
        if (stripos($line, $second[$j]))
          $step=2;
//    elseif (stripos($line, $stop))
//      $step=0;
    if (stripos($line, $str))
      {
      $line=text(substr($line, stripos($line, $str)+$plus));
//      if (stripos($line, $stop))
//        $line=substr($line, 0, stripos($line, $stop));
      if ($step==1)
        $orig.=' '.$line;
      elseif ($step==2)
        $chang.=' '.$line;
      }
    }
  fclose($f);
  print $orig.'<br><br>'.$chang.'<br><br>';
  mysqli_query($db,"INSERT INTO `note`(`cont`,`dop`,`time`,`user`) VALUES ('$orig','$chang','$time','$user');");
  $in=fopen('input.txt','a');
  $out=fopen('output.txt','a');
  fwrite($in,$orig.'
');
  fwrite($out,$chang.'
');
  fclose($in);
  fclose($out);
  }

print 'OK';
?>