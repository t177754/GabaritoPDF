<html>
<head>
    <title>Rodar Gabarito</title>
</head>
<body>
    <?php
        $caminhoDoArquivo = $_FILES['provas']['tmp_name'];
        $nomeDoArquivo = $_FILES['provas']['name'];
        #copy($caminhoDoArquivo,$nomeDoArquivo);

        $command = ('gabaritoPDF.py -i'.$nomeDoArquivo.'-o respostas.txt');
        $escapedCommand = escapeshellcmd($command);
        $output = shell_exec('python gabaritoPDF.py -i'.$nomeDoArquivo.' -o respostas.txt');
        
        echo $output;
    ?>
</body>
</html>