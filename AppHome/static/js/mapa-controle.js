// Função para fechar o mapa de rotas
document.addEventListener('DOMContentLoaded', function() {
  const fecharMapaBtn = document.getElementById('fecharMapaRota');
  const mapaRotaContainer = document.getElementById('mapaRotaContainer');

  if (fecharMapaBtn && mapaRotaContainer) {
    fecharMapaBtn.addEventListener('click', function() {
      console.log('Fechando o mapa de rotas...');
      
      // Esconde o container do mapa
      mapaRotaContainer.style.display = 'none';
      
      // Remove o mapa se existir
      if (window.mapInstance) {
        try {
          window.mapInstance.remove();
          window.mapInstance = null;
          console.log('Mapa removido com sucesso');
        } catch (e) {
          console.error('Erro ao remover o mapa:', e);
        }
      }
      
      // Remove o controle de rota se existir
      if (window.routingControl) {
        try {
          window.mapInstance.removeControl(window.routingControl);
          window.routingControl = null;
          console.log('Controle de rota removido com sucesso');
        } catch (e) {
          console.error('Erro ao remover o controle de rota:', e);
        }
      }
    });
  } else {
    console.warn('Elementos do mapa não encontrados');
  }
});
