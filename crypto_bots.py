import requests
import time
import schedule
import telebot
from datetime import datetime

# Configuración del bot de Telegram
BOT_TOKEN = 'inser_code' 
CHAT_ID = 'chat_id'  

# Inicializar el bot
bot = telebot.TeleBot(BOT_TOKEN)

def obtener_top_criptomonedas():
    """Obtiene información de las 10 principales criptomonedas por capitalización de mercado"""
    try:
        # Utilizamos la API de CoinGecko para obtener las top 10 criptomonedas
        url = 'https://api.coingecko.com/api/v3/coins/markets'
        params = {
            'vs_currency': 'usd',
            'order': 'market_cap_desc',
            'per_page': 10,
            'page': 1,
            'sparkline': False,
            'price_change_percentage': '24h'
        }
        response = requests.get(url, params=params)
        data = response.json()
        return data
    except Exception as e:
        return f"Error al obtener información: {str(e)}"

def formato_precio(precio):
    """Formatea el precio según su magnitud"""
    if precio >= 1:
        return f"${precio:,.2f}"
    else:
        return f"${precio:.6f}"

def enviar_actualizacion():
    """Envía información de las top 10 criptomonedas a Telegram"""
    try:
        criptos = obtener_top_criptomonedas()
        fecha_hora = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        
        if isinstance(criptos, str):  # Si hay un error
            mensaje = f"❌ Error: {criptos}"
        else:
            mensaje = f"🚨 TOP 10 CRIPTOMONEDAS POR CAPITALIZACIÓN 🚨\n⏰ {fecha_hora}\n\n"
            
            for i, cripto in enumerate(criptos, 1):
                nombre = cripto['name']
                simbolo = cripto['symbol'].upper()
                precio = cripto['current_price']
                cambio_24h = cripto['price_change_percentage_24h']
                cap_mercado = cripto['market_cap']
                
                # Formateamos el cambio con emoji según sea positivo o negativo
                if cambio_24h > 0:
                    cambio_formato = f"🟢 +{cambio_24h:.2f}%"
                else:
                    cambio_formato = f"🔴 {cambio_24h:.2f}%"
                
                # Agregamos cada cripto al mensaje
                mensaje += f"{i}. {nombre} ({simbolo})\n"
                mensaje += f"   💰 Precio: {formato_precio(precio)}\n"
                mensaje += f"   📈 24h: {cambio_formato}\n"
                mensaje += f"   💼 Cap. Mercado: ${cap_mercado:,}\n\n"
        
        # Enviamos el mensaje
        bot.send_message(chat_id=CHAT_ID, text=mensaje)
        print(f"Mensaje enviado a las {fecha_hora}")
    except Exception as e:
        error_msg = f"Error al enviar mensaje: {str(e)}"
        print(error_msg)
        try:
            bot.send_message(chat_id=CHAT_ID, text=f"❌ {error_msg}")
        except:
            pass

def iniciar_servicio():
    """Inicia el servicio de actualizaciones cada minuto"""
    print("Iniciando servicio de actualizaciones de las top 10 criptomonedas...")
    
    schedule.every(30).minutes.do(enviar_actualizacion)
    
    enviar_actualizacion()
    
    while True:
        schedule.run_pending()
        time.sleep(1)

if __name__ == "__main__":
    iniciar_servicio()