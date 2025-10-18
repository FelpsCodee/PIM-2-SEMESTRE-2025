import tkinter as tk
from tkinter import messagebox, simpledialog
import re

alunos = {}

def validar_ra(ra):
    padrao = r"^[A-Z]{1}\d{4}[A-Z]{1}\d{1}$"
    return re.match(padrao, ra) is not None

def cadastrar_aluno():
    nome = entry_nome.get().strip()
    ra = entry_ra.get().strip().upper()

    if not nome or not ra:
        messagebox.showwarning("Atenção", "Preencha todos os campos.")
        return

    if not validar_ra(ra):
        messagebox.showerror("Erro", "RA inválido! Use o padrão A****B* (ex: R8613D7).")
        return

    if ra in alunos:
        messagebox.showerror("Erro", "Esse RA já foi cadastrado!")
        return

    alunos[ra] = {"nome": nome, "notas": []}
    messagebox.showinfo("Sucesso", f"Aluno {nome} cadastrado com sucesso!")
    entry_nome.delete(0, tk.END)
    entry_ra.delete(0, tk.END)
    atualizar_lista()

def atribuir_nota():
    ra = simpledialog.askstring("Atribuir Nota", "Digite o RA do aluno:").strip().upper()
    if not ra or ra not in alunos:
        messagebox.showerror("Erro", "RA não encontrado!")
        return

    try:
        nota = float(simpledialog.askstring("Nota", "Digite a nota da prova (0-10):"))
        if 0 <= nota <= 10:
            alunos[ra]["notas"].append(nota)
            messagebox.showinfo("Sucesso", f"Nota {nota} adicionada para {alunos[ra]['nome']}.")
            atualizar_lista()
        else:
            messagebox.showerror("Erro", "A nota deve estar entre 0 e 10.")
    except (TypeError, ValueError):
        messagebox.showerror("Erro", "Digite um número válido.")

def calcular_media(ra):
    if ra in alunos and alunos[ra]["notas"]:
        return sum(alunos[ra]["notas"]) / len(alunos[ra]["notas"])
    return None

def consultar_media():
    ra = simpledialog.askstring("Consultar Média", "Digite o RA do aluno:").strip().upper()
    if not ra or ra not in alunos:
        messagebox.showerror("Erro", "RA não encontrado!")
        return

    media = calcular_media(ra)
    if media is not None:
        messagebox.showinfo("Média", f"Aluno: {alunos[ra]['nome']}\nMédia: {media:.2f}")
    else:
        messagebox.showinfo("Média", f"Aluno: {alunos[ra]['nome']} ainda não possui notas.")


def atualizar_lista():
    lista.delete(0, tk.END)
    for ra, dados in alunos.items():
        media = calcular_media(ra)
        if media is not None:
            lista.insert(tk.END, f"{ra} - {dados['nome']} | Média: {media:.2f}")
        else:
            lista.insert(tk.END, f"{ra} - {dados['nome']} | Sem notas ainda")

janela = tk.Tk()
janela.title("Sistema de Notas - Luiz Otávio")
janela.geometry("600x400")
janela.config(bg="#1e1e2f")

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
tk.Button(frame_botoes, text="Consultar Média", command=consultar_media, **estilo_botao).grid(row=1, column=0, padx=5, pady=5)
tk.Button(frame_botoes, text="Atualizar Lista", command=atualizar_lista, **estilo_botao).grid(row=1, column=1, padx=5, pady=5)

tk.Label(janela, text="Alunos cadastrados:", **estilo_label).pack(pady=5)
lista = tk.Listbox(janela, width=70, height=10, bg="#2b2b40", fg="white", font=("Consolas", 10))
lista.pack()


janela.mainloop()
