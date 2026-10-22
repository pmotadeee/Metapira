import os
import re
import shutil
import logging
from dataclasses import dataclass, field
from typing import List, Optional

COLUMNS_22 = [
    "ID", "Layer1_Style", "ENTITY", "Impact", "Layer2_Archetype",
    "Layer3_Domain", "Layer4_Valence", "Layer5_Strategy", "Influence_Weight",
    "Conflict_Status", "Activation_Phrase_1", "Activation_Phrase_2",
    "Activation_Phrase_3", "Activation_Phrase_4", "Activation_Phrase_5",
    "Activation_Phrase_6", "Activation_Phrase_7", "Activation_Phrase_8",
    "Activation_Phrase_9", "Activation_Phrase_10", "Activation_Phrase_11",
    "Activation_Phrase_12"
]

@dataclass
class SkillGene:
    id: int
    layer1_style: str
    entity: str
    impact: str
    layer2_archetype: str
    layer3_domain: str
    layer4_valence: str
    layer5_strategy: str
    influence_weight: str
    conflict_status: str
    activation_phrases: List[str] = field(default_factory=lambda: [""] * 12)

    def to_markdown_row(self) -> str:
        phrases = self.activation_phrases + [""] * (12 - len(self.activation_phrases))
        phrases = phrases[:12]
        fields = [
            str(self.id),
            self.layer1_style.strip(),
            self.entity.strip(),
            self.impact.strip(),
            self.layer2_archetype.strip(),
            self.layer3_domain.strip(),
            self.layer4_valence.strip(),
            self.layer5_strategy.strip(),
            self.influence_weight.strip(),
            self.conflict_status.strip()
        ] + [p.strip() for p in phrases]
        return "| " + " | ".join(fields) + " |"

    @classmethod
    def from_markdown_row(cls, row_str: str) -> Optional["SkillGene"]:
        parts = [p.strip() for p in row_str.strip().strip("|").split("|")]
        if len(parts) < 10:
            return None
        
        try:
            skill_id = int(re.sub(r"[^\d]", "", parts[0]))
        except ValueError:
            return None

        phrases = parts[10:22]
        while len(phrases) < 12:
            phrases.append("")
        
        return cls(
            id=skill_id,
            layer1_style=parts[1] if len(parts) > 1 else "Direto",
            entity=parts[2] if len(parts) > 2 else "Metapira",
            impact=parts[3] if len(parts) > 3 else "Base",
            layer2_archetype=parts[4] if len(parts) > 4 else "Executor",
            layer3_domain=parts[5] if len(parts) > 5 else "Geral",
            layer4_valence=parts[6] if len(parts) > 6 else "Neutra",
            layer5_strategy=parts[7] if len(parts) > 7 else "Heurística",
            influence_weight=parts[8] if len(parts) > 8 else "0.5",
            conflict_status=parts[9] if len(parts) > 9 else "Alinhado",
            activation_phrases=phrases[:12]
        )

class SkillManager:
    MAX_SKILLS = 10

    def __init__(self, table_path: str, staging_path: str = "", backup_path: str = ""):
        self.table_path = table_path
        self.staging_path = staging_path or table_path.replace(".md", "_staging.md")
        self.backup_path = backup_path or table_path.replace(".md", "_backup.md")
        os.makedirs(os.path.dirname(self.table_path), exist_ok=True)

    def load_skills(self) -> List[SkillGene]:
        skills = []
        if not os.path.exists(self.table_path):
            return skills

        try:
            with open(self.table_path, "r", encoding="utf-8") as f:
                for line in f:
                    line = line.strip()
                    if line.startswith("|") and not ("---" in line) and not ("Layer1_Style" in line):
                        gene = SkillGene.from_markdown_row(line)
                        if gene:
                            skills.append(gene)
        except Exception as e:
            logging.error(f"Erro ao carregar genes da tabela: {e}")

        # Ordenar por ID
        skills.sort(key=lambda s: s.id)
        return skills[:self.MAX_SKILLS]

    def save_skills(self, skills: List[SkillGene], target_file: str = None) -> bool:
        dest = target_file or self.table_path
        skills.sort(key=lambda s: s.id)
        skills = skills[:self.MAX_SKILLS]

        header = "| " + " | ".join(COLUMNS_22) + " |"
        sep = "| " + " | ".join([":---:" if c == "ID" else ":---" for c in COLUMNS_22]) + " |"
        rows = [gene.to_markdown_row() for gene in skills]

        content = (
            "# TABELA GENÉTICA DE SKILLS DO METAPIRA\n\n"
            f"> Capacidade: {len(skills)}/{self.MAX_SKILLS} slots de habilidades cognitivas ativas.\n\n"
            f"{header}\n{sep}\n" + "\n".join(rows) + "\n"
        )

        try:
            with open(dest, "w", encoding="utf-8") as f:
                f.write(content)
            return True
        except Exception as e:
            logging.error(f"Erro ao salvar tabela de skills em {dest}: {e}")
            return False

    def get_table_markdown(self) -> str:
        if os.path.exists(self.table_path):
            try:
                with open(self.table_path, "r", encoding="utf-8") as f:
                    return f.read()
            except Exception:
                pass
        return "Tabela genética não encontrada."

    def deploy_staging(self) -> str:
        if not os.path.exists(self.staging_path):
            return "Nenhum staging pendente para deploy."
        try:
            if os.path.exists(self.table_path):
                shutil.copy(self.table_path, self.backup_path)
            shutil.move(self.staging_path, self.table_path)
            return "🚀 Deploy concluído! Tabela Genética de Skills atualizada."
        except Exception as e:
            return f"[ERRO]: Falha no deploy: {str(e)}"

    def rollback(self) -> str:
        if not os.path.exists(self.backup_path):
            return "Nenhum backup disponível para rollback."
        try:
            shutil.copy(self.backup_path, self.table_path)
            return "⏪ Rollback executado com sucesso! Backup restaurado."
        except Exception as e:
            return f"[ERRO]: Falha no rollback: {str(e)}"

    def evaluate_and_evolve(self, user_msg: str, bot_response: str, llm_client) -> Optional[str]:
        skills = self.load_skills()
        qtd_atual = len(skills)

        prompt_sistema = (
            "Você é o Auditor Genético do Metapira Engine.\n"
            "Sua tarefa é analisar a interação recente entre o usuário e o bot para determinar se houve o surgimento de uma nova habilidade/estratégia relevante ou necessidade de ajuste nos genes existentes.\n\n"
            f"ESTADO ATUAL DA TABELA: {qtd_atual}/{self.MAX_SKILLS} habilidades preenchidas.\n"
            "COLUNAS OBRIGATÓRIAS (22):\n"
            "ID | Layer1_Style | ENTITY | Impact | Layer2_Archetype | Layer3_Domain | Layer4_Valence | Layer5_Strategy | Influence_Weight | Conflict_Status | Activation_Phrase_1 .. Activation_Phrase_12\n\n"
            "REGRAS DE DECISÃO:\n"
            "1. Se a interação for trivial, irrelevante ou não trouxer novo padrão cognitivo/habilidade: responda APENAS: NENHUMA_MUDANCA\n"
            f"2. Se for relevante E houver menos de 10 skills ({qtd_atual} < 10): Crie UMA nova linha para ID {qtd_atual + 1} com todas as 22 colunas preenchidas separadas por '|'.\n"
            "3. Se for relevante E a tabela JÁ TIVER 10 skills (10/10): Selecione o ID (de 1 a 10) mais impactado por essa interação e reescreva sua linha completa atualizando estratégias, pesos ou frases de ativação.\n\n"
            "FORMATO DE RETORNO:\n"
            "Se for mudar, retorne EXCLUSIVAMENTE a linha markdown correspondente no formato:\n"
            "| ID | Layer1_Style | ENTITY | Impact | Layer2_Archetype | Layer3_Domain | Layer4_Valence | Layer5_Strategy | Influence_Weight | Conflict_Status | Frase1 | Frase2 | Frase3 | Frase4 | Frase5 | Frase6 | Frase7 | Frase8 | Frase9 | Frase10 | Frase11 | Frase12 |\n"
            "Não adicione introduções ou conclusões."
        )

        user_content = (
            f"[INTERAÇÃO RECENTE]\nUsuário: {user_msg}\nBot: {bot_response}\n\n"
            f"[TABELA ATUAL]\n{self.get_table_markdown()}"
        )

        try:
            resposta = llm_client.chat(prompt_sistema, user_content, temp=0.5)
            if not resposta or "NENHUMA_MUDANCA" in resposta.upper():
                return None

            for line in resposta.splitlines():
                line = line.strip()
                if line.startswith("|") and ("|" in line[1:]):
                    gene_novo = SkillGene.from_markdown_row(line)
                    if gene_novo:
                        # Se já existe esse ID, atualiza
                        updated = False
                        for i, g in enumerate(skills):
                            if g.id == gene_novo.id:
                                skills[i] = gene_novo
                                updated = True
                                break
                        
                        if not updated:
                            if len(skills) < self.MAX_SKILLS:
                                gene_novo.id = len(skills) + 1
                                skills.append(gene_novo)
                            else:
                                # Se atingiu 10 e id veio fora do escopo, atualiza o ID 10
                                gene_novo.id = 10
                                skills[9] = gene_novo

                        # Backup e salvar
                        if os.path.exists(self.table_path):
                            shutil.copy(self.table_path, self.backup_path)
                        self.save_skills(skills)
                        logging.info(f"🧬 Gene {gene_novo.id} atualizado/adicionado com sucesso.")
                        return f"Gene ID {gene_novo.id} ({gene_novo.layer3_domain}) sintetizado."
        except Exception as e:
            logging.warning(f"Falha ao avaliar evolução de skills: {e}")

        return None
