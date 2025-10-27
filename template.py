import mysql.connector

conexao = mysql.connector.connect(
        host="ip do Banco de Dados",
        user="usuario",
        password="senha", 
        database="Nome do Banco de Dados"
    )