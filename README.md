# MotoTec - Plataforma de Gestão para Motoboys

![MotoTec Logo](AppHome/static/imagem/logo.png)  <!-- Adicione o caminho para sua logo se tiver uma -->

O MotoTec é uma aplicação web desenvolvida para auxiliar motoboys a identificar áreas de alta demanda de entregas em tempo real, com foco em pedidos de restaurantes na região de Praia Grande.

## 🚀 Funcionalidades

- **Mapa de Calor Interativo**: Visualize as áreas com maior concentração de pedidos
- **Roteamento Inteligente**: Encontre a rota mais rápida até os pontos de entrega
- **Análise de Tendências**: Identifique os horários e bairros com maior movimento
- **Gestão de Entregas**: Acompanhe pedidos e otimize suas rotas
- **Interface Responsiva**: Acessível de qualquer dispositivo

## 🛠️ Tecnologias Utilizadas

- **Backend**: Django (Python)
- **Frontend**: HTML5, CSS3 (Tailwind), JavaScript
- **Banco de Dados**: 
  - MongoDB (dados de pedidos e restaurantes)
  - SQLite/PostgreSQL (autenticação e perfis de usuário)
- **Mapas**: Leaflet.js com plugins de roteamento e heatmap

## 📋 Pré-requisitos

- Python 3.8+
- Node.js e npm (para gerenciamento de pacotes frontend)
- MongoDB
- (Opcional) PostgreSQL

## 🚀 Instalação

1. **Clone o repositório**
   ```bash
   git clone [URL_DO_REPOSITÓRIO]
   cd MotoTec
   ```

2. **Configure o ambiente virtual**
   ```bash
   python -m venv venv
   .\venv\Scripts\activate  # No Windows
   ```

3. **Instale as dependências**
   ```bash
   pip install -r requirements.txt
   ```

4. **Configure as variáveis de ambiente**
   Crie um arquivo `.env` na raiz do projeto com:
   ```
   SECRET_KEY=sua_chave_secreta_aqui
   DEBUG=True
   MONGODB_URI=mongodb://localhost:27017/mototec
   ```

5. **Execute as migrações**
   ```bash
   python manage.py migrate
   ```

6. **Crie um superusuário**
   ```bash
   python manage.py createsuperuser
   ```

7. **Inicie o servidor de desenvolvimento**
   ```bash
   python manage.py runserver
   ```

8. **Acesse a aplicação**
   Abra seu navegador em http://127.0.0.1:8000/


## 🗺️ Estrutura do Projeto

```
MotoTec/
├── AppHome/                 # Aplicação principal
│   ├── migrations/          # Migrações do banco de dados
│   ├── static/              # Arquivos estáticos (JS, CSS, imagens)
│   ├── templates/           # Templates HTML
│   ├── __init__.py
│   ├── admin.py             # Configuração do admin
│   ├── apps.py
│   ├── forms.py             # Formulários
│   ├── models.py            # Modelos de dados
│   ├── urls.py              # URLs da aplicação
│   └── views.py             # Lógica de visualização
├── venv/                    # Ambiente virtual
├── .env                     # Variáveis de ambiente
├── .gitignore
├── manage.py                # Script de gerenciamento do Django
└── requirements.txt         # Dependências do Python
```

## 🌐 Rotas Principais

- `/` - Tela de splash inicial
- `/principal/` - Página inicial com o mapa interativo
- `/login/` - Página de login
- `/cadastro/` - Página de cadastro de usuários
- `/tendencias/` - Análise de tendências de pedidos
- `/restaurantes/` - Lista de restaurantes

## 🤝 Como Contribuir

1. Faça um Fork do projeto
2. Crie uma Branch para sua Feature (`git checkout -b feature/AmazingFeature`)
3. Adicione suas mudanças (`git add .`)
4. Comite suas mudanças (`git commit -m 'Add some AmazingFeature'`)
5. Faça o Push da Branch (`git push origin feature/AmazingFeature`)
6. Abra um Pull Request

## 📄 Licença

Este projeto está sob a licença MIT. Veja o arquivo [LICENSE](LICENSE) para mais detalhes.

## ✨ Créditos

- [Seu Nome](https://github.com/seu-usuario)

---

Desenvolvido com ❤️ para motoboys de Praia Grande - SP
