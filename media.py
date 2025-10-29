import tkinter as tk
from tkinter import messagebox, simpledialog, ttk
import re
import mysql.connector
import meutemplate


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
   
estilo_label = {"bg": "#1e1e2f", "fg": "white", "font": ("Arial", 12, "bold")}
estilo_botao = {"bg": "#4e4eb1", "fg": "white", "font": ("Arial", 11, "bold"), "width": 18}
estilo_cabecalho = {"bg": "#4e4eb1", "fg": "white", "font": ("Arial", 12, "bold")}
estilo_linha_par = {"bg": "#2c2c3e", "fg": "white", "font": ("Arial", 11)}
estilo_linha_impar = {"bg": "#3c3c4e", "fg": "white", "font": ("Arial", 11)}
estilo_media_par = {"bg": "#2c2c3e", "fg": "white", "font": ("Arial", 12, "bold")}
estilo_media_impar = {"bg": "#3c3c4e", "fg": "white", "font": ("Arial", 12, "bold")}


def carregar_alunos():
    
    i = 0
    
    for widget in frame_dados_alunos.winfo_children():
        widget.destroy()
        
        
    cursor.execute("SELECT ra, nome, nota1, nota2, nota3, notaPIM FROM alunos")
    resultado = cursor.fetchall()
    alunos.clear()
    
    for ra, nome, nota1, nota2, nota3, notaPIM in resultado:
        try:
            n1 = float(nota1 if nota1 is not None else 0)
            n2 = float(nota2 if nota2 is not None else 0)
            n3 = float(nota3 if nota3 is not None else 0)
            nPIM = float(notaPIM if notaPIM is not None else 0)
            media = (n1 + n2 + n3 + nPIM) / 4
            media_formatada = f"{media:.2f}"
            
            estilo_linha = estilo_linha_par if i % 2 == 0 else estilo_linha_impar
            

        
            label_nome = tk.Label(frame_dados_alunos, text=nome, anchor="w", **estilo_linha)
           
            label_media = tk.Label(frame_dados_alunos, text=media_formatada, **estilo_linha)

            
            label_nome.grid(row=i, column=0, sticky="ew", padx=5, pady=2)
            label_media.grid(row=i, column=1, sticky="ew", padx=5, pady=2)

            i += 1
        except (ValueError, TypeError):
            media_formatada = "N/A"
        
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
        if nota_str is None: 
            return

        nota = float(nota_str.replace(',', '.'))
        if 0 <= nota <= 10:
            cursor.execute("INSERT INTO notas (aluno_id, nota) VALUES (%s, %s)", (aluno_id, nota))
            conexao.commit()
            messagebox.showinfo("Sucesso", f"Nota {nota} adicionada para {nome}.")
        else:
            messagebox.showerror("Erro", "A nota deve estar entre 0 e 10.")
    except (TypeError, ValueError):
        messagebox.showerror("Erro", "Digite um número válido para a nota.")
    except mysql.connector.Error as err:
        messagebox.showerror("Erro SQL", f"Erro ao inserir nota: {err}")


def consultar_media_aluno():

    
    ra_temporario = simpledialog.askstring("Consultar Média", "Digite o RA do aluno:")

   
    if ra_temporario is None:
        return  

    ra = ra_temporario.strip().upper()
    if not ra:
        messagebox.showwarning("Aviso", "Nenhum RA foi digitado.")
        return

    try:
       
        cursor.execute("SELECT nome, nota1, nota2, nota3, notaPIM FROM alunos WHERE ra = %s", (ra,))
        
        aluno_data = cursor.fetchone() 

       
        if aluno_data is None:
            messagebox.showerror("Erro", f"O RA '{ra}' não foi encontrado!")
            return

        
        nome, nota1, nota2, nota3, notaPIM = aluno_data

        
        n1 = float(nota1 if nota1 is not None else 0)
        n2 = float(nota2 if nota2 is not None else 0)
        n3 = float(nota3 if nota3 is not None else 0)
        nPIM = float(notaPIM if notaPIM is not None else 0)
        
        media = (n1 + n2 + n3 + nPIM) / 4

      
        messagebox.showinfo("Média do Aluno", f"Aluno: {nome}\nRA: {ra}\nMédia: {media:.2f}")

    except mysql.connector.Error as err:
        messagebox.showerror("Erro de Banco de Dados", f"Erro ao consultar o aluno: {err}")

janela = tk.Tk()
janela.title("Sistema de Notas - Luiz Otávio")
janela.geometry("600x400")
janela.config(bg="#1e1e2f")

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
tk.Button(frame_botoes, text="Atualizar ", command=carregar_alunos, **estilo_botao).grid(row=1, column=0, padx=5, pady=5)
tk.Button(frame_botoes, text="Consultar Média", command=consultar_media_aluno, **estilo_botao).grid(row=1, column=1, padx=5, pady=5)

frame_tabela = tk.Frame(janela, bg="#0000ff")
frame_tabela.pack(pady=10, padx=10, fill="both", expand=True)
frame_cabecalho = tk.Frame(frame_tabela)
frame_cabecalho.pack(fill="x")

label_cabecalho_nome = tk.Label(frame_cabecalho, text="Alunos Cadastrados:", anchor="w", **estilo_cabecalho)
label_cabecalho_nome.pack(side="left", fill="x", expand=True, padx=5, pady=5)



frame_dados_alunos = tk.Frame(frame_tabela, bg="#1e1e2f")
frame_dados_alunos.pack(fill="both", expand=True)

frame_dados_alunos.grid_columnconfigure(0, weight=3) 
frame_dados_alunos.grid_columnconfigure(1, weight=1) 

carregar_alunos()

janela.mainloop()


if 'conexao' in locals() and conexao.is_connected():
    cursor.close()
    conexao.close()