from urllib import request
import json
from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, get_user_model, update_session_auth_hash, logout
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.urls import reverse_lazy
from django.views.generic import FormView, TemplateView
from django.contrib.auth.forms import UserCreationForm, PasswordResetForm, SetPasswordForm, PasswordChangeForm
from django.http import JsonResponse, HttpResponse
from datetime import datetime, timedelta
from collections import Counter, defaultdict
from pymongo import MongoClient
from .models import Perfil
from .forms import CadastroForm, SenhaRecuperadaForm, CustomPasswordChangeForm
import os
import openai


def splash_view(request):
    return render(request, 'splash.html')


def login_view(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        
        user = authenticate(request, username=username, password=password)
        
        if user is not None:
            login(request, user)
            return redirect('home')
        else:
            messages.error(request, 'Usuário ou senha inválidos.')
    
    return render(request, 'login.html')

def cadastro_view(request):
    if request.method == 'POST':
        form = CadastroForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            return redirect('home')
    else:
        form = CadastroForm()

    return render(request, 'cadastro.html', {'form': form})


def home_view(request):
    return render(request, 'home.html')


@login_required
def tendencias_view(request):
    dia_param = request.GET.get("dia", "hoje")
    client = MongoClient("mongodb://localhost:27017")
    db = client["mototec"]
    
    if dia_param == "tendencia":
        tendencias = analisar_tendencias_locais(db)
        
        # Pré-processamento dos dados para o template
        dados_tendencias = []
        for faixa in ["Manhã", "Almoço", "Tarde", "Noite"]:
            bairros_faixa = [t for t in tendencias if t['periodo'] == faixa]
            if bairros_faixa:
                top_bairro = max(bairros_faixa, key=lambda x: x['projecao'])
                dados_tendencias.append({
                    'faixa': faixa,
                    'bairro': top_bairro['bairro'],
                    'tendencia': top_bairro['tendencia'],
                    'projecao': top_bairro['projecao']
                })
        
        return render(request, "tendencias.html", {
            "modo": "tendencia",
            "dados_tendencias": dados_tendencias,
            "referencia": "Tendência (Próxima Semana)"
        })
        
    dias_ref = {
        "hoje": 0,
        "ontem": 1,
    }
    delta = dias_ref.get(dia_param, 0)
    data_alvo = (datetime.now() - timedelta(days=delta)).date()
    data_str = data_alvo.strftime("%Y-%m-%d")

    pipeline = [
        {"$match": {
            "data_hora": {"$regex": f"^{data_str}"},
            "bairro": {"$exists": True, "$ne": ""}
        }},
        {"$addFields": {
            "data_parse": {
                "$dateFromString": {
                    "dateString": "$data_hora",
                    "format": "%Y-%m-%d %H:%M:%S"
                }
            }
        }},
        {"$addFields": {
            "hora": {"$hour": "$data_parse"}
        }},
        {"$addFields": {
            "faixa": {
                "$switch": {
                    "branches": [
                        {"case": {"$and": [{"$gte": ["$hora", 5]}, {"$lt": ["$hora", 11]}]}, "then": "Manhã"},
                        {"case": {"$and": [{"$gte": ["$hora", 11]}, {"$lt": ["$hora", 15]}]}, "then": "Almoço"},
                        {"case": {"$and": [{"$gte": ["$hora", 15]}, {"$lt": ["$hora", 18]}]}, "then": "Tarde"},
                        {"case": {"$or": [{"$gte": ["$hora", 18]}, {"$lt": ["$hora", 5]}]}, "then": "Noite"}
                    ],
                    "default": "Outro"
                }
            }
        }},
        {"$group": {
            "_id": {
                "bairro": "$bairro",
                "faixa": "$faixa"
            },
            "total": {"$sum": 1}
        }},
        {"$sort": {"total": -1}}
    ]

    resultados = list(db["pedidos"].aggregate(pipeline))

    faixas = ["Manhã", "Almoço", "Tarde", "Noite"]
    agrupados = {faixa: {} for faixa in faixas}
    for doc in resultados:
        faixa = doc["_id"]["faixa"]
        bairro = doc["_id"]["bairro"]
        total = doc["total"]
        if faixa in faixas:
            agrupados[faixa][bairro] = total

    top_bairros = []
    for faixa in faixas:
        bairros = agrupados.get(faixa, {})
        if bairros:
            bairro_top = max(bairros.items(), key=lambda x: x[1])
            top_bairros.append({
                "bairro": bairro_top[0],
                "horario": faixa,
                "pedidos": bairro_top[1],
                "dia": data_alvo.strftime("%A")
            })

    context = {
        "modo": "dia",
        "referencia": dia_param.capitalize(),
        "semana": top_bairros,
        "tendencias": [],
        "logs": []
    }
    return render(request, "tendencias.html", context)

@login_required
def restaurantes_view(request):
    client = MongoClient("mongodb://localhost:27017")
    db = client["mototec"]
    pedidos_col = db["pedidos"]
    restaurantes_col = db["restaurantes"]

    agora = datetime.now()
    hoje_str = agora.strftime("%Y-%m-%d")
    inicio_hoje = datetime.strptime(f"{hoje_str} 00:00:00", "%Y-%m-%d %H:%M:%S")
    fim_hoje = inicio_hoje + timedelta(days=1)

    pipeline = [
        {
            "$addFields": {
                "data_parse": {
                    "$dateFromString": {
                        "dateString": "$data_hora",
                        "format": "%Y-%m-%d %H:%M:%S"
                    }
                }
            }
        },
        {
            "$match": {
                "data_parse": {"$gte": inicio_hoje, "$lt": fim_hoje},
                "restaurante_id": {"$exists": True}
            }
        },
        {
            "$group": {
                "_id": "$restaurante_id",
                "count": {"$sum": 1}
            }
        },
        {
            "$sort": {"count": -1}
        },
        {
            "$limit": 3
        }
    ]

    top_ids = list(pedidos_col.aggregate(pipeline, allowDiskUse=True))

    restaurantes = []
    for doc in top_ids:
        rest_id = doc["_id"]
        count_pedidos = doc["count"]

        resta = restaurantes_col.find_one({"id": rest_id})
        if not resta:
            continue

        restaurantes.append({
            "nome": resta.get("nome", "N/D"),
            "bairro": resta.get("bairro", "N/D"),
            "latitude": resta.get("latitude", 0.0),
            "longitude": resta.get("longitude", 0.0),
            "pedidos_hoje": count_pedidos
        })

    return render(request, "lista_restaurantes.html", {
        "restaurantes": restaurantes
    })

def mapa_view(request):
    return redirect('home')

def recuperar_senha_view(request):
    if request.method == 'POST':
        form = SenhaRecuperadaForm(request.POST)
        if form.is_valid():
            cpf_cnh = form.cleaned_data['cpf_cnh']
            email = form.cleaned_data['email']
            
            perfil = Perfil.objects.get(cpf_cnh=cpf_cnh)
            user = perfil.user
            
            request.session['reset_user_id'] = user.id
            return redirect('definir_nova_senha')  
    else:
        form = SenhaRecuperadaForm()
    
    return render(request, 'recuperacao.html', {'form': form})


def definir_nova_senha_view(request):
    if 'reset_user_id' not in request.session:
        messages.error(request, 'Sessão expirada ou inválida. Por favor, tente novamente.')
        return redirect('password_reset')
    
    user_id = request.session['reset_user_id']
    user = get_user_model().objects.get(id=user_id)
    
    if request.method == 'POST':
        form = SetPasswordForm(user, request.POST)
        if form.is_valid():
            form.save()
            del request.session['reset_user_id']
            messages.success(request, 'Sua senha foi alterada com sucesso! Por favor, faça login com sua nova senha.')
            return redirect('login')
    else:
        form = SetPasswordForm(user)
    
    return render(request, 'definir_nova_senha.html', {'form': form})

def demanda_view(request):
    if not request.user.is_authenticated:
        return JsonResponse({"status": "error", "message": "Não autenticado"}, status=401)
        
    check_status = request.GET.get('check_status')
    if check_status:
        return JsonResponse({"status": "ok", "pipeline_ready": True})

    try:
        client = MongoClient("mongodb://localhost:27017")
        db = client["mototec"]
        pedidos = db["pedidos"]
        restaurantes_col = db["restaurantes"]
        
        colecoes = db.list_collection_names()
        print(f"[DEBUG] Coleções disponíveis: {colecoes}")
        
        if "pedidos" not in colecoes or "restaurantes" not in colecoes:
            msg = f"Coleções não encontradas. 'pedidos' existe: {'pedidos' in colecoes}, 'restaurantes' existe: {'restaurantes' in colecoes}"
            print(f"[ERRO] {msg}")
            return JsonResponse({
                "status": "ok", 
                "data": [],
                "message": msg
            })

        print("[DEBUG] Buscando restaurantes ativos...")
        restaurantes_ativos = list(restaurantes_col.find({"status": "Ativo"}))
        print(f"[DEBUG] Total de restaurantes ativos: {len(restaurantes_ativos)}")
        
        restaurantes_map = {}
        for r in restaurantes_ativos:
            if '_id' in r:
                restaurantes_map[str(r['_id'])] = r
            if 'id' in r and str(r['id']) not in restaurantes_map:
                restaurantes_map[str(r['id'])] = r
        
        print("[DEBUG] Executando pipeline de agregação...")
        pipeline = demanda_pipeline_para_hoje(limite=1000)
        print(f"[DEBUG] Pipeline: {json.dumps(pipeline, indent=2, default=str)}")
        
        try:
            cursor = pedidos.aggregate(pipeline, allowDiskUse=True)
            resultado = list(cursor)
            print(f"[DEBUG] Resultado da agregação: {len(resultado)} registros")
            
            for item in resultado:
                restaurante_id = str(item.get('_id', ''))
                if restaurante_id in restaurantes_map:
                    rest_info = restaurantes_map[restaurante_id]
                    item['nome'] = rest_info.get('nome', f'Restaurante {restaurante_id}')
                    item['bairro'] = rest_info.get('bairro', '')
                    
                    if 'latitude' not in item or not item['latitude']:
                        item['latitude'] = rest_info.get('latitude')
                        item['longitude'] = rest_info.get('longitude')
                else:
                    item['nome'] = f'Restaurante {restaurante_id}'
                    item['bairro'] = ''
                
                try:
                    item['latitude'] = float(item.get('latitude', 0))
                    item['longitude'] = float(item.get('longitude', 0))
                except (ValueError, TypeError):
                    item['latitude'] = 0
                    item['longitude'] = 0
            
            resultado = [r for r in resultado if r.get('latitude') and r.get('longitude')]
            print(f"[DEBUG] Total de itens com coordenadas válidas: {len(resultado)}")
            
            resultado.sort(key=lambda x: x.get('total_pedidos', 0), reverse=True)
            
            resultado = resultado[:1000]
            
            for item in resultado:
                item['restaurante_id'] = str(item.pop('_id', ''))
                item['total_pedidos'] = int(item.get('total_pedidos', 0))
            
            return JsonResponse({
                "status": "ok",
                "data": resultado,
                "pipeline_ready": True
            })
            
        except Exception as e:
            print(f"[ERRO] Erro ao executar pipeline: {str(e)}")
            import traceback
            traceback.print_exc()
            return JsonResponse({
                "status": "error",
                "message": f"Erro ao processar pedidos: {str(e)}"
            }, status=500)
            
    except Exception as e:
        print(f"[ERRO] Erro na view demanda_view: {str(e)}")
        import traceback
        traceback.print_exc()
        return JsonResponse({
            "status": "error",
            "message": f"Erro interno do servidor: {str(e)}"
        }, status=500)

        def adicionar_nome_restaurante(pedidos_list, restaurantes_map):
            if not pedidos_list:
                return []
                
            for pedido in pedidos_list:
                try:
                    if 'pedido_id' not in pedido and 'numero_pedido' in pedido:
                        pedido['pedido_id'] = pedido['numero_pedido']
                    
                    restaurante_id = pedido.get('restaurante_id')
                    if restaurante_id is None:
                        pedido['nome_restaurante'] = 'Restaurante não informado'
                        continue
                        
                    restaurante_id_str = str(restaurante_id)
                    if restaurante_id_str in restaurantes_map:
                        restaurante = restaurantes_map[restaurante_id_str]
                        pedido['nome_restaurante'] = restaurante.get('nome', f'Restaurante {restaurante_id}')
                        
                        if not pedido.get('latitude') and 'latitude' in restaurante:
                            pedido['latitude'] = float(restaurante['latitude'])
                            pedido['longitude'] = float(restaurante['longitude'])
                        
                        if not pedido.get('bairro') and 'bairro' in restaurante:
                            pedido['bairro'] = restaurante['bairro']
                    else:
                        pedido['nome_restaurante'] = f'Restaurante {restaurante_id}'
                        pedido['bairro'] = pedido.get('bairro', 'Bairro não informado')
                        
                except Exception as e:
                    pedido_id = pedido.get('pedido_id', pedido.get('numero_pedido', 'desconhecido'))
                    print(f"[ERRO] Erro ao processar pedido {pedido_id}: {str(e)}")
                    pedido['nome_restaurante'] = 'Erro ao processar'
            
            return pedidos_list
            
        try:
            hoje = datetime.now().strftime("%Y-%m-%d")
            data_inicio = f"{hoje} 00:00:00"
            data_fim = f"{hoje} 23:59:59"
            
            pipeline = [
                {
                    "$match": {
                        "data_hora": {
                            "$gte": data_inicio,
                            "$lte": data_fim
                        },
                        "restaurante_id": {"$exists": True, "$ne": None},
                        "numero_pedido": {"$exists": True, "$ne": None}
                    }
                },
                {
                    "$group": {
                        "_id": "$restaurante_id",
                        "total_pedidos": {"$sum": 1},
                        "latitude": {"$first": "$latitude"},
                        "longitude": {"$first": "$longitude"}
                    }
                },
                {"$limit": 1000}
            ]
            
            print("[DEBUG] Executando pipeline de agregação...")
            cursor = pedidos.aggregate(pipeline, allowDiskUse=True)
            restaurantes_com_pedidos = list(cursor)
            print("[DEBUG] Pipeline executada com sucesso")
            
            restaurantes_com_pedidos = adicionar_nome_restaurante(restaurantes_com_pedidos, restaurantes_map)
            
            print(f"[DEBUG] Total de pedidos após processamento: {len(restaurantes_com_pedidos)}")
            if restaurantes_com_pedidos:
                print("[DEBUG] Primeiros 3 pedidos processados:")
                for i, p in enumerate(restaurantes_com_pedidos[:3], 1):
                    print(f"[DEBUG]   {i}. Pedido: {p.get('pedido_id')}, Restaurante: {p.get('nome_restaurante', 'N/A')}")
                    print(f"[DEBUG]     Coordenadas: {p.get('latitude')}, {p.get('longitude')}")
            
            resultado = []
            for pedido in restaurantes_com_pedidos:
                try:
                    pedido['latitude'] = float(pedido.get('latitude', 0))
                    pedido['longitude'] = float(pedido.get('longitude', 0))
                    
                    # Adiciona ao resultado apenas se as coordenadas forem válidas
                    if -90 <= pedido['latitude'] <= 90 and -180 <= pedido['longitude'] <= 180:
                        resultado.append({
                            'restaurante_id': pedido.get('_id'),
                            'nome': pedido.get('nome_restaurante', 'Restaurante desconhecido'),
                            'bairro': pedido.get('bairro', 'Bairro não informado'),
                            'latitude': pedido['latitude'],
                            'longitude': pedido['longitude'],
                            'total_pedidos': pedido.get('total_pedidos', 0)
                        })
                except (ValueError, TypeError) as e:
                    print(f"[AVISO] Erro ao processar coordenadas do pedido {pedido.get('_id')}: {str(e)}")
            
            print(f"[DEBUG] Total de itens válidos para retorno: {len(resultado)}")
            
            print(f"[DEBUG] Total de pedidos encontrados: {len(restaurantes_com_pedidos)}")
            if restaurantes_com_pedidos:
                print("[DEBUG] Primeiros 3 pedidos retornados:")
                for i, p in enumerate(restaurantes_com_pedidos[:3], 1):
                    print(f"[DEBUG]   {i}. Pedido: {p.get('pedido_id', 'N/A')}, Restaurante: {p.get('nome_restaurante', 'Sem nome')}")
                    try:
                        # Tenta converter para float e depois formatar
                        valor = float(p.get('valor_total', 0) or 0)
                        print(f"[DEBUG]     Data/Hora: {p.get('data_hora_formatada', 'N/A')}, Valor: R${valor:.2f}")
                    except (ValueError, TypeError):
                        # Se falhar, mostra o valor original como string
                        print(f"[DEBUG]     Data/Hora: {p.get('data_hora_formatada', 'N/A')}, Valor: R${p.get('valor_total', '0.00')}")
                    print(f"[DEBUG]     Coordenadas: {p.get('latitude', 'N/A')}, {p.get('longitude', 'N/A')}")
            
            if not resultado:
                # Verifica se há algum problema com os dados
                exemplo_pedido = pedidos.find_one({
                    "data_hora": {"$gte": data_inicio, "$lte": data_fim},
                    "restaurante_id": {"$exists": True, "$ne": None}
                })
                
                if exemplo_pedido:
                    print(f"[DEBUG] Exemplo de pedido encontrado: {exemplo_pedido}")
                else:
                    print("[DEBUG] Nenhum pedido encontrado com os critérios de busca")
                
                return JsonResponse({
                    "status": "ok", 
                    "data": [],
                    "pipeline_ready": True,
                    "debug": {
                        "total_pedidos_periodo": total_pedidos,
                        "exemplo_pedido": str(exemplo_pedido) if exemplo_pedido else None
                    }
                })
            
            # Se chegou até aqui, temos resultados válidos
            return JsonResponse({
                "status": "ok",
                "data": resultado,
                "pipeline_ready": True
            })
                
        except Exception as e:
            print(f"[ERRO] Erro ao executar agregação: {str(e)}")
            import traceback
            traceback.print_exc()
            return JsonResponse({
                "status": "error",
                "message": f"Erro ao processar dados: {str(e)}"
            }, status=500)
        
        # 4. Retorna os dados formatados
        print(f"[DEBUG] Total de pontos de calor gerados: {len(pontos)}")
        
        return JsonResponse({
            "status": "ok", 
            "data": pontos,
            "pipeline_ready": True
        })
        
    except Exception as e:
        import traceback
        traceback.print_exc()
        return JsonResponse({
            "status": "error",
            "message": str(e)
        }, status=500)


def demanda_pipeline_para_hoje(limite=1000, pular=0):
    """
    Versão simplificada da pipeline que:
    1. Busca pedidos do dia atual
    2. Agrupa por restaurante
    3. Retorna com informações básicas para o mapa
    """
    hoje = datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)
    amanha = hoje + timedelta(days=1)
    
    # Formata as datas como strings no formato esperado
    data_inicio = hoje.strftime("%Y-%m-%d %H:%M:%S")
    data_fim = amanha.strftime("%Y-%m-%d %H:%M:%S")
    
    # Pipeline simplificada
    pipeline = [
        # 1. Filtra pedidos de hoje
        {
            "$match": {
                "data_hora": {
                    "$gte": data_inicio,
                    "$lt": data_fim
                },
                "restaurante_id": {"$exists": True, "$ne": None},
                "latitude": {"$exists": True, "$ne": None},
                "longitude": {"$exists": True, "$ne": None}
            }
        },
        # 2. Converte coordenadas para número
        {
            "$addFields": {
                "latitude": {"$toDouble": "$latitude"},
                "longitude": {"$toDouble": "$longitude"}
            }
        },
        # 3. Filtra coordenadas válidas
        {
            "$match": {
                "latitude": {"$gte": -90, "$lte": 90},
                "longitude": {"$gte": -180, "$lte": 180}
            }
        },
        # 4. Agrupa por restaurante
        {
            "$group": {
                "_id": "$restaurante_id",
                "total_pedidos": {"$sum": 1},
                "latitude": {"$first": "$latitude"},
                "longitude": {"$first": "$longitude"}
            }
        },
        # 5. Ordena por total de pedidos (decrescente)
        {"$sort": {"total_pedidos": -1}},
        # 6. Paginação
        {"$skip": pular},
        {"$limit": limite}
    ]
    
    return pipeline


def calcular_cor_intensidade(intensidade):
    # Função para calcular a cor baseada na intensidade
    # (ajuste esses valores conforme necessário)
    if intensidade < 0.3:
        return '#FF0000'  # Vermelho
    elif intensidade < 0.6:
        return '#FFFF00'  # Amarelo
    else:
        return '#00FF00'  # Verde

def pedidos_por_restaurante(request):
    from datetime import datetime, timedelta
    client = MongoClient("mongodb://localhost:27017")
    db = client["mototec"]
    pedidos = db["pedidos"]
    restaurantes_col = db["restaurantes"]

    # Calcula a data de 24 horas atrás
    data_limite = (datetime.now() - timedelta(hours=24)).strftime("%Y-%m-%d %H:%M:%S")
    
    pipeline = [
        # 1. Filtra pedidos das últimas 24 horas
        {
            "$match": {
                "data_hora": {"$gte": data_limite},
                "restaurante_id": {"$exists": True, "$ne": None},
                "latitude": {"$exists": True, "$ne": None, "$ne": ""},
                "longitude": {"$exists": True, "$ne": None, "$ne": ""}
            }
        },
        # 2. Converte coordenadas para número
        {
            "$addFields": {
                "latitude": {"$toDouble": "$latitude"},
                "longitude": {"$toDouble": "$longitude"}
            }
        },
        # 3. Filtra coordenadas válidas
        {
            "$match": {
                "latitude": {"$gte": -90, "$lte": 90},
                "longitude": {"$gte": -180, "$lte": 180}
            }
        },
        # 4. Agrupa por restaurante e conta os pedidos
        {
            "$group": {
                "_id": "$restaurante_id",
                "total_pedidos": {"$sum": 1},
                "latitude": {"$first": "$latitude"},
                "longitude": {"$first": "$longitude"}
            }
        },
        # 5. Ordena por quantidade de pedidos (decrescente)
        {"$sort": {"total_pedidos": -1}}
    ]
    
    try:
        resultado = list(pedidos.aggregate(pipeline))
        print(f"[API] Encontrados {len(resultado)} restaurantes com pedidos nas últimas 24 horas")
    except Exception as e:
        print(f"[ERRO] Ao buscar pedidos: {str(e)}")
        resultado = []

    for item in resultado:
        restaurante = restaurantes_col.find_one({"id": item["_id"]})
        if restaurante:
            item["nome"] = restaurante.get("nome", f"Restaurante {item['_id']}")
            item["bairro"] = restaurante.get("bairro", "")
        else:
            item["nome"] = f"Restaurante {item['_id']}"
            item["bairro"] = ""
        try:
            item["latitude"] = float(item.get("latitude", 0))
            item["longitude"] = float(item.get("longitude", 0))
            item["total_pedidos"] = int(item.get("total_pedidos", 0))
        except (ValueError, TypeError):
            item["latitude"] = 0
            item["longitude"] = 0
            item["total_pedidos"] = 0

    pontos = [r for r in resultado if r.get("latitude") and r.get("longitude")]
    return JsonResponse({"status": "ok", "data": pontos})

def pagina_de_teste(request):
    return render(request, 'teste.html')


def analisar_tendencias_gemini(dados):
    """
    Analisa dados de pedidos usando Google Gemini API
    Retorna análise formatada
    """
    try:
        import google.generativeai as genai
        from dotenv import load_dotenv
        import os
        
        load_dotenv()
        GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
        
        if not GEMINI_API_KEY:
            raise ValueError("Chave API do Gemini não configurada")
            
        genai.configure(api_key=GEMINI_API_KEY)
        
        model = genai.GenerativeModel('gemini-pro')
        
        prompt = f"""
        Você é um especialista em análise de dados de delivery. 
        Analise estes dados e identifique:
        - Padrões por dia da semana e horário
        - Bairros com maior crescimento
        - Sugestões para alocação de motoboys
        
        Dados:
        {dados}
        
        Retorne em formato markdown com tópicos claros.
        """
        
        response = model.generate_content(prompt)
        return response.text
        
    except Exception as e:
        print(f"Erro ao analisar com Gemini: {str(e)}")
        return "Erro ao gerar análise"

def obter_dados_tendencias(db):
    """
    Coleta dados das últimas 3 semanas para análise de tendências
    Retorna dados formatados para o Gemini
    """
    end_date = datetime.now()
    start_date = end_date - timedelta(weeks=3)
    
    pipeline = [
        {"$match": {
            "data_hora": {
                "$gte": start_date.strftime("%Y-%m-%d"),
                "$lte": end_date.strftime("%Y-%m-%d")
            },
            "bairro": {"$exists": True, "$ne": ""}
        }},
        {"$group": {
            "_id": {
                "bairro": "$bairro",
                "dia_semana": {"$dayOfWeek": {"$dateFromString": {"dateString": "$data_hora"}}},
                "faixa_horaria": {
                    "$switch": {
                        "branches": [
                            {"case": {"$and": [{"$gte": [{"$hour": {"$dateFromString": {"dateString": "$data_hora"}}}, 5]}, {"$lt": [{"$hour": {"$dateFromString": {"dateString": "$data_hora"}}}, 11]}]}, "then": "Manhã"},
                            {"case": {"$and": [{"$gte": [{"$hour": {"$dateFromString": {"dateString": "$data_hora"}}}, 11]}, {"$lt": [{"$hour": {"$dateFromString": {"dateString": "$data_hora"}}}, 14]}]}, "then": "Almoço"},
                            {"case": {"$and": [{"$gte": [{"$hour": {"$dateFromString": {"dateString": "$data_hora"}}}, 15]}, {"$lt": [{"$hour": {"$dateFromString": {"dateString": "$data_hora"}}}, 18]}]}, "then": "Tarde"},
                            {"case": {"$or": [{"$gte": [{"$hour": {"$dateFromString": {"dateString": "$data_hora"}}}, 18]}, {"$lt": [{"$hour": {"$dateFromString": {"dateString": "$data_hora"}}}, 5]}]}, "then": "Noite"}
                        ]
                    }
                }
            },
            "total": {"$sum": 1}
        }}
    ]
    
    return list(db["pedidos"].aggregate(pipeline))

def analisar_tendencias_locais(db):
    """
    Preve tendências para próxima semana baseada nas últimas 4 semanas
    Retorna: Lista de dicionários com {'bairro', 'periodo', 'tendencia', 'projecao'}
    """
    from datetime import datetime, timedelta
    
    end_date = datetime.now()
    start_date = end_date - timedelta(weeks=4)
    
    # Coleta dados históricos
    pipeline = [
        {"$match": {
            "data_hora": {
                "$gte": start_date.strftime("%Y-%m-%d"),
                "$lte": end_date.strftime("%Y-%m-%d")
            },
            "bairro": {"$exists": True, "$ne": ""}
        }},
        {"$group": {
            "_id": {
                "bairro": "$bairro",
                "dia_semana": {"$dayOfWeek": {"$dateFromString": {"dateString": "$data_hora"}}},
                "periodo": {
                    "$switch": {
                        "branches": [
                            {"case": {"$lt": [{"$hour": {"$dateFromString": {"dateString": "$data_hora"}}}, 11]}, "then": "Manhã"},
                            {"case": {"$lt": [{"$hour": {"$dateFromString": {"dateString": "$data_hora"}}}, 14]}, "then": "Almoço"},
                            {"case": {"$lt": [{"$hour": {"$dateFromString": {"dateString": "$data_hora"}}}, 18]}, "then": "Tarde"},
                            {"case": {"$gte": [{"$hour": {"$dateFromString": {"dateString": "$data_hora"}}}, 18]}, "then": "Noite"}
                        ]
                    }
                }
            },
            "total": {"$sum": 1}
        }}
    ]
    
    dados = list(db["pedidos"].aggregate(pipeline))
    
    # Calcula média por dia da semana e período
    tendencias = {}
    for item in dados:
        key = (item["_id"]["bairro"], item["_id"]["dia_semana"], item["_id"]["periodo"])
        if key not in tendencias:
            tendencias[key] = []
        tendencias[key].append(item["total"])
    
    # Prepara resultado com projeção para próxima semana
    resultado = []
    for (bairro, dia_semana, periodo), valores in tendencias.items():
        media = sum(valores) / len(valores)
        
        # Classifica a tendência
        if len(valores) >= 2:
            variacao = (valores[-1] - valores[0]) / valores[0] if valores[0] != 0 else 0
            status = "Alta" if variacao > 0.1 else "Queda" if variacao < -0.1 else "Estável"
        else:
            status = "Novo"
            
        resultado.append({
            "bairro": bairro,
            "periodo": periodo,
            "tendencia": status,
            "projecao": round(media * 1.1)  # Ajuste conservador (+10%)
        })
    
    # Ordena por bairro e período
    return sorted(resultado, key=lambda x: (x["bairro"], x["periodo"]))

from django.contrib.auth import logout
from django.contrib.auth.views import LogoutView
from django.views.generic import TemplateView
from django.shortcuts import redirect

class CustomLogoutView(TemplateView):
    template_name = 'registration/logout.html'
    
    def get(self, request, *args, **kwargs):
        if request.user.is_authenticated:
            return render(request, self.template_name)
        return redirect('home')
    
    def post(self, request, *args, **kwargs):
        logout(request)
        return redirect('home')