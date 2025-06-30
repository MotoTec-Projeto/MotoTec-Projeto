from django import forms
from .models import Perfil
from django.contrib.auth.models import User
from django.contrib.auth.forms import UserCreationForm, PasswordResetForm, SetPasswordForm, PasswordChangeForm
from django.contrib.auth import get_user_model, password_validation
from django.utils.translation import gettext_lazy as _
from django.core.exceptions import ValidationError

def __init__(self, *args, **kwargs):
    super(CadastroForm, self).__init__(*args, **kwargs)
    for field in self.fields.values():
        field.widget.attrs.update({
            'class': 'mt-1 block w-full px-4 py-2 border border-gray-300 rounded shadow-sm focus:ring-blue-500 focus:border-blue-500',
        })
    

class CadastroForm(UserCreationForm):
    email = forms.EmailField(required=True)
    cpf_cnh = forms.CharField(max_length=18, required=True)

    class Meta:
        model = User
        fields = ['username', 'email', 'password1', 'password2']

    def save(self, commit=True):
        user = super().save(commit=False)
        user.email = self.cleaned_data['email']
        # O campo CPF/CNH será salvo depois em um perfil ou model à parte
        if commit:
            user.save()
            Perfil.objects.create(user=user, cpf_cnh=self.cleaned_data['cpf_cnh']) 
        return user


class SenhaRecuperadaForm(forms.Form):
    cpf_cnh = forms.CharField(
        label=_("CPF/CNH"),
        max_length=14,
        widget=forms.TextInput(attrs={
            'class': 'form-input',
            'placeholder': 'Digite seu CPF ou CNH',
            'required': 'required',
            'data-mask': '000.000.000-00'
        })
    )
    email = forms.EmailField(
        label=_("Email"),
        max_length=254,
        widget=forms.EmailInput(attrs={
            'class': 'form-input',
            'placeholder': 'seu@email.com',
            'autocomplete': 'email',
            'required': 'required'
        })
    )
    
    def clean_cpf_cnh(self):
        cpf_cnh = self.cleaned_data.get('cpf_cnh', '').replace('.', '').replace('-', '').replace('/', '').strip()
        
        # Validação básica de CPF (11 dígitos) ou CNH (11 ou 12 dígitos)
        if not cpf_cnh.isdigit() or (len(cpf_cnh) != 11 and len(cpf_cnh) != 12):
            raise forms.ValidationError('Por favor, insira um CPF (11 dígitos) ou CNH (11 ou 12 dígitos) válido.')
            
        return cpf_cnh
        
    def clean_email(self):
        email = self.cleaned_data.get('email', '').strip().lower()
        if not email:
            raise forms.ValidationError('Este campo é obrigatório.')
        return email
    
    def clean(self):
        cleaned_data = super().clean()
        cpf_cnh = cleaned_data.get('cpf_cnh')
        email = cleaned_data.get('email')
        
        if cpf_cnh and email:
            try:
                # Remove formatação do CPF/CNH para busca
                cpf_cnh_limpo = cpf_cnh.replace('.', '').replace('-', '').replace('/', '')
                perfil = Perfil.objects.get(cpf_cnh=cpf_cnh_limpo)
                
                # Verifica se o e-mail corresponde ao usuário
                if perfil.user.email.lower() != email.lower():
                    # Mensagem genérica por segurança
                    raise forms.ValidationError({
                        'cpf_cnh': 'CPF/CNH ou e-mail inválidos.',
                        'email': 'CPF/CNH ou e-mail inválidos.'
                    })
            except Perfil.DoesNotExist:
                # Mensagem genérica por segurança
                raise forms.ValidationError({
                    'cpf_cnh': 'CPF/CNH ou e-mail inválidos.',
                    'email': 'CPF/CNH ou e-mail inválidos.'
                })
        
        return cleaned_data


class CustomPasswordChangeForm(PasswordChangeForm):
    """
    Formulário personalizado para alteração de senha com validações adicionais.
    """
    new_password1 = forms.CharField(
        label=_("Nova senha"),
        widget=forms.PasswordInput(attrs={
            'class': 'form-input',
            'placeholder': 'Digite sua nova senha',
            'autocomplete': 'new-password',
            'required': 'required'
        }),
        strip=False,
        help_text=password_validation.password_validators_help_text_html(),
    )
    new_password2 = forms.CharField(
        label=_("Confirme a nova senha"),
        widget=forms.PasswordInput(attrs={
            'class': 'form-input',
            'placeholder': 'Confirme sua nova senha',
            'autocomplete': 'new-password',
            'required': 'required'
        }),
        strip=False,
    )
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Remove o campo de senha antiga, pois não é necessário para recuperação
        self.fields.pop('old_password', None)
    
    def clean_new_password2(self):
        password1 = self.cleaned_data.get('new_password1')
        password2 = self.cleaned_data.get('new_password2')
        if password1 and password2 and password1 != password2:
            raise ValidationError(
                self.error_messages['password_mismatch'],
                code='password_mismatch',
            )
        password_validation.validate_password(password2, self.user)
        return password2
