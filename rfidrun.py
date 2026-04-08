import RPi.GPIO as GPIO
from mfrc522 import SimpleMFRC522
import time
from datetime import datetime
import csv

# LEDs
LED_VERDE = 4
LED_VERMELHO = 3
BUZZER = 2

GPIO.setmode(GPIO.BCM)
GPIO.setup(LED_VERDE, GPIO.OUT)
GPIO.setup(LED_VERMELHO, GPIO.OUT)
GPIO.setup(BUZZER, GPIO.OUT)

reader = SimpleMFRC522()

# Banco de dados
colaboradores = {
    "635367804909": {"nome": "João", "autorizado": True, "dentro": False, "entrada": None, "tempo_total": 0},
}

tentativas_invasao = 0

# Log para CSV
log_eventos = []

# BUZZER
def beep(tempo=0.2):
    print("audio tocado")
    GPIO.output(BUZZER, True)
    time.sleep(tempo)
    GPIO.output(BUZZER, False)
    time.sleep(0.1)

def som_autorizado():
    beep(0.2)

def som_nao_autorizado():
    beep(0.2)
    beep(0.2)

def som_invasao():
    for _ in range(10):
        beep(0.1)

# LEDs
def led_verde():
    print("verde ligado")
    GPIO.output(LED_VERDE, True)
    time.sleep(5)
    GPIO.output(LED_VERDE, False)
    print("verde desligado")


def led_vermelho():
    print("vermelho ligado")
    GPIO.output(LED_VERMELHO, True)
    time.sleep(5)
    GPIO.output(LED_VERMELHO, False)
    print("verde desligado")

def piscar_vermelho():
    for _ in range(10):
        GPIO.output(LED_VERMELHO, True)
        time.sleep(0.3)
        GPIO.output(LED_VERMELHO, False)
        time.sleep(0.3)

# log de eventos
def registrar_evento(nome, uid, tipo):
    log_eventos.append({
        "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "nome": nome,
        "uid": uid,
        "evento": tipo
    })

def processar_tag(uid):
    global tentativas_invasao

    uid = str(uid)

    if uid in colaboradores:
        user = colaboradores[uid]

        # NÃO AUTORIZADO
        if not user["autorizado"]:
            user["tentativas"] = user.get("tentativas", 0) + 1
            print(f"Você não tem acesso a este projeto, {user['nome']}")
            
            registrar_evento(user["nome"], uid, "NAO_AUTORIZADO")
            som_nao_autorizado()
            led_vermelho()
            return

        # AUTORIZADO
        agora = datetime.now()

        if not user["dentro"]:
            if user["entrada"] is None:
                print(f"Bem-vindo, {user['nome']}")
            else:
                print(f"Bem-vindo de volta, {user['nome']}")

            user["dentro"] = True
            user["entrada"] = agora

            registrar_evento(user["nome"], uid, "ENTRADA")
            som_autorizado()
            led_verde()

        else:
            # SAÍDA
            tempo = (agora - user["entrada"]).total_seconds()
            user["tempo_total"] += tempo
            user["dentro"] = False
            user["entrada"] = None

            print(f"{user['nome']} saiu da sala.")

            registrar_evento(user["nome"], uid, "SAIDA")
            som_autorizado()
            led_verde()

    else:
        # INVASÃO
        tentativas_invasao += 1
        print("Identificação não encontrada!")

        registrar_evento("DESCONHECIDO", uid, "INVASAO")
        som_invasao()
        piscar_vermelho()

# EXPORTAR CSV
def exportar_csv():
    with open("relatorio_acessos.csv", "w", newline="") as file:
        writer = csv.DictWriter(file, fieldnames=["timestamp", "nome", "uid", "evento"])
        writer.writeheader()
        writer.writerows(log_eventos)

    print("\nArquivo CSV gerado: relatorio_acessos.csv")

# LOOP
try:
    print("Sistema iniciado...")

    while True:
        uid, _ = reader.read()
        processar_tag(uid)
        time.sleep(1)

except KeyboardInterrupt:
    print("\n\n=== RELATÓRIO FINAL ===")

    for uid, user in colaboradores.items():
        if user.get("autorizado"):
            tempo_horas = user["tempo_total"] / 3600
            print(f"{user['nome']} ficou {tempo_horas:.2f} horas na sala.")
        else:
            print(f"{user['nome']} tentou acessar {user.get('tentativas', 0)} vezes.")

    print(f"Tentativas de invasão: {tentativas_invasao}")

    exportar_csv()

finally:
    GPIO.cleanup()
