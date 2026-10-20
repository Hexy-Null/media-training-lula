# Media Training — Luiz Inácio Lula da Silva

Projeto de preparação e assessoria de comunicação para Luiz Inácio Lula da Silva (Lula), centrado na análise factual de debates e na formulação colaborativa de roteiros de respostas estratégicas para futuras sabatinas e debates.

---

## Estrutura do Projeto

O trabalho está estruturado em duas etapas principais:

1. **Parte 1 — Registro Factual do Debate:**
   - Levantamento, transcrição e mapeamento estruturado de perguntas, respostas, réplicas, tréplicas e intervenções da mediação do primeiro debate da Band (conforme material fornecido).
   - Fidelidade irrestrita à fonte, sem invenção de falas ou suposições sobre trechos inaudíveis.
2. **Parte 2 — Construção Colaborativa de Respostas:**
   - Elaboração iterativa e orientada pelo usuário de propostas de roteiros de respostas favoráveis ao candidato.
   - Linguagem clara para oralidade, argumentos consistentes e identificação rigorosa de dados pendentes de checagem.

---

## Diretrizes de Atuação

- **Atuação Favorável:** Direciona a construção das estratégias de resposta, sem distorcer o registro histórico ou factual.
- **Separação de Camadas:** Fatos (o que foi dito), análises (avaliação técnica de comunicação) e simulações (propostas de roteiros) nunca se misturam.
- **Preservação Semântica:** A autoria e intenção do usuário são integralmente preservadas em revisões de texto.
- **Não-programação:** Este projeto não utiliza código-fonte, frameworks de desenvolvimento ou contêineres Docker.

---

## Organização do Repositório

```text
├── AGENTS.md                  # Instruções oficiais e regras de conduta dos agentes
├── CLAUDE.md                  # Instruções adaptadas para Claude Code
├── README.md                  # Apresentação do projeto e visão geral
├── ROADMAP.md                 # Planejamento, marcos e progresso das fases
├── HISTORY.md                 # Registro cronológico de entregas e decisões
├── .agents/                   # Regras, procedimentos e modelos reutilizáveis
│   ├── rules/                 # Regras de linguagem, fluxo de trabalho e execução
│   ├── templates/             # Modelos de registro e de roteiro
│   └── skills/                # Habilidades auxiliares (init, sync, etc.)
└── .metadocs/                 # Documentação detalhada de planos e conclusões
```

---

## Como Trabalhar

1. Consulte as diretrizes em `AGENTS.md`.
2. Mantenha os registros e roteiros organizados conforme os modelos em `.agents/templates/`.
3. Acompanhe e atualize o progresso em `ROADMAP.md`.
