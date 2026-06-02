# Problema do Caixeiro Viajante - Otimização por Colônia de Formigas (ACO)

Este repositório contém a solução da equipe para o Trabalho Prático da disciplina de Grafos. Implementamos uma metaheurística baseada em **Ant Colony Optimization (ACO)** para buscar rotas de custo mínimo em instâncias de cidades.

## Tecnologias Utilizadas
- **Linguagem:** Python 3
- **Bibliotecas:** `sys`, `math`, `random`, `time`, `signal` (apenas bibliotecas nativas, conforme especificação).

## Como Executar

O programa foi construído para ler dados da entrada padrão (`stdin`) e gerar a saída na saída padrão (`stdout`), sem mensagens de log ou debug, facilitando o uso em corretores automáticos.

### 1. Testar uma única instância
Para rodar um arquivo de teste específico (ex: `tsp51.tsp`) e gerar a resposta:

```bash
python3 tsp_solver.py < tsp51.tsp > solucao_tsp51.tour
```
### Testando de uma vez

```bash

for arquivo in *.tsp; do
    echo "Executando $arquivo..."
    time python3 tsp_solver.py < "$arquivo" > "solucao_${arquivo}.tour"
    grep "TOTAL WEIGHT" "solucao_${arquivo}.tour"
    echo "----------------------------------------"
done

```