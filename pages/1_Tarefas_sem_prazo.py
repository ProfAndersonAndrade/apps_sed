# Importações necessárias
import chromedriver_autoinstaller
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium import webdriver as opcoesSelenium  # Importa o módulo Selenium para automação do navegador
from selenium.webdriver.common.by import By  # Permite localizar elementos na página usando diferentes métodos (e.g., XPATH, ID)
from selenium.webdriver.support.ui import WebDriverWait  # Utilizado para esperar elementos na página
from selenium.webdriver.support import expected_conditions as EC  # Define condições que serão esperadas no WebDriverWait
import streamlit as st  # Framework para criar aplicações web simples e interativas
import tempfile  # Para criar arquivos temporários para armazenar credenciais de forma transitória
import time  # Permite controlar o tempo de execução (e.g., atrasos com sleep)
import os  # Fornece funções para interagir com o sistema operacional

# Inicialize a chave 'temp_file_path' no session_state se ainda não existir
if 'temp_file_path' not in st.session_state:
    st.session_state['temp_file_path'] = None

# Função para armazenar credenciais em um arquivo temporário
def salvar_credenciais(username, password):
    """
    Salva o nome de usuário e a senha em um arquivo temporário.
    :param username: Nome de usuário digitado pelo usuário.
    :param password: Senha digitada pelo usuário.
    :return: Caminho do arquivo temporário onde as credenciais foram salvas.
    """
    with tempfile.NamedTemporaryFile(delete=False, mode='w') as temp_file:
        temp_file.write(f'username={username}\npassword={password}')
        return temp_file.name  # Retorna o caminho do arquivo temporário

# Função para ler as credenciais do arquivo temporário
def ler_credenciais(caminho_arquivo):
    """
    Lê as credenciais armazenadas no arquivo temporário.
    :param caminho_arquivo: Caminho do arquivo temporário com as credenciais.
    :return: Um dicionário com 'username' e 'password'.
    """
    with open(caminho_arquivo, 'r') as file:
        credentials = file.read()
        # Transformar as credenciais em um dicionário
        creds_dict = dict(line.split('=') for line in credentials.splitlines())
        return creds_dict

# Função para deletar o arquivo temporário
def deletar_arquivo(caminho_arquivo):
    """
    Deleta o arquivo temporário onde as credenciais estão armazenadas.
    :param caminho_arquivo: Caminho do arquivo temporário a ser deletado.
    """
    try:
        os.remove(caminho_arquivo)
        st.success("Senhas apagadas com sucesso!")
    except Exception as e:
        st.error(f"Erro ao deletar o arquivo: {e}")

# Função para carregar o navegador Selenium com as opções desejadas
def carregar_selenium():
    """
    Carrega o navegador Chrome com as configurações necessárias para rodar em segundo plano.
    :return: Instância do navegador Chrome.
    """
    # Defina o caminho do chromedriver
    chromedriver_path = '/home/appuser/.cache/selenium/chromedriver/linux64/129.0.6668.89/chromedriver'

    chrome_options = Options()
    chrome_options.add_argument('--headless')  # Roda o navegador em modo headless (sem interface gráfica)
    chrome_options.add_argument('--no-sandbox')  # Desativa o sandbox do navegador
    chrome_options.add_argument('--disable-dev-shm-usage')  # Desativa o uso excessivo de memória compartilhada
    navegador = opcoesSelenium.Chrome(options=chrome_options)
    # Utilize o caminho explicitamente no Service
    service = Service(chromedriver_path)
    driver = opcoesSelenium.Chrome(service=service, options=chrome_options)
    return navegador

# Função de login que tenta autenticar e, se falhar, retorna ao fluxo de entrada de dados
def login(documento, password):
    """
    Realiza o login na plataforma e processa as atividades com prazos.
    :param documento: Documento do usuário (ex: RG com dígito).
    :param password: Senha do usuário.
    :return: True se o login e o processamento forem bem-sucedidos, False caso contrário.
    """
    navegador = carregar_selenium()
    navegador.get('https://cmsp.ip.tv/')  # Navega até a URL da aplicação
    time.sleep(5)
    try:
        # Realiza o processo de login automatizado
        navegador.find_element(By.XPATH, '//*[@id="root"]/div[2]/div/div[1]/div/div[3]/form/div/div[1]/div/div').click()
        time.sleep(2)
        navegador.find_element(By.XPATH, '//*[@id=":r4:"]/li[1]').click()
        time.sleep(2)
        navegador.find_element(By.ID, 'document').send_keys(documento)
        time.sleep(2)
        navegador.find_element(By.ID, 'password').send_keys(password)
        time.sleep(2)
        navegador.find_element(By.XPATH, '//*[@id="root"]/div[2]/div/div[1]/div/div[3]/form/div/div[5]/button').click()
        time.sleep(5)

        # Verificar a presença do elemento de falha de login usando WebDriverWait
        try:
            WebDriverWait(navegador, 10).until(
                EC.presence_of_element_located((By.XPATH, '/html/body/div[1]/div[1]/div/div'))
            )
            st.error("Falha no login. Por favor, verifique suas credenciais e tente novamente.")
            return False  # Indica que o login falhou e precisa ser tentado novamente
        except:
            st.success("Login efetuado com sucesso! Aguarde verificação de atividades.")
            
            # Processo de navegação e remoção de prazos de atividades
            navegador.find_element(By.XPATH, '//*[@id="1"]/ul/li/button').click()
            time.sleep(2)
            navegador.find_element(By.XPATH, '//*[@id="1"]/ul/li/div/div/div/ul/li[2]/a').click()
            time.sleep(2)
            navegador.find_element(By.XPATH, '/html/body/div[1]/div[2]/div[3]/div/div/div/div[1]/div[2]/div/div/div/div/div/div[3]/div/div[2]/div[2]/div/div[2]').click()
            time.sleep(2)
            navegador.find_element(By.XPATH, '/html/body/div[5]/div[3]/ul/li[3]').click()
            time.sleep(3)
            tabela = navegador.find_element(By.XPATH, '//*[@id="root"]/div[2]/div[3]/div/div/div/div[1]/div[2]/div/div/div/div/div/div[3]/div/div[1]/div[1]/div[2]/div/div/div/table')
            time.sleep(2)
            linhas = tabela.find_elements(By.TAG_NAME, 'tr')
            time.sleep(2)
            dados = []
            ids = []
            # Coleta os dados da tabela para identificar atividades com prazo
            for linha_atual in linhas:
                colunas = linha_atual.find_elements(By.TAG_NAME, 'td')
                linha_dados = [coluna.text for coluna in colunas]
                dados.append(linha_dados)
            del dados[0]
            for id in dados:
                if id[9] != '-':
                    ids.append(id[8])

            # Inicializa a barra de progresso para o processamento dos IDs
            total_ids = len(ids)
            if total_ids == 0:
                st.error("Nenhuma data válida encontrada para processamento.")
            else:
                st.info(f'Foram encontradas {total_ids} atividades com prazo', icon="ℹ️")
                progress_text = "Processando a remoção de prazo. Por favor, aguarde."
                my_bar = st.progress(0, text=progress_text)

                # Processa cada ID, atualizando a barra de progresso a cada passo
                for index, id in enumerate(ids):
                    # Executa a remoção do prazo para cada atividade
                    navegador.find_element(By.XPATH, f'//*[@id="{id}"]/div/button').click()
                    time.sleep(2)
                    navegador.find_element(By.XPATH, '/html/body/div[5]/div[3]/ul/li[3]/div[2]').click()
                    time.sleep(3)
                    navegador.find_element(By.XPATH, '/html/body/div[1]/div[2]/div/div/div/div/div[1]/div[2]/div/div/div/div/div/div/div[1]/button[2]').click()
                    time.sleep(3)
                    checkbox = navegador.find_element(By.XPATH, '/html/body/div[5]/div[3]/div/div/div[1]/div[1]/div[2]/div[1]/span/span[1]/input')
                    if checkbox.is_selected():  # Verifica se o checkbox está checado
                        checkbox.click()  # Clica para desmarcar
                        time.sleep(2)
                        navegador.find_element(By.XPATH, '/html/body/div[5]/div[3]/div/div/div[2]/button[2]').click()
                        time.sleep(3)
                    else:
                        navegador.find_element(By.XPATH, '/html/body/div[5]/div[3]/div/div/div[2]/button[1]').click()
                        time.sleep(3)

                    # Salva a mudança de data
                    navegador.find_element(By.XPATH, '//*[@id="root"]/div[2]/div/div/div/div/div[1]/div[2]/div/div/div/div/div/div/button[2]').click()
                    time.sleep(3)
                    navegador.find_element(By.XPATH, '//*[@id="root"]/div[2]/div/div/div/div/div[1]/div[2]/div/div/div/div/div/div/button[1]').click()
                    time.sleep(3)
                    navegador.find_element(By.XPATH, '/html/body/div[1]/div[2]/div[3]/div/div/div/div[1]/div[2]/div/div/div/div/div/div[3]/div/div[2]/div[2]/div/div[2]').click()
                    time.sleep(2)
                    navegador.find_element(By.XPATH, '/html/body/div[5]/div[3]/ul/li[3]').click()
                    time.sleep(3)  # Simule o tempo que leva para processar um ID (substitua pelo código real)

                    # Atualiza a barra de progresso
                    progresso = (index + 1) / total_ids * 100
                    my_bar.progress(int(progresso), text=f"{progress_text} ({index + 1} de {total_ids}) processados.")

                # Conclui o processo e limpa a barra de progresso
                my_bar.empty()
                st.success("Todas as atividades foram processadas com sucesso!")

    except Exception as e:
        st.error(f"Erro durante o processo: {e}")
    finally:
        navegador.quit()  # Garantir que o navegador seja fechado

    return True  # Indica que o login foi bem-sucedido

if __name__ == '__main__':
    # Interface do Streamlit para capturar o login e senha
    st.title("Removedor de prazos do Tarefas SP")
    
    # Campos de entrada para o usuário
    username = st.text_input("RG com dígito")  # Entrada para o nome de usuário
    password = st.text_input("Senha", type="password")  # Entrada para a senha

    # Botão de login
    if st.button("Entrar"):
        if username and password:
            # Salvar as credenciais em um arquivo temporário
            temp_file_path = salvar_credenciais(username, password)
            st.success("Credenciais salvas com sucesso! Não se preocupe, elas serão apagadas ao final do processo!")
            st.session_state['temp_file_path'] = temp_file_path  # Salvar o caminho na sessão
        else:
            st.error("Por favor, insira o RG com dígito e a senha.")

    # Verificar se há um caminho salvo no session_state e tentar login
    if st.session_state['temp_file_path']:
        credenciais = ler_credenciais(st.session_state['temp_file_path'])
        login_sucesso = login(credenciais.get('username'), credenciais.get('password'))
        st.link_button('Acesse o Tarefas SP', 'https://cmsp.ip.tv/')
        # Excluir o arquivo temporário após o uso
        deletar_arquivo(st.session_state['temp_file_path'])
        st.session_state['temp_file_path'] = None  # Remover o caminho da sessão
        
        # Se o login falhar, mostre uma mensagem para o usuário tentar novamente
        if not login_sucesso:
            st.warning("Tente novamente digitando suas credenciais corretamente.")


