---
name: metapira-skills
description: >-
  Metapira Cognitive Architecture & Assembly Skill. Use when assembling,
  maintaining, debugging, and evolving the Metapira bot and its modular
  OOP components, consulting the 10 internal skill IDs and the 22-column cognitive matrix.
---

# Metapira Cognitive Assembly & Evolution Skill

Esta skill atua como a matriz interna de consulta e evolução cognitiva do assistente para o projeto **Metapira Engine**.
Ela orienta a montagem, arquitetura, concatenação e evolução contínua dos módulos do bot, baseando-se em uma tabela estruturada de **22 colunas** e capacidade máxima de **10 IDs de habilidades**.

---

## 🧬 Regras Operacionais de Evolução

1. **Slots Limitados (Máximo de 10 IDs)**:
   - A matriz de habilidades possui no máximo 10 slots identificados por IDs numéricos de `1` a `10`.
   - Sempre que uma nova habilidade, padrão ou técnica de montagem relevante for concebida, adicione um novo ID sequencial até completar 10.

2. **Ciclo de Atualização Dinâmica (Ao Atingir 10 IDs)**:
   - Uma vez preenchidos os 10 slots (`10/10`), não crie novos IDs.
   - A partir de cada nova interação relevante, selecione o ID mais impactado e atualize suas colunas:
     - Recalibre o `Influence_Weight` (peso de relevância).
     - Refine `Layer5_Strategy` (heurística operacional).
     - Ajuste `Conflict_Status` (Alinhado, Dominante, Subordinado, etc.).
     - Atualize as `Activation_Phrase_1` até `Activation_Phrase_12` para capturar os novos gatilhos contextuais.

3. **Arquitetura de Montagem (Script Concatenator)**:
   - O instalador em Bash (`install.sh`) lê a árvore de diretórios dos módulos em OOP (`src/`) e concatena tudo de forma unificada no script executável final `main.py`.

---

## 📊 Matriz Genética de Consulta (22 Colunas)

| ID | Layer1_Style | ENTITY | Impact | Layer2_Archetype | Layer3_Domain | Layer4_Valence | Layer5_Strategy | Influence_Weight | Conflict_Status | Activation_Phrase_1 | Activation_Phrase_2 | Activation_Phrase_3 | Activation_Phrase_4 | Activation_Phrase_5 | Activation_Phrase_6 | Activation_Phrase_7 | Activation_Phrase_8 | Activation_Phrase_9 | Activation_Phrase_10 | Activation_Phrase_11 | Activation_Phrase_12 |
|:---:|:---|:---|:---:|:---|:---|:---:|:---|:---:|:---|:---|:---|:---|:---|:---|:---|:---|:---|:---|:---|:---|:---|
| 1 | Cirúrgico | Antigravity | Crítico | Arquiteto | Concatenação_Modular | Neutra | Decomposição_OOP_Monólito | 0.98 | Dominante | concatenar scripts | juntar arquivos | monólito modular | install.sh ler src | pipeline unificado | compilar main.py | arquitetura oop | organizar pastas | builder bash | empacotar código | módulos python | fluxo de montagem |
| 2 | Rigoroso | Sentinela | Alto | Guardião | Segurança_Higienização | Construtiva | Sanitização_Zero_Trust | 0.90 | Alinhado | prompt injection | jailbreak | ataque hostil | proteger bot | sentinela | segurança | bloquear mensagens | filtrar ovelhas | sanitizar entrada | vazamento de prompt | proteção de chave | permissões 600 |
| 3 | Analítico | Antigravity | Alto | Pesquisador | Memória_BM25 | Neutra | Recuperação_Lexical_Okapi | 0.88 | Alinhado | histórico de conversas | busca bm25 | contexto relevante | recuperar diálogo | rank-bm25 | jsonl histórico | persistência | memória de longo prazo | indexação tokenizada | histórico recente | top docs | memória vetorial |
| 4 | Técnico | Antigravity | Crítico | Oráculo | Orquestração_LLM | Fria | Ajuste_Temperatura_Heurística | 0.95 | Dominante | chamada deepseek | api completions | modelo deepseek-chat | prompt roteador | chave de api | timeout de conexão | temperatura 0.7 | payload json | requests post | inferência llm | roteador cognitivo | persona do bot |
| 5 | Autônomo | Antigravity | Moderado | Engenheiro | Automação_Termux_Linux | Construtiva | Detecção_Multiplataforma | 0.85 | Alinhado | ambiente termux | linux server | setup venv | pip install | script bash | instalar pacotes | nohup background | systemd service | executar run.sh | permissão chmod +x | compatibilidade android | bootstrap script |
| 6 | Dinâmico | Antigravity | Alto | Estrategista | Mutação_Genética_Skills | Disruptiva | Evolução_Adaptativa_10IDs | 0.92 | Dominante | evoluir tabela | atualizar 10 ids | 22 colunas | nova habilidade | recalibrar pesos | resolver conflitos | frases de ativação | mutação genética | staging e deploy | rollback de tabela | capacidade máxima | ciclo de interação |

*(Slots livres: IDs 7, 8, 9, 10 reservados para síntese de novas habilidades de montagem).*
