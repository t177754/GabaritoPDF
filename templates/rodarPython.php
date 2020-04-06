<html>
<head>
    <title>Rodar Gabarito</title>
</head>
<body>
    <?php
        $filePath = $_FILES['provas']['tmp_name'];
        $fileName = $_FILES['provas']['name'];
        #copy($caminhoDoArquivo,$nomeDoArquivo);

        $command = ('Corrector.py -i'.$fileName.'-o respostas.txt');
        $escapedCommand = escapeshellcmd($command);
      //  $output = shell_exec('python gabaritoPDF.py -i'.$fileName.' -o respostas.txt');
        
        echo $output;
    ?>
</body>
</html>