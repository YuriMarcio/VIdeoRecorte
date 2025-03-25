import os
from moviepy.editor import VideoFileClip
import speech_recognition as sr
from tqdm import tqdm
from pydub import AudioSegment
from pydub.utils import make_chunks
import subprocess
import sys
from colorama import init, Fore
from PIL import Image
import numpy as np

# Inicializa o colorama
init(autoreset=True)

def open_terminal():
    if sys.platform == "win32":
        # Para Windows
        subprocess.run(["start", "cmd", "/k"], shell=True)
    elif sys.platform == "darwin":
        # Para macOS
        subprocess.run(["open", "-a", "Terminal"], shell=True)
    else:
        # Para Linux
        subprocess.run(["gnome-terminal"], shell=True)

def mostrar_mensagem_aviso():
    aviso = (
        "Aviso Importante:\n\n"
        "Ao iniciar o sistema, o processo de corte de vídeo irá criar uma pasta chamada `VideoToCorte` "
        "caso ela ainda não exista. Dentro desta pasta, será criada uma subpasta com o nome do vídeo que "
        "está sendo cortado. Certifique-se de que você tem permissão para criar pastas no diretório de destino "
        "e que há espaço suficiente para armazenar os arquivos resultantes.\n\n"
        "Resumo das Ações:\n"
        "1. **Criação da Pasta `VideoToCorte`:** Se a pasta `VideoToCorte` não existir no diretório atual, "
        "o sistema a criará automaticamente.\n"
        "2. **Criação de Subpasta para Vídeo Cortado:** Para cada vídeo que for cortado, o sistema criará uma "
        "subpasta dentro da pasta `VideoToCorte`. Esta subpasta será nomeada de acordo com o nome do vídeo original.\n\n"
        "Essas ações são necessárias para organizar os arquivos e facilitar o acesso aos vídeos cortados. Caso tenha "
        "qualquer dúvida ou encontre problemas, não hesite em entrar em contato com o suporte."
    )
    print(Fore.YELLOW + aviso)

def listar_videos(diretorio):
    try:
        arquivos = os.listdir(diretorio)
        extensoes_video = ('.mp4')
        videos = [arquivo for arquivo in arquivos if arquivo.lower().endswith(extensoes_video)]
        return videos
    except FileNotFoundError:
        print(f"Erro: O diretório {diretorio} não foi encontrado.")
        return []
    except PermissionError:
        print(f"Erro: Permissão negada para acessar o diretório {diretorio}.")
        return []
    except Exception as e:
        print(f"Erro inesperado: {e}")
        return []
    
def mostrar_opcoes(videos):
    if not videos:
        print("Nenhum vídeo encontrado.")
        return
    
    print("Escolha um vídeo:")
    for i, video in enumerate(videos):
        print(f"{i + 1}. {video}")
    
    try:
        escolha = int(input("Digite o número do vídeo desejado: ")) - 1
        if 0 <= escolha < len(videos):
            video_escolhido = videos[escolha]
            return video_escolhido
        else:
            print("Escolha inválida.")
            return None
    except ValueError:
        print("Entrada inválida. Por favor, digite um número.")
        return None

# def transcrever_audio(trecho_audio_path):
#     recognizer = sr.Recognizer()
#     audio_segment = AudioSegment.from_file(trecho_audio_path)
    
#     # Dividindo o áudio em pedaços menores para melhorar a transcrição
#     chunks = make_chunks(audio_segment, 10000)  # 10 segundos cada chunk
#     full_transcription = ""

#     for i, chunk in enumerate(chunks):
#         chunk.export("temp_chunk.wav", format="wav")
#         with sr.AudioFile("temp_chunk.wav") as source:
#             audio = recognizer.record(source)
#             try:
#                 text = recognizer.recognize_google(audio, language="pt-BR")
#                 full_transcription += text + " "
#             except sr.UnknownValueError:
#                 print("Áudio não foi compreendido")
#             except sr.RequestError as e:
#                 print(f"Erro ao requisitar resultados; {e}")
    
#     os.remove("temp_chunk.wav")
#     return full_transcription.strip()

def resize_frame(frame, new_size):
    image = Image.fromarray(frame)
    image = image.resize(new_size, Image.LANCZOS)
    return np.array(image)

def cortar_video(diretorio_entrada, diretorio_saida, nome_video, duracao_corte=120):
    if not os.path.exists(diretorio_saida):
        os.makedirs(diretorio_saida)

    video_path = os.path.join(diretorio_entrada, nome_video)
    clip = VideoFileClip(video_path)
    duracao_total = clip.duration
    print(f"Duração total do vídeo: {duracao_total} segundos")

    start_time = 0
    contador = 1

    # Definindo a resolução para o formato horizontal
    largura = 1920
    altura = 1080

    num_cortes = int(duracao_total / duracao_corte) + 1
    with tqdm(total=num_cortes, desc="Cortando vídeos", unit="corte") as pbar:
        while start_time < duracao_total:
            end_time = min(start_time + duracao_corte, duracao_total)
            trecho = clip.subclip(start_time, end_time)
            
            # Redimensionar o vídeo para a resolução horizontal
            trecho = trecho.fl_image(lambda x: resize_frame(x, (largura, altura)))
            
            # Extraindo áudio para transcrição
            trecho_audio_path = os.path.join(diretorio_saida, f"temp_audio_{contador}.wav")
            trecho.audio.write_audiofile(trecho_audio_path)

            # Transcrever áudio
            # transcricao = transcrever_audio(trecho_audio_path)
            # print(f"Transcrição: {transcricao}")

            # Salvar o vídeo cortado
            nome_trecho = f"{nome_video}_corte_{contador}.mp4"
            caminho_trecho = os.path.join(diretorio_saida, nome_trecho)
            trecho.write_videofile(caminho_trecho, verbose=False, logger=None)
            print(f"Trecho salvo em: {caminho_trecho}")
            
            start_time += duracao_corte
            contador += 1
            pbar.update(1)

            # Remover o arquivo de áudio temporário
            os.remove(trecho_audio_path)

    print("Cortes finalizados.")
# Executa o terminal e exibe a mensagem
open_terminal()
mostrar_mensagem_aviso()

diretorio_entrada = "C:\\Users\\yuri\\Videos\\VideoParaCorte"

# Listar vídeos no diretório
videos = listar_videos(diretorio_entrada)

# Mostrar opções para o usuário
video_escolhido = mostrar_opcoes(videos)

if video_escolhido:
    # Define o diretório de saída baseado no vídeo escolhido
    diretorio_saida = os.path.join("C:\\Users\\yuri\\Videos", f"cortes_{video_escolhido.replace('.mp4', '')}")
    cortar_video(diretorio_entrada, diretorio_saida, video_escolhido)
