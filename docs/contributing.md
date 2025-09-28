# Contribuição

## 🤝 Como Contribuir

Agradecemos seu interesse em contribuir com o projeto Car API! Este guia detalha como você pode participar do desenvolvimento, reportar problemas e sugerir melhorias.

## 📋 Tipos de Contribuição

### 🐛 Reportar Bugs
- Descreva o problema claramente
- Inclua passos para reproduzir
- Forneça informações do ambiente
- Use o template de issue apropriado

### ✨ Sugerir Features
- Explique o caso de uso
- Descreva a solução proposta
- Considere alternativas
- Discuta o impacto na API

### 📝 Melhorar Documentação
- Corrigir erros ou informações desatualizadas
- Adicionar exemplos práticos
- Traduzir documentação
- Melhorar clareza e organização

### 🔧 Contribuir com Código
- Implementar novas funcionalidades
- Corrigir bugs
- Melhorar performance
- Adicionar testes

## 🚀 Processo de Contribuição

### 1. Configurar Ambiente

```bash
# Fork do repositório no GitHub
# Clone do seu fork
git clone https://github.com/seu-usuario/car_api.git
cd car_api

# Adicionar remote upstream
git remote add upstream https://github.com/pycodebr/car_api.git

# Configurar ambiente
poetry install
poetry run alembic upgrade head
```

### 2. Criar Branch para Feature

```bash
# Atualizar main
git checkout main
git pull upstream main

# Criar branch para feature
git checkout -b feature/nome-da-feature

# Ou para bugfix
git checkout -b fix/nome-do-bug
```

### 3. Desenvolver e Testar

```bash
# Desenvolver seguindo os padrões
# Escrever testes
poetry run pytest

# Verificar qualidade do código
poetry run task lint
poetry run task format

# Executar todos os testes
poetry run task test
```

### 4. Commit e Push

```bash
# Commit seguindo Conventional Commits
git add .
git commit -m "feat: add new car insurance endpoint"

# Push para seu fork
git push origin feature/nome-da-feature
```

### 5. Criar Pull Request

- Acesse GitHub e crie PR do seu fork para o repositório principal
- Use o template de PR
- Descreva as mudanças claramente
- Referencie issues relacionadas

## 📐 Padrões de Código

### Conventional Commits

Seguimos a especificação [Conventional Commits](https://www.conventionalcommits.org/):

```bash
# Tipos de commit
feat: nova funcionalidade
fix: correção de bug
docs: documentação
style: formatação (sem mudança de lógica)
refactor: refatoração de código
test: testes
chore: tarefas de manutenção
perf: melhorias de performance
ci: mudanças no CI/CD

# Exemplos
feat: add insurance support to car model
fix: resolve JWT token expiration issue
docs: update API documentation for new endpoints
test: add unit tests for car validation
```

### Estrutura de Commits

```bash
# Formato
<tipo>(<escopo>): <descrição>

[corpo opcional]

[rodapé opcional]

# Exemplos
feat(auth): add refresh token endpoint

Add endpoint to refresh JWT tokens without requiring
full authentication. This improves user experience
by reducing login frequency.

Closes #123

fix(cars): resolve price validation error

The price field was not properly validating decimal
precision, causing errors with valid prices.

Breaking change: Price format now requires exactly
2 decimal places.
```

### Code Review

#### Checklist para Revisores

**Funcionalidade:**
- [ ] A feature funciona conforme especificado
- [ ] Todos os casos de uso são cobertos
- [ ] Não há regressões

**Código:**
- [ ] Código é limpo e legível
- [ ] Segue padrões do projeto
- [ ] Não há duplicação desnecessária
- [ ] Performance é adequada

**Testes:**
- [ ] Testes cobrem funcionalidade nova
- [ ] Testes são significativos
- [ ] Todos os testes passam
- [ ] Coverage mantido ou melhorado

**Documentação:**
- [ ] Documentação atualizada
- [ ] Docstrings adicionadas/atualizadas
- [ ] Changelog atualizado se necessário

#### Feedback Construtivo

```markdown
# ✅ Bom feedback
Considere usar o método `validate_plate()` existente aqui em vez de
reimplementar a validação. Isso mantém a consistência e reduz duplicação.

# ❌ Feedback não construtivo
Este código está errado.

# ✅ Sugestão específica
```python
# Em vez de:
if len(plate) != 7:
    raise ValueError("Invalid plate")

# Considere:
validate_plate(plate)  # Reutiliza validação existente
```

# ✅ Reconhecer pontos positivos
Excelente implementação dos testes! A cobertura de casos edge está muito boa.
```

## 🐛 Reportar Issues

### Template de Bug Report

```markdown
## 🐛 Descrição do Bug
Descrição clara e concisa do problema.

## 🔄 Passos para Reproduzir
1. Vá para '...'
2. Clique em '....'
3. Veja o erro

## ✅ Comportamento Esperado
Descrição do que deveria acontecer.

## 📱 Screenshots/Logs
Se aplicável, adicione screenshots ou logs de erro.

## 🖥️ Ambiente
- OS: [e.g. Ubuntu 22.04]
- Python: [e.g. 3.13.0]
- Poetry: [e.g. 1.7.1]
- Browser: [e.g. Chrome 119]

## 📋 Contexto Adicional
Qualquer informação adicional sobre o problema.
```

### Template de Feature Request

```markdown
## 🚀 Feature Request

### 📝 Descrição
Descrição clara da funcionalidade desejada.

### 🎯 Problema
Que problema esta feature resolve?

### 💡 Solução Proposta
Como você imagina que a feature funcionaria?

### 🔄 Alternativas
Outras maneiras de resolver o problema?

### 📋 Critérios de Aceitação
- [ ] Critério 1
- [ ] Critério 2
- [ ] Critério 3

### 📊 Impacto
- **Usuários**: Quem se beneficia?
- **Performance**: Impacto na performance?
- **Breaking**: É uma breaking change?
```

## 🏗️ Arquitetura de Contribuições

### Estrutura para Novas Features

```
feature/new-endpoint/
├── models/           # Novos modelos se necessário
├── schemas/          # Schemas de validação
├── routers/          # Endpoints da API
├── tests/            # Testes completos
└── docs/             # Documentação atualizada
```

### Exemplo: Adicionar Sistema de Avaliações

```python
# 1. Modelo
# car_api/models/reviews.py
class Review(Base):
    __tablename__ = 'reviews'

    id: Mapped[int] = mapped_column(primary_key=True)
    rating: Mapped[int] = mapped_column(Integer)  # 1-5
    comment: Mapped[Optional[str]] = mapped_column(Text)
    car_id: Mapped[int] = mapped_column(ForeignKey('cars.id'))
    reviewer_id: Mapped[int] = mapped_column(ForeignKey('users.id'))

# 2. Schema
# car_api/schemas/reviews.py
class ReviewSchema(BaseModel):
    rating: int = Field(..., ge=1, le=5)
    comment: Optional[str] = Field(None, max_length=1000)
    car_id: int

# 3. Router
# car_api/routers/reviews.py
@router.post('/')
async def create_review(
    review: ReviewSchema,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_session)
):
    # Implementação

# 4. Testes
# tests/integration/test_reviews.py
class TestReviewsAPI:
    async def test_create_review_success(self, client, auth_headers):
        # Teste implementação

# 5. Migração
# poetry run alembic revision --autogenerate -m "add reviews table"
```

## 🧪 Guidelines de Testes

### Cobertura de Testes

**Mínimo requerido:**
- Unit tests: 80%+
- Integration tests para novos endpoints
- E2E tests para fluxos críticos

### Estrutura de Testes

```python
class TestNewFeature:
    """Teste para nova funcionalidade."""

    async def test_success_case(self):
        """Testar caso de sucesso."""
        # Arrange
        # Act
        # Assert

    async def test_validation_error(self):
        """Testar validação de entrada."""
        # Teste com dados inválidos

    async def test_authorization_error(self):
        """Testar autorização."""
        # Teste acesso negado

    async def test_not_found_error(self):
        """Testar recurso não encontrado."""
        # Teste 404

    async def test_edge_cases(self):
        """Testar casos extremos."""
        # Testes de boundary conditions
```

### Mocks e Fixtures

```python
# Fixture reutilizável
@pytest.fixture
async def sample_review(db_session, sample_car, sample_user):
    """Review de exemplo para testes."""
    review = Review(
        rating=5,
        comment="Excelente carro!",
        car_id=sample_car.id,
        reviewer_id=sample_user.id
    )
    db_session.add(review)
    await db_session.commit()
    return review

# Mock de serviço externo
@pytest.fixture
def mock_notification_service(mocker):
    """Mock do serviço de notificações."""
    return mocker.patch('car_api.services.notification.send_email')
```

## 📝 Documentação

### Docstrings

```python
async def create_car(
    car: CarSchema,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_session),
) -> Car:
    """
    Criar novo carro no sistema.

    Registra um novo carro para o usuário autenticado, validando
    todas as informações e associando à marca especificada.

    Args:
        car: Dados do carro a ser criado
        current_user: Usuário autenticado via JWT
        db: Sessão do banco de dados

    Returns:
        Car: Carro criado com relacionamentos carregados

    Raises:
        HTTPException: 400 se placa já existe ou marca inválida
        HTTPException: 401 se usuário não autenticado

    Examples:
        >>> car_data = CarSchema(model="Civic", brand_id=1, ...)
        >>> car = await create_car(car_data, user, db)
        >>> assert car.owner_id == user.id
    """
```

### Comentários no Código

```python
def verify_car_ownership(current_user: User, car_owner_id: int):
    """Verificar propriedade do carro."""

    # Implementar autorização granular para garantir que usuários
    # só possam acessar/modificar seus próprios recursos
    if current_user.id != car_owner_id:
        # Retornar 403 em vez de 404 para não vazar informações
        # sobre existência de recursos de outros usuários
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail='Acesso negado'
        )
```

### Atualizações na Documentação

```markdown
# Ao adicionar nova feature, atualizar:

1. **API Endpoints** (`docs/api-endpoints.md`)
   - Documentar novos endpoints
   - Adicionar exemplos de request/response
   - Incluir códigos de erro

2. **Modelagem do Sistema** (`docs/system-modeling.md`)
   - Atualizar ERD se novos modelos
   - Incluir novos fluxos se aplicável

3. **README** (se mudança significativa)
   - Atualizar features principais
   - Modificar instruções se necessário
```

## 🚀 Release Process

### Versionamento Semântico

Seguimos [Semantic Versioning](https://semver.org/):

```
MAJOR.MINOR.PATCH

1.0.0 → 1.0.1 (patch: bug fix)
1.0.1 → 1.1.0 (minor: new feature)
1.1.0 → 2.0.0 (major: breaking change)
```

### Critérios para Release

**Patch (x.x.X):**
- Bug fixes
- Melhorias de segurança
- Atualizações de documentação

**Minor (x.X.x):**
- Novas features
- Melhorias de performance
- Novos endpoints (não breaking)

**Major (X.x.x):**
- Breaking changes na API
- Mudanças na estrutura do banco
- Remoção de features deprecated

### Processo de Release

```bash
# 1. Atualizar CHANGELOG.md
# 2. Bump version no pyproject.toml
# 3. Criar release tag
git tag -a v1.2.0 -m "Release v1.2.0"

# 4. Push tag
git push origin v1.2.0

# 5. GitHub Actions cria release automaticamente
```

## 🏆 Reconhecimento

### Hall of Fame

Contribuidores que fizeram diferença significativa:

- **@pycodebr** - Criador e maintainer principal
- **@contributor1** - Sistema de autenticação
- **@contributor2** - Documentação e testes
- **@contributor3** - Performance e otimizações

### Como ser Reconhecido

**First-time Contributor:**
- Badge especial no primeiro PR merged
- Menção no README

**Regular Contributor:**
- Adição ao CONTRIBUTORS.md
- Acesso a discussões de roadmap

**Core Contributor:**
- Direitos de review
- Participação em decisões técnicas
- Mentor para novos contribuidores

## 📞 Comunicação

### Canais de Comunicação

**GitHub Issues:**
- Reportar bugs
- Solicitar features
- Discussões técnicas

**GitHub Discussions:**
- Dúvidas gerais
- Compartilhar ideias
- Ajuda da comunidade

**Discord (em breve):**
- Chat em tempo real
- Mentoria
- Networking

### Código de Conduta

Seguimos o [Contributor Covenant](https://www.contributor-covenant.org/):

#### Nosso Compromisso

Estamos comprometidos em tornar a participação no projeto uma experiência livre de assédio para todos, independentemente de idade, corpo, deficiência, etnia, identidade de gênero, nível de experiência, nacionalidade, aparência pessoal, raça, religião ou identidade sexual.

#### Padrões

**Comportamentos que contribuem para um ambiente positivo:**
- Usar linguagem acolhedora e inclusiva
- Respeitar diferentes pontos de vista
- Aceitar críticas construtivas
- Focar no que é melhor para a comunidade
- Mostrar empatia com outros membros

**Comportamentos inaceitáveis:**
- Linguagem ou imagens sexualizadas
- Trolling, comentários insultuosos
- Assédio público ou privado
- Publicar informações privadas sem permissão
- Outras condutas consideradas inadequadas

## 🎯 Roadmap

### Próximas Features (v1.1.0)

- [ ] Sistema de avaliações de carros
- [ ] Upload de imagens de carros
- [ ] Filtros avançados de busca
- [ ] Notificações por email
- [ ] API de favoritos

### Melhorias Técnicas

- [ ] Rate limiting com Redis
- [ ] Cache de queries frequentes
- [ ] Logs estruturados
- [ ] Métricas de performance
- [ ] Documentação interativa

### Como Influenciar o Roadmap

1. **Participar de discussões** no GitHub
2. **Votar em features** através de 👍 nas issues
3. **Propor novas ideias** com justificativa
4. **Implementar features** prioritárias

## 🚀 Começar Agora

### Issues para Iniciantes

Procure por labels:
- `good first issue` - Ideal para primeiro PR
- `help wanted` - Precisamos de ajuda
- `documentation` - Melhorar docs
- `bug` - Correções de bugs

### Primeiros Passos

1. **Escolha uma issue** marcada como `good first issue`
2. **Comente na issue** manifestando interesse
3. **Faça fork** do repositório
4. **Implemente** seguindo os guidelines
5. **Abra PR** usando o template

---

## 🙏 Agradecimentos

Obrigado por considerar contribuir com o Car API! Sua participação faz toda a diferença para o crescimento e qualidade do projeto.

Para dúvidas sobre contribuição:
- 📧 **Email**: pycodebr@gmail.com
- 🐛 **Issues**: [GitHub Issues](https://github.com/pycodebr/car_api/issues)
- 💬 **Discussions**: [GitHub Discussions](https://github.com/pycodebr/car_api/discussions)

**Juntos construímos software melhor! 🚀**