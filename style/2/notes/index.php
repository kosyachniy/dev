<?php
include('../sys/func.php');
start('Статьи - ZODZU', 'notes', 'Статьи');
$db = db();

$list = mysqli_query($db, "SELECT * FROM `notes` WHERE ORDER BY `priority` DESC");
while ($note = mysqli_fetch_array($list))
	print '<a href="?i='.$note['id'].'"><div style="background-image: url(../load/img/'.$note['id'].'.jpg);"><div>'.$note['nam'].'</div></div>';
?>

</body>
</html>