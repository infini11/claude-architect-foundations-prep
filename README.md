# claude-architect-foundations-prep

Kata Python pour apprendre la Claude Messages API (préparation certif Claude Architect Foundations),
construit étape par étape, avec un modèle local (Ollama) derrière un proxy LiteLLM.

---

## 1. Vue d'ensemble : qui parle à qui ?

![alt text](assets/image.png)

Une requête fait l'aller-retour complet :

1. Ton code envoie une requête au **format Anthropic** à LiteLLM.
2. LiteLLM vérifie la clé, cherche l'alias `llama3.2-3b` dans sa config et découvre qu'il
   correspond à `ollama_chat/llama3.2:3b`.
3. LiteLLM **réécrit** la requête au format Ollama et l'envoie à Ollama.
4. Ollama fait tourner le modèle et renvoie la réponse au format Ollama.
5. LiteLLM **retraduit** cette réponse au format Anthropic (`content`, `stop_reason`, `usage`…).
6. Ton code reçoit une réponse identique à celle de la vraie API Claude.

## 2. Pourquoi LiteLLM ?

Ollama ne comprend pas la Messages API d'Anthropic : il a sa propre API (`/api/chat`). Sans
traducteur, il faudrait écrire du code spécifique à Ollama, et ce code ne servirait à rien le
jour où tu passes sur Claude.

LiteLLM est un **proxy** qui expose un endpoint compatible Anthropic (`/v1/messages`) et le
traduit vers une centaine de fournisseurs (Ollama, OpenAI, Bedrock…). Grâce à lui :

- tu apprends la **vraie** Messages API et tu utilises le **vrai** SDK `anthropic` ;
- pour passer sur Claude, tu changes seulement l'URL, la clé et le nom du modèle, sans toucher
  au code ;
- c'est gratuit, ça tourne en local et ça marche hors ligne.

Les limites à garder en tête :
- Le modèle local est petit (3 milliards de paramètres) : il est bien moins bon que Claude,
  surtout pour utiliser des outils.
- Les fonctionnalités propres à Claude (extended thinking, prompt caching…) sont ignorées.
- En cas d'erreur, le problème peut venir de l'un des trois maillons. Pour voir ce que fait
  LiteLLM : `docker compose logs -f litellm`.

Les points importants :

- **Réseau interne** : Compose crée un réseau où chaque service est joignable par son nom.
  Depuis le conteneur LiteLLM, Ollama s'appelle donc `http://ollama:11434`, et non `localhost`.
  Dans un conteneur, `localhost` désigne le conteneur lui-même.
- **`ports`** : il ne sert qu'à ouvrir l'accès depuis **ta machine**. Les conteneurs, eux, se
  parlent entre eux même sans `ports`.
- **Deux sortes de `volumes`** :
  - `ollama_data:` est un **volume nommé**, stocké par Docker (le modèle pèse environ 2 Go, on
    ne veut pas le retélécharger) ;
  - `./litellm-config.yaml:` est un **bind mount** : c'est ton fichier local, et tu le modifies
    directement. Il faut redémarrer LiteLLM pour qu'il soit pris en compte (`docker compose
    restart litellm`).

Les commandes utiles :

| Commande | Effet |
|---|---|
| `docker compose up -d` | démarre tout en arrière-plan |
| `docker compose ps` | état des services |
| `docker compose logs -f litellm` | logs en direct du proxy |
| `docker compose exec ollama ollama list` | modèles installés dans Ollama |
| `docker compose restart litellm` | recharge la config LiteLLM |
| `docker compose down` | arrête tout (le volume est conservé) |

Pour ajouter un modèle, par exemple `qwen2.5:7b`, qui est plus fiable avec les outils :
1. `docker compose exec ollama ollama pull qwen2.5:7b`
2. ajouter une entrée `model_name: qwen2.5-7b` / `model: ollama_chat/qwen2.5:7b` dans le YAML ;
3. `docker compose restart litellm`.

## 3. Deux backends : Ollama en local ou l'API Anthropic

Le même code parle à l'un ou à l'autre. Seules **3 variables d'environnement** changent :

```
                         ┌─► LiteLLM (localhost:4000) ─► Ollama ─► llama3.2:3b   gratuit, local
Ton code (SDK anthropic) ┤
                         └─► api.anthropic.com ──────────────────► Claude        payant, vrai modèle
```

| Variable | Ollama (`.env.ollama`) | Anthropic (`.env.anthropic`) |
|---|---|---|
| `ANTHROPIC_BASE_URL` | `http://localhost:4000` | `https://api.anthropic.com` |
| `ANTHROPIC_API_KEY` | `sk-local-dummy` (la `master_key` LiteLLM) | ta vraie clé `sk-ant-...` |
| `MODEL` | `llama3.2-3b` (alias LiteLLM) | `claude-opus-5-5` (id de modèle Claude) |

Le SDK Python lit **automatiquement** `ANTHROPIC_BASE_URL` et `ANTHROPIC_API_KEY` : un simple
`anthropic.Anthropic()` sans argument suffit. `MODEL` est notre variable à nous.

**Mise en place (une seule fois) :**
```bash
cp .env.ollama.example .env.ollama
cp .env.anthropic.example .env.anthropic   # puis colle ta clé dedans, dans l'éditeur
```

Les fichiers `.env.*` sont ignorés par git (seuls les `.example` sont versionnés). Ne colle jamais
ta clé dans le code, un commit ou une conversation. Si elle fuit, révoque-la sur la console
Anthropic (https://platform.claude.com/settings/keys).

**Charger un backend dans le terminal** (pour `curl`) :
```bash
set -a; source .env.anthropic; set +a   # ou .env.ollama
```

**Ce qui diffère entre les deux, à connaître pour la certif :**

| | LiteLLM / Ollama | API Anthropic |
|---|---|---|
| Header `anthropic-version` | facultatif | **obligatoire** (le SDK l'envoie pour toi ; en curl : `2026-10-21`) |
| Coût | gratuit | facturé au token (voir `usage` dans chaque réponse) |
| `temperature`, `top_p`, `top_k` | acceptés | **refusés (400)** depuis la version d'API `2026-10-21` |
| Thinking | inexistant | toujours actif sur Opus 5.5 : `content` peut contenir des blocs `thinking` **avant** le bloc `text` |
| Qualité du tool use | fragile | fiable |

Côté modèles Claude (prix par million de tokens, entrée / sortie) :
- `claude-opus-5-5` (4 $ / 20 $) : le modèle par défaut ;
- `claude-sonnet-5-5` (2 $ / 10 $) ;
- `claude-haiku-5-5` (0,10 $ / 0,50 $) : très économique pour des exercices.

Pour les exercices, garde un `max_tokens` raisonnable afin de maîtriser le coût.

## 5. Documentation de référence

| Sujet | Lien |
|---|---|
| Messages API (Anthropic) | https://docs.claude.com/en/api/messages |
| Tool use (Anthropic) | https://docs.claude.com/en/docs/agents-and-tools/tool-use/overview |
| LiteLLM : fichier de config du proxy | https://docs.litellm.ai/docs/proxy/configs |
| LiteLLM : endpoint `/v1/messages` (format Anthropic) | https://docs.litellm.ai/docs/anthropic_unified |
| LiteLLM : fournisseur Ollama | https://docs.litellm.ai/docs/providers/ollama |
| Ollama : API REST | https://github.com/ollama/ollama/blob/main/docs/api.md |
| Docker Compose : référence des services | https://docs.docker.com/reference/compose-file/services/ |
| YAML : syntaxe en 5 minutes | https://learnxinyminutes.com/docs/yaml/ |

---

## Démarrage

```bash
docker compose up -d 
docker compose exec ollama ollama pull llama3.2:3b
```

## Environnement Python

L'environnement virtuel est **à côté** du repo, pas dedans :

```
INFINI/claude/
├── claude-architect-foundations-prep/        ← le repo (code, README, requirements.txt)
└── env/                                      ← le venv (Python + paquets installés)
```

Création, une seule fois :
```bash
cd ..
python3 -m venv env
source env/bin/activate
pip install -r claude-architect-foundations-prep/requirements.txt
```

À chaque nouveau terminal :
```bash
source ../env/bin/activate   # le prompt affiche (env)
deactivate            # pour en sortir
```

> ⚠️ Ton `~/.zshrc` contient `alias python=/usr/local/bin/python3` : cet alias **court-circuite le
> venv**. Venv activé, utilise `python3` (ou supprime l'alias). Vérification :
> `python3 -c "import sys; print(sys.executable)"` doit afficher `.../env/bin/python3`.
>
> Ne renomme pas un venv : les chemins sont écrits en dur dedans. Supprime-le et recrée-le.

Les paquets installés (`requirements.txt`) :
- `anthropic` : le SDK officiel de la Messages API ;
- `python-dotenv` : charge un fichier `.env.*` dans les variables d'environnement, via
  `load_dotenv(".env.ollama")`. Par défaut, il **n'écrase pas** une variable déjà définie dans
  le terminal ; passe `override=True` pour forcer.

Dans VS Code : `Cmd+Shift+P` → *Python: Select Interpreter* → *Enter interpreter path* →
`../env/bin/python`.

## Journal des étapes

- [ ] 0. Requête brute avec curl (Ollama puis Anthropic)
