import requests
import json
from utils.helpers import carregar_config, salvar_config

# Constantes
CHAVE_GROQ = "groq_api_key"
CHAVE_GROQ_FALLBACK = "groq_api_key_fallback"
CHAVE_MODELO = "groq_modelo"
CHAVE_PROVIDER = "ia_provider"
CHAVE_URL_CUSTOM = "ia_url_custom"
URL_GROQ = "https://api.groq.com/openai/v1/chat/completions"
URL_GROQ_MODELS = "https://api.groq.com/openai/v1/models"

# Cache de modelos descobertos
_modelos_cache = None


def descobrir_modelos_groq(forcar_atualizar=False):
    """
    Descobre os modelos disponíveis na API da Groq.
    Faz cache para não chamar a API toda hora.
    
    Returns:
        list: Lista de IDs dos modelos disponíveis
    """
    global _modelos_cache
    
    if _modelos_cache is not None and not forcar_atualizar:
        return _modelos_cache
    
    api_key = get_api_key()
    if not api_key:
        return []
    
    headers = {"Authorization": f"Bearer {api_key}"}
    
    try:
        resp = requests.get(URL_GROQ_MODELS, headers=headers, timeout=10)
        resp.raise_for_status()
        dados = resp.json()
        modelos = sorted([m["id"] for m in dados.get("data", [])])
        _modelos_cache = modelos
        return modelos
    except Exception:
        # Se não conseguir, retorna vazio
        return []


def get_provider():
    """Retorna o provider configurado."""
    return carregar_config(CHAVE_PROVIDER) or "Groq"


def get_api_url():
    """Retorna a URL da API baseada no provider."""
    provider = get_provider()
    if provider == "Custom":
        url = carregar_config(CHAVE_URL_CUSTOM)
        return url if url else URL_GROQ
    return URL_GROQ


def get_api_key():
    """Retorna a API key principal ou fallback."""
    key = carregar_config(CHAVE_GROQ)
    if not key:
        key = carregar_config(CHAVE_GROQ_FALLBACK)
    return key


def get_modelo():
    """Retorna o modelo configurado."""
    modelo = carregar_config(CHAVE_MODELO)
    if modelo and modelo not in ("llama3-8b-8192", "llama3-70b-8192", "mixtral-8x7b-32768"):
        return modelo
    # Se o modelo salvo é descontinuado, descobre um válido
    modelo_valido = modelo_padrao()
    if modelo_valido != modelo:
        salvar_config(CHAVE_MODELO, modelo_valido)
    return modelo_valido

def modelo_padrao():
    """Retorna um modelo que com certeza funciona."""
    modelos = descobrir_modelos_groq()
    if modelos:
        # Prefere modelos conhecidos que funcionam
        preferidos = ["llama-3.3-70b-versatile", "llama-3.1-8b-instant", "qwen/qwen3-32b"]
        for p in preferidos:
            if p in modelos:
                return p
        return modelos[0]
    return "llama-3.3-70b-versatile"


def perguntar(mensagem: str, contexto: str = "") -> str:
    """
    Envia uma pergunta para a Groq e retorna a resposta.

    Args:
        mensagem: A pergunta do usuário
        contexto: Contexto adicional (ex: dados do sistema)

    Returns:
        str: Resposta da IA
    """
    api_key = get_api_key()
    if not api_key:
        return "⚠️  Chave da API Groq não configurada.\n\nVá em ⚙️ Configurações e adicione sua chave."

    modelo = get_modelo()

    system_prompt = """Você é um assistente especializado em gestão de estúdio de tatuagem.
Você ajuda tatuadores a gerenciar clientes, agendamentos, finanças e projetos.
Suas respostas são:
- Profissionais e amigáveis
- Em português brasileiro
- Objetivas e práticas
- Baseadas nos dados fornecidos pelo sistema

Quando não tiver dados suficientes, peça mais informações de forma educada."""

    if contexto:
        system_prompt += f"\n\nContexto atual do sistema:\n{contexto}"

    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json"
    }

    data = {
        "model": modelo,
        "messages": [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": mensagem}
        ],
        "temperature": 0.7,
        "max_tokens": 1024,
    }

    url = get_api_url()
    try:
        resp = requests.post(url, headers=headers, json=data, timeout=30)
        resp.raise_for_status()
        resultado = resp.json()
        return resultado["choices"][0]["message"]["content"]

    except requests.exceptions.Timeout:
        return "⏱️  A requisição excedeu o tempo limite. Tente novamente."
    except requests.exceptions.HTTPError as e:
        status = resp.status_code
        if status == 401:
            return "🔑  Chave da API inválida. Verifique suas configurações."
        elif status == 404:
            # Pode ser URL ou modelo errado
            return (f"❌  URL ou modelo não encontrado (404).\n\n"
                   f"URL: {url}\nModelo: {modelo}\n\n"
                   f"Dica: Vá em Config > IA e clique ↻ para descobrir modelos disponíveis.")
        elif status == 400:
            try:
                erro = resp.json().get("error", {}).get("message", "")
                return f"❌  Erro na requisição: {erro}"
            except:
                return f"❌  Erro 400: {resp.text[:200]}"
        return f"❌  Erro HTTP {status}: {resp.text[:200]}"
    except Exception as e:
        return f"❌  Erro ao conectar com a IA: {str(e)}"


def gerar_descricao_projeto(nome: str, estilo: str = "", detalhes: str = "") -> str:
    """Gera uma descrição profissional para um projeto de tattoo."""
    prompt = f"""Crie uma descrição profissional e atraente para uma tatuagem com as seguintes características:

Nome do projeto: {nome}
Estilo: {estilo or "Não especificado"}
Detalhes: {detalhes or "Não especificados"}

A descrição deve ser:
- Em português brasileiro
- Profissional e convidativa
- De 2 a 4 frases
- Adequada para portfolio ou Instagram"""
    return perguntar(prompt)


def analisar_financeiro(resumo: str) -> str:
    """Analisa dados financeiros e dá insights."""
    prompt = f"""Analise os seguintes dados financeiros de um estúdio de tatuagem e dê insights práticos:

{resumo}

Forneça:
1. Um resumo em linguagem natural
2. Pontos de atenção (se houver)
3. Sugestões de melhoria"""
    return perguntar(prompt)


def sugerir_mensagem_whatsapp(cliente_nome: str, data: str, horario: str, tipo: str = "lembrete") -> str:
    """Gera mensagem personalizada para WhatsApp."""
    if tipo == "lembrete":
        prompt = f"""Crie uma mensagem curta e profissional para WhatsApp lembrando {cliente_nome} sobre sua sessão de tatuagem.
Data: {data}
Horário: {horario}

A mensagem deve ser:
- Amigável e profissional
- Pedir confirmação de presença
- Incluir um toque pessoal
- Máximo 200 caracteres"""
    elif tipo == "cobranca":
        prompt = f"""Crie uma mensagem educada para WhatsApp cobrando pagamento pendente de {cliente_nome}.
Seja profissional e discreto. Máximo 200 caracteres."""
    else:
        prompt = f"""Crie uma mensagem profissional para WhatsApp para {cliente_nome}.
Seja cordial e profissional. Máximo 200 caracteres."""

    return perguntar(prompt)