import os
import re
import shutil
import logging
from dataclasses import dataclass, field
from typing import List, Optional

COLUNAS_SKILLS = [
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

    def to_markdown(self) -> str:
        frases = self.activation_phrases + [""] * (12 - len(self.activation_phrases))
        frases = frases[:12]
        colunas = [
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
        ] + [f.strip() for f in frases]
        return "| " + " | ".join(colunas) + " |"

    @classmethod
    def from_markdown(cls, linha: str) -> Optional["SkillGene"]:
        partes = [p.strip() for p in linha.strip().strip("|").split("|")]
        if len(partes) < 10:
            return None
        try:
            gene_id = int(re.sub(r"[^\d]", "", partes[0]))
        except ValueError:
            return None

        frases = partes[10:22]
        while len(frases) < 12:
            frases.append("")

        return cls(
            id=gene_id,
            layer1_style=partes[1] if len(partes) > 1 else "Direto",
            entity=partes[2] if len(partes) > 2 else "Metapira",
            impact=partes[3] if len(partes) > 3 else "Base",
            layer2_archetype=partes[4] if len(partes) > 4 else "Executor",
            layer3_domain=partes[5] if len(partes) > 5 else "Geral",
            layer4_valence=partes[6] if len(partes) > 6 else "Neutra",
            layer5_strategy=partes[7] if len(partes) > 7 else "Heurística",
            influence_weight=partes[8] if len(partes) > 8 else "0.5",
            conflict_status=partes[9] if len(partes) > 9 else "Alinhado",
            activation_phrases=frases[:12]
        )

class TabelaSkills:
    """
    Classe TabelaSkills:
    Controla os 10 IDs da matriz de habilidades de 22 colunas.
    Soma novas habilidades até 10 IDs e, ao atingir 10,
    atualiza o ID mais relevante com base em cada interação.
    """
    MAX_SKILLS = 10

    def __init__(self, caminho_tabela: str, caminho_staging: str = "", caminho_backup: str = ""):
        self.caminho_tabela = caminho_tabela
        self.caminho_staging = caminho_staging or caminho_tabela.replace(".md", "_staging.md")
        self.caminho_backup = caminho_backup or caminho_tabela.replace(".md", "_backup.md")
        os.makedirs(os.path.dirname(self.caminho_tabela), exist_ok=True)

    def carregar(self) -> List[SkillGene]:
        skills = []
        if not os.path.exists(self.caminho_tabela):
            return skills
        try:
            with open(self.caminho_tabela, "r", encoding="utf-8") as f:
                for line in f:
                    line = line.strip()
                    if line.startswith("|") and not ("---" in line) and not ("Layer1_Style" in line):
                        gene = SkillGene.from_markdown(line)
                        if gene:
                            skills.append(gene)
        except Exception as e:
            logging.error(f"Erro ao carregar skills: {e}")
        skills.sort(key=lambda s: s.id)
        return skills[:self.MAX_SKILLS]

    def salvar(self, skills: List[SkillGene], destino: str = None) -> bool:
        dest = destino or self.caminho_tabela
        skills.sort(key=lambda s: s.id)
        skills = skills[:self.MAX_SKILLS]

        header = "| " + " | ".join(COLUNAS_SKILLS) + " |"
        sep = "| " + " | ".join([":---:" if c == "ID" else ":---" for c in COLUNAS_SKILLS]) + " |"
        linhas = [g.to_markdown() for g in skills]

        conteudo = (
            "# TABELA GENÉTICA DE SKILLS DO METAPIRA\n\n"
            f"> Capacidade: {len(skills)}/{self.MAX_SKILLS} slots de habilidades cognitivas.\n\n"
            f"{header}\n{sep}\n" + "\n".join(linhas) + "\n"
        )
        try:
            with open(dest, "w", encoding="utf-8") as f:
                f.write(conteudo)
            return True
        except Exception as e:
            logging.error(f"Erro ao salvar tabela: {e}")
            return False

    def obter_markdown(self) -> str:
        if os.path.exists(self.caminho_tabela):
            try:
                with open(self.caminho_tabela, "r", encoding="utf-8") as f:
                    return f.read()
            except Exception:
                pass
        return "Tabela de skills não encontrada."

    def deploy(self) -> str:
        if not os.path.exists(self.caminho_staging):
            return "Nenhum staging pendente."
        try:
            if os.path.exists(self.caminho_tabela):
                shutil.copy(self.caminho_tabela, self.caminho_backup)
            shutil.move(self.caminho_staging, self.caminho_tabela)
            return "Deploy concluído. Tabela de skills atualizada."
        except Exception as e:
            return f"[ERRO]: {str(e)}"

    def rollback(self) -> str:
        if not os.path.exists(self.caminho_backup):
            return "Nenhum backup disponível."
        try:
            shutil.copy(self.caminho_backup, self.caminho_tabela)
            return "Rollback executado. Tabela restaurada."
        except Exception as e:
            return f"[ERRO]: {str(e)}"

    def avaliar_e_evoluir(self, user_msg: str, bot_msg: str, api_deepseek) -> Optional[str]:
        skills = self.carregar()
        qtd = len(skills)

        prompt_sistema = (
            "Você é o Auditor Genético do Metapira.\n"
            "Analise a interação entre usuário e bot para avaliar se surgiu nova habilidade relevante ou necessidade de ajuste nos genes existentes.\n"
            f"ESTADO: {qtd}/{self.MAX_SKILLS} skills preenchidas.\n"
            "COLUNAS (22): ID | Layer1_Style | ENTITY | Impact | Layer2_Archetype | Layer3_Domain | Layer4_Valence | Layer5_Strategy | Influence_Weight | Conflict_Status | Frase1 .. Frase12\n\n"
            "REGRAS:\n"
            "1. Se a interação não for relevante para habilidades cognitivas: responda unicamente: NENHUMA_MUDANCA\n"
            f"2. Se for relevante e houver menos de 10 skills ({qtd} < 10): Crie UMA nova linha para ID {qtd + 1} com as 22 colunas separadas por '|'.\n"
            "3. Se já houver 10 skills (10/10): Selecione o ID (1 a 10) mais impactado e retorne a linha completa atualizada com as 22 colunas.\n"
            "Retorne EXCLUSIVAMENTE a linha markdown com as 22 colunas."
        )

        user_content = f"Interação:\nUsuário: {user_msg}\nBot: {bot_msg}\n\nTabela Atual:\n{self.obter_markdown()}"
        try:
            res = api_deepseek.chamar(prompt_sistema, user_content, temp=0.5)
            if not res or "NENHUMA_MUDANCA" in res.upper():
                return None

            for linha in res.splitlines():
                linha = linha.strip()
                if linha.startswith("|") and ("|" in linha[1:]):
                    gene_novo = SkillGene.from_markdown(linha)
                    if gene_novo:
                        atualizado = False
                        for i, g in enumerate(skills):
                            if g.id == gene_novo.id:
                                skills[i] = gene_novo
                                atualizado = True
                                break
                        if not atualizado:
                            if len(skills) < self.MAX_SKILLS:
                                gene_novo.id = len(skills) + 1
                                skills.append(gene_novo)
                            else:
                                gene_novo.id = 10
                                skills[9] = gene_novo

                        if os.path.exists(self.caminho_tabela):
                            shutil.copy(self.caminho_tabela, self.caminho_backup)
                        self.salvar(skills)
                        return f"Gene ID {gene_novo.id} atualizado/sintetizado com sucesso."
        except Exception as e:
            logging.warning(f"Erro na auto-evolução de skills: {e}")
        return None
