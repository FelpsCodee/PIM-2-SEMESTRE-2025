import tkinter as tk
from tkinter import messagebox, simpledialog, ttk
import re
import mysql.connector
import meutemplate

# --- CONEXÃO COM O BANCO ---
def conectar_banco():
    try:
        conexao = mysql.connector.connect(
            host=meutemplate.ip,
            user=meutemplate.user,
            password=meutemplate.senha,
            database=meutemplate.nomeDB
        )
        cursor = conexao.cursor()
        return conexao, cursor
    except mysql.connector.Error as err:
        messagebox.showerror("Erro de Conexão", f"Não foi possível conectar ao banco de dados:\n{err}")
        return None, None

# --- CONECTAR LOGO AO INICIAR ---
conexao, cursor = conectar_banco()
if not conexao or not cursor:
    raise SystemExit("Erro: não foi possível conectar ao banco de dados. Verifique as credenciais e tente novamente.")

# --- ESTILOS ---
estilo_label = {"bg": "#1e1e2f", "fg": "white", "font": ("Arial", 12, "bold")}
estilo_botao = {"bg": "#4e4eb1", "fg": "white", "font": ("Arial", 11, "bold"), "width": 18}
estilo_cabecalho = {"bg": "#4e4eb1", "fg": "white", "font": ("Arial", 12, "bold")}
estilo_linha_par = {"bg": "#2c2c3e", "fg": "white", "font": ("Arial", 11)}
estilo_linha_impar = {"bg": "#3c3c4e", "fg": "white", "font": ("Arial", 11)}

def on_canvas_resize(event):
    canvas_width = event.width
    canvas.itemconfig(canvas_window, width=canvas_width)

def carregar_alunos():
    if not conexao or not cursor:
        messagebox.showerror("Erro", "Conexão com o banco não estabelecida.")
        return

    for widget in frame_dados_alunos.winfo_children():
        widget.destroy()

    cursor.execute("SELECT ra, nome, curso, nota1, nota2, nota3, notaPIM FROM alunos ORDER BY nome")
    resultado = cursor.fetchall()

    for i, (ra, nome, curso, nota1, nota2, nota3, notaPIM) in enumerate(resultado):
        estilo_linha = estilo_linha_par if i % 2 == 0 else estilo_linha_impar

        notas_validas = []
        for nota in [nota1, nota2, nota3, notaPIM]:
            if nota is not None:
                try:
                    notas_validas.append(float(str(nota).replace(',', '.')))
                except (ValueError, TypeError):
                    continue

        if notas_validas:
            media = sum(notas_validas) / len(notas_validas)
            media_formatada = f"{media:.2f}"
        else:
            media_formatada = "Sem notas"

        status = "(Parcial)" if len(notas_validas) < 4 else "(Final)"
        tk.Label(frame_dados_alunos, text=f"{ra} - {nome} ({curso})", anchor="w", **estilo_linha).grid(row=i, column=0, sticky="ew", padx=5, pady=2)
        tk.Label(frame_dados_alunos, text=f"{media_formatada} {status}", anchor="center", width=20, **estilo_linha).grid(row=i, column=1, sticky="ew", padx=5, pady=2)

def validar_ra(ra):
    return re.match(r"^[A-Z0-9]{6,8}$", ra) is not None

def cadastrar_aluno():
    nome = entry_nome.get().strip().upper()
    ra = entry_ra.get().strip().upper()
    curso = entry_curso.get().strip().upper()

    if not nome or not ra or not curso:
        messagebox.showwarning("Atenção", "Preencha todos os campos.")
        return

    if not validar_ra(ra):
        messagebox.showerror("Erro", "RA inválido! Use 6 a 8 caracteres, letras e números.")
        return

    cursor.execute("SELECT ra FROM alunos WHERE ra = %s", (ra,))
    if cursor.fetchone():
        messagebox.showerror("Erro", "Esse RA já foi cadastrado!")
        return

    try:
        cursor.execute("INSERT INTO alunos (nome, ra, curso) VALUES (%s, %s, %s)", (nome, ra, curso))
        conexao.commit()
        messagebox.showinfo("Sucesso", f"Aluno {nome} do curso {curso} cadastrado com sucesso!")
        entry_nome.delete(0, tk.END)
        entry_ra.delete(0, tk.END)
        entry_curso.delete(0, tk.END)
        carregar_alunos()
    except mysql.connector.Error as err:
        messagebox.showerror("Erro SQL", f"Erro ao inserir aluno: {err}")

def atribuir_nota():
    ra = simpledialog.askstring("Atribuir Nota", "Digite o RA do aluno:").strip().upper()
    if not ra:
        return

    cursor.execute("SELECT nome FROM alunos WHERE ra = %s", (ra,))
    aluno = cursor.fetchone()
    if not aluno:
        messagebox.showerror("Erro", "RA não encontrado!")
        return

    nome = aluno[0]
    coluna = simpledialog.askstring("Qual nota?", "Digite: nota1, nota2, nota3 ou notaPIM").strip()
    if coluna not in ['nota1', 'nota2', 'nota3', 'notaPIM']:
        messagebox.showerror("Erro", "Coluna inválida.")
        return

    nota_str = simpledialog.askstring("Nota", "Digite a nota (0 a 10):")
    try:
        nota_valor = float(nota_str.replace(',', '.'))
        if 0 <= nota_valor <= 10:
            cursor.execute(f"UPDATE alunos SET {coluna} = %s WHERE ra = %s", (nota_valor, ra))
            conexao.commit()
            messagebox.showinfo("Sucesso", f"{coluna.upper()} ({nota_valor:.2f}) atribuída a {nome}.")
            carregar_alunos()
        else:
            messagebox.showerror("Erro", "A nota deve estar entre 0 e 10.")
    except (ValueError, TypeError):
        messagebox.showerror("Erro", "Digite um número válido.")

def consultar_media_aluno():
    ra = simpledialog.askstring("Consultar Média", "Digite o RA do aluno:")
    if not ra:
        return

    cursor.execute("SELECT nome, nota1, nota2, nota3, notaPIM FROM alunos WHERE ra = %s", (ra,))
    aluno = cursor.fetchone()
    if not aluno:
        messagebox.showerror("Erro", f"RA '{ra}' não encontrado.")
        return

    nome, nota1, nota2, nota3, notaPIM = aluno
    notas_validas = [float(str(n).replace(',', '.')) for n in [nota1, nota2, nota3, notaPIM] if n is not None]

    if notas_validas:
        media = sum(notas_validas) / len(notas_validas)
        status = "Parcial" if len(notas_validas) < 4 else "Final"
        messagebox.showinfo("Média", f"Aluno: {nome}\nRA: {ra}\nMédia {status}: {media:.2f}")
    else:
        messagebox.showinfo("Média", f"Aluno: {nome}\nRA: {ra}\nNenhuma nota registrada.")

# --- INTERFACE TKINTER ---
janela = tk.Tk()
janela.title("Sistema de Notas - PIM 2º Semestre")
janela.geometry("1000x700")
janela.config(bg="#1e1e2f")

tk.Label(janela, text="Nome do(a) aluno(a):", **estilo_label).pack(pady=5)
entry_nome = tk.Entry(janela, width=40); entry_nome.pack()
tk.Label(janela, text="RA do aluno:", **estilo_label).pack(pady=5)
entry_ra = tk.Entry(janela, width=40); entry_ra.pack()
tk.Label(janela, text="Nome do Curso:", **estilo_label).pack(pady=5)
entry_curso = tk.Entry(janela, width=40); entry_curso.pack()

frame_botoes = tk.Frame(janela, bg="#1e1e2f")
frame_botoes.pack(pady=15)
tk.Button(frame_botoes, text="Cadastrar Aluno", command=cadastrar_aluno, **estilo_botao).grid(row=0, column=0, padx=5, pady=5)
tk.Button(frame_botoes, text="Atribuir Nota", command=atribuir_nota, **estilo_botao).grid(row=0, column=1, padx=5, pady=5)
tk.Button(frame_botoes, text="Atualizar Lista", command=carregar_alunos, **estilo_botao).grid(row=1, column=0, padx=5, pady=5)
tk.Button(frame_botoes, text="Consultar Média", command=consultar_media_aluno, **estilo_botao).grid(row=1, column=1, padx=5, pady=5)

frame_tabela = tk.Frame(janela, bg="#1e1e2f")
frame_tabela.pack(pady=10, padx=10, fill="both", expand=True)
frame_cabecalho = tk.Frame(frame_tabela, bg="#4e4eb1")
frame_cabecalho.pack(fill="x")
tk.Label(frame_cabecalho, text="Alunos Cadastrados:", anchor="w", **estilo_cabecalho).pack(side="left", fill="x", expand=True, padx=5, pady=5)
tk.Label(frame_cabecalho, text="MÉDIA", anchor="e", **estilo_cabecalho, width=15).pack(side="right", padx=5, pady=5)

canvas = tk.Canvas(frame_tabela, bg="#1e1e2f", highlightthickness=0)
canvas.pack(side="left", fill="both", expand=True)
scrollbar = ttk.Scrollbar(frame_tabela, orient="vertical", command=canvas.yview)
scrollbar.pack(side="right", fill="y")
canvas.configure(yscrollcommand=scrollbar.set)

frame_dados_alunos = tk.Frame(canvas, bg="#1e1e2f")
canvas_window = canvas.create_window((0, 0), window=frame_dados_alunos, anchor="nw")

frame_dados_alunos.bind("<Configure>", lambda e: canvas.configure(scrollregion=canvas.bbox("all")))
canvas.bind("<Configure>", on_canvas_resize)

frame_dados_alunos.grid_columnconfigure(0, weight=1)
frame_dados_alunos.grid_columnconfigure(1, weight=0)

carregar_alunos()

try:
    janela.mainloop()
finally:
    if conexao and conexao.is_connected():
        cursor.close()
        conexao.close()
