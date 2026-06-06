# Gerador de APAC Física por Remessa - v4

Este projeto lê uma remessa TXT de APAC/SIA já gerada pelo sistema da Prefeitura e gera as APACs físicas em PDF.

## Fluxo

1. Selecione o arquivo `.txt` da remessa.
2. Clique em **Ler remessa**.
3. Escolha o **CNES executante**.
4. Marque um ou mais **procedimentos principais**.
5. Escolha a pasta de saída.
6. Clique em **Gerar APACs físicas**.

O programa sempre gera um PDF único contendo todas as APACs que passaram pelos filtros.

## Novidades da v4

- Filtro por múltiplos procedimentos principais usando checkboxes.
- Botões para marcar ou desmarcar todos os procedimentos.
- Estrutura preparada para empacotamento em `.exe`.
- Arquivos `data/` e `assets/` ficam fora do `.exe`, para edição sem recompilar.
- Regra do campo CNS/CPF: quando o procedimento principal começa com `09`, o programa usa o CPF do paciente no campo de CNS/CPF da APAC física.

## Rodar pelo Python

No PowerShell, dentro da pasta do projeto:

```powershell
pip install -r requirements.txt
python main.py
```

## Gerar EXE pelo PowerShell

### Opção 1 - usando o script PowerShell

Dentro da pasta do projeto, execute:

```powershell
.\build.ps1
```

Se o Windows bloquear scripts PowerShell, execute uma vez:

```powershell
Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass
.\build.ps1
```

O executável será gerado em:

```text
dist/Gerador_APAC_Fisica.exe
```

### Opção 2 - usando diretamente o arquivo `.spec`

```powershell
pip install -r requirements.txt
pip install pyinstaller
pyinstaller .\Gerador_APAC_Fisica.spec
Copy-Item -Recurse -Force data dist\data
Copy-Item -Recurse -Force assets dist\assets
New-Item -ItemType Directory -Force dist\output
```

## Estrutura depois de empacotar

A pasta final deve ficar assim:

```text
dist/
├── Gerador_APAC_Fisica.exe
├── data/
│   ├── procedimentos.csv
│   ├── medicos.csv
│   ├── estabelecimentos.csv
│   └── cid_oftalmologia.csv
├── assets/
│   └── template_apac.png
└── output/
```

## Editar procedimentos, médicos ou unidades

Depois que o `.exe` estiver pronto, você pode editar normalmente os arquivos abaixo, sem gerar outro executável:

```text
data/procedimentos.csv
data/medicos.csv
data/estabelecimentos.csv
data/cid_oftalmologia.csv
```

Basta fechar e abrir o programa novamente para ele reconhecer as alterações.

## Formato do procedimentos.csv

```csv
codigo;descricao
0905010035;OCI AVALIACAO INICIAL EM OFTALMOLOGIA - A PARTIR DE 9 ANOS
0905010019;OCI AVALIACAO INICIAL EM OFTALMOLOGIA - 0 A 8 ANOS
```
