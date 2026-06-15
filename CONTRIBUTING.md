## Documentação simples e resumida para estrutura e organização dos commits


## Estrutura

```
<tipo>: <descrição curta no imperativo>
```

## Tipos

| Prefixo     | Quando usar                                                             |
|-------------|-------------------------------------------------------------------------|
| `feat:`     | Nova funcionalidade (ex: nova rota, novo módulo, novo comportamento)    |
| `fix:`      | Correção de bug                                                         |
| `refactor:` | Mudança na estrutura/organização do código sem alterar o comportamento  |
| `docs:`     | Mudanças em documentação (README, comentários, este arquivo, etc.)      |
| `chore:`    | Tarefas de manutenção (dependências, configs, scripts, build)           |
| `test:`     | Adição ou ajuste de testes                                              |
| `style:`    | Formatação, espaçamento, nomes — sem mudança de lógica                  |
| `perf:`     | Melhoria de performance                                                 |

## Exemplos

```
feat: captura de câmera do celular via DroidCam USB
fix: corrige inversão de sentido do motor direito
refactor: substitui camera.py por white_filter.py
chore: adiciona requirements.txt com dependências do projeto
docs: adiciona convenções de commit
```

## Regras

- Use o imperativo: "adiciona", "corrige", "remove" (não "adicionado", "corrigindo").
- Mantenha a primeira linha curta (até ~72 caracteres).
- Se precisar explicar o "porquê", use o corpo do commit (linha em branco + parágrafo). (provavelmente não vamos precisar)
