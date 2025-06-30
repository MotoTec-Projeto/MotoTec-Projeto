document.addEventListener('DOMContentLoaded', function() {
  // Elementos do formulário
  const form = document.querySelector('form');
  const usernameInput = document.getElementById('id_username');
  const emailInput = document.getElementById('id_email');
  const password1Input = document.getElementById('id_password1');
  const password2Input = document.getElementById('id_password2');
  const cpfCnhInput = document.getElementById('id_cpf_cnh');
  const submitButton = form.querySelector('button[type="submit"]');
  
  // Criar elementos de feedback visual
  function createValidationIcon() {
    const icon = document.createElement('div');
    icon.className = 'absolute inset-y-0 right-0 pr-3 flex items-center pointer-events-none hidden';
    icon.innerHTML = `
      <svg class="h-5 w-5 text-green-500" xmlns="http://www.w3.org/2000/svg" viewBox="0 0 20 20" fill="currentColor">
        <path fill-rule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zm3.707-9.293a1 1 0 00-1.414-1.414L9 10.586 7.707 9.293a1 1 0 00-1.414 1.414l2 2a1 1 0 001.414 0l4-4z" clip-rule="evenodd" />
      </svg>
    `;
    return icon;
  }
  
  // Adicionar ícones de validação
  let usernameValidIcon = null;
  let emailValidIcon = null;
  let cpfCnhValidIcon = null;
  
  // Função para adicionar ícone de validação a um campo
  function setupValidationIcon(input, container) {
    if (!input || !container) return null;
    
    container.classList.add('relative');
    const icon = createValidationIcon();
    container.appendChild(icon);
    return container.querySelector('div');
  }
  
  // Configurar ícones de validação apenas para os campos existentes
  if (usernameInput) {
    usernameValidIcon = setupValidationIcon(usernameInput, usernameInput.parentElement);
  }
  if (emailInput) {
    emailValidIcon = setupValidationIcon(emailInput, emailInput.parentElement);
  }
  if (cpfCnhInput) {
    cpfCnhValidIcon = setupValidationIcon(cpfCnhInput, cpfCnhInput.parentElement);
  }
  
  // Função para validar CPF/CNH
  function validateCpfCnh(value) {
    const cleanValue = value.replace(/\D/g, '');
    const isValid = cleanValue.length >= 11; // Mínimo 11 dígitos para CPF
    
    if (cpfCnhValidIcon) {
      cpfCnhValidIcon.classList.toggle('hidden', !isValid);
    }
    
    if (cpfCnhInput) {
      cpfCnhInput.classList.toggle('border-red-500', !isValid && cleanValue.length > 0);
      cpfCnhInput.classList.toggle('border-green-500', isValid);
    }
    
    return isValid;
  }
  
  // Função para validar e-mail
  function validateEmail(email) {
    const re = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
    const isValid = re.test(String(email).toLowerCase());
    
    if (emailValidIcon) {
      emailValidIcon.classList.toggle('hidden', !isValid);
    }
    
    if (emailInput) {
      emailInput.classList.toggle('border-red-500', !isValid && email.length > 0);
      emailInput.classList.toggle('border-green-500', isValid);
    }
    
    return isValid;
  }
  
  // Função para validar nome de usuário
  function validateUsername(username) {
    const isValid = username.length >= 3; // Mínimo 3 caracteres
    
    if (usernameValidIcon) {
      usernameValidIcon.classList.toggle('hidden', !isValid);
    }
    
    if (usernameInput) {
      usernameInput.classList.toggle('border-red-500', !isValid && username.length > 0);
      usernameInput.classList.toggle('border-green-500', isValid);
    }
    
    return isValid;
  }
  
  // Função para validar senha
  function validatePassword(password) {
    const minLength = 8;
    const hasNumber = /[0-9]/.test(password);
    const hasSpecialChar = /[!@#$%^&*(),.?\":{}|<>\[\]\\/\-+=_~`]/.test(password);
    
    // Verifica se atende a todos os requisitos
    const isLongEnough = password.length >= minLength;
    const isValid = isLongEnough && hasNumber && hasSpecialChar;
    
    if (password1Input) {
      // Atualiza as classes de borda
      password1Input.classList.toggle('border-red-500', !isValid && password.length > 0);
      password1Input.classList.toggle('border-green-500', isValid);
      
      // Atualiza a dica para o usuário
      const hint = document.getElementById('password-strength-hint');
      if (hint) {
        hint.className = 'text-xs mt-1';
        
        if (password.length === 0) {
          hint.textContent = '';
          hint.className += ' text-gray-500';
        } else if (!isLongEnough) {
          hint.textContent = `A senha deve ter pelo menos ${minLength} caracteres`;
          hint.className += ' text-red-600';
        } else if (!hasNumber) {
          hint.textContent = 'A senha deve conter pelo menos 1 número';
          hint.className += ' text-red-600';
        } else if (!hasSpecialChar) {
          hint.textContent = 'A senha deve conter pelo menos 1 caractere especial (ex: !@#$%^&*)';
          hint.className += ' text-red-600';
        } else {
          hint.textContent = 'Senha válida!';
          hint.className += ' text-green-600';
        }
      }
    }
    
    return isValid;
  }
  
  // Função para validar confirmação de senha
  function validatePasswordConfirmation(password, confirmation) {
    const isValid = password === confirmation && password.length > 0;
    
    if (password2Input) {
      password2Input.classList.toggle('border-red-500', !isValid && confirmation.length > 0);
      password2Input.classList.toggle('border-green-500', isValid && confirmation.length > 0);
    }
    
    return isValid;
  }
  
  // Função para mostrar mensagem de erro
  function showError(input, message) {
    let errorElement = input.nextElementSibling;
    
    // Se não existir um elemento de erro, cria um
    if (!errorElement || !errorElement.classList.contains('error-message')) {
      errorElement = document.createElement('p');
      errorElement.className = 'mt-1 text-xs text-red-600 error-message';
      input.parentNode.insertBefore(errorElement, input.nextSibling);
    }
    
    errorElement.textContent = message;
    input.classList.add('border-red-500');
  }
  
  // Função para limpar mensagem de erro
  function clearError(input) {
    const errorElement = input.nextElementSibling;
    if (errorElement && errorElement.classList.contains('error-message')) {
      errorElement.remove();
    }
    input.classList.remove('border-red-500');
  }
  
  // Função para mostrar mensagem de sucesso
  function showSuccessMessage(message) {
    // Cria o elemento de mensagem de sucesso se não existir
    let successMessage = document.querySelector('.success-message');
    
    if (!successMessage) {
      successMessage = document.createElement('div');
      successMessage.className = 'mb-4 bg-green-100 border border-green-400 text-green-700 px-4 py-3 rounded relative success-message';
      
      const messageText = document.createElement('p');
      messageText.className = 'text-sm';
      successMessage.appendChild(messageText);
      
      const closeButton = document.createElement('button');
      closeButton.className = 'absolute top-0 bottom-0 right-0 px-4 py-3';
      closeButton.innerHTML = '&times;';
      closeButton.onclick = function() {
        successMessage.remove();
      };
      successMessage.appendChild(closeButton);
      
      form.insertBefore(successMessage, form.firstChild);
    }
    
    const messageText = successMessage.querySelector('p');
    messageText.textContent = message;
  }
  
  // Função para alternar visibilidade da senha
  function setupPasswordToggle(inputId, buttonId) {
    const passwordInput = document.getElementById(inputId);
    const toggleButton = document.getElementById(buttonId);
    if (passwordInput && toggleButton) {
      const svg = toggleButton.querySelector('svg');
      const path1 = svg.querySelectorAll('path')[0];
      const path2 = svg.querySelectorAll('path')[1];
      toggleButton.addEventListener('click', function () {
        const isPassword = passwordInput.getAttribute('type') === 'password';
        passwordInput.setAttribute('type', isPassword ? 'text' : 'password');
        if (isPassword) {
          // Olho cortado (ocultando)
          path1.setAttribute('d', 'M13.875 18.825A10.05 10.05 0 0112 19c-4.478 0-8.268-2.943-9.543-7a9.97 9.97 0 011.563-3.029m5.858.908a3 3 0 114.243 4.243M9.878 9.878l4.242 4.242M3 3l3.59 3.59');
          path2.setAttribute('d', '');
        } else {
          // Olho aberto (mostrando)
          path1.setAttribute('d', 'M10 12a2 2 0 100-4 2 2 0 000 4z');
          path2.setAttribute('d', 'M.458 10C1.732 5.943 5.522 3 10 3s8.268 2.943 9.542 7c-1.274 4.057-5.064 7-9.542 7S1.732 14.057.458 10zM14 10a4 4 0 11-8 0 4 4 0 018 0z');
        }
      });
    }
  }

  // Configurar toggles de senha apenas se os elementos existirem
  if (document.getElementById('id_password1') && document.getElementById('togglePassword1')) {
    setupPasswordToggle('id_password1', 'togglePassword1');
  }
  if (document.getElementById('id_password2') && document.getElementById('togglePassword2')) {
    setupPasswordToggle('id_password2', 'togglePassword2');
  }

  // Adicionar máscara para CPF/CNH
  if (cpfCnhInput) {
    cpfCnhInput.addEventListener('input', function(e) {
      let value = e.target.value.replace(/\D/g, '');
      
      // Formatação para CPF (11 dígitos) ou CNH (11+ dígitos)
      if (value.length <= 11) {
        // Formato CPF: 000.000.000-00
        value = value.replace(/(\d{3})(\d)/, '$1.$2');
        value = value.replace(/(\d{3})(\d)/, '$1.$2');
        value = value.replace(/(\d{3})(\d{1,2})$/, '$1-$2');
      } else {
        // Formato CNH: 000000000-00 (sem pontos, apenas hífen)
        value = value.replace(/^(\d{11})(\d{0,2})$/, '$1-$2');
      }
      
      e.target.value = value;
      validateCpfCnh(value);
    });
  }
  
  // Validação em tempo real para nome de usuário
  if (usernameInput) {
    usernameInput.addEventListener('input', function(e) {
      const value = e.target.value.trim();
      if (value.length > 0) {
        validateUsername(value);
        clearError(usernameInput);
      } else {
        if (usernameValidIcon) usernameValidIcon.classList.add('hidden');
        usernameInput.classList.remove('border-green-500', 'border-red-500');
      }
    });
  }
  
  // Validação em tempo real para e-mail
  if (emailInput) {
    emailInput.addEventListener('input', function(e) {
      const value = e.target.value.trim();
      if (value.length > 0) {
        validateEmail(value);
        clearError(emailInput);
      } else {
        if (emailValidIcon) emailValidIcon.classList.add('hidden');
        emailInput.classList.remove('border-green-500', 'border-red-500');
      }
    });
  }
  
  // Validação em tempo real para senha
  if (password1Input) {
    password1Input.addEventListener('input', function(e) {
      const value = e.target.value;
      if (value.length > 0) {
        validatePassword(value);
        clearError(password1Input);
        // Atualiza a validação da confirmação de senha também
        if (password2Input.value.length > 0) {
          validatePasswordConfirmation(value, password2Input.value);
        }
      } else {
        password1Input.classList.remove('border-green-500', 'border-red-500');
      }
    });
  }
  
  // Validação em tempo real para confirmação de senha
  if (password2Input) {
    password2Input.addEventListener('input', function(e) {
      const value = e.target.value;
      if (value.length > 0 && password1Input.value.length > 0) {
        validatePasswordConfirmation(password1Input.value, value);
        clearError(password2Input);
      } else {
        password2Input.classList.remove('border-green-500', 'border-red-500');
      }
    });
  }
  
  // Validação ao enviar o formulário
  if (form) {
    form.addEventListener('submit', function(e) {
      e.preventDefault();
      
      const username = usernameInput ? usernameInput.value.trim() : '';
      const email = emailInput ? emailInput.value.trim() : '';
      const password1 = password1Input ? password1Input.value : '';
      const password2 = password2Input ? password2Input.value : '';
      const cpfCnh = cpfCnhInput ? cpfCnhInput.value.replace(/\D/g, '') : '';
      
      let isValid = true;
      
      // Validar nome de usuário
      if (!username) {
        showError(usernameInput, 'Por favor, informe um nome de usuário.');
        isValid = false;
      } else if (username.length < 3) {
        showError(usernameInput, 'O nome de usuário deve ter pelo menos 3 caracteres.');
        isValid = false;
      }
      
      // Validar e-mail
      if (!email) {
        showError(emailInput, 'Por favor, informe um endereço de e-mail.');
        isValid = false;
      } else if (!validateEmail(email)) {
        showError(emailInput, 'Por favor, informe um endereço de e-mail válido.');
        isValid = false;
      }
      
      // Validar senha
      if (!password1) {
        showError(password1Input, 'Por favor, informe uma senha.');
        isValid = false;
      } else if (!validatePassword(password1)) {
        showError(password1Input, 'A senha deve ter pelo menos 8 caracteres, incluindo letras maiúsculas, minúsculas, números e caracteres especiais.');
        isValid = false;
      }
      
      // Validar confirmação de senha
      if (!password2) {
        showError(password2Input, 'Por favor, confirme sua senha.');
        isValid = false;
      } else if (password1 !== password2) {
        showError(password2Input, 'As senhas não conferem.');
        isValid = false;
      }
      
      // Validar CPF/CNH
      if (!cpfCnh) {
        showError(cpfCnhInput, 'Por favor, informe um CPF ou CNH.');
        isValid = false;
      } else if (!validateCpfCnh(cpfCnhInput.value)) {
        showError(cpfCnhInput, 'Por favor, informe um CPF ou CNH válido.');
        isValid = false;
      }
      
      // Se todos os campos forem válidos, envia o formulário
      if (isValid) {
        // Desabilita o botão e mostra o spinner
        const buttonText = submitButton.querySelector('span');
        const spinner = document.createElement('div');
        spinner.className = 'loading-spinner ml-2';
        
        submitButton.disabled = true;
        if (buttonText) {
          buttonText.textContent = 'Criando conta...';
        } else {
          submitButton.textContent = 'Criando conta...';
        }
        submitButton.appendChild(spinner);
        
        // Envia o formulário via AJAX
        const formData = new FormData(form);
        
        // Mostra mensagem de carregamento
        const loadingMessage = document.createElement('div');
        loadingMessage.className = 'mb-4 bg-blue-100 border border-blue-400 text-blue-700 px-4 py-3 rounded';
        loadingMessage.textContent = 'Enviando dados...';
        form.prepend(loadingMessage);
        
        // Configuração do fetch com timeout
        const controller = new AbortController();
        const timeoutId = setTimeout(() => controller.abort(), 30000); // 30 segundos de timeout
        
        fetch(form.action, {
          method: 'POST',
          body: formData,
          headers: {
            'X-Requested-With': 'XMLHttpRequest',
            'X-CSRFToken': form.querySelector('[name=csrfmiddlewaretoken]').value
          },
          signal: controller.signal
        })
        .then(response => {
          clearTimeout(timeoutId);
          loadingMessage.remove();
          
          if (!response.ok) {
            return response.text().then(text => {
              try {
                const data = JSON.parse(text);
                return Promise.reject(new Error(data.message || 'Erro no servidor'));
              } catch {
                return Promise.reject(new Error(`Erro ${response.status}: ${response.statusText}`));
              }
            });
  }
}, 2000);
                window.location.href = data.redirect_url;
              } else {
                window.location.href = '/';
              }
            }, 2000);
          } else {
            // Mostra erros do servidor
            if (data.errors) {
              Object.keys(data.errors).forEach(field => {
                const input = document.getElementById(`id_${field}`);
                if (input) {
                  showError(input, data.errors[field]);
                } else {
                  // Se não encontrar o campo específico, mostra os erros gerais
                  showError(form, data.errors[field]);
                }
              });
            } else {
              showError(form, data.message || 'Ocorreu um erro ao processar seu cadastro. Por favor, tente novamente.');
            }
            
            // Rola até o primeiro erro
            const firstError = form.querySelector('.border-red-500');
            if (firstError) {
              firstError.scrollIntoView({ behavior: 'smooth', block: 'center' });
            }
          }
        })
        .catch(error => {
          console.error('Erro ao enviar formulário:', error);
          
          // Remove mensagens de carregamento antigas
          const loadingMessages = document.querySelectorAll('.bg-blue-100');
          loadingMessages.forEach(msg => msg.remove());
          
          // Mostra mensagem de erro específica
          let errorMessage = 'Erro ao enviar o formulário. ';
          
          if (error.name === 'AbortError') {
            errorMessage += 'Tempo de conexão esgotado. Verifique sua internet e tente novamente.';
          } else if (error.message.includes('Failed to fetch')) {
            errorMessage = 'Não foi possível conectar ao servidor. Verifique sua conexão com a internet e tente novamente.';
          } else {
            errorMessage += error.message || 'Tente novamente mais tarde.';
          }
          
          showError(form, errorMessage);
          
          // Rola até o topo para mostrar a mensagem de erro
          window.scrollTo({ top: 0, behavior: 'smooth' });
        })
        .finally(() => {
          // Reativa o botão e remove o spinner
          submitButton.disabled = false;
          const spinner = submitButton.querySelector('.loading-spinner');
          if (spinner) spinner.remove();
          
          if (buttonText) {
            buttonText.textContent = 'Criar conta';
          } else {
            submitButton.textContent = 'Criar conta';
          }
        });
      
      return false;
