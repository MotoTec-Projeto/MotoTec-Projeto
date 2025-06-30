/**
 * Função principal que é executada quando o DOM estiver totalmente carregado
 */
document.addEventListener('DOMContentLoaded', function() {
  // Elementos do formulário
  const form = document.getElementById('passwordResetForm');
  if (!form) return; // Sai se o formulário não existir

  // Elementos de entrada
  const emailInput = document.getElementById('id_email');
  const cpfInput = document.getElementById('id_cpf_cnh');
  const submitButton = document.getElementById('submitButton');
  const buttonText = document.querySelector('.button-text');
  const loadingSpinner = document.getElementById('loading-spinner');
  const cpfValidIcon = document.getElementById('cpf-valid-icon');
  const emailValidIcon = document.getElementById('email-valid-icon');

  /**
   * Valida o formato do CPF/CNH
   * @param {string} value - Valor do campo CPF/CNH
   * @returns {boolean} Retorna true se o formato for válido
   */
  function validateCpfCnh(value) {
    const cleanValue = value.replace(/\D/g, '');
    const isValid = cleanValue.length >= 11; // Mínimo 11 dígitos para CPF
    
    // Atualiza o ícone de validação
    if (cpfValidIcon) {
      cpfValidIcon.classList.toggle('hidden', !isValid);
    }
    
    // Atualiza as classes de estilo do campo
    if (cpfInput) {
      if (isValid) {
        cpfInput.classList.remove('border-red-500', 'focus:ring-red-500');
        cpfInput.classList.add('border-green-500', 'focus:ring-green-500');
      } else if (value.trim() !== '') {
        cpfInput.classList.add('border-red-500', 'focus:ring-red-500');
        cpfInput.classList.remove('border-green-500', 'focus:ring-green-500');
      } else {
        cpfInput.classList.remove('border-red-500', 'focus:ring-red-500', 'border-green-500', 'focus:ring-green-500');
      }
    }
    
    return isValid;
  }
  
  /**
   * Valida o formato do e-mail
   * @param {string} email - Endereço de e-mail a ser validado
   * @returns {boolean} Retorna true se o formato for válido
   */
  function validateEmail(email) {
    const re = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
    const isValid = re.test(String(email).toLowerCase());
    
    // Atualiza o ícone de validação
    if (emailValidIcon) {
      emailValidIcon.classList.toggle('hidden', !isValid);
    }
    
    // Atualiza as classes de estilo do campo
    if (emailInput) {
      if (isValid) {
        emailInput.classList.remove('border-red-500', 'focus:ring-red-500');
        emailInput.classList.add('border-green-500', 'focus:ring-green-500');
      } else if (email.trim() !== '') {
        emailInput.classList.add('border-red-500', 'focus:ring-red-500');
        emailInput.classList.remove('border-green-500', 'focus:ring-green-500');
      } else {
        emailInput.classList.remove('border-red-500', 'focus:ring-red-500', 'border-green-500', 'focus:ring-green-500');
      }
    }
    
    return isValid;
  }
  
  /**
   * Exibe uma mensagem de erro acima do formulário
   * @param {string} message - Mensagem de erro a ser exibida
   */
  function showError(message) {
    // Remove mensagens de erro existentes
    const existingError = document.querySelector('.error-message');
    if (existingError) {
      existingError.remove();
    }
    
    // Cria a mensagem de erro
    const errorDiv = document.createElement('div');
    errorDiv.className = 'error-message bg-red-50 border-l-4 border-red-500 p-4 mb-6';
    errorDiv.innerHTML = `
      <div class="flex">
        <div class="flex-shrink-0">
          <svg class="h-5 w-5 text-red-500" xmlns="http://www.w3.org/2000/svg" viewBox="0 0 20 20" fill="currentColor">
            <path fill-rule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zM8.707 7.293a1 1 0 00-1.414 1.414L8.586 10l-1.293 1.293a1 1 0 101.414 1.414L10 11.414l1.293 1.293a1 1 0 001.414-1.414L11.414 10l1.293-1.293a1 1 0 00-1.414-1.414L10 8.586 8.707 7.293z" clip-rule="evenodd" />
          </svg>
        </div>
        <div class="ml-3">
          <p class="text-sm text-red-700">${message}</p>
        </div>
      </div>
    `;
    
    // Insere a mensagem de erro no início do formulário
    const formHeader = form.querySelector('div.text-center');
    if (formHeader && formHeader.nextElementSibling) {
      formHeader.parentNode.insertBefore(errorDiv, formHeader.nextElementSibling);
    } else {
      form.prepend(errorDiv);
    }
    
    // Rola a página para o topo do formulário
    window.scrollTo({
      top: 0,
      behavior: 'smooth'
    });
  }
  
  // Adiciona máscara ao campo CPF/CNH
  if (cpfInput) {
    cpfInput.addEventListener('input', function(e) {
      let value = e.target.value.replace(/\D/g, '');
      
      // Limita o tamanho máximo (14 para CPF, 20 para CNH)
      if (value.length > 14) {
        value = value.substring(0, 14);
      }
      
      // Aplica a formatação
      if (value.length > 11) {
        // Formato CNPJ: 00.000.000/0000-00
        value = value.replace(/(\d{2})(\d{3})(\d{3})(\d{4})(\d{0,2})/, '$1.$2.$3/$4-$5');
      } else if (value.length > 9) {
        // Formato CPF: 000.000.000-00
        value = value.replace(/(\d{3})(\d{3})(\d{3})(\d{0,2})/, '$1.$2.$3-$4');
      } else if (value.length > 6) {
        value = value.replace(/(\d{3})(\d{3})(\d{0,3})/, '$1.$2.$3');
      } else if (value.length > 3) {
        value = value.replace(/(\d{3})(\d{0,3})/, '$1.$2');
      }
      
      e.target.value = value;
      validateCpfCnh(value);
    });
  }
  
  // Validação de e-mail em tempo real
  if (emailInput) {
    emailInput.addEventListener('input', function(e) {
      validateEmail(e.target.value);
    });
  }
  
  // Evento de envio do formulário
  form.addEventListener('submit', async function(e) {
    e.preventDefault();
    
    // Valida os campos antes de enviar
    const isCpfValid = cpfInput ? validateCpfCnh(cpfInput.value) : true;
    const isEmailValid = emailInput ? validateEmail(emailInput.value) : true;
    
    if (isCpfValid && isEmailValid) {
      // Mostra o spinner e desabilita o botão
      if (buttonText) buttonText.textContent = 'Enviando...';
      if (loadingSpinner) loadingSpinner.classList.remove('hidden');
      if (submitButton) submitButton.disabled = true;
      
      try {
        const formData = new FormData(form);
        const response = await fetch(form.getAttribute('data-ajax-url') || form.action, {
          method: 'POST',
          body: formData,
          headers: {
            'X-Requested-With': 'XMLHttpRequest',
            'X-CSRFToken': document.querySelector('[name=csrfmiddlewaretoken]').value
          },
          credentials: 'same-origin'
        });
        
        const result = await response.json();
        
        if (response.ok && result.success) {
          // Redireciona para a página de confirmação
          window.location.href = result.redirect_url || '{% url "password_reset_done" %}';
        } else {
          // Exibe mensagem de erro
          showError(result.error || 'Ocorreu um erro ao processar sua solicitação. Tente novamente.');
        }
      } catch (error) {
        console.error('Erro:', error);
        showError('Ocorreu um erro ao processar sua solicitação. Tente novamente.');
      } finally {
        // Restaura o botão
        if (buttonText) buttonText.textContent = 'Enviar Instruções';
        if (loadingSpinner) loadingSpinner.classList.add('hidden');
        if (submitButton) submitButton.disabled = false;
      }
    } else {
      showError('Por favor, preencha todos os campos corretamente.');
    }
  });
});
