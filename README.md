<div align="center">
  <h1>✨ Olivia Tattoo | Premium Landing Page</h1>
  <p>Uma landing page de altíssima conversão e estética premium desenvolvida para a artista de fineline Olivia. Criada com foco em experiência do usuário (UX), animações fluidas e design responsivo.</p>
</div>

---

## 🎨 Sobre o Projeto

Este projeto foi desenhado para transmitir a exclusividade e a delicadeza da arte fineline. O site atua como um portfólio digital e uma ferramenta direta de captação de clientes, integrado diretamente com o WhatsApp da artista.

### ✨ Principais Funcionalidades

- **Design Aesthetic Premium (Dark Mode):** Interface imersiva que destaca os traços finos e as fotografias reais do estúdio.
- **Galeria Interativa (Reels & Fotos):** Grid otimizado com suporte nativo a vídeos em autoplay (formato Reels) e Lightbox customizado para visualização de fotos.
- **Animações Fluidas:** Efeitos magnéticos sutis, scroll suave, contador animado e partículas no header.
- **Mobile-First & Responsividade:** Experiência nativa em dispositivos móveis, com um menu mobile super otimizado e legível.
- **SEO & Performance:** Desenvolvido com Vanilla JS e CSS puro para garantir carregamento ultrarrápido (Vite como bundler).
- **Adequação LGPD:** Modal nativo com Termos de Uso, Políticas de Privacidade e Banner de Consentimento de Cookies integrados.

## 🛠️ Tecnologias Utilizadas

- **HTML5 Semântico**
- **Vanilla CSS3** (Custom Properties, Flexbox, CSS Grid)
- **Vanilla JavaScript** (ES6+)
- **[Vite](https://vitejs.dev/)** (Ferramenta de Build e Dev Server)

## 📂 Estrutura do Projeto

```text
olivia-tattoo/
├── public/                 # Assets públicos (não processados pelo Vite)
│   ├── images/             # Fotos reais, Reels (.mp4) e logo
│   └── favicon.svg         # Ícone da aba do navegador
├── src/                    # Código-fonte
│   ├── style.css           # Estilos globais (Design System, Animações, Responsividade)
│   └── main.js             # Lógica de Interação (Modais, Lightbox, Menu Mobile)
├── index.html              # Estrutura principal da página
├── package.json            # Dependências e scripts do projeto
└── vite.config.js          # Configuração do bundler
```

## 🚀 Como rodar o projeto localmente

Siga os passos abaixo para rodar o projeto na sua máquina:

1. **Clone o repositório:**
   \`\`\`bash
   git clone https://github.com/haaspaulo4/olivia-tattoo-landing.git
   \`\`\`

2. **Acesse a pasta do projeto:**
   \`\`\`bash
   cd olivia-tattoo-landing
   \`\`\`

3. **Instale as dependências:**
   \`\`\`bash
   npm install
   \`\`\`

4. **Inicie o servidor de desenvolvimento:**
   \`\`\`bash
   npm run dev
   \`\`\`
   O site estará disponível no seu navegador em \`http://localhost:5173\`.

## 🌐 Como fazer o Deploy (Vercel)

Este projeto está pronto para ser publicado na [Vercel](https://vercel.com/) em poucos cliques:

1. Acesse o seu painel da Vercel.
2. Clique em **Add New > Project**.
3. Conecte sua conta do GitHub e importe o repositório \`olivia-tattoo-landing\`.
4. A Vercel detectará automaticamente que é um projeto **Vite**.
5. Clique em **Deploy** e aguarde 30 segundos!

## 💻 Sistema Interno (CRM & Gestão)

Junto com a Landing Page, desenvolvemos um **Sistema Desktop de Gestão e CRM** exclusivo para o estúdio da Olivia. Ele fica na pasta `sistema-tattoo/` e foi construído em Python.

### ✨ Funcionalidades do Sistema
- **Gestão de Clientes e Agendamentos:** Controle completo da agenda e ficha de clientes.
- **Automação de WhatsApp (Neonize):** Envio silencioso e em background de mensagens.
  - *Boas-vindas* para novos clientes.
  - *Confirmação de Agendamento* automático.
  - Lembrete de *Cobrança* e saldo pendente.
  - Mensagem de *Pós-Venda* com instruções de cicatrização.
- **QR Code na Interface Gráfica:** O QR Code para conectar o WhatsApp é exibido diretamente na tela do sistema (funciona tanto em modo dev quanto no executável compilado).
- **Assistente IA Integrado:** Chatbot para WhatsApp usando IA (Groq) para responder dúvidas automaticamente.
- **Módulo Financeiro:** Controle de caixa, transações e relatórios em PDF.
- **Interface Gráfica Moderna:** Desenvolvido com `customtkinter` (Dark Mode nativo).

### 📦 Dependências Principais
| Pacote | Uso |
|--------|-----|
| `customtkinter` | Interface gráfica moderna (Dark Mode) |
| `neonize` | Integração WhatsApp (protocolo nativo) |
| `segno` | Geração de QR Code para autenticação |
| `groq` | IA para chatbot automático |
| `Pillow` | Manipulação de imagens |
| `reportlab` | Geração de relatórios em PDF |
| `matplotlib` | Gráficos financeiros |

### 🚀 Como rodar o CRM localmente

1. **Acesse a pasta do sistema:**
   ```bash
   cd sistema-tattoo
   ```

2. **Instale as dependências:**
   ```bash
   pip install -r requirements.txt
   ```

3. **Inicie o Sistema:**
   Você pode dar um clique duplo no arquivo `executar.bat` ou rodar via terminal:
   ```bash
   python main.py
   ```

4. **Conectar o WhatsApp:**
   Ao abrir, acesse a aba "WhatsApp", clique em "🔌 Conectar" e escaneie o QR Code que aparecerá **na interface gráfica** com o celular do estúdio.

### 🔨 Como compilar o executável (.exe)

Para gerar um executável standalone que roda sem precisar do Python instalado:

```bash
cd sistema-tattoo
build_debug.bat
```

O executável será gerado em `dist/Sistema-OliviaTattoo.exe`. Basta distribuir esse arquivo único.

> **Nota:** O build usa PyInstaller com `--collect-all neonize` e `--collect-all segno` para garantir que todas as dependências nativas sejam incluídas.

---
<div align="center">
  <p>Feito com paixão pela arte do código e da tatuagem. 🖤</p>
</div>
