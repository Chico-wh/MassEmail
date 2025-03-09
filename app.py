import smtplib
import time
import threading
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.base import MIMEBase
from email import encoders
import os
import tkinter as tk
from tkinter import filedialog, messagebox, simpledialog, ttk
import sqlite3
import configparser
conexao = sqlite3.connect('banco.db')
cursor = conexao.cursor()

# Criação das tabelas no banco de dados
cursor.execute('CREATE TABLE IF NOT EXISTS contatos (id INTEGER PRIMARY KEY, nome TEXT, empresa TEXT, email TEXT, pais TEXT)')
conexao.commit()

# Variáveis globais
servidor_smtp = ""
porta_smtp = ""
usuario_smtp = ""
senha_smtp = ""
# Função para enviar email com personalização
def enviar_email_personalizado(para_email, assunto, corpo_email, nome_remetente, dados_contato, caminhos_anexos=None):
    global servidor_smtp, porta_smtp, usuario_smtp, senha_smtp
    msg = MIMEMultipart()
    msg['From'] = usuario_smtp
    msg['To'] = para_email
    msg['Subject'] = assunto

    # Substitui os placeholders no corpo do email
    corpo_email = corpo_email.replace('$nome$', dados_contato['nome'])
    corpo_email = corpo_email.replace('$empresa$', dados_contato['empresa'])
    corpo_email = corpo_email.replace('$email$', dados_contato['email'])
    corpo_email = corpo_email.replace('$pais$', dados_contato['pais'])

    # Adiciona o corpo do email como HTML
    msg.attach(MIMEText(corpo_email, 'html'))

    # Adiciona múltiplos anexos
    if caminhos_anexos:
        for caminho_anexo in caminhos_anexos:
            if os.path.isfile(caminho_anexo):
                with open(caminho_anexo, 'rb') as anexo:
                    parte = MIMEBase('application', 'octet-stream')
                    parte.set_payload(anexo.read())
                    encoders.encode_base64(parte)
                    parte.add_header('Content-Disposition', f'attachment; filename={os.path.basename(caminho_anexo)}')
                    msg.attach(parte)

    try:
        servidor = smtplib.SMTP(servidor_smtp, porta_smtp)
        servidor.starttls()
        servidor.login(usuario_smtp, senha_smtp)
        texto = msg.as_string()
        servidor.sendmail(usuario_smtp, para_email, texto)
        servidor.quit()
        c = 0
        print(f'{valor}Email enviado para {para_email}')
        return True
    except Exception as e:
        print(f'Erro ao enviar email para {para_email}: {e}')
        return False


# Função para iniciar o envio de emails personalizados
def iniciar_envio_personalizado():

    global servidor_smtp, porta_smtp, usuario_smtp, senha_smtp, anexos
    if os.path.isfile('config.ini') is False:
        servidor_smtp = entrada_servidor_smtp.get()
        porta_smtp = int(entrada_porta_smtp.get())
        usuario_smtp = entrada_usuario_smtp.get()
        senha_smtp = entrada_senha_smtp.get()
        
    else:
        config = configparser.ConfigParser()
        config.read('config.ini')
        servidor_smtp = config['SMTP']['servidor_smtp']
        porta_smtp = config['SMTP']['porta_smtp']
        usuario_smtp = config['SMTP']['usuario_smtp']
        senha_smtp = config['SMTP']['senha_smtp']
    assunto = entrada_assunto.get()
    anexos = entrada_anexo.get().split(';')  #Adcionada funcionalidade pra pegar mais que um arquivo)
    corpo_email = entrada_corpo.get("1.0", tk.END)  # Pega o texto do corpo do email
    nome_remetente = entrada_nome.get()
    tempo_espera = int(entrada_tempo_espera.get()) * 60
    cursor.execute('SELECT nome, empresa, email, pais FROM contatos')
    lista_contatos = cursor.fetchall()

    # Iniciar envio de emails em thread separada
    threading.Thread(target=envio_emails_background, args=(lista_contatos, assunto, corpo_email, nome_remetente, anexos, tempo_espera)).start()

def envio_emails_background(lista_contatos, assunto, corpo_email, nome_remetente, anexos, tempo_espera):
    tamanho_lote = 50
    for i in range(0, len(lista_contatos), tamanho_lote):
        lote = lista_contatos[i:i + tamanho_lote]
        todos_enviados = True
        for contato in lote:
            dados_contato = {
                'nome': contato[0],
                'empresa': contato[1],
                'email': contato[2],
                'pais': contato[3]
            }
            if not enviar_email_personalizado(dados_contato['email'], assunto, corpo_email, nome_remetente, dados_contato, anexos):
                todos_enviados = False
        if todos_enviados:
            print(f'Todos os emails do lote {i // tamanho_lote + 1} foram enviados com sucesso.')
        else:
            print(f'Erro ao enviar alguns emails do lote {i // tamanho_lote + 1}.')
        if i + tamanho_lote < len(lista_contatos) and len(lote) == tamanho_lote:
            print(f'Aguardando {tempo_espera / 60} minutos antes de enviar o próximo lote...')
            time.sleep(tempo_espera)
    print('Envio de emails concluído.')

# Função para selecionar arquivo
def selecionar_arquivos(entrada):
    arquivos = filedialog.askopenfilenames()
    entrada.delete(0, tk.END)
    entrada.insert(0, ';'.join(arquivos))


# Função para selecionar múltiplos arquivos
def selecionar_arquivos(entrada):
    arquivos = filedialog.askopenfilenames()
    entrada.delete(0, tk.END)
    entrada.insert(0, ';'.join(arquivos))
# Função para inserir dados na tabela
def inserir_dados():
    nome = entrada_nome_info.get()
    empresa = entrada_empresa_info.get()
    email = entrada_email_info.get()
    pais = entrada_pais_info.get()
    cursor.execute('INSERT INTO contatos (nome, empresa, email, pais) VALUES (?, ?, ?, ?)', (nome, empresa, email, pais))
    conexao.commit()
    messagebox.showinfo("Sucesso", "Dados inseridos com sucesso!")
    entrada_nome_info.delete(0, tk.END)
    entrada_empresa_info.delete(0, tk.END)
    entrada_email_info.delete(0, tk.END)
    entrada_pais_info.delete(0, tk.END)
    atualizar_lista()

# Função para visualizar dados
def visualizar_dados():
    cursor.execute('SELECT * FROM contatos')
    rows = cursor.fetchall()
    lista_dados.delete(0, tk.END)
    for row in rows:
        lista_dados.insert(tk.END, row)

# Função para editar dados
def editar_dados():
    try:
        item_selecionado = lista_dados.get(lista_dados.curselection())
        id = item_selecionado[0]
        novo_nome = simpledialog.askstring("Editar Nome", "Novo nome:", initialvalue=item_selecionado[1])
        nova_empresa = simpledialog.askstring("Editar Empresa", "Nova empresa:", initialvalue=item_selecionado[2])
        novo_email = simpledialog.askstring("Editar Email", "Novo email:", initialvalue=item_selecionado[3])
        novo_pais = simpledialog.askstring("Editar País", "Novo país:", initialvalue=item_selecionado[4])
        cursor.execute('UPDATE contatos SET nome = ?, empresa = ?, email = ?, pais = ? WHERE id = ?', (novo_nome, nova_empresa, novo_email, novo_pais, id))
        conexao.commit()
        messagebox.showinfo("Sucesso", "Dados atualizados com sucesso!")
        atualizar_lista()
    except:
        messagebox.showerror("Erro", "Selecione um item para editar.")

# Função para excluir dados
def excluir_dados():
    try:
        item_selecionado = lista_dados.get(lista_dados.curselection())
        id = item_selecionado[0]
        cursor.execute('DELETE FROM contatos WHERE id = ?', (id,))
        conexao.commit()
        messagebox.showinfo("Sucesso", "Dados excluídos com sucesso!")
        atualizar_lista()
    except:
        messagebox.showerror("Erro", "Selecione um item para excluir.")

# Função para atualizar lista
def atualizar_lista():
    lista_dados.delete(0, tk.END)
    visualizar_dados()

#função pra salvar os dados de configuração 
def configsave():
    import configparser
    config = configparser.ConfigParser()
    config['SMTP'] = {
        'servidor_smtp': entrada_servidor_smtp.get(),
        'porta_smtp': int(entrada_porta_smtp.get()),
        'usuario_smtp': entrada_usuario_smtp.get(),
        'senha_smtp': entrada_senha_smtp.get()
    }

    with open('config.ini', 'w') as configfile:
        config.write(configfile)

    


def ler_arquivos_csv():
    caminhos_arquivos = filedialog.askopenfilenames(filetypes=[("Arquivos CSV", "*.csv")])
    if not caminhos_arquivos:
        return

    for caminho_arquivo in caminhos_arquivos:
        with open(caminho_arquivo, 'r', encoding='utf-8') as file:
            for line in file:
                quantidade.append(line)
                print(f"Lendo linha: {line}")  # Adicionado para depuração
                dados = line.strip().split(',')
                print(f"Dados extraídos: {dados}")  # Adicionado para depuração
                if len(dados) == 4:
                    nome, empresa, email, pais = dados
                    cursor.execute('INSERT INTO contatos (nome, empresa, email, pais) VALUES (?, ?, ?, ?)',
                                   (nome, empresa, email, pais))
                    print(f"Inserido: {nome}, {empresa}, {email}, {pais}")  # Adicionado para depuração
            conexao.commit()
            print("Commit feito")  # Adicionado para depuração

    messagebox.showinfo("Sucesso", "Dados dos arquivos inseridos com sucesso!")
    atualizar_lista()

    
janela_principal = tk.Tk()
janela_principal.title("Disparador de Email")

# Criação das abas
abas = ttk.Notebook(janela_principal)
abas.pack(expand=1, fill="both")

# Aba de Envio de Emails
aba_envio = ttk.Frame(abas)
abas.add(aba_envio, text="Envio de Emails")

tk.Label(aba_envio, text="Assunto:").grid(row=4, column=0, sticky=tk.W)
entrada_assunto = tk.Entry(aba_envio)
entrada_assunto.grid(row=4, column=1)

tk.Label(aba_envio, text="Anexos:").grid(row=5, column=0, sticky=tk.W)
entrada_anexo = tk.Entry(aba_envio)
entrada_anexo.grid(row=5, column=1)
tk.Button(aba_envio, text="Selecionar", command=lambda: selecionar_arquivos(entrada_anexo)).grid(row=5, column=2)
tk.Label(aba_envio, text="Corpo do Email:").grid(row=6, column=0, sticky=tk.W)
entrada_corpo = tk.Text(aba_envio, width=60, height=10)  # Aumenta a caixa de texto para o corpo do email
entrada_corpo.grid(row=6, column=1)

tk.Label(aba_envio, text="Nome do Remetente:").grid(row=7, column=0, sticky=tk.W)
entrada_nome = tk.Entry(aba_envio)
entrada_nome.grid(row=7, column=1)

tk.Label(aba_envio, text="Tempo de Espera (minutos):").grid(row=8, column=0, sticky=tk.W)
entrada_tempo_espera = tk.Entry(aba_envio)
entrada_tempo_espera.grid(row=8, column=1)

tk.Button(aba_envio, text="Iniciar Envio Personalizado", command=iniciar_envio_personalizado).grid(row=10, columnspan=3, pady=10)

# Aba de Gerenciamento de Contatos
aba_contatos = ttk.Frame(abas)
abas.add(aba_contatos, text="Contatos")

tk.Label(aba_contatos, text="Nome:").grid(row=0, column=0, sticky=tk.W)
entrada_nome_info = tk.Entry(aba_contatos)
entrada_nome_info.grid(row=0, column=1)

tk.Label(aba_contatos, text="Empresa:").grid(row=1, column=0, sticky=tk.W)
entrada_empresa_info = tk.Entry(aba_contatos)
entrada_empresa_info.grid(row=1, column=1)

tk.Label(aba_contatos, text="Email:").grid(row=2, column=0, sticky=tk.W)
entrada_email_info = tk.Entry(aba_contatos)
entrada_email_info.grid(row=2, column=1)

tk.Label(aba_contatos, text="País:").grid(row=3, column=0, sticky=tk.W)
entrada_pais_info = tk.Entry(aba_contatos)
entrada_pais_info.grid(row=3, column=1)

tk.Button(aba_contatos, text="Inserir Dados", command=inserir_dados).grid(row=4, columnspan=2, pady=10)
tk.Button(aba_contatos, text="Visualizar Dados", command=visualizar_dados).grid(row=5, columnspan=2, pady=10)
tk.Button(aba_contatos, text="Editar Dados", command=editar_dados).grid(row=6, columnspan=2, pady=10)
tk.Button(aba_contatos, text="Excluir Dados", command=excluir_dados).grid(row=7, columnspan=2, pady=10)
tk.Button(aba_contatos, text="Importar arquivo CSV", command=ler_arquivos_csv).grid(row=8, columnspan=2, pady=10)

lista_dados = tk.Listbox(aba_contatos, width=100)
lista_dados.grid(row=9, column=0, columnspan=2, padx=10, pady=10)


# Aba de Configurações
aba_configuracoes = ttk.Frame(abas)
abas.add(aba_configuracoes, text="Configurações")

tk.Label(aba_configuracoes, text="Servidor SMTP:").grid(row=0, column=0, sticky=tk.W)
entrada_servidor_smtp = tk.Entry(aba_configuracoes)
entrada_servidor_smtp.grid(row=0, column=1)

tk.Label(aba_configuracoes, text="Porta SMTP:").grid(row=1, column=0, sticky=tk.W)
entrada_porta_smtp = tk.Entry(aba_configuracoes)
entrada_porta_smtp.grid(row=1, column=1)

tk.Label(aba_configuracoes, text="Usuário SMTP:").grid(row=2, column=0, sticky=tk.W)
entrada_usuario_smtp = tk.Entry(aba_configuracoes)
entrada_usuario_smtp.grid(row=2, column=1)

tk.Label(aba_configuracoes, text="Senha SMTP:").grid(row=3, column=0, sticky=tk.W)
entrada_senha_smtp = tk.Entry(aba_configuracoes, show="*")
entrada_senha_smtp.grid(row=3, column=1)

# Inicializa a interface
tk.Button(aba_configuracoes, text="Salvar Configurações", command=configsave).grid(row=4, columnspan=2, pady=10)

# Função para atualizar a lista ao iniciar
atualizar_lista()

# Iniciar o loop principal da interface
janela_principal.mainloop()