-- Tabela de Clientes
CREATE TABLE IF NOT EXISTS clientes (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    nome TEXT NOT NULL,
    telefone TEXT,
    email TEXT,
    instagram TEXT,
    data_nascimento DATE,
    observacoes TEXT,
    data_cadastro TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    ativo INTEGER DEFAULT 1
);

-- Tabela de Agendamentos
CREATE TABLE IF NOT EXISTS agendamentos (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    cliente_id INTEGER NOT NULL,
    data_sessao DATE NOT NULL,
    horario TIME NOT NULL,
    descricao TEXT,
    valor_total REAL DEFAULT 0,
    valor_entrada REAL DEFAULT 0,
    status TEXT DEFAULT 'confirmada' CHECK(status IN ('confirmada', 'realizada', 'cancelada')),
    observacoes TEXT,
    data_criacao TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (cliente_id) REFERENCES clientes(id) ON DELETE CASCADE
);

-- Tabela de Projetos/Tattoos
CREATE TABLE IF NOT EXISTS projetos (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    cliente_id INTEGER NOT NULL,
    nome TEXT NOT NULL,
    descricao TEXT,
    valor REAL DEFAULT 0,
    status TEXT DEFAULT 'rascunho' CHECK(status IN ('rascunho', 'aprovado', 'realizado')),
    foto_antes TEXT,
    foto_depois TEXT,
    data_criacao TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (cliente_id) REFERENCES clientes(id) ON DELETE CASCADE
);

-- Tabela de Transações Financeiras
CREATE TABLE IF NOT EXISTS transacoes (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    tipo TEXT NOT NULL CHECK(tipo IN ('entrada', 'saida')),
    descricao TEXT NOT NULL,
    valor REAL NOT NULL,
    categoria TEXT,
    data_transacao DATE NOT NULL,
    cliente_id INTEGER,
    agendamento_id INTEGER,
    forma_pagamento TEXT,
    observacoes TEXT,
    data_criacao TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (cliente_id) REFERENCES clientes(id) ON DELETE SET NULL,
    FOREIGN KEY (agendamento_id) REFERENCES agendamentos(id) ON DELETE SET NULL
);

-- Tabela de Configurações
CREATE TABLE IF NOT EXISTS configuracoes (
    chave TEXT PRIMARY KEY,
    valor TEXT NOT NULL
);

-- Inserir configurações padrão
INSERT OR IGNORE INTO configuracoes (chave, valor) VALUES
    ('nome_estudio', 'Olivia Tattoo'),
    ('telefone', ''),
    ('email', ''),
    ('endereco', ''),
    ('formas_pagamento', 'Dinheiro,Pix,Cartão de Crédito,Cartão de Débito'),
    ('tema', 'dark');