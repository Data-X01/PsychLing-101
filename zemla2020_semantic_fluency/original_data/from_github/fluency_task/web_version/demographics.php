<?php

session_start();
$file=fopen("logs/demographics.csv", "a");

$postwrite=$_POST;
array_push($postwrite,$_SESSION['userid']);
fputcsv($file, $postwrite );
fclose($file);

// re-direct to completion code
header('Location: http://www.google.com'); 

?>
