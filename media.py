import tkinter as tk
from tkinter import messagebox, simpledialog
import re
import mysql.connector
import meutemplate

# Variável alunos estava sendo usada sem ser definida
alunos = {}

try:
    conexao = mysql.connector.connect(
        host= meutemplate.ip,
        user=meutemplate.user,
        password=meutemplate.senha, 
        database=meutemplate.nomeDB
    )
    cursor = conexao.cursor()
except mysql.connector.Error as err:
    messagebox.showerror("Erro de Conexão", f"Não foi possível conectar ao banco de dados: {err}")
    # Você pode querer sair do programa aqui se a conexão for vital
    # exit()


def carregar_alunos():
    # Esta função não é estritamente necessária se atualizar_lista já busca os dados
    # do banco, mas a mantive para mostrar a correção da variável 'alunos'.
    cursor.execute("SELECT ra, nome FROM alunos")
    resultado = cursor.fetchall()
    alunos.clear()
    for ra, nome in resultado:
        alunos[ra] = {"nome": nome, "notas": []}
        # Para evitar muitas consultas individuais, o ideal seria uma única
        # consulta com JOIN e depois processar os dados em Python.
        cursor.execute("""
            SELECT nota FROM notas n 
            JOIN alunos a ON n.aluno_id = a.id 
            WHERE a.ra = %s
        """, (ra,))
        notas = [float(n[0]) for n in cursor.fetchall()]
        alunos[ra]["notas"] = notas

def validar_ra(ra):
    # Padrão da UNIP: 6 a 8 caracteres alfanuméricos maiúsculos
    padrao = r"^[A-Z0-9]{6,8}$"
    return re.match(padrao, ra) is not None

def cadastrar_aluno():
    nome = entry_nome.get().strip()
    ra = entry_ra.get().strip().upper()

    if not nome or not ra:
        messagebox.showwarning("Atenção", "Preencha todos os campos.")
        return

    if not validar_ra(ra):
        messagebox.showerror("Erro", "RA inválido! Use o padrão da UNIP (6 a 8 caracteres, letras/números).")
        return

    cursor.execute("SELECT ra FROM alunos WHERE ra = %s", (ra,))
    if cursor.fetchone():
        messagebox.showerror("Erro", "Esse RA já foi cadastrado!")
        return
    
    try:
        cursor.execute("INSERT INTO alunos (nome, ra) VALUES (%s, %s)", (nome, ra))
        conexao.commit()
        messagebox.showinfo("Sucesso", f"Aluno {nome} cadastrado com sucesso!")
        entry_nome.delete(0, tk.END)
        entry_ra.delete(0, tk.END)
        atualizar_lista()
    except mysql.connector.Error as err:
        messagebox.showerror("Erro SQL", f"Erro ao inserir aluno: {err}")

def atribuir_nota():
    ra = simpledialog.askstring("Atribuir Nota", "Digite o RA do aluno:").strip().upper()
    if not ra: return

    cursor.execute("SELECT id, nome FROM alunos WHERE ra = %s", (ra,))
    aluno = cursor.fetchone()

    if not aluno:
        messagebox.showerror("Erro", "RA não encontrado!")
        return

    aluno_id, nome = aluno

    try:
        nota_str = simpledialog.askstring("Nota", f"Digite a nota da prova (0-10) para {nome}:")
        if nota_str is None: # Usuário cancelou
            return

        nota = float(nota_str.replace(',', '.')) # Permite vírgula como separador
        if 0 <= nota <= 10:
            cursor.execute("INSERT INTO notas (aluno_id, nota) VALUES (%s, %s)", (aluno_id, nota))
            conexao.commit()
            messagebox.showinfo("Sucesso", f"Nota {nota} adicionada para {nome}.")
            atualizar_lista()
        else:
            messagebox.showerror("Erro", "A nota deve estar entre 0 e 10.")
    except (TypeError, ValueError):
        messagebox.showerror("Erro", "Digite um número válido para a nota.")
    except mysql.connector.Error as err:
        messagebox.showerror("Erro SQL", f"Erro ao inserir nota: {err}")


def calcular_media(ra):
    """Retorna a média do aluno ou None se não houver notas."""
    cursor.execute("""
        SELECT AVG(nota)
        FROM notas n
        JOIN alunos a ON a.id = n.aluno_id
        WHERE a.ra = %s
    """, (ra,))
    # fetchone() retorna uma tupla. O primeiro elemento [0] é a média ou None.
    resultado = cursor.fetchone()[0]
    return resultado

# FUNÇÃO CORRIGIDA PARA O BOTÃO "Consultar Média"
def consultar_media_aluno():
    """Pede o RA e exibe a média do aluno em uma messagebox."""
    ra = simpledialog.askstring("Consultar Média", "Digite o RA do aluno:").strip().upper()
    if not ra: return

    cursor.execute("SELECT nome FROM alunos WHERE ra = %s", (ra,))
    aluno = cursor.fetchone()

    if not aluno:
        messagebox.showerror("Erro", "RA não encontrado!")
        return
    
    nome = aluno[0]
    media = calcular_media(ra)

    if media is not None:
        messagebox.showinfo("Média do Aluno", f"Aluno: {nome}\nRA: {ra}\nMédia: {media:.2f}")
    else:
        messagebox.showinfo("Média do Aluno", f"Aluno: {nome}\nRA: {ra}\nNenhuma nota encontrada.")

def atualizar_lista():
    lista.delete(0, tk.END)
    
    try:
        cursor.execute("SELECT ra, nome FROM alunos ORDER BY nome")
        alunos_db = cursor.fetchall() # Usando outro nome para evitar confusão com o global 'alunos'

        for ra, nome in alunos_db:
            media = calcular_media(ra)
            if media is not None:
                lista.insert(tk.END, f"{ra} - {nome} | Média: {media:.2f}")
            else:
                lista.insert(tk.END, f"{ra} - {nome} | Sem notas ainda")
    except mysql.connector.Error as err:
        messagebox.showerror("Erro SQL", f"Erro ao carregar lista: {err}")


janela = tk.Tk()
janela.title("Sistema de Notas - Luiz Otávio")
janela.geometry("600x400")
janela.config(bg="#1e1e2f")

# --- Interface Gráfica (Sem mudanças) ---
estilo_label = {"bg": "#1e1e2f", "fg": "white", "font": ("Arial", 12, "bold")}
estilo_botao = {"bg": "#4e4eb1", "fg": "white", "font": ("Arial", 11, "bold"), "width": 18}

tk.Label(janela, text="Nome do aluno:", **estilo_label).pack(pady=5)
entry_nome = tk.Entry(janela, width=40)
entry_nome.pack()

tk.Label(janela, text="RA do aluno (A****B*):", **estilo_label).pack(pady=5)
entry_ra = tk.Entry(janela, width=40)
entry_ra.pack()

frame_botoes = tk.Frame(janela, bg="#1e1e2f")
frame_botoes.pack(pady=15)

tk.Button(frame_botoes, text="Cadastrar Aluno", command=cadastrar_aluno, **estilo_botao).grid(row=0, column=0, padx=5, pady=5)
tk.Button(frame_botoes, text="Atribuir Nota", command=atribuir_nota, **estilo_botao).grid(row=0, column=1, padx=5, pady=5)

# CORREÇÃO: Usando a nova função que trata a consulta
tk.Button(frame_botoes, text="Consultar Média", command=consultar_media_aluno, **estilo_botao).grid(row=1, column=0, padx=5, pady=5)
tk.Button(frame_botoes, text="Atualizar Lista", command=atualizar_lista, **estilo_botao).grid(row=1, column=1, padx=5, pady=5)

tk.Label(janela, text="Alunos cadastrados:", **estilo_label).pack(pady=5)
lista = tk.Listbox(janela, width=70, height=10, bg="#2b2b40", fg="white", font=("Consolas", 10))
lista.pack()

# CHAMADA INICIAL: Carregar a lista na inicialização
atualizar_lista()

janela.mainloop()

# Fechar conexão ao sair
if 'conexao' in locals() and conexao.is_connected():
    cursor.close()
    conexao.close()