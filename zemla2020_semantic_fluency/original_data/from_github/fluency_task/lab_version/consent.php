<?php
    session_start();
    $_SESSION['userid'] = $_POST['userid'];
    $_SESSION['segment'] = $_POST['segment'];
?>

<form action="main.html">

<h1>Ready to begin?</h1>
<input type="submit" value="Click to begin">
</form>
