<?php

    session_start();

    // Set user name
    if (!isset($_SESSION['userid'])) {
        $file = fopen('subj.txt', 'r+');
        $subj=trim(fgets($file));
        $_SESSION['userid'] = 'S'.$subj;
        fseek($file,0);
        fwrite($file,$subj+1);
    }

    // Disable magic quotes
    if (get_magic_quotes_gpc()) {
        $process = array(&$_GET, &$_POST, &$_COOKIE, &$_REQUEST);
        while (list($key, $val) = each($process)) {
            foreach ($val as $k => $v) {
                unset($process[$key][$k]);
                if (is_array($v)) {
                    $process[$key][stripslashes($k)] = $v;
                    $process[] = &$process[$key][stripslashes($k)];
                } else {
                    $process[$key][stripslashes($k)] = stripslashes($v);
                }
            }
        }
        unset($process);
    }

    $file = $_SESSION['userid']."_data.txt";
    $file = fopen('./logs/'.$file, 'w');
    fwrite($file, $_POST['json']);
    fclose($file);    
?>
