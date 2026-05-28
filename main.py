import threading
import time
import random
from datetime import datetime

CAPACIDADE = 5

caldeirao = [] #fila de chamdos acessada pelos atendentes
fila_chamados = [f"CHAMADO_{i:04d}" for i in range(1, 21)] #todos os chamados

#registrar_log(fila_chamados)

mutex = threading.Lock()
log_mutex = threading.Lock()
acordar_cozinheiro = threading.Semaphore()
caldeirao_pronto = threading.Semaphore()
conzinheiro_chamado = False

ARQUIVO_LOG = "log_central_atendimento.txt"

def registrar_log(mensagem):
#strftime é uma classe que indica uma hora, dia ,  segundo
    instante = datetime.now().strftime("%Y=%m-%d %H:%M:%S")
    linha = f"[{instante}] {mensagem}"

#para evitar q 2 processos acessar aquela váriavel no mesmo momento, isso é para evitar incosistência, evitando sobrescrição
    with log_mutex:
        with open(ARQUIVO_LOG, "a", encoding = "utf-8") as arquivo:
            arquivo.write(linha + "\n")

    print(linha)
    

def cozinheiro():
    global caldeirao, cozinheiro_ja_foi_chamado

    while True:
        acordar_cozinheiro.acquire()

        with mutex:
            registrar_log("[COZINHEIRO] Fila interna vazia.")
            registrar_log("[COZINHEIRO] Buscando novos chamados na central...")

            quantidade = min(CAPACIDADE, len(fila_chamados))

            for _ in range(quantidade):
                chamado = fila_chamados.pop(0)
                caldeirao.append(chamado)

            cozinheiro_ja_foi_chamado = False

            registrar_log(
                f"[COZINHEIRO] {quantidade} chamados adicionados."
            )
            registrar_log(
                f"[COZINHEIRO] Fila interna atual: {caldeirao}"
            )

            caldeirao_pronto.release()

def atendente(id_atendente):
    global cozinheiro_ja_foi_chamado

    while True:
        with mutex:
            registrar_log(
                f"[ATENDENTE {id_atendente}] Solicitou um chamado."
            )

            if len(caldeirao) == 0:
                registrar_log(
                    f"[ATENDENTE {id_atendente}] Fila interna vazia."
                )

                if not cozinheiro_ja_foi_chamado:
                    registrar_log(
                        f"[ATENDENTE {id_atendente}] Acionando reposição."
                    )

                    cozinheiro_ja_foi_chamado = True
                    acordar_cozinheiro.release()

                else:
                    registrar_log(
                        f"[ATENDENTE {id_atendente}] Reposição já acionada."
                    )

        caldeirao_pronto.acquire()

        with mutex:
            if len(caldeirao) > 0:
                chamado = caldeirao.pop(0)

                registrar_log(
                    f"[ATENDENTE {id_atendente}] Atendeu {chamado}."
                )

                registrar_log(
                    f"[ATENDENTE {id_atendente}] Restam {len(caldeirao)} chamados."
                )

                if len(caldeirao) > 0:
                    caldeirao_pronto.release()

        time.sleep(random.uniform(0.5, 2))


threading.Thread(target=cozinheiro, daemon=True).start()
for i in range(1, 4): 
    threading.Thread(target=atendente, args=(i,), daemon=True).start()

time.sleep(20)